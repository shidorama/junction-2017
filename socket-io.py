from socketIO_client import SocketIO, LoggingNamespace

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
        print(data['orderedRecords'])


with SocketIO('balabanovo.westeurope.cloudapp.azure.com', 80, LoggingNamespace) as socketIO:
    socketIO.on('connect', on_connect)
    socketIO.on('disconnect', on_disconnect)
    socketIO.on('reconnect', on_reconnect)
    socketIO.on('inventory', inventory)
    socketIO.wait(seconds=1000)