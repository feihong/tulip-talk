import tulip
import viol
from demolib import set_title, make_widget

set_title('Foo and bar run at the same time')

@viol.connect('#go click')
def start(client, data):
    task1 = tulip.Task(foo(client))
    task2 = tulip.Task(bar(client))

    while True:
        if task1.done() and task2.done():
            client.log(task1.result())
            client.log(task2.result())
            break
        else:
            yield from tulip.sleep(1)

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
