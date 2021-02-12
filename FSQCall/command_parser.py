import glob
import os
import time
import asyncio
import serial
import serial_asyncio
import pandas as pd
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class Output(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        #self.transport.serial.rts = True #set RTS to HIGH
        log(f"port opened")
        log(f"{transport}")

    def data_received(self, data):
        #print("data received", repr(data))
        if data == b"TX;":
            ser.setRTS(True)
            log("sending...")
        elif data == b"RX;":
            ser.setRTS(False)
            log("receiving...")
        if b"\n" in data:
            log("closing...")
            self.transport.close()

    def connection_lost(self, exc):
        log("port closed")
        self.transport.loop.stop()

    def pause_writing(self):
        log("pause writing")
        log(self.transport.get_write_buffer_size())

    def resume_writing(self):
        log(self.transport.get_write_buffer_size())
        log("resume writing")

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        logfile = glob.glob(r".\**Messagelog.txt", recursive=False) #search for log files
        logfile_sorted = sorted(logfile, key=lambda t: -os.stat(t).st_mtime) #sort the list of files by modification time
        path = logfile_sorted[0] if len(logfile_sorted)>0 else "" #if the list is not empty -> take the latest log
        if event.event_type == "modified" and event.src_path == path: #if this is the file that was changed
            #log(f"event type: {event.event_type}  path : {event.src_path}") #print the event and the file name
            data = pd.read_csv(path, header=None) #read it (it does not have a header)
            d = data.tail(1) #take the last record
            raw_commands = d[6].to_string(index=False).split() #take the 6th column (it contains the station callsign and command) -> split it to get each value
            if len(raw_commands) == 2: #if it contains 2 values i.e. the callsign and command
                [callsign,command] = raw_commands[0:2] #unpack
                log("received:")
                log(f"callsign:{callsign} command:{command}")
                f = open("Shared/data.txt", "w") #create data.txt file
                f.write(f"{callsign} {command}") #write callsign and command to file
                f.close()
            else: #if its len is not 2 -> just print the faulty command
                log(raw_commands)


def log(msg):
    t = time.localtime()
    current_time = time.strftime("%D %H:%M:%S", t)
    print(f"{current_time}  {msg}")

if __name__ == "__main__":
    #messagelog watch dog -> gets the command received from the base station
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    global ser
    ser = serial.Serial("COM9")
    ser.setRTS(False)

    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, Output, "COM12", baudrate=38400,rtscts=False)
    loop.run_until_complete(coro)
    loop.run_forever()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    loop.close()