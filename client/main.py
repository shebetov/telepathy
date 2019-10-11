# Copied with minimal modifications from curio
# https://github.com/dabeaz/curio


import asyncio
import ssl
from utils import threaded
from client.audio import AudioPlayer, AudioRecorderCM

__version__ = "0.1.1"
SERVER_IP = "178.128.206.199"
SERVER_PORT = 8888
server_transport = None
in_audio_data = b""


class ClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        global server_transport
        server_transport = transport
        print('connecting to {} port {}'.format(*transport.get_extra_info('peername')))

    def data_received(self, data):
        print("< " + str(data))
        global in_audio_data
        in_audio_data += data

    def connection_lost(self, exc):
        print('The server closed the connection')
        global server_transport
        server_transport.close()
        super().connection_lost(exc)


def main():
    print(f'will connect to {SERVER_IP}:{SERVER_PORT}')
    audio_recorder = AudioRecorderCM()
    audio_recorder.__enter__()
    audio_player = AudioPlayer()

    @threaded
    def vvsend():
        while True:
            if server_transport is not None:
                break
        while True:
            try:
                rec_data = audio_recorder.read_stream()
                print("> " + str(rec_data))
                server_transport.write(rec_data)
            except Exception as e:
                print(e)

    @threaded
    def vvplay():
        global in_audio_data
        while True:
            try:
                if len(in_audio_data) != 0:
                    audio_player.play_bytes(in_audio_data)
                    in_audio_data = b""
            except Exception as e:
                print(e)

    vvsend()
    vvplay()

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    if hasattr(ssl_context, 'check_hostname'):
        ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(ClientProtocol, SERVER_IP, SERVER_PORT)#, ssl=ssl_context)
    try:
        loop.run_until_complete(coro)
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
