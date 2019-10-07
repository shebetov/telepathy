import argparse
import asyncio
import gc
import os.path
import pathlib
import socket
import ssl


PRINT = 0


async def echo_server(loop, address, unix):
    if unix:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    sock.setblocking(False)
    if PRINT:
        print('Server listening at', address)
    with sock:
        while True:
            client, addr = await loop.sock_accept(sock)
            if PRINT:
                print('Connection from', addr)
            loop.create_task(echo_client(loop, client))


async def echo_client(loop, client):
    try:
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (OSError, NameError):
        pass

    with client:
        while True:
            data = await loop.sock_recv(client, 1000000)
            if not data:
                break
            await loop.sock_sendall(client, data)
    if PRINT:
        print('Connection closed')


async def echo_client_streams(reader, writer):
    sock = writer.get_extra_info('socket')
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (OSError, NameError):
        pass
    if PRINT:
        print('Connection from', sock.getpeername())
    while True:
        data = await reader.read(1000000)
        if not data:
            break
        writer.write(data)
    if PRINT:
        print('Connection closed')
    writer.close()


class EchoProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None

    def data_received(self, data):
        print("ok")
        self.transport.write(data)


async def print_debug(loop):
    while True:
        print(chr(27) + "[2J")  # clear screen
        loop.print_debug_info()
        await asyncio.sleep(0.5, loop=loop)


if __name__ == '__main__':
    import uvloop
    loop = uvloop.new_event_loop()
    print('using UVLoop')

    asyncio.set_event_loop(loop)
    loop.set_debug(False)

    PRINT = 1

    if hasattr(loop, 'print_debug_info'):
        loop.create_task(print_debug(loop))
        PRINT = 0

    unix = False
    addr = args.addr.split(':')
    addr[1] = int(addr[1])
    addr = tuple(addr)

    print('serving on: {}'.format(addr))

    print('with SSL')
    server_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    server_context.load_cert_chain('ssl_cert.pem', 'ssl_key.pem')
    if hasattr(server_context, 'check_hostname'):
        server_context.check_hostname = False
    server_context.verify_mode = ssl.CERT_NONE

    print('using simple protocol')
    protocol = EchoProtocol
    coro = loop.create_server(protocol, *addr, ssl=server_context)
    print("1")
    srv = loop.run_until_complete(coro)
    print("2")
    try:
        loop.run_forever()
        print("3")
    finally:
        if hasattr(loop, 'print_debug_info'):
            gc.collect()
            print(chr(27) + "[2J")
            loop.print_debug_info()

        loop.close()
