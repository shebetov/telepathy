import socket
import errno
import sys
from utils import threaded
import time
import logging
from ncommon import send_message, receive_message


HEADER_LENGTH = 5
logger = logging.getLogger("telepathy_client")


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

        send_message(self.socket, str(self.user_id).encode('utf-8'))

        self.listen_loop()

    @threaded
    def listen_loop(self):
        while True:
            try:
                # send msg or ping
                if self.pending_send_messages:
                    logger.debug(len(self.pending_send_messages))
                    print("c1")
                    send_message(self.socket, self.pending_send_messages.pop(0))
                    print("c2")
                    self.socket.setblocking(True)
                else:
                    self.socket.setblocking(False)

                print("c3")
                message_data = receive_message(self.socket)
                print("c4")
                #if not message_data:
                #    logger.info('Connection closed by the server')
                #    sys.exit()
                if message_data:
                    self.handler(message_data)
                print("c5")
                time.sleep(0.1)
            except IOError as e:
                logger.error(e, exc_info=True)
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    logger.error(e, exc_info=True)
                    logger.info('Reading error: {}'.format(str(e)))
                    sys.exit()

    def send_bytes(self, bytes_data):
        self.pending_send_messages.append(bytes_data)


if __name__ == '__main__':
    def hand(message):
        logger.info(message)
    c = Client("127.0.0.1", 1234, 111, hand)
    c.send_bytes(b"allo")
    time.sleep(3)
    c.send_bytes(b"heh")
    time.sleep(100)
