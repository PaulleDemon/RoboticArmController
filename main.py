import sys
import serial
from PyQt5 import QtWidgets, QtCore


class RoboInterface(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(RoboInterface, self).__init__(*args, **kwargs)

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

        self.servo1_spin = QtWidgets.QSpinBox()
        self.servo2_spin = QtWidgets.QSpinBox()
        self.servo3_spin = QtWidgets.QSpinBox()

        self.servo1_spin.setRange(0, 180)
        self.servo2_spin.setRange(0, 180)
        self.servo3_spin.setRange(0, 180)

        self.base_controller = QtWidgets.QDial()
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
        self.servo_combo.addItems(["Base controller", "Servo1", "Servo2", "Servo3"])
        self.servo_combo.currentTextChanged.connect(self.changeSpinRange)

        self.angle_spin = QtWidgets.QSpinBox()
        self.add_btn = QtWidgets.QPushButton(text="Add")
        self.add_btn.clicked.connect(self.addkey)

        self.start_stop_btn = QtWidgets.QPushButton(text='start/Stop')

        self.animate_layout.addWidget(QtWidgets.QLabel("Animator", alignment=QtCore.Qt.AlignCenter), 0, 0, 1, 3)
        self.animate_layout.addWidget(self.start_stop_btn, 1, 2)
        self.animate_layout.addWidget(self.scroll_area, 2, 0, 1, 3)

        self.animate_layout.addWidget(self.servo_combo, 3, 0)
        self.animate_layout.addWidget(self.angle_spin, 3, 1)
        self.animate_layout.addWidget(self.add_btn, 3, 2)

    def addkey(self):
        self.scroll_layout.addWidget(SequenceLabel("SAMPLE"))

    def changeSpinRange(self, text):

        if text == "Base controller":
            self.angle_spin.setRange(0, 360)

        elif text in ["Servo1", "Servo2", "Servo3"]:
            self.angle_spin.setRange(0, 180)

    def connectDevice(self):  # Todo: move this to instructions class

        com = f"COM{self.com_port.text()}"
        baud = int(self.baud_rate.currentText())
        try:
            self.serial = serial.Serial(com, baud, timeout=2)

        except serial.serialutil.SerialException as e:
            self.connection_status_lbl.setText(str(e))


class Instructions(QtCore.QThread):
    completedInstruction = QtCore.pyqtSignal()

    def __init__(self, socket, *args, **kwargs):
        super(Instructions, self).__init__(*args, **kwargs)

        self.socket = socket

    def run(self) -> None:
        pass

    def setInstructions(self, instruction):
        pass


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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    robo = RoboInterface()
    robo.show()

    sys.exit(app.exec())
