import sys
from robointerface import RoboInterface
from PyQt5 import QtWidgets


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    robo = RoboInterface()
    robo.setWindowTitle("Robot interface")
    robo.show()

    with open(r"theme.qss", "r") as f_obj:
        theme = f_obj.read()
        robo.setStyleSheet(theme)

    sys.exit(app.exec())
