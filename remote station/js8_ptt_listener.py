import time
import asyncio
import serial
import serial_asyncio
import sys

def log(msg):
    t = time.localtime()
    current_time = time.strftime("%D %H:%M:%S", t)
    print(f"{current_time}  {msg}")

class Output(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        #log(f"{transport}")
        log("port open")
        log("waiting for ptt...")
    def data_received(self, data):
        #print("data received", repr(data))
        if data == b"on":
            ser.setRTS(True)
            log("transmitting...")
        elif data == b"off":
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
if __name__ == "__main__":
    global ser
    ser = serial.Serial("COM9")
    ser.setRTS(False)

    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, Output, "COM12", baudrate=38400)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()