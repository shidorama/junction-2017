import logging
import os
from json import load

from socketIO_client import SocketIO, LoggingNamespace

import settings
from ebay_poller import get_price, get_url

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
    'E28068100000003C4E1F9311': {
        'name': 'Router HUAWEI E5186'}
}

box_reg = {1: "Kitten", 2: "Yellow", 3: "Wolf", 4: "Blue"}

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
            if tag['tid'] in online_tags:
                online_tags[tag['tid']]['timeout'] = settings.TTL
                online_tags[tag['tid']]['age'] += 1
                age = online_tags[tag['tid']]['age']
                if age >= settings.T and age % settings.T == 0:
                    box_name = box_reg.get(online_tags[tag['tid']]['box'])
                    if online_tags[tag['tid']]['price'] is None:
                        online_tags[tag['tid']]['price'] = get_price(online_tags[tag['tid']]['name'])
                    print("Do you really need " + online_tags[tag['tid']][
                        'name'] + " in " + box_name + " box? You haven\'t used it for " + str(
                        age) + " seconds. You can sell it on ebay!")
                    if online_tags[tag['tid']]['price']:
                        print("We found it for %s. Check it out: %s" % (online_tags[tag['tid']]['price'], get_url(online_tags[tag['tid']]['name'])))
                pass
            elif tag['tid'] not in skip_tags:  # tag['tid'] in prod_tags: #
                online_tags[tag['tid']] = {'timeout': settings.TTL, 'age': 0, 'name': '', 'box': tag['antenna_port']}
                if tag['tid'] in prod_tags:
                    online_tags[tag['tid']]['name'] = prod_tags[tag['tid']].get('name', '')
                log.debug('New tag %s' % tag['tid'])
                # print(online_tags[tag['tid']])
                while online_tags[tag['tid']]['name'] == '':
                    print("Enter name for new item")
                    online_tags[tag['tid']]['name'] = input()
                    online_tags[tag['tid']]['age'] = 0
                    online_tags[tag['tid']]['price'] = None

                    # print(online_tags[tag['tid']]['name'])
    for tag in list(online_tags.keys()):
        online_tags[tag]['timeout'] -= 1
        if online_tags[tag]['timeout'] < 0:
            online_tags.pop(tag)
            log.debug('Removing tag %s' % tag)


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
