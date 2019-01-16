#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    :author: HaoRongMango<me@hehaorong.vip>
    :date: 2019年1月16日05:23:33
    :desc: 本脚本用于更新DNSPOD的子域名A记录(DDNS)
"""
import re
import json
import socket
import urllib.request
import urllib.parse

import logging
from logging.handlers import  RotatingFileHandler

BASE_URL = "https://dnsapi.cn"
LOGIN_TOKEN = 'ID,TOKEN'                    # DNSPOD consle, 用户中心->安全设置->API Token

HEADERS_DICT = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    "Content-type": "application/x-www-form-urlencoded",
}


class DNSPod:

    def __init__(self, **kwargs):
        self.params = dict(login_token=LOGIN_TOKEN, format="json")
        self.params.update(kwargs)
        self.url_path = None
        self.response_json = None   # 应答内容为json格式

    def request(self, *args, **kwargs):
        self.params.update(kwargs)
        data = urllib.parse.urlencode(self.params).encode('UTF-8')
        # 生成访问URL路径
        path = re.sub(r"([A-Z][a-z]*)([A-Z][a-z]*)", r"\1.\2", self.__class__.__name__)
        self.url_path = urllib.request.urljoin(BASE_URL, path)
        # 发送URL请求并获取json数据
        request = urllib.request.Request(url=self.url_path, data=data, headers=HEADERS_DICT)
        with urllib.request.urlopen(request) as response:
            self.response_json = json.loads(response.read())

    @classmethod
    def get_current_ip(cls, format="ipv4"):
        family = socket.AF_INET if format == "ipv4" else socket.AF_INET6
        client = socket.socket(family=family, type=socket.SOCK_STREAM)
        with client:
            client.connect(("ns1.dnspod.net", 6666))
            ipaddr = client.recv(1024).decode('UTF-8')
        return ipaddr

    @classmethod
    def get_domain_ip(cls):
        return socket.gethostbyname("hehaorong.vip")

    @classmethod
    def is_need_update(cls):
        return DNSPod.get_domain_ip() != DNSPod.get_current_ip()



class DomainList(DNSPod):
    def __init__(self, *args, **kwargs):
        super(DomainList, self).__init__(*args, **kwargs)
        self.request()

    def get_domain_id(self):
        return self.response_json['domains'][0]['id']

    def get_domain_name(self):
        return self.response_json['domains'][0]['name']


class RecordList(DNSPod):
    def __init__(self, domain: DomainList, record_type='A', *args, **kwargs):
        kwargs.update(domain_id=domain.get_domain_id(), record_type=record_type)
        super(RecordList, self).__init__(*args, **kwargs)
        self.request()

    def get_record_list(self):
        """[(record_id, subdomain, ipaddr, line_id),]"""
        record_list = []
        for item in self.response_json['records']:
            record_list.append((item['id'], item['name'], item['value'], item['line_id']))
        return record_list


class RecordModify(DNSPod):
    def __init__(self, domain: DomainList, record_type='A', *args, **kwargs):
        kwargs.update(domain_id=domain.get_domain_id(), record_type=record_type)
        super(RecordModify, self).__init__(*args, **kwargs)

    def update_record(self, record: RecordList, **kwargs):
        # 构造请求, 发送请求, 检查是否需要更新
        ipaddr = DNSPod.get_current_ip()
        for item in record.get_record_list():  # [(record_id, subdomain, ipaddr, line_id), ...]
            # 更新记录
            if ipaddr != item[2]:
                kwargs.update(record_id=item[0], sub_domain=item[1], value=ipaddr, record_line_id=item[3])
                super(RecordModify, self).request(**kwargs)
                if self.response_json['status']['code'] != '1':
                    logging.error('subdomain(%s) update A record failed, info:%s.' %
                                  (item[1], self.response_json['status']['message']))
                else:
                    logging.info('subdomain(%s) update success.' % item[1])


def logger_init():
    # 创建回滚文件处理器
    file_handler = RotatingFileHandler('dnspod.log', maxBytes=10 * 1024 * 1024, backupCount=1)
    # 设置日志输出格式
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] [line:%(lineno)d] %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        handlers=(file_handler, )
                        )


def ddns_handler():
    if DNSPod.is_need_update():
        logging.info('------------------ update domain begin ---------------------------------')
        logging.info('current domain ip:%s, new ip addr:%s' % (DNSPod.get_domain_ip(), DNSPod.get_current_ip()))
        # 获取域名、记录信息
        domain = DomainList()
        record = RecordList(domain)
        # 更新记录
        setter = RecordModify(domain)
        setter.update_record(record)
        logging.info('------------------ update domain end ---------------------------------')
    else:
        logging.info('Domain IP:%s, not changed!' % (DNSPod.get_domain_ip(), ))


if __name__ == "__main__":
    logger_init()
    ddns_handler()





