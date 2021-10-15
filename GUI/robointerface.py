import serial
from PyQt5 import QtWidgets, QtCore


class RoboInterface(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(RoboInterface, self).__init__(*args, **kwargs)

        self.instexe: QtCore.QThread = None  # instruction executor object
        self.current_instruction_index = -1
        self.instructions = []
        self.com = "COM1"
        self.baud = 9600

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QtWidgets.QVBoxLayout())

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)

        self.controller_frame = QtWidgets.QFrame()
        self.animate_frame = QtWidgets.QFrame()

        self.controller_layout = QtWidgets.QFormLayout()
        self.controller_layout.setSpacing(50)
        self.controller_frame.setLayout(self.controller_layout)

        self.animate_layout = QtWidgets.QGridLayout()
        self.animate_frame.setLayout(self.animate_layout)

        self.splitter.addWidget(self.controller_frame)
        self.splitter.addWidget(self.animate_frame)

        self.layout().addWidget(self.splitter)

        self.initController()
        self.initAnimator()

    def initController(self):

        self.com_port = QtWidgets.QSpinBox()
        self.com_port.setRange(1, 10)
        self.baud_rate = QtWidgets.QComboBox()
        self.baud_rate.addItems(["300", "1200", "9600", "19200", "38400", "57600"])

        self.start_connection_btn = QtWidgets.QPushButton(text="Start connection")
        self.start_connection_btn.clicked.connect(self.connectDevice)

        self.connection_status_lbl = QtWidgets.QLabel()
        self.connection_status_lbl.setWordWrap(True)

        self.servo1_spin = QtWidgets.QSpinBox()
        self.servo2_spin = QtWidgets.QSpinBox()

        self.servo1_spin.setRange(-90, 90) # servo 1 range
        self.servo2_spin.setRange(120, 180)

        self.servo1_spin.valueChanged.connect(self.controllerInstruction)
        self.servo2_spin.valueChanged.connect(self.controllerInstruction)

        self.base_controller = QtWidgets.QDial()
        self.base_controller.valueChanged.connect(self.controllerInstruction)
        self.dial_lbl = QtWidgets.QLabel(text="0")

        self.base_controller.valueChanged.connect(lambda val: self.dial_lbl.setText(str(val)))
        self.base_controller.setRange(-180, 180)

        self.controller_layout.addWidget(QtWidgets.QLabel("Controller", alignment=QtCore.Qt.AlignCenter))

        self.controller_layout.addRow("Enter COM port", self.com_port)
        self.controller_layout.addRow("Enter baud rate (eg: 38400)",
                                      self.baud_rate)  # baud rate of both bluetooth and this must be same

        self.controller_layout.addWidget(self.connection_status_lbl)
        self.controller_layout.addWidget(self.start_connection_btn)

        self.controller_layout.addRow("Servo1", self.servo1_spin)
        self.controller_layout.addRow("Servo2", self.servo2_spin)
        self.controller_layout.addWidget(QtWidgets.QLabel("Base controller", alignment=QtCore.Qt.AlignCenter))
        self.controller_layout.addRow(self.dial_lbl, self.base_controller)

    def initAnimator(self):

        self.scroll_area = QtWidgets.QScrollArea()
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_bar.rangeChanged.connect(lambda: scroll_bar.setValue(scroll_bar.maximum()))

        widget = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(widget)

        self.scroll_area.setWidget(widget)
        self.scroll_area.setWidgetResizable(True)

        self.servo_combo = QtWidgets.QComboBox()
        self.servo_combo.setEditable(False)
        self.servo_combo.addItems(["Base controller", "Servo1", "Servo2", "delay"])
        self.servo_combo.currentTextChanged.connect(self.changeSpinRange)

        self.angle_spin = QtWidgets.QSpinBox()
        self.add_btn = QtWidgets.QPushButton(text="Add", clicked=self.addkey)

        self.start_stop_btn = QtWidgets.QPushButton(text='Start')
        self.start_stop_btn.setCheckable(True)
        self.start_stop_btn.clicked.connect(self.animatorInstruction)

        self.save_btn = QtWidgets.QPushButton(text="Save", clicked=self.save)
        self.load_btn = QtWidgets.QPushButton(text="load", clicked=self.load)

        self.animate_layout.addWidget(QtWidgets.QLabel("Animator", alignment=QtCore.Qt.AlignCenter), 0, 0, 1, 3)

        self.animate_layout.addWidget(self.load_btn, 1, 0)
        self.animate_layout.addWidget(self.save_btn, 1, 1)
        self.animate_layout.addWidget(self.start_stop_btn, 1, 2)
        self.animate_layout.addWidget(self.scroll_area, 2, 0, 1, 3)

        self.animate_layout.addWidget(self.servo_combo, 3, 0)
        self.animate_layout.addWidget(self.angle_spin, 3, 1)
        self.animate_layout.addWidget(self.add_btn, 3, 2)

    def addkey(self):
        component = self.servo_combo.currentText()
        value = self.angle_spin.text()

        self.addInstruction(component, value)

    def addInstruction(self, component, value):
        self.scroll_layout.addWidget(SequenceLabel(f"{component}: {value}", objectName="instruction"))

    def changeSpinRange(self, text):

        if text == "Base controller":
            self.angle_spin.setRange(-180, 180)

        elif text == "Servo1":
            self.angle_spin.setRange(-90, 90)

        elif text == "Servo2":
            self.angle_spin.setRange(120, 180)

        elif text == "delay":
            self.angle_spin.setRange(1, 18000)

    def connectDevice(self):

        self.com = f"COM{self.com_port.text()}"
        self.baud = int(self.baud_rate.currentText())
        self.startExecutor()

    def startExecutor(self):

        if self.instexe:
            self.instexe.requestInterruption()

        self.instexe = InstructionsExecutor(self.com, self.baud)
        self.instexe.start()
        self.instexe.connectionStatus.connect(self.changeConnectionStatus)

    def changeConnectionStatus(self, text: str):
        self.connection_status_lbl.setText(text)

        if text == "connection success":
            self.start_connection_btn.setText("Stop connection")
        
        else:
            self.start_connection_btn.setText("Start connection")

    def controllerInstruction(self, val):

        if not self.instexe:
            return

        if self.sender() == self.servo1_spin:
            ins = "S1"

        elif self.sender() == self.servo2_spin:
            ins = "S2"

        elif self.sender() == self.base_controller:
            ins = "B1"

        else:
            print(self.sender(), val)

        ins = f"{ins}:{val}"

        self.instexe.setInstruction(ins)

    def updateInstruction(self):

        if self.current_instruction_index >= 0:
            self.instructions[self.current_instruction_index].setStyleSheet(self.styleSheet())

        self.current_instruction_index += 1

        if self.current_instruction_index == len(self.instructions):
            self.current_instruction_index = 0

        instruction_widget = self.instructions[self.current_instruction_index]
        instruction_widget.setStyleSheet("QFrame{border: 2px solid #f5c518; color: #ede4e4;} QLabel{border:none; font-size: 16px;}")

        inst, val = instruction_widget.getInstruction().split(":")

        ins = ""
        if inst == "Servo1":
            ins = "S1"

        elif inst == "Servo2":
            ins = "S2"

        elif inst == "delay":
            ins = "delay"

        elif inst == "Base controller":
            ins = "B1"

        self.instexe.setInstruction(f"{ins}:{val.strip()}")

    def animatorInstruction(self, checked):

        if not any(self.getInstructions()):
            self.start_stop_btn.setChecked(not checked)
            return

        if checked:
            self.connectDevice()
            self.scroll_area.widget().setDisabled(True)
            self.add_btn.setDisabled(True)
            self.load_btn.setDisabled(True)
            self.controller_frame.setDisabled(True)
            self.instructions = [self.scroll_layout.itemAt(i).widget() for i in range(self.scroll_layout.count())]
            self.start_stop_btn.setText("Stop")
            self.instexe.completedInstruction.connect(self.updateInstruction)
            self.updateInstruction()

        else:

            if self.instexe:
                self.instexe.requestInterruption()

            self.scroll_area.widget().setDisabled(False)
            self.add_btn.setDisabled(False)
            self.load_btn.setDisabled(False)
            self.controller_frame.setDisabled(False)
            self.instexe.completedInstruction.disconnect(self.updateInstruction)
            self.start_stop_btn.setText("Start")
            self.instructions[self.current_instruction_index].setStyleSheet(self.styleSheet())
            self.current_instruction_index = -1

    def getInstructions(self):
        return [self.scroll_layout.itemAt(i).widget().getInstruction() for i in range(self.scroll_layout.count())]

    def clear(self):

        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def save(self):

        file_name, file_type = QtWidgets.QFileDialog.getSaveFileName(self, "Select save folder", filter="txt")

        if not file_name:
            return

        instructions = self.getInstructions()

        with open(f"{file_name}.{file_type}", "w") as f_obj:
            for ins in instructions:
                f_obj.write(ins)
                f_obj.write("\n")

    def load(self):

        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select open file", filter="txt(*.txt)")

        if not file:
            return

        self.clear()

        with open(file, "r") as f_obj:
            instructions = f_obj.readlines()

        for ins in instructions:
            inst, value = ins.split(":")
            self.addInstruction(inst, int(value.strip()))


class InstructionsExecutor(QtCore.QThread):
    completedInstruction = QtCore.pyqtSignal(bool)  # sent when instruction execution is complete
    connectionStatus = QtCore.pyqtSignal(str)

    def __init__(self, com, baud=9000, *args, **kwargs):
        super(InstructionsExecutor, self).__init__(*args, **kwargs)
        self.com = com
        self.baud = baud
        self.instruction = ""
        self.serial_port = None

        print(repr(com), baud, repr(baud))

    def run(self) -> None:
        print("STARTING INSTRUCTION....")
        self.connectionStatus.emit("Connecting...")

        try:
            self.serial_port = serial.Serial(self.com, self.baud, timeout=2)
            self.connectionStatus.emit("connection success")

        except serial.serialutil.SerialException as e:
            self.connectionStatus.emit(str(e))
            return

        while not self.isInterruptionRequested():  # run until interrupt request becomes False
            print("Instruction", repr(self.instruction))

            if "delay" in self.instruction:
                ins, val = self.instruction.split(":")
                self.msleep(int(val))
                self.completedInstruction.emit(True)
                continue

            if self.instruction:

                self.serial_port.write(bytes(self.instruction, "utf-8"))
                self.instruction = ""  # reset instruction else it will run the same instruction again and again

            read = self.serial_port.readline()
            print("read: ", read)
            if read and read == b"Done":
                self.completedInstruction.emit(True)
                print("Completed")

        self.serial_port.close()
        self.connectionStatus.emit("Disconnected")

    def setInstruction(self, instruction):
        self.instruction = instruction


class SequenceLabel(QtWidgets.QWidget):

    def __init__(self, text: str, *args, **kwargs):
        super(SequenceLabel, self).__init__(*args, **kwargs)

        self.setMaximumHeight(100)
        self.setLayout(QtWidgets.QVBoxLayout())

        frame = QtWidgets.QFrame()
        h_box = QtWidgets.QHBoxLayout(frame)

        self.sequence_lbl = QtWidgets.QLabel(text=text)
        self.sequence_lbl.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.delete_btn = QtWidgets.QPushButton(text="X")
        self.delete_btn.clicked.connect(self.deleteLater)
        self.delete_btn.setMaximumWidth(35)

        h_box.addWidget(self.sequence_lbl)
        h_box.addWidget(self.delete_btn)
        self.layout().addWidget(frame)

    def setText(self, text: str):
        self.sequence_lbl.setText(text)

    def getInstruction(self):
        return self.sequence_lbl.text()
