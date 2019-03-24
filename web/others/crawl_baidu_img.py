import requests
import urllib.request
import urllib.parse

import os
import uuid
import json
import gzip

import threading
from io import BytesIO


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Host': 'image.baidu.com',
}

# queryWord?word????, ????urllib.parse.urlencode()????
# rn=30k, ??????30???(??)
# pn=xx, ???offset, ???offset?????30?(rn=30)??, offset?0?????30?????0, 30, 60, 120
# gsn=hex(pn).__str__()[2:], ?hex(567).__str__() => 0x237, ?????0x
# encode_img_args('???', '???', pn), pn???30???
def make_baidu_img_url(query_word: str, word: str, pn: int, rn:int=30):
    """
    ??????image????
    :param query_word: str??, ??????(???????)
    :param word: str?????????(???????)
    :param pn: int???????????, ?0??,???rn???, ?????60??60????30???
    :param rn: int???????????,??rn=30
    :return: ??????????urlencode()??????
    """
    baidu_img_url = 'https://image.baidu.com/search/acjson'
    img_args = {
        'tn': 'resultjson_com',
        'ipn': 'rj',
        'ct': '201326592',
        'is': '',
        'fp': 'result',
        'queryWord': '',   # ???????img_args['word']???, ?'??'?'NBA', ????urlencode????
        'cl': '2',
        'lm': '-1',
        'ie': 'utf-8',
        'oe': 'utf-8',
        'adpicid': '',
        'st': '-1',
        'z': '',
        'ic': '',
        'hd': '',
        'latest': '',
        'copyright': '',
        'word': '',   # ???????img_args['queryWord']???, ?'??'?'NBA', ????urlencode????
        's': '',
        'tab': '',
        'width': '',
        'height': '',
        'face': '0',
        'istype': '2',
        'qc': '',
        'nc': '1',
        'fr': '',
        'expermode': '',
        'force': '',
        'pn': '',       # ????(offset), ???30(rn=30)???, ?0, 30, 120,???????????30???
        'rn': '30',     # ????????30???
        'gsm': '0',     # gsm=hex(pn), ?????????0x, hex(pn).__str__()[2:]   => ?????0x
    }
    # ?????????
    data = img_args.update(queryWord=query_word, word=word, pn=pn, gsn=hex(pn).__str__()[2:])
    # ????URL
    return baidu_img_url + '?' + urllib.parse.urlencode(img_args)


def extract(encoding, data):
    """
    ?gzip?????????
    :param encoding: ????, ?????'gzip'
    :param data: ?????
    :return: ????????
    """
    if encoding and encoding.lower() == 'gzip':
        file = gzip.GzipFile(fileobj=BytesIO(data))
        return file.read()
    else:
        return data  # ????, ?????


def dwn_file(keyword, dwn_url):
    """
    ??????
    :param keyword: ?????./photo/<keyword>??
    :param dwn_url: ??????
    :return: ?
    """
    img_dir = "./photo" if True else './photo/{0}'.format(keyword)
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    filename = img_dir + '/' + uuid.uuid4().hex + '.jpg'
    print('type=%s, filename=%s, url=%s' % (keyword, filename.split('/')[-1], dwn_url))
    response = requests.get(dwn_url)
    with open(filename, 'wb') as f:
        f.write(response.content)


def downloads_task(keyword: str):
    """
    ?????????????????
    :param keyword: str?????????????: '??', 'NBA'? '??? ??'
    :return:
    """
    url = make_baidu_img_url(query_word=keyword, word=keyword, pn=0)
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    # ??????????
    content = extract(response.info().get('Content-Encoding', None), response.read())
    json_obj = json.loads(urllib.parse.unquote(content.decode('UTF-8')))

    for img_desc in json_obj['data']:
        try:
            if 'middleURL' in img_desc:
                dwn_url = img_desc['middleURL']
                dwn_file(keyword, dwn_url)
        except (Exception, ) as e:
            print(e, '\n', img_desc)



if __name__ == "__main__":
    thrd_list = []
    keywords_list = ('??', '??', 'NBA', '??')

    import time

    for keyword in keywords_list:
        downloads_task(keyword)
        time.sleep(2)

