from socketIO_client import SocketIO, LoggingNamespace


TTL = 3

class BoxManager(object):
    def __init__(self):
        self.tags = {}


class ItemManager(object):
    def __init__(self):
        self.tags = {}

    def check_tags(self, id):
        return id in self.tags

    def register_tag(self, id, name, photo):
        pass


skip_tags = {
    'E28068100000003C4E1FD805': [],
    'E28068100000003C4E1FD9C8': [],
    'E28068100000003C4E1FDA6C': [],
    'E28068100000003C4E1FE755': [],
    'E28068100000003C4E1F95E5': [],
    '********': []
}

prod_tags = {
    'E28068100000003C4E20212C': {
        'name': 'Mouse'},
    'E28068100000003C4E1F3E05': {},
    'E28068100000003C4E1F3DCB': {},
    'E28068100000003C4E1F7F8C': {},
    'E28068100000003C4E1F7F01': {},
    'E28068100000003C4E1F7EC7': {},
    'E28068100000003C4E1F81EF': {},
    'E28068100000003C4E1F8164': {},
    'E28068100000003C4E1F8129': {},
    'E28068100000003C4E1F939C': {},
    'E28068100000003C4E1F9311': {}
}

online_tags = {}

new_tags = []


def on_connect():
    print('connect')


def on_disconnect():
    print('disconnect')


def on_reconnect():
    print('reconnect')


def on_response(*args):
    print('on_aaa_response', args)


def inventory(data):
    if data['macAddress'] == "00:16:25:12:16:4F":
        for tag in data['orderedRecords']:
            if tag['epc'] in online_tags:
                online_tags[tag['epc']]['timeout'] = TTL
                online_tags[tag['epc']]['age'] += 1
                pass
            elif tag['epc'] not in skip_tags:
                online_tags[tag['epc']] = {'timeout': TTL, 'age': 0}
                print('New tag %s' % tag['epc'])
    for tag in list(online_tags.keys()):
        online_tags[tag]['timeout'] -= 1
        if online_tags[tag]['timeout'] < 0:
            online_tags.pop(tag)
            print('Removing tag %s' % tag )


with SocketIO('balabanovo.westeurope.cloudapp.azure.com', 80, LoggingNamespace) as socketIO:
    socketIO.on('connect', on_connect)
    socketIO.on('disconnect', on_disconnect)
    socketIO.on('reconnect', on_reconnect)
    socketIO.on('inventory', inventory)
    socketIO.wait(seconds=1000)
