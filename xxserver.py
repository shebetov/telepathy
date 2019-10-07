import asyncio
import gc
import socket
import ssl
import uvloop


PRINT = 0


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
    loop = uvloop.new_event_loop()
    print('using UVLoop')

    asyncio.set_event_loop(loop)
    loop.set_debug(False)

    PRINT = 1

    if hasattr(loop, 'print_debug_info'):
        loop.create_task(print_debug(loop))
        PRINT = 0

    unix = False
    addr = ["46.101.142.225", "8888"]
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
