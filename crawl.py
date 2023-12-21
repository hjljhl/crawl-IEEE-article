from bs4 import BeautifulSoup
from selenium import webdriver
import requests,time,re,os,warnings
import pandas as pd
from lxml import etree
from loguru import logger
warnings.filterwarnings('ignore')
import csv, json


def loadJson(fname):
    with open(fname,'r') as load_f:
        load_param = json.load(load_f)
    return load_param

def saveJson(fname, cont):
    with open(fname, 'w') as fp:
        json.dump(cont, fp, indent=4)


def read_cookie(headers):
    # read cookie
    with open('cookie.txt','r',encoding='utf-8') as f:
        cookie = f.read().strip()
        headers['Cookie'] = cookie


def reload_cookie(headers):
    logger.error('Cookie fail, please reload cookie!')
    os.system('mv cookie.txt .cookie.txt.bak')
    with open('cookie.txt', 'w') as f:
        f.write('')
    if input('reloaded?(enter to continue): ').strip().lower() == '':
        read_cookie(headers)


def request(headers, session, url, params=None, data=None):
    trynum = 5
    res = None
    for i in range(trynum):
        try:
            if data is not None:
                res = session.post(url, headers=headers, params=params, json=data, allow_redirects=False)
            else:
                res = session.get(url, headers=headers, params=params, json=data, allow_redirects=False)
            if res.status_code == 200:
                break
            elif res.status_code == 302:
                reload_cookie(headers)
                continue
            # else:
            #     raise Exception(res.status_code)
        except Exception as ec:
            logger.error(ec.__str__() + '(auto retry...)')
            time.sleep(1)
    if res is None:
        logger.error('request for '+url+' failed')
    return res


def search(headers, session, queryText, pageNumber=1, pageSize=100):
    # search the keyword
    url = 'https://ieeexplore.ieee.org/rest/search'
    data = {
        "newsearch": True,
        "queryText": queryText,
        "highlight": True,
        "returnType": "SEARCH",
        "matchPubs": True,
        "rowsPerPage": str(pageSize),
        "pageNumber": str(pageNumber),
        "returnFacets": [
            "ALL"
        ]
    }
    logger.debug(f'search {queryText} {pageNumber}')
    while True:
        try:
            res = request(headers, session, url, data=data)
            res_json = res.json()
            break
        except:
            reload_cookie(headers)
            continue
    records = res_json.get('records',[])
    if pageNumber == 1:
        totalPages = res_json['totalPages']
        totalRecords = res_json['totalRecords']
        return records, totalRecords, totalPages
    return records


def download(headers, session, url, articleTitle, save_directory):
    # download pdf
    pdfName = re.sub('\\|/|:|\*|\?|"|<|>|\||/',' ',articleTitle) + '.pdf'
    path = '/'.join([save_directory,pdfName])
    # get pdf link
    logger.debug(f'Getting {articleTitle} pdf link')
    while True:
        res = request(headers, session, url)
        if res.status_code == 302:
            reload_cookie(headers)
            continue
        break
    html = etree.HTML(res.text)
    pdf_link = html.xpath('//iframe[@src and @frameborder]/@src')[0]
    # download pdf
    logger.debug(f'Downloading {articleTitle} pdf')
    while True:
        pdf = request(headers, session, pdf_link)
        if res.status_code == 302:
            reload_cookie(headers)
            continue
        break
    if pdf.headers['Content-Type'] == 'application/pdf':
        with open(path,'wb') as f:
            f.write(pdf.content)
        return True


def get_search_res(headers, session, recordCfgf, keyword=None, pageSize=100):
    read_cookie(headers)
    csvHeader = True
    page, lastindex = 1, -1
    # read recordcfg
    if os.path.exists(recordCfgf):
        recordCfg = loadJson(recordCfgf)
        recordf = recordCfg['recordf']
        max_page = recordCfg['max_page']
        if keyword is None:
            keyword = recordCfg['keyword']
        if keyword != recordCfg['keyword']:
            raise('keyword mismatch')
    else:
        recordCfg = {}
        recordf = recordCfgf.split('.')[0]+'.csv'
        recordCfg['recordf'] = recordf
        recordCfg['keyword'] = keyword
        recordCfg['pageSize'] = pageSize
        recordCfg['pdfdir'] = recordCfgf.split('.')[0]+'_pdfs'
        max_page = 1
    # read csv
    if os.path.exists(recordf):
        with open(recordf, 'r', encoding='utf_8_sig') as f:
            csvreader = csv.DictReader(f)
            csvCont = list(csvreader)
        page = int(csvCont[-1]['Page'])
        lastindex = int(csvCont[-1]['Index'])
        csvHeader = False
    # running
    while page <= max_page:
        # search
        if page == 1:
            records, totalRecords, max_page = search(headers, session, keyword, pageSize=pageSize)
            if totalRecords == 0:
                logger.warning(f'We were unable to find results for {keyword}')
                break
            logger.debug(f'Key word: \"{keyword}\" found {totalRecords} results in {max_page} pages')
            # save recordCfg
            recordCfg['max_page'] = max_page
            recordCfg['total_records'] = totalRecords
            saveJson(recordCfgf, recordCfg)
        else:
            records = search(headers, session, keyword, pageNumber=page, pageSize=pageSize)
        # save csv
        for index,record in enumerate(records):
            if index <= lastindex:
                continue
            articleTitle = record['articleTitle']
            doi = record.get('doi')
            pdfLink = base_url + record['pdfLink']
            logger.debug(f'Collecting Page {page} Index {index}: {articleTitle}')
            result = {'Page':page, 'Index':index, 'Title':articleTitle, 'DOI':doi, 'PDFLink':pdfLink, 'Downloaded':'0'}
            df = pd.DataFrame(result,index=[0])
            df.to_csv(recordf, mode='a', index=False, header=csvHeader, encoding='utf_8_sig')
            csvHeader = False
        page += 1
        lastindex = -1


def batch_download(headers, session, recordCfgf, start_id=0):
    read_cookie(headers)
    # read recordcfg
    recordCfg = loadJson(recordCfgf)
    recordf = recordCfg['recordf']
    pageSize = recordCfg['pageSize']
    pdfdir = recordCfg['pdfdir']
    if not os.path.exists(pdfdir):
        os.mkdir(pdfdir)
    # read csv
    with open(recordf, 'r', encoding='utf_8_sig') as f:
        csvreader = csv.DictReader(f)
        csvCont = list(csvreader)
    csvContNew = csvCont.copy()
    cnt = 0
    for i in range(start_id, len(csvCont)):
        oneitem = csvCont[i]
        if oneitem['Downloaded']=='1':
            continue
        pdflink = oneitem['PDFLink']
        logger.debug(f'Downloading PDF of Page {oneitem["Page"]} Index {oneitem["Index"]}: {oneitem["Title"]}')
        pdftitle = oneitem["Title"]
        if download(headers, session, pdflink, pdftitle, pdfdir):
            logger.success(f'PDF download success:{oneitem["Title"]}')
            oneitem['Downloaded'] = '1'
            csvContNew[i] = oneitem
            with open(recordf, 'w', encoding='utf_8_sig') as f:
                writer = csv.DictWriter(f, fieldnames=csvreader.fieldnames) 
                writer.writeheader()  
                writer.writerows(csvContNew)
            cnt += 1
            logger.success(f'A total of {cnt} papers downloaded')


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
session = requests.Session()
base_url = 'https://ieeexplore.ieee.org'
