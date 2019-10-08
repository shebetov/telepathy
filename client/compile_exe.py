import os
import shutil
import PyInstaller.__main__


def _(path):
    if os.path.isdir(path):
        return path + os.pathsep + path
    else:
        dirname = os.path.dirname(path)
        return path + os.pathsep + ("." if dirname == "" else dirname)


cmd = [
    '--noconfirm',
    '-F',
    '--distpath=%s' % os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop'),
    '--key=4rbY65y79V6b9Hb64j5m',
    'xxclient.py',
]

print("pyinstaller " + " ".join(cmd))
PyInstaller.__main__.run(cmd)

shutil.rmtree(os.path.join(".", "build"))
