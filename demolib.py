"""
Utility library for demo code.
"""
import time
import random
import tulip
import viol

EYES = ['^', 'ᵒ', '♥', '•', 'ಠ', '°', 'ಥ', '・', '$', "'"]
MOUTHS = ['_', '◡', 'ᴥ', '□', 'Д', '益', 'ェ', 'ω', '∀']

def set_title(text):
    @viol.connect('document_ready')
    def func(client, data):
        client.set_text('h1', text)

def make_widget():
    yield from tulip.sleep(random.random())
    return _make_widget()

def make_widget_synchronous():
    time.sleep(random.random())
    return _make_widget()

def _make_widget():
    eye = random.choice(EYES)
    mouth = random.choice(MOUTHS)
    return eye + mouth + eye

class Client(viol.Client):
    def log(self, html):
        self.append_html('#log', html + '<br>')

    def append_widget(self, producer, text):
        self.append_html('#' + producer, '<span>{}</span>&nbsp;'.format(text))

viol.app.client_class = Client
