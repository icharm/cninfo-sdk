# -*- coding: UTF-8 -*-
# Tencent stock data

import requests
import time
from tornado.httpclient import AsyncHTTPClient
from .base import log
from .sina import prefix

logger = log.Log()

base_url = 'http://data.gtimg.cn/flashdata/hushen'

def base_request(url):
    response = requests.get(url)
    if response.status_code != 200:
        logger.error('Request error url:' + url + ' ,response code: ' + str(response.status_code))
        return None
    return response.text

async def base_asyncrequest(url):
    response = await AsyncHTTPClient().fetch(url)
    if response.code != 200:
        logger.error('Request error url:' + url + ' ,response code: ' + str(response.code))
        return None
    html = response.body if isinstance(response.body, str) else response.body.decode()
    return html

# Synchronization methods
def daily_year(code, year='19'):
    '''
    Daily nodes of whole year.
    :param code: stock code
    :param year: year 19 means 2019
    :return: None or List [{'date': 1552233600000, 'open': 7.0, 'close': 7.24, 'high': 7.25, 'low': 7.0, 'volume': 698387}, ...]
    '''
    url = base_url + year + '/daily/' + prefix(code) + '.js?visitDstTime=1'
    content = base_request(url)
    if content is None:
        return None
    return parse(content)

async def daily_year_async(code, year='19'):
    url = base_url + year + '/daily/' + prefix(code) + '.js?visitDstTime=1'
    content = await base_asyncrequest(url)
    if content is None:
        return None
    return parse(content)

def daily_lately(code):
    '''
    100 daily nodes lately.
    :param code: stock code
    :return: None or List
    '''
    url = base_url + '/latest/daily/' + prefix(code) + '.js?maxage=43201&visitDstTime=1'
    content = base_request(url)
    if content is None:
        return None
    return parse(content, 2)

async def daily_lately_async(code):
    url = base_url + '/latest/daily/' + prefix(code) + '.js?maxage=43201&visitDstTime=1'
    content = await base_asyncrequest(url)
    if content is None:
        return None
    return parse(content, 2)

def weekly_lately(code):
    '''
    100 Weekly nodes lately.
    :param code: stock code
    :return: None or List
    '''
    url = base_url + '/latest/weekly/' + prefix(code) + '.js?maxage=43201&visitDstTime=1'
    content = base_request(url)
    if content is None:
        return None
    return parse(content, 2)

async def weekly_lately_async(code):
    url = base_url + '/latest/weekly/' + prefix(code) + '.js?maxage=43201&visitDstTime=1'
    content = await base_asyncrequest(url)
    if content is None:
        return None
    return parse(content, 2)


def parse(str, flag=1):
    lt = str.split('\n')[flag:-1]
    alt = []
    for item in lt:
        tmp = item.split(' ')
        tmp[5] = int(tmp[5].replace('\\n\\', ''))
        tmp[0] = time.strftime('%Y-%m-%d', time.strptime(tmp[0], '%y%m%d'))
        for i in range(1, 5):
            tmp[i] = float(tmp[i])
        alt.append({
            'date': tmp[0],
            'open': tmp[1],
            'close': tmp[2],
            'high': tmp[3],
            'low': tmp[4],
            'volume': tmp[5]
        })
    return alt

