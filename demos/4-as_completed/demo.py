import tulip
import viol
from demolib import set_title, make_widget

set_title('Do something when either foo or bar finishes')

@viol.connect('#go click')
def start(client, data):
    coroutines = [foo(client), bar(client)]
    for future in tulip.as_completed(coroutines):
        result = yield from future
        client.log(result)

def foo(client):
    for i in range(12):
        widget = yield from make_widget()
        client.append_widget('foo', widget)
    return 'foo is done!'

def bar(client):
    for i in range(8):
        widget = yield from make_widget()
        client.append_widget('bar', widget)
    return 'bar is done!'

if __name__ == '__main__':
    viol.run()
