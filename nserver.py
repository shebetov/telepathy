import socket
import select
import time
from utils import threaded, clean_port


HEADER_LENGTH = 5
SERVER_IP = "46.101.142.225"
SERVER_PORT = 8888


def prepare_message(bytes_data):
    return f"{len(bytes_data):<{HEADER_LENGTH}}".encode('utf-8') + bytes_data


class Server:

    @staticmethod
    def receive_message(client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False

            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

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
        print(f'Listening for connections on {self.server_ip}:{self.server_port}...')

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
                    print('Accepted new connection from {}:{}, user_id: {}'.format(*client_address, user_msg['data'].decode('utf-8')))
                else:
                    message = self.receive_message(notified_socket)
                    if message is False:
                        print('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    user = self.clients[notified_socket]

                    if message != b"ping":
                        print(f'< {user["data"].decode("utf-8")}: {message["data"]}')

                        # Iterate over connected clients and broadcast message
                        for client_socket in self.clients:

                            # But don't sent it to sender
                            if client_socket != notified_socket:
                                msg = user['header'] + user['data'] + message['header'] + message['data']
                            else:
                                msg = prepare_message(b"pong")
                            print(f'> {msg}')
                            client_socket.send(msg)

            # It's not really necessary to have this, but will handle some socket exceptions just in case
            for notified_socket in exception_sockets:
                # Remove from list for socket.socket()
                self.sockets_list.remove(notified_socket)

                # Remove from our list of users
                del self.clients[notified_socket]


if __name__ == '__main__':
    clean_port(SERVER_PORT)
    s = Server(SERVER_IP, SERVER_PORT)
    time.sleep(999999)
