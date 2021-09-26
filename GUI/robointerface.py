import serial
from PyQt5 import QtWidgets, QtCore


class RoboInterface(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(RoboInterface, self).__init__(*args, **kwargs)

        self.instructions:  QtCore.QThread = None

        self.setLayout(QtWidgets.QVBoxLayout())

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

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
        self.servo3_spin = QtWidgets.QSpinBox()

        self.servo1_spin.setRange(0, 180)
        self.servo2_spin.setRange(0, 180)
        self.servo3_spin.setRange(0, 180)

        self.servo1_spin.valueChanged.connect(self.sendInstruction)
        self.servo2_spin.valueChanged.connect(self.sendInstruction)
        self.servo3_spin.valueChanged.connect(self.sendInstruction)

        self.base_controller = QtWidgets.QDial()
        self.base_controller.valueChanged.connect(self.sendInstruction)
        self.dial_lbl = QtWidgets.QLabel(text="0")

        self.base_controller.valueChanged.connect(lambda val: self.dial_lbl.setText(str(val)))
        self.base_controller.setRange(0, 360)

        self.controller_layout.addWidget(QtWidgets.QLabel("Controller", alignment=QtCore.Qt.AlignCenter))

        self.controller_layout.addRow("Enter COM port", self.com_port)
        self.controller_layout.addRow("Enter baud rate (eg: 38400)",
                                      self.baud_rate)  # baud rate of both bluetooth and this must be same

        self.controller_layout.addWidget(self.connection_status_lbl)
        self.controller_layout.addWidget(self.start_connection_btn)

        self.controller_layout.addRow("Servo1", self.servo1_spin)
        self.controller_layout.addRow("Servo2", self.servo2_spin)
        self.controller_layout.addRow("Servo3", self.servo3_spin)
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
        self.servo_combo.addItems(["Base controller", "Servo1", "Servo2", "Servo3", "delay"])
        self.servo_combo.currentTextChanged.connect(self.changeSpinRange)

        self.angle_spin = QtWidgets.QSpinBox()
        self.add_btn = QtWidgets.QPushButton(text="Add", clicked=self.addkey)

        self.start_stop_btn = QtWidgets.QPushButton(text='start/Stop')

        self.animate_layout.addWidget(QtWidgets.QLabel("Animator", alignment=QtCore.Qt.AlignCenter), 0, 0, 1, 3)
        self.animate_layout.addWidget(self.start_stop_btn, 1, 2)
        self.animate_layout.addWidget(self.scroll_area, 2, 0, 1, 3)

        self.animate_layout.addWidget(self.servo_combo, 3, 0)
        self.animate_layout.addWidget(self.angle_spin, 3, 1)
        self.animate_layout.addWidget(self.add_btn, 3, 2)

    def addkey(self):
        component = self.servo_combo.currentText()
        value = self.angle_spin.text()
        self.scroll_layout.addWidget(SequenceLabel(f"{component}: {value}"))

    def changeSpinRange(self, text):

        if text == "Base controller":
            self.angle_spin.setRange(0, 360)

        elif text in ["Servo1", "Servo2", "Servo3"]:
            self.angle_spin.setRange(0, 180)

        elif text == "delay":
            self.angle_spin.setRange(1, 18000)

    def connectDevice(self):

        com = f"COM{self.com_port.text()}"
        baud = int(self.baud_rate.currentText())

        if self.instructions:
            self.instructions.requestInterruption()

        self.instructions = Instructions(com, baud)
        self.instructions.start()
        self.instructions.connectionStatus.connect(self.connection_status_lbl.setText)

    def sendInstruction(self, val):
        if not self.instructions:
            return
        print(self.sender(), val)
        self.instructions.setInstruction(val)


class Instructions(QtCore.QThread):
    completedInstruction = QtCore.pyqtSignal(bool)
    connectionStatus = QtCore.pyqtSignal(str)

    def __init__(self, com, baud=9000, *args, **kwargs):
        super(Instructions, self).__init__(*args, **kwargs)
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

        print(self.isInterruptionRequested())
        while not self.isInterruptionRequested():  # run until interrupt request becomes False

            if self.instruction:
                self.serial_port.write(bytes(self.instruction, "utf-8"))

            read = self.serial_port.readline()

            if read and read.decode("utf-8") == "done":
                self.completedInstruction.emit(True)

            self.instruction = ""  # reset instruction else it will run the same instruction again and again

        self.serial_port.close()

    def setInstruction(self, instruction):
        self.instruction = instruction


class SequenceLabel(QtWidgets.QWidget):

    def __init__(self, text: str, *args, **kwargs):
        super(SequenceLabel, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QHBoxLayout())

        self.sequence_lbl = QtWidgets.QLabel(text=text)
        self.delete_btn = QtWidgets.QPushButton(text="X")
        self.delete_btn.clicked.connect(self.deleteLater)
        self.delete_btn.setMaximumWidth(25)

        self.layout().addWidget(self.sequence_lbl)
        self.layout().addWidget(self.delete_btn)

    def setText(self, text: str):
        self.sequence_lbl.setText(text)

    def getText(self):
        return self.sequence_lbl.text()
