import threading
import re
import subprocess


def threaded(func):
    def wrapped(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t
    return wrapped


def clean_port(port):
    s = subprocess.getoutput('lsof -i :%i'%(port))
    try:
        p_id = re.findall('.*?python\s+[0-9]{4,7}', s)[0].split(' ')[-1]
    except IndexError:
        p_id = None
    p_id = int(p_id) if p_id else None
    if p_id:
        subprocess.getoutput('kill -9 {}'.format(p_id))
