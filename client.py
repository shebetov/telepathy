from audio import AudioPlayer, AudioRecorderCM
from utils import *
import time
from nclient import Client


CHUNK_SIZE = 4096
SERVER_IP = "46.101.142.225"
SERVER_PORT = 8888


contacts = [
    {"id": 112, "name": "Alex", "ip": "127.0.0.1"}
]


class TelepathyClient:

    def __init__(self, user_id):
        self.is_recording = False
        self.is_online = False
        self.playing_contact = None
        self.dest_addr = None
        self.audio_player = AudioPlayer()
        self.user_id = user_id
        self.frames = {112: []}
        self.pending_messages = []

        self.process_messages_loop()
        self.client = Client(SERVER_IP, SERVER_PORT, self.user_id, lambda message: self.socket_handler(message))

    @threaded
    def process_messages_loop(self):
        while True:
            if self.pending_messages:
                self.process_bytes(self.pending_messages.pop(0), None)
            else:
                time.sleep(0.1)

    def socket_handler(self, message):
        if message == b"pong": return
        self.pending_messages.append(message)

    @threaded
    def start_record(self):
        self.is_recording = True
        with AudioRecorderCM() as rec:
            while self.is_recording:
                frame = rec.read_stream()
                print(len(frame))
                self.client.send_bytes(frame)

    def stop_record(self):
        self.is_recording = False

    def process_bytes(self, data, addr):
        self.frames[112].append(data)
        if self.is_online:
            if self.playing_contact is None:
                self.playing_contact = 112
            if self.playing_contact == 112:
                self.audio_player.play_bytes(data)


if __name__ == '__main__':
    if False:
        c = TelepathyClient(user_id=113)
        c.is_online = True
        time.sleep(9999)
    else:
        c = TelepathyClient(user_id=114)
        c.start_record()
        time.sleep(3)
        c.stop_record()
        time.sleep(9999)
