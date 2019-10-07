# Copied with minimal modifications from curio
# https://github.com/dabeaz/curio


import socket
import ssl
import time
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

    with AudioRecorderCM() as rec:
        player = AudioPlayer()
        while True:
            st = time.time()
            if ttt:
                sock.sendall(rec.read_stream())
            else:
                player.play_bytes(sock.recv(1024))
            #nrecv_target = 4096
            #nrecv = 0
            #while nrecv < nrecv_target:
            #    resp = sock.recv(nrecv_target)
            #    if not resp:
            #        raise SystemExit()
            #    nrecv += len(resp)
            #print(time.time() - st)


if __name__ == '__main__':
    run_test(False)
