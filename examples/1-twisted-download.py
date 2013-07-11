from twisted.internet import reactor
from twisted.internet.defer import Deferred, succeed
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent

def print_headers(response):
    for k, v in response.headers.getAllRawHeaders():
        print('{}: {}'.format(k, v[0][:80]))

    return get_response_body(response)

def get_response_body(response):
    class BodyReceiver(Protocol):
        def dataReceived(self, data):
            chunks.append(data)
        def connectionLost(self, reason):
            finished.callback(''.join(chunks))

    finished = Deferred()
    chunks = []
    response.deliverBody(BodyReceiver())
    return finished

def print_body(data):
    print('\nReceived {} bytes.\n'.format(len(data)))
    return succeed(None)

if __name__ == '__main__':
    agent = Agent(reactor)
    d = agent.request('GET', 'http://megafeihong.tumblr.com')
    d.addCallback(print_headers)
    d.addCallback(print_body)
    d.addCallback(lambda x: reactor.stop())
    reactor.run()
