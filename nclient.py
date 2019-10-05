import socket
import errno
import sys
from utils import threaded
import time
import logging


HEADER_LENGTH = 5


def prepare_message(bytes_data):
    return f"{len(bytes_data):<{HEADER_LENGTH}}".encode('utf-8') + bytes_data


class Client():

    def __init__(self, server_ip, server_port, user_id, handler):
        self.server_ip = server_ip
        self.server_port = server_port
        self.user_id = user_id
        self.handler = handler
        self.pending_send_messages = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip, self.server_port))
        self.socket.setblocking(False)  # .recv() call won;t block, just return some exception we'll handle

        self.socket.send(prepare_message(str(self.user_id).encode('utf-8')))

        self.listen_loop()

    @threaded
    def listen_loop(self):
        while True:
            try:
                # send msg or ping
                if self.pending_send_messages:
                    msg = prepare_message(self.pending_send_messages.pop(0))
                    print(f"> {msg}")
                    self.socket.send(msg)

                message_header = self.socket.recv(HEADER_LENGTH)
                print(f"< {message_header}")

                if not len(message_header):
                    print('Connection closed by the server')
                    sys.exit()

                message_length = int(message_header.decode('utf-8').strip())
                message = self.socket.recv(message_length)
                print(f"< {message}")
                self.handler(message)
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    logging.error(e, exc_info=True)
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()

    def send_bytes(self, bytes_data):
        self.pending_send_messages.append(bytes_data)


if __name__ == '__main__':
    def hand(message):
        print(message)
    c = Client("127.0.0.1", 1234, 111, hand)
    c.send_bytes(b"allo")
    time.sleep(3)
    c.send_bytes(b"heh")
    time.sleep(100)
