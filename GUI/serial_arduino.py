import serial
import time
import sys
import base64


# import signal


def signal_handler(_signal, frame):
    print("closing program")
    SerialPort.close()
    sys.exit(0)


COM = input("Enter the COM Port: ")
BAUD = input("Enter the Baudrate: ")
SerialPort = serial.Serial(f"COM{COM}", BAUD, timeout=2)
# time.sleep(0.2)
# SerialPort.write("I")
#
while 1:
    try:
        OutgoingData = input(">")
        # print(bytes(OutgoingData, 'utf-8'))
        # SerialPort.write(OutgoingData.encode('ascii').strip())
        SerialPort.write(bytes(OutgoingData, 'utf-8'))
        # print(bytes(OutgoingData, 'ascii'))
    except KeyboardInterrupt:
        print("Closing and exiting the program")
        SerialPort.close()
        sys.exit(0)
    IncomingData = SerialPort.readline()
    print(IncomingData, type(IncomingData))

    if IncomingData:
        # print(IncomingData.decode('ascii'))
        print("Incoming", IncomingData.decode("utf-8"))
    time.sleep(0.01)
