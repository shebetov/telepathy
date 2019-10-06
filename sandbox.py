import socket
import select
import time
from utils import threaded, clean_port
from logger import setup_logger


logger = setup_logger("telepathy_server", "./logs.txt")


class Server:

    @staticmethod
    def receive_message(client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            logger.debug(f"< {time.time()}  {message_header}")
            if not len(message_header):
                return False

            message_length = int(message_header.decode('utf-8').strip())
            message_data = client_socket.recv(message_length)
            logger.debug(f"< {time.time()} {message_data}")
            return {'header': message_header, 'data': message_data}
        except:
            return False

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.server_ip, self.server_port))
        self.socket.listen()

        self.listen_loop()
        logger.info(f'Listening for connections on {self.server_ip}:{self.server_port}...')

    def broadcast_message(self, client_sockets, bytes_message):
        for client_socket in client_sockets:
            logger.info(f'> {time.time()} {bytes_message}')
            client_socket.send(bytes_message)

    @threaded
    def listen_loop(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == self.socket:
                    client_socket, client_address = self.socket.accept()

                    user_msg = self.receive_message(client_socket)
                    if user_msg is False:
                        continue

                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user_msg
                    logger.info('Accepted new connection from {}:{}, user_id: {}'.format(*client_address, user_msg['data'].decode('utf-8')))
                else:
                    message = self.receive_message(notified_socket)
                    if message is False:
                        logger.info('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    user = self.clients[notified_socket]

                    if message != b"ping":
                        self.broadcast_message([notified_socket], prepare_message(b"pong"))
                        threaded(self.broadcast_message)([client_socket for client_socket in self.clients if client_socket != notified_socket], prepare_message(message["data"]))

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]


if __name__ == '__main__':
    clean_port(SERVER_PORT)
    s = Server(SERVER_IP, SERVER_PORT)
    time.sleep(999999)
