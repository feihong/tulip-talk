import tulip
import viol
from demolib import set_title, make_widget, make_widget_synchronous

set_title('Bar runs code in another thread')

@viol.connect('#go click')
def start(client, data):
    coroutines = [foo(client), bar(client)]
    for future in tulip.as_completed(coroutines):
        result = yield from future
        client.log(result)

def foo(client):
    client.log('Starting foo.')
    for i in range(8):
        widget = yield from make_widget()
        client.append_widget('foo', widget)
    return 'foo is done!'

def bar(client):
    client.log('Starting bar work in another thread.')
    loop = tulip.get_event_loop()
    widgets = yield from loop.run_in_executor(None, bar_synchronous)
    for widget in widgets:
        client.append_widget('bar', widget)
    return 'bar is done!'

def bar_synchronous():
    widgets = []
    for i in range(12):
        widget = make_widget_synchronous()
        widgets.append(widget)
    return widgets

if __name__ == '__main__':
    viol.run()
