import tulip
import viol
from demolib import set_title, make_widget, make_widget_synchronous

set_title('Bar runs in another thread but communicates with event loop')

@viol.connect('#go click')
def start(client, data):
    coroutines = [foo(client), bar(client)]
    for future in tulip.as_completed(coroutines):
        result = yield from future
        client.log(result)

def foo(client):
    client.log('Starting foo.')
    for i in range(10):
        widget = yield from make_widget()
        client.append_widget('foo', widget)
    return 'foo is done!'

def bar(client):
    client.log('Starting bar work in another thread.')
    loop = tulip.get_event_loop()
    yield from loop.run_in_executor(None, bar_synchronous, loop, client)
    return 'bar is done!'

def bar_synchronous(loop, client):
    for i in range(10):
        widget = make_widget_synchronous()
        loop.call_soon_threadsafe(client.append_widget, 'bar', widget)
        loop.call_soon_threadsafe(client.log,
            'Made widget {} in another thread'.format(i))

if __name__ == '__main__':
    viol.run()
