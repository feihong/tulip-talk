from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.protocol import Protocol

@inlineCallbacks
def download(url):
    agent = Agent(reactor)
    response = yield agent.request('GET', url)
    for k, v in response.headers.getAllRawHeaders():
        print('{}: {}'.format(k, v[0][:80]))

    data = yield get_body(response)
    print('\nReceived {} bytes.\n'.format(len(data)))

    reactor.stop()

def get_body(response):
    class BodyReceiver(Protocol):
        def dataReceived(self, data):
            chunks.append(data)
        def connectionLost(self, reason):
            finished.callback(''.join(chunks))

    finished = Deferred()
    chunks = []
    response.deliverBody(BodyReceiver())
    return finished

if __name__ == '__main__':
    download('http://omegafeihong.tumblr.com')
    reactor.run()
