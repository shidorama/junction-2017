from urllib.parse import urlencode

import requests
import lxml.html as html

url_string = 'https://www.ebay.com/sch/i.html?_from=R40&%s&_sacat=0&LH_ItemCondition=3000'
def get_price(name):
    data = requests.get(get_url(name))
    x=data.content
    tree  = html.fromstring(x)
    try:
        price = tree.find_class('prc')[0].find_class('bold')[0].text
    except IndexError as e:
        return None
    return price.split()[0]

def get_url(item):
    enc_item = urlencode({'_nkw': item})
    return url_string % enc_item
