import time
import serial

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pysstv.color import Robot36
from pysstv.color import MartinM1
from PIL import Image
import sounddevice as sd
import soundfile as sf

rt = time.time()-60

def log(msg):
    t = time.localtime()
    current_time = time.strftime("%D %H:%M:%S", t)
    print(f"{current_time}  {msg}")

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global rt
        #log(f"event type: {event.event_type}  path : {event.src_path}") #print the event and the file name
        if event.event_type == "modified" and event.src_path.find('.bmp') != -1 and (time.time() - rt) > 60: #if this is the file that was changed
            rt = time.time()
            log(f"event type: {event.event_type}  path : {event.src_path}") #print the event and the file name
            send_image(event.src_path)

def send_image(image_path):
        wavfile = 'x.wav'
        img = Image.open(image_path)
        sstv = Robot36(img, 44100, 16)
        #sstv = MartinM1(img, 44100, 16)
        sstv.write_wav(wavfile)
        # Extract data and sampling rate from file
        data, fs = sf.read(wavfile, dtype='float32')  
        ser = serial.Serial(port="COM1", baudrate=38400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO)
        if ser.isOpen():
            ser.write([0,0,0,0,0x8])
            sd.play(data, fs)
            status = sd.wait()  # Wait until file is done playing
            ser.write([0,0,0,0,0x88])
            ser.close()

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path="C:\HAM\MMSSTV\History", recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()