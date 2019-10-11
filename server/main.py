import asyncio
import gc
import ssl
import time
import uvloop


class EchoProtocol(asyncio.Protocol):
    all_transports = []

    def connection_made(self, transport):
        print(transport.get_extra_info('peername'))
        self.i = len(self.all_transports)
        self.all_transports.append(transport)
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None

    def data_received(self, data):
        print("< " + str(len(data)))
        for i, t in enumerate(self.all_transports):
            if i == self.i: continue
            print(f"send_to {self.transport.get_extra_info('peername')}[{self.i}] > {t.get_extra_info('peername')}")
            t1 = time.time()
            try:
                t.write(data)
            except Exception as e:
                print(e)
            print(f"write in {time.time() - t1}")


async def print_debug(loop):
    while True:
        print(chr(27) + "[2J")  # clear screen
        loop.print_debug_info()
        await asyncio.sleep(0.5, loop=loop)


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(False)

    if hasattr(loop, 'print_debug_info'):
        loop.create_task(print_debug(loop))

    unix = False
    addr = ["178.128.206.199", "8888"]
    addr[1] = int(addr[1])
    addr = tuple(addr)

    print('serving on: {}'.format(addr))

    server_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    server_context.load_cert_chain('ssl_cert.pem', 'ssl_key.pem')
    if hasattr(server_context, 'check_hostname'):
        server_context.check_hostname = False
    server_context.verify_mode = ssl.CERT_NONE

    coro = loop.create_server(EchoProtocol, *addr)#, ssl=server_context)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
    finally:
        if hasattr(loop, 'print_debug_info'):
            gc.collect()
            print(chr(27) + "[2J")
            loop.print_debug_info()

        loop.close()
