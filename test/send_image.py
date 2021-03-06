from pysstv.color import MartinM1
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

#initialise pygame   
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0",(width,height))
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
sstv = MartinM1(img, 44100, 16)
sstv.write_wav(wavfile)


# Extract data and sampling rate from file
data, fs = sf.read(wavfile, dtype='float32')  
ser.setRTS(True)
sd.play(data, fs)
status = sd.wait()  # Wait until file is done playing
ser.setRTS(False)