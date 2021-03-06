
import time
import serial


ser = serial.Serial(port="COM1", baudrate=38400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO)
if ser.isOpen():
    ser.write([0,0,0,0,0x8])
    time.sleep(2)
    ser.write([0,0,0,0,0x88])
    ser.close()