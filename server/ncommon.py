import time
from server.logger import setup_logger


logger = setup_logger("telepathy_server", "./logs.txt")
HEADER_LENGTH = 5


def prepare_message(bytes_data):
    return f"{len(bytes_data):<{HEADER_LENGTH}}".encode('utf-8') + bytes_data


def send_message(to_socket, bytes_data):
    msg = prepare_message(bytes_data)
    logger.info(f'> {time.time()} {len(msg)} {msg}')
    to_socket.send(msg)


def receive_message(from_socket):
    try:
        message_header = from_socket.recv(HEADER_LENGTH)
        logger.debug(f"< {time.time()} {len(message_header)} {message_header}")
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        logger.warning(message_length)
        message_data = b""
        while True:
            logger.debug(message_data)
            logger.debug(len(message_data))
            message_data += from_socket.recv(message_length - len(message_data))
            if len(message_data) == message_length:
                break
        logger.debug(f"< {time.time()} {len(message_data)} {message_data}")
        return message_data
    except:
        return False
