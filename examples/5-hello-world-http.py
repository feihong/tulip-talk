import tulip
from tulip import http

class HttpServer(http.ServerHttpProtocol):
    @tulip.coroutine
    def handle_request(self, message, payload):
        response = tulip.http.Response(self.transport, 200, close=True)
        response.add_header('Content-type', 'text/html')
        response.send_headers()

        if message.path == '/':
            html = '<h1>Hello World!</h1>'
            response.write(html.encode())

        response.write_eof()
        self.keep_alive(False)

if __name__ == '__main__':
    loop = tulip.get_event_loop()
    task = loop.start_serving(HttpServer, '127.0.0.1', 8000)
    socks = loop.run_until_complete(task)
    print('serving on', socks[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
