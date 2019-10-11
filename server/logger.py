import os, sys
import logging


def setup_logger(name, filename, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.handlers.clear()
    formatter = logging.Formatter('[%(levelname)-5s][%(asctime)s %(filename)-20s:%(lineno)-4d] %(message)s')
    formatter_console = logging.Formatter('[%(levelname)-5s] %(asctime)s %(message)s')
    file_dirname = os.path.dirname(filename)
    if not os.path.exists(file_dirname):
        os.makedirs(file_dirname)
    fh = logging.FileHandler(filename, 'a', 'utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(formatter_console)
    logger.setLevel(level)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


