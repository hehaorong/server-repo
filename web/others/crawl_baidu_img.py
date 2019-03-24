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

# queryWord、word内容相同, 需要通过urllib.parse.urlencode()进行编码
# rn=30k, 表示每次获取30条数据(默认)
# pn=xx, 相当于offset, 表示从offset开始连续读30条(rn=30)数据, offset从0开始必须时30的倍数，如0, 30, 60, 120
# gsn=hex(pn).__str__()[2:], 因hex(567).__str__() => 0x237, 需要去除前0x
# encode_img_args('小黄图', '小黄图', pn), pn必须是30的倍数
def make_baidu_img_url(query_word: str, word: str, pn: int, rn:int=30):
    """
    根据参数更新image参数字典
    :param query_word: str类型, 为搜索的内容(用于数据库显示)
    :param word: str类型，为搜索的类型(用于在页面显示)
    :param pn: int类型，当前搜索的索引值, 从0开始,必须是rn的倍数, 例如该值为60则从60开始加载30条数据
    :param rn: int类型，每次查询的记录数,默认rn=30
    :return: 参数更新到字典并通过urlencode()编码进行返回
    """
    baidu_img_url = 'https://image.baidu.com/search/acjson'
    img_args = {
        'tn': 'resultjson_com',
        'ipn': 'rj',
        'ct': '201326592',
        'is': '',
        'fp': 'result',
        'queryWord': '',   # 查询关键字，与img_args['word']值相同, 如'校花'、'NBA', 必须使用urlencode进行编码
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
        'word': '',   # 查询关键字，与img_args['queryWord']值相同, 如'校花'、'NBA', 必须使用urlencode进行编码
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
        'pn': '',       # 查询偏移(offset), 必须是30(rn=30)的倍数, 如0, 30, 120,表示从该位置开始连续查30条数据
        'rn': '30',     # 表示每次连续查询30条数据
        'gsm': '0',     # gsm=hex(pn), 注意不能带有开头的0x, hex(pn).__str__()[2:]   => 避免开头的0x
    }
    # 对参数部分进行编码
    data = img_args.update(queryWord=query_word, word=word, pn=pn, gsn=hex(pn).__str__()[2:])
    # 返回完整URL
    return baidu_img_url + '?' + urllib.parse.urlencode(img_args)


def extract(encoding, data):
    """
    对gzip加密的内容进行解码
    :param encoding: 加密类型, 目前只支持'gzip'
    :param data: 解密的内容
    :return: 返回解码后的内容
    """
    if encoding and encoding.lower() == 'gzip':
        file = gzip.GzipFile(fileobj=BytesIO(data))
        return file.read()
    else:
        return data  # 类型为止, 不进行解码


def dwn_file(keyword, dwn_url):
    """
    下载文件函数
    :param keyword: 图片存放在./photo/<keyword>目录
    :param dwn_url: 待下载的图片
    :return: 无
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
    该任务负责下载关键字相关的所有图片
    :param keyword: str类型，搜索图片的关键字，如: '校草', 'NBA'， '世界杯 国足'
    :return:
    """
    url = make_baidu_img_url(query_word=keyword, word=keyword, pn=0)
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    # 若内容进行压缩则解压
    content = extract(response.info().get('Content-Encoding', None), response.read())
    json_obj = json.loads(urllib.parse.unquote(content.decode('UTF-8')))

    for img_desc in json_obj['data']:
        try:
            if 'middleURL' in img_desc:
                dwn_url = img_desc['middleURL']
                dwn_file(keyword, dwn_url)
        except (Exception, ) as e:
            print(e)
            print(img_desc)



if __name__ == "__main__":
    thrd_list = []
    keywords_list = ('帅哥', '美女', 'NBA', '国足')

    import time

    for keyword in keywords_list:
        downloads_task(keyword)
        time.sleep(2)

