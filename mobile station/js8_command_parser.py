import time
import pandas as pd
import re
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from gpiozero import LED
from gpiozero import AngularServo
from gpiozero import Motor
from time import sleep

from pysstv.color import Robot36
from PIL import Image
from resizeimage import resizeimage
import sounddevice as sd
import soundfile as sf
import serial
import os
import pygame, sys
from pygame.locals import *
import pygame.camera

width = 320
height = 256
wavfile = 'x.wav'
led = LED(4)
servo = AngularServo(27, min_angle=0, max_angle=180)
fb_motor = Motor(17, 18)
lr_motor = Motor(22, 23)

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        #path = r'C:\Users\Gil\AppData\Local\JS8Call - sdr\DIRECTED.TXT'
        path = r"/home/pi/.local/share/JS8Call/DIRECTED.TXT"
        log(f"event type: {event.event_type}  path : {event.src_path}") #print the event and the file name
        if event.event_type == "modified" and event.src_path == path: #if this is the file that was changed
            log_file = pd.read_csv(path, sep='\t', header=None) #read it (it does not have a header)
            last_record = log_file.tail(1) #take the last record
            raw_data = last_record[4].to_string(index=False) #take the 4th column (it contains the stations callsign and command)
            #log(raw_data)
            match = re.search("^\w+: \w+/?\w+> (\w+!?)+ \*DE\* \w+", raw_data) #try matching a routed command
            if (match != None):
                command = match.group(1)
                log(command)
                commandExecuter(command)
            else :
                match = re.search("^\w+: \w+/?\w+  (\w+!?)+", raw_data) # try to match a direct command
                if (match != None):
                    command = match.group(1)
                    log(command)
                    commandExecuter(command)
                else :
                    log(f"parsing failed: {raw_data}")

def commandExecuter(command):
    command_u = command.upper()
    if command_u == "ON":
        log("led on")
        led.on()
    elif command_u == "OFF":
        log("led off")
        led.off()
    elif command_u == "IMG":
        log("capture image")
        send_image()
    else:
        match = re.search("^(F|B|FR|FL|BR|BL)(\d\d?\d?)", command)
        if (match != None):
            direction = match.group(1)
            duration = int(match.group(2))
            log(f"direction: {direction}  duration: {duration}")
            if (direction.upper() == "F"):
                speed = 1
                fb_motor.forward(speed)
                sleep(duration)
                fb_motor.stop()
            if (direction.upper() == "B"):
                speed = 1
                fb_motor.backward(speed)
                sleep(duration)
                fb_motor.stop()
            if (direction.upper() == "FR"):
#                 servo.angle = 120
#                 sleep(duration)
                speed = 1
                lr_motor.forward(speed)
                fb_motor.forward(speed)
                sleep(duration)
                lr_motor.stop()
                fb_motor.stop()
            if (direction.upper() == "FL"):
#                 servo.angle = 60
#                 sleep(duration)
                speed = 1
                lr_motor.backward(speed)
                fb_motor.forward(speed)
                sleep(duration)
                lr_motor.stop()
                fb_motor.stop()
            if (direction.upper() == "BR"):
#                 servo.angle = 120
#                 sleep(duration)
                speed = 1
                lr_motor.forward(speed)
                fb_motor.backward(speed)
                sleep(duration)
                lr_motor.stop()
                fb_motor.stop()
            if (direction.upper() == "BL"):
#                 servo.angle = 60
#                 sleep(duration)
                speed = 1
                lr_motor.backward(speed)
                fb_motor.backward(speed)
                sleep(duration)
                lr_motor.stop()
                fb_motor.stop()
            servo.angle = 90
                
def log(msg):
    t = time.localtime()
    current_time = time.strftime("%D %H:%M:%S", t)
    print(f"[{current_time}]  {msg}")

def send_image():
    cam.start()

    #setup window
    windowSurfaceObj = pygame.display.set_mode((width,height),1,16)
    pygame.display.set_caption('Camera')

    #take a picture
    image = cam.get_image()
    cam.stop()

    #display the picture
    catSurfaceObj = image
    windowSurfaceObj.blit(catSurfaceObj,(0,0))
    pygame.display.update()

    #save picture
    pygame.image.save(windowSurfaceObj,'fx.jpg')

    ser = serial.Serial("/dev/ttyUSB0")
    ser.setRTS(False)
        
    wavfile = 'x.wav'

    with open('fx.jpg', 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [width, height], validate=False)
            cover.save('fx.jpg', image.format)

    img = Image.open("fx.jpg")
    sstv = Robot36(img, 44100, 16)
    sstv.write_wav(wavfile)

    # Extract data and sampling rate from file
    data, fs = sf.read(wavfile, dtype='float32')  
    ser.setRTS(True)
    sd.play(data, fs)
    status = sd.wait()  # Wait until file is done playing
    ser.setRTS(False)

if __name__ == "__main__":
    #messagelog watch dog -> gets the command received from the base station
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path="/home/pi/.local/share/JS8Call", recursive=False)
    observer.start()
    pygame.init()
    pygame.camera.init()
    global cam
    cam = pygame.camera.Camera("/dev/video0",(width,height))
    
    log("listening...")
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        fb_motor.close()
    observer.join()
