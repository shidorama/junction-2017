from urllib.parse import urlencode

import requests
import lxml.html as html

url_string = 'https://www.ebay.com/sch/i.html?_from=R40&%s&_sacat=0&LH_ItemCondition=3000'
def get_price(name):
    data = requests.get(get_url(name))
    x=data.content
    tree  = html.fromstring(x)
    try:
        count = int(tree.find_class('rcnt')[0].text)
        if count > 0:
            price = tree.find_class('prc')[0].find_class('bold')[0].text.split()[0]
        else:
            price = None
    except IndexError as e:
        return None
    except AttributeError as e:
        return None
    return price

def get_url(item):
    enc_item = urlencode({'_nkw': item})
    return url_string % enc_item
