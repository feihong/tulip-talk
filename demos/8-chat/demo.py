import cgi
import random
from viol import connect, app

app.index_page = 'index.lim'

COLORS = ('chocolate', 'coral', 'crimson', 'firebrick', 'fuchsia', 'goldenrod',
    'indigo', 'magenta', 'maroon', 'navy', 'olive', 'orchid', 'peru', 'plum',
    'salmon', 'sienna', 'tan', 'teal', 'thistle', 'tomato',)

# Dict where keys are client objects, values are tuples of the form
# (username, color).
userdata = {}

@connect('div#signin form submit')
def signin(client, data):
    username = data['username']
    color = random.choice(COLORS)
    userdata[client] = (username, color)

    client.hide('div#signin')
    client.show('div#chat')
    broadcast(username + ' entered the room.', color)
    client.jquery('input[name=message]', 'focus')

@connect('div#chat form submit')
def talk(client, data):
    username, color = userdata[client]
    client.set_val('input[name=message]', '')
    broadcast(username + ': ' + data['message'], color)

@connect('connection_lost')
def logoff(client, data):
    username, color = userdata.get(client)
    if username:
        del userdata[client]
        broadcast(username + ' left the room.', color)

def broadcast(message, color):
    message = cgi.escape(message)
    for client in userdata.keys():
        client.append_html('#messages', '<p style="color: {}">{}</p>'.format(
            color, message))

if __name__ == '__main__':
    app.run()
