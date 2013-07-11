import tulip
from tulip import http

def print_headers(task):
    response = task.result()
    for k, v in response.items():
        print('{}: {}'.format(k, v[:80]))

    task = tulip.Task(response.read())
    task.add_done_callback(print_body)

def print_body(task):
    data = task.result()
    print('\nReceived {} bytes.\n'.format(len(data)))
    tulip.get_event_loop().stop()

if __name__ == '__main__':
    loop = tulip.get_event_loop()

    t = tulip.Task(http.request('GET', 'http://megafeihong.tumblr.com'))
    t.add_done_callback(print_headers)

    loop.run_forever()
