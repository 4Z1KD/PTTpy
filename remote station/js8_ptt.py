import serial
import sys

#this application expects "on" or "off" as argv and sends it through the serial port
ser = serial.Serial("COM11") #set the virtual com port number
b = sys.argv[1].encode('utf-8') #convert to bytes
ser.write(b) #send