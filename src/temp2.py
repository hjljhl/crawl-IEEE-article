
import requests
from lxml import etree
import re
baseusl = "https://ieeexplore.ieee.org"
url = "https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=6276646&ref="
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}
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


session = requests.Session()

read_cookie('cookie.txt', session)

pdf = session.get(url,headers=headers)

# download pdf
pdfName = 'test.pdf'
path = '/'.join(['pdf', pdfName])


if pdf.headers['Content-Type'] == 'application/pdf':
    with open(path,'wb') as f:
        f.write(pdf.content)