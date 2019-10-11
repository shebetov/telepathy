import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label
import network
from server.utils import threaded


__version__ = "0.1.1"


class MyApp(App):

    def build(self):
        return Label(text=f'ВОЙСЫ v{__version__}')


if __name__ == '__main__':
    threaded(network.main)()
    MyApp().run()
