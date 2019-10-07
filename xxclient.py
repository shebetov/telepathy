# Copied with minimal modifications from curio
# https://github.com/dabeaz/curio


import socket
import ssl
import time
from utils import threaded
from audio import AudioPlayer, AudioRecorderCM


SERVER_IP = "46.101.142.225"
SERVER_PORT = 8888


def run_test(ttt):
    print(f'will connect to {SERVER_IP}:{SERVER_PORT}')

    # SSL
    client_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    if hasattr(client_context, 'check_hostname'):
        client_context.check_hostname = False
    client_context.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (OSError, NameError):
        pass
    sock = client_context.wrap_socket(sock)
    sock.connect((SERVER_IP, SERVER_PORT))

    rec = AudioRecorderCM()
    rec.__enter__()
    player = AudioPlayer()

    in_data = []
    out_data = []

    @threaded
    def vvrecord():
        try:
            while True:
                out_data.append(rec.read_stream())
        except Exception as e:
            print(e)

    @threaded
    def vvsend():
        try:
            while True:
                if out_data:
                    sock.sendall(out_data.pop(0))
        except Exception as e:
            print(e)

    @threaded
    def vvrecive():
        try:
            while True:
                in_data.append(sock.recv(1024))
        except Exception as e:
            print(e)

    @threaded
    def vvplay():
        try:
            while True:
                if in_data:
                    player.play_bytes(in_data.pop(0))
        except Exception as e:
            print(e)

    vvsend()
    vvrecive()


if __name__ == '__main__':
    run_test(False)
