import os,re
import requests
from loguru import logger
import json,csv
import pandas as pd
from selenium import webdriver
from lxml import etree
import time

import threading

def loadJson(fname):
    with open(fname,'r') as load_f:
        load_param = json.load(load_f)
    return load_param

def saveJson(fname, cont):
    # 如果要保存的文件不存在，创建文件
    # if not os.path.exists(os.path.dirname(fname)):
    #     os.makedirs(os.path.dirname(fname))
    # 如果 fname 以 .json 或 .csv 结尾， 保存到index文件夹
    # if re.match(r'.*\.json$', fname):
    #     fname = os.path.join('index/', fname)
    # # 如果以 .pdf 结尾，保存到pdfs文件夹
    # if re.match(r'.*\.pdf$', fname):
    #     fname = os.path.join('pdfs/', fname)
    with open(fname, 'w') as fp:
        json.dump(cont, fp, indent=4)


def read_cookie(file, session):
    with open(file, 'r') as f:
        cookie_str = f.read()
    # 创建一个空字典来存储 cookie
    cookies = {}
    # 将 cookie 字符串分割成多个键值对
    cookie_pairs = cookie_str.split(";")
    # 遍历每个键值对，将键和值分割开来，并存储在字典中
    for pair in cookie_pairs:
        key_value = pair.strip().split("=")
        if len(key_value) == 2:
            key, value = key_value
            cookies[key] = value
    session.cookies.update(cookies)



def request(headers, session, url, params=None, data=None, file='cookie.txt', thread_id=0):
    """模拟浏览器发送请求，返回响应

    Args:
        headers (dict): 请求头
        session (requests.Session): 会话
        url (str): 请求的url
        params (dict, optional): get请求的params参数. Defaults to None.
        data (dict, optional): post请求的data参数. Defaults to None.
        file (str): cookie文件路径. Defaults to 'cookie.txt'.
        thread_id (int, optional): 线程id. Defaults to 0.
    Returns:
        if res.status_code == 200: 返回响应
        else: return None
    """
    try:
        if data is not None:
            res = session.post(url=url, headers=headers, json=data, allow_redirects=False)
        else:
            res = session.get(url=url, headers=headers, params=params, allow_redirects=False)
        if res.status_code == 200:
            return res
        else:
            logger.error(f"thread {thread_id}: Request to {url} failed with status code {res.status_code}")
            return None
    except Exception as e:
        logger.error(f"thread {thread_id}:Request to {url} failed: {str(e)}")
        return None
    


