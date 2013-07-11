import re
from pprint import pformat
import viol

app = viol.app
app.index_page = 'index.lim'

@viol.connect('edit')
def start(client, data):
    if not data['regex'] and not data['input']:
        return

    try:
        match = re.match(data['regex'], data['input'])
        if match:
            client.set_html('#match', 'yes')
            client.set_html('#group', pformat(match.group()))
            client.set_html('#groups', pformat(match.groups()))
            client.set_html('#groupdict', pformat(match.groupdict()))
        else:
            client.set_html('#match', 'no')

        client.set_html('#error', '')
    except Exception as ex:
        client.set_html('#error', str(ex))

if __name__ == '__main__':
    app.run()
