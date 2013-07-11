import viol
from demolib import set_title, make_widget

set_title('Foo runs, then bar runs')

@viol.connect('#go click')
def start(client, data):
    result = yield from foo(client)
    client.log(result)

    result = yield from bar(client)
    client.log(result)

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
