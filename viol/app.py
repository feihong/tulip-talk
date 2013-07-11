"""
tbd
"""
import sys
import os.path as op
import functools
import json
from urllib.parse import urlparse
import mimetypes
import tulip
import tulip.http
from tulip.http import websocket

from . import lim

HERE = op.dirname(__file__)
FAVICON = open(op.join(HERE, 'favicon.ico'), 'rb').read()
JQUERY_JS = open(op.join(HERE, 'jquery.js'), 'rb').read()
VIOL_JS = open(op.join(HERE, 'viol.js')).read()


def connect(route):
    return functools.partial(app.add_connection, route)

def run(host='127.0.0.1', port=8000):
    app.run(host, port)

def set_app(an_app):
    global app
    app = an_app


class App(object):
    def __init__(self):
        self.index_page = 'index.html'
        self.connections = {}
        self.client_class = Client

    @tulip.coroutine
    def get_index_html(self):
        if self.index_page.endswith('.lim'):
            markup = open(self.index_page).read()
            html = yield from self.loop.run_in_executor(None, lim.parse, markup)
            with open('index.html', 'w') as fout:
                fout.write(html)

        return get_file('index.html')

    def add_connection(self, route, fn):
        fn = tulip.task(fn)
        self.connections[route] = fn
        return fn

    @tulip.coroutine
    def get_compiled_js(self, js_file):
        return get_compiled_js(self.coffee_outputs[js_file], js_file)

    @tulip.coroutine
    def handle(self, route, client, data):
        fn = self.connections.get(route)
        if fn is not None:
            yield from fn(client, data)

    def run(self, host='127.0.0.1', port=8000, call_soon=None):
        if sys.platform == 'win32':
            from tulip.windows_events import ProactorEventLoop
            loop = ProactorEventLoop()
            tulip.set_event_loop(loop)
        else:
            loop = tulip.get_event_loop()

        self.loop = loop

        task = loop.start_serving(
            lambda: HttpServer(debug=True, app=self), host, port)
        socks = loop.run_until_complete(task)

        if call_soon:
            loop.call_soon(call_soon)

        print('Serving on', socks[0].getsockname())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()

class Client(object):
    def __init__(self, writer):
        self.writer = writer

    def set_text(self, selector, value):
        self.jquery(selector, 'text', value)

    def set_html(self, selector, value):
        self.jquery(selector, 'html', value)

    def append_html(self, selector, value):
        self.jquery(selector, 'append', value)

    def set_val(self, selector, value):
        self.jquery(selector, 'val', value)

    def show(self, selector):
        self.jquery(selector, 'show')

    def hide(self, selector):
        self.jquery(selector, 'hide')

    def log(self, value):
        self.send('log', {'value': value})

    def jquery(self, selector, funcname, *args):
        self.send('jquery.' + funcname, {
            'selector': selector,
            'args': args,
        })

    def send(self, route, content):
        mesg = {'route': route, 'content': content}
        self.writer.send(json.dumps(mesg))


class HttpServer(tulip.http.ServerHttpProtocol):
    app = None

    @tulip.coroutine
    def handle_request(self, message, payload):
        if message.path == '/socket':
            status, headers, parser, writer = websocket.do_handshake(
                message, self.transport)

            response = tulip.http.Response(self.transport, status)
            response.add_headers(*headers)
            response.send_headers()
            databuffer = self.stream.set_parser(parser)

            client = self.app.client_class(writer)
            yield from self.app.handle('connection_made', client, None)

            while True:
                message = yield from databuffer.read()

                if message is None or message.tp == websocket.MSG_CLOSE:
                    # You cannot use yield from here because this coroutine is
                    # about to be cancelled.
                    handle_conn_lost = tulip.task(
                        lambda: self.app.handle('connection_lost', client, None))
                    handle_conn_lost()
                    break
                elif message.tp == websocket.MSG_PING:
                    writer.pong()
                elif message.tp == websocket.MSG_TEXT:
                    data = json.loads(message.data)
                    yield from self.app.handle(data['route'], client,
                        data['content'])
        else:
            response = tulip.http.Response(self.transport, 200)
            path = urlparse(message.path).path

            mtype, encoding = mimetypes.guess_type(path)
            response.add_header('Content-type', mtype or 'text/html')
            response.send_headers()

            if path == '/':
                result = yield from self.app.get_index_html()
            elif path == '/viol.js':
                result = get_viol_js()
            elif path == '/jquery.js':
                result = JQUERY_JS
            elif path == '/favicon.ico':
                result = FAVICON
            else:
                result = get_file(path[1:])
            response.write(result)

        response.write_eof()
        self.keep_alive(False)

def get_file(filename):
    with open(filename, 'rb') as fin:
        html = fin.read()
    return html

def get_viol_js():
    result = VIOL_JS + '\n'

    for key in app.connections.keys():
        if ' ' in key:
            result += 'viol.register("{}");\n'.format(key)

    return result.encode()


app = App()
