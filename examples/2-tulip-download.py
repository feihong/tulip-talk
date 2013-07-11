import tulip
from tulip import http

@tulip.coroutine
def download(url):
    response = yield from http.request('GET', url)
    for k, v in response.items():
        print('{}: {}'.format(k, v[:80]))

    data = yield from response.read()
    print('\nReceived {} bytes.\n'.format(len(data)))

if __name__ == '__main__':
    loop = tulip.get_event_loop()
    coroutine = download('http://omegafeihong.tumblr.com')
    loop.run_until_complete(coroutine)
