import time
from nserver import Server
from client import TelepathyClient


def main():
    s = Server("127.0.0.1", 1234)
    c1 = TelepathyClient(user_id=113)
    c1.is_online = True
    c2 = TelepathyClient(user_id=115)
    c2.is_online = True
    c = TelepathyClient(user_id=114)
    c.start_record()
    time.sleep(3)
    c.stop_record()
    time.sleep(9999)


if __name__ == '__main__':
    main()
