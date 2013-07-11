import tulip
import viol
from demolib import set_title, make_widget

set_title('Do something after foo and bar are both done')

@viol.connect('#go click')
def start(client, data):
    coroutines = [foo(client), bar(client)]
    done, pending = yield from tulip.wait(coroutines)
    for future in done:
        client.log(future.result())

def foo(client):
    for i in range(10):
        widget = yield from make_widget()
        client.append_widget('foo', widget)
    return 'foo is done!'

def bar(client):
    for i in range(10):
        widget = yield from make_widget()
        client.append_widget('bar', widget)
    return 'bar is done!'

if __name__ == '__main__':
    viol.run()
