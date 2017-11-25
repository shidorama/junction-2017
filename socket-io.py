import os
from socketIO_client import SocketIO, LoggingNamespace
from json import load, dump
import logging
import settings

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
log = logging.getLogger(__name__)


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
        'name': 'Mouse A4Tech K4-61X'},
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
    log.debug('disconnect')


def on_reconnect():
    log.debug('reconnect')



def inventory(data):
    if data['macAddress'] == "00:16:25:12:16:4F":
        for tag in data['orderedRecords']:
            if tag['epc'] in online_tags:
                online_tags[tag['epc']]['timeout'] = settings.TTL
                online_tags[tag['epc']]['age'] += 1
                age = online_tags[tag['epc']]['age']
                t = 20
                if age >= t and age%t==0:
                    print("Do you really need "+online_tags[tag['epc']]['name']+"? You haven\'t used it for " +str(age)+" seconds. You can sell it on ebay!")
                pass
            elif tag['epc'] not in skip_tags: #tag['epc'] in prod_tags: #
                online_tags[tag['epc']] = {'timeout': settings.TTL, 'age': 0, 'name': ''}
                if tag['epc'] in prod_tags:
                    online_tags[tag['epc']]['name'] = prod_tags[tag['epc']].get('name', '')
                print('New tag %s' % tag['epc'])
                while online_tags[tag['epc']]['name']=='':
                    print("Enter name for new item")
                    name = input()
                    online_tags[tag['epc']]['name'] = name
                #print(online_tags[tag['epc']]['name'])
    for tag in list(online_tags.keys()):
        online_tags[tag]['timeout'] -= 1
        if online_tags[tag]['timeout'] < 0:
            online_tags.pop(tag)
            log.debug('Removing tag %s' % tag )


def load_data():
    if os.path.exists(settings.DB_FILE):
        if os.path.getsize(settings.DB_FILE) > 0:
            with open(settings.DB_FILE, 'rb') as fp:
                try:
                    load(fp)
                except ValueError:
                    pass
                except IOError as e:
                    raise

with SocketIO('balabanovo.westeurope.cloudapp.azure.com', 80, LoggingNamespace) as socketIO:
    socketIO.on('connect', on_connect)
    socketIO.on('disconnect', on_disconnect)
    socketIO.on('reconnect', on_reconnect)
    socketIO.on('inventory', inventory)
    socketIO.wait(seconds=1000)
