# Copied with minimal modifications from curio
# https://github.com/dabeaz/curio


import argparse
import concurrent.futures
import socket
import ssl
import time


if __name__ == '__main__':

    print('with SSL')
    client_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    if hasattr(client_context, 'check_hostname'):
        client_context.check_hostname = False
    client_context.verify_mode = ssl.CERT_NONE

    unix = False
    addr = ["46.101.142.225", "8888"]
    addr[1] = int(addr[1])
    addr = tuple(addr)
    print('will connect to: {}'.format(addr))

    msize = 1000
    mpr = 1
    MSGSIZE = msize
    REQSIZE = MSGSIZE * mpr

    msg = b'x' * (MSGSIZE - 1) + b'\n'
    msg *= mpr

    def run_test(n):
        print('Sending', NMESSAGES, 'messages')
        n //= mpr

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except (OSError, NameError):
            pass

        if client_context:
            sock = client_context.wrap_socket(sock)

        sock.connect(addr)

        while n > 0:
            sock.sendall(msg)
            nrecv = 0
            while nrecv < REQSIZE:
                resp = sock.recv(REQSIZE)
                if not resp:
                    raise SystemExit()
                nrecv += len(resp)
            n -= 1

    TIMES = 1
    N = 3
    NMESSAGES = 200000
    start = time.time()
    for _ in range(TIMES):
        with concurrent.futures.ProcessPoolExecutor(max_workers=N) as e:
            for _ in range(N):
                e.submit(run_test, NMESSAGES)
    end = time.time()
    duration = end - start
    print(NMESSAGES * N * TIMES, 'in', duration)
    print(NMESSAGES * N * TIMES / duration, 'requests/sec')
