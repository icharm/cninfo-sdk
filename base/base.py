# -*- coding: UTF-8 -*- 
import http.client
import urllib
import json

from base import config
from base import log
from base import cache

log = log.Log(__name__)

def token():
    '''Main entrance to get access_token, first, get token from cache file
    if token is '', then update it from service.
    '''
    token = cache.get(config.token)
    if token.strip() == '':
        token = token_service()
    return token

def token_service():
    '''Get access_token form service and update it into cache.
    '''
    url = 'http://webapi.cninfo.com.cn/api-cloud-platform/oauth2/token'
    params = {
        'grant_type' : 'client_credentials',
        'client_id' : config.access_key,
        'client_secret' : config.access_sercet
    }
    paramsbyte = bytes(urllib.parse.urlencode(params), 'utf8')
    response = urllib.request.urlopen(url, paramsbyte)
    respContent = response.read()
    dataDict=json.loads(respContent)
    token=dataDict['access_token']
    cache.set(config.token, token)
    return token

def call(url, params):
    '''Main function to call cninfo services.
    Args:
        url: api url. String
        params: request params. Dict
    Returns:
        if service return code is not 200, then return ''.
        if call service success, then return response Json string.
    '''
    params['access_token'] = token()
    paramsbyte = bytes(urllib.parse.urlencode(params), 'utf8')
    response = urllib.request.urlopen(config.base_url+url, paramsbyte)
    respContentStr = response.read()
    respContent = json.loads(respContentStr)
    respCode = respContent['resultcode']
    if respCode == 401 or respCode == 404 or respCode == 405:
        log.debug('Token invalid. Updating it from service')
        token_service()
        return call(url, params)
    elif respCode != 200:
        log.error('Api调用出错：' + respContent['resultmsg'])
        return ''
    else:
        return respContentStr

def call_cache(fileName, url, params):
    '''Before call service, get data from cache first, if not data from cache, 
    then call service and cache it.
    Args: 
        fileName: cache file name.
        url: service api url.
        params: request params. Dict
    Returns:
        Response content: Json String
        if not any data from cache and service, then return ''.
    '''
    respContent = cache.getWithParams(fileName, params)
    if respContent != '' and config.enable_cache:
        log.debug('Return cache data, from :' + cache.spliceFileName(fileName, params))
        return respContent
    respContent = call(url, params)
    if respContent != '':
        cache.setWithParams(fileName, params, respContent)
    return respContent
        
    

