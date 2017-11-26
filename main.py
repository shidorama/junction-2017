import logging
import os
import re
import tty
from json import load

import select

import termios

import sys
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
    'E28068100000003C4E1F3E05': {
        'name': 'Box of boxes (metabox)'
    },
    'E28068100000003C4E1F3DCB': {
        "name": ""
    },
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
                if age == settings.T:
                    # and age % settings.T == 0 and online_tags[tag['tid']].get('sell_prop'):
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

def show_boxes():
    boxes = set()
    for num, name in box_reg.items():
        boxes.add(name)
    return list(boxes)

def show_items(box):
    items = []
    for uid, item in online_tags.items():
        if item['box'] == box:
            items.append(item)
    return items


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

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def reactor(cmd):
    if len(cmd) == 0:
        return
    cmd_a = cmd.split()
    cmd_a[0] = cmd_a[0].upper()
    if cmd_a[0] == 'L':
        print('Current boxes')
        for num, box in box_reg.items():
            print('%s box: %s' % (num, box))

    elif cmd_a[0] == 'B':
        if len(cmd_a) == 2:
            try:
                box_id = int(cmd_a[1])
                if box_id in box_reg:
                    print('Listing content of box "%s"' % box_reg[box_id])
                    items = show_items(box_id)
                    for num, item in enumerate(items):
                        print("#%s - %s" % (num, item['name']))
            except ValueError as e:
                pass
    elif cmd_a[0] == 'S':
        if len(cmd_a) == 2:
            search_pattern = '.*%s.*' % cmd_a[1]
            found = []
            for uid, item in online_tags.items():
                if re.match(search_pattern, item['name']):
                    found.append(item)
            print("You've searched for '%s'" % cmd_a[1])
            if found:
                print("We've found it in:")
                for item in found:
                    print('Item: "%s" in "%s"' % (item['name'], box_reg[item['box']]))



with SocketIO('balabanovo.westeurope.cloudapp.azure.com', 80, LoggingNamespace) as socketIO:
    socketIO.on('connect', on_connect)
    socketIO.on('disconnect', on_disconnect)
    socketIO.on('reconnect', on_reconnect)
    socketIO.on('inventory', inventory)
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        linebuf = []
        i = 0
        while 1:
            if isData():
                c = sys.stdin.read(1)
                if c == '\x1b':  # x1b is ESC
                    break
                if c[-1] == '\n':
                    linebuf.append(c[:-1])
                    cmd = ''.join(linebuf)
                    reactor(cmd)
                    linebuf = []
                else:
                    linebuf.append(c)
            socketIO.wait(seconds=0.2)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
