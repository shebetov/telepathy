import socket
import pyaudio
import wave
import threading

# record
CHUNK = 1024 # 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 20000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("46.101.142.225", 8888))

p = pyaudio.PyAudio()

receive_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
send_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Voice chat running")

def receive_data():
    while True:
        try:
            data = s.recv(1024)
            receive_stream.write(data)
        except:
            pass


def send_data():
    while True:
        try:
            data = send_stream.read(CHUNK)
            s.sendall(data)
        except:
            pass

threading.Thread(target=receive_data).start()
threading.Thread(target=send_data).start()

while True:
    pass
