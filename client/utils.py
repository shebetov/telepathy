import threading
import re
import subprocess


def threaded(func):
    def wrapped(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t
    return wrapped
