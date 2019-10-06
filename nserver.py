import socket
import select
import time
from utils import threaded, clean_port
from logger import setup_logger
from ncommon import send_message, receive_message


logger = setup_logger("telepathy_server", "./server.log")
SERVER_IP = "46.101.142.225"
#SERVER_IP = "localhost"
SERVER_PORT = 8888


class Server:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.server_ip, self.server_port))
        self.socket.listen()

        self.sockets_list = [self.socket]
        self.clients = {}

        self.listen_loop()
        logger.info(f'Listening for connections on {self.server_ip}:{self.server_port}...')

    def broadcast_message(self, client_sockets, bytes_message):
        for client_socket in client_sockets:
            send_message(client_socket, bytes_message)

    @threaded
    def listen_loop(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == self.socket:
                    client_socket, client_address = self.socket.accept()

                    user_msg = receive_message(client_socket)
                    if user_msg is False:
                        continue

                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user_msg
                    logger.info('Accepted new connection from {}:{}, user_id: {}'.format(*client_address, user_msg.decode('utf-8')))
                else:
                    notified_socket.setblocking(True)
                    message = receive_message(notified_socket)
                    if message is False:
                        logger.info('Closed connection from: {}'.format(self.clients[notified_socket].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    user = self.clients[notified_socket]

                    if message != b"ping":
                        self.broadcast_message([notified_socket], b"pong")
                        threaded(self.broadcast_message)([client_socket for client_socket in self.clients if client_socket != notified_socket], message)

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]


if __name__ == '__main__':
    clean_port(SERVER_PORT)
    s = Server(SERVER_IP, SERVER_PORT)
    time.sleep(999999)
