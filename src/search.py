from basic import *

def search(headers, session, query_text, page_number=1, thread_id=0):
    """搜索指定页码的文章

    Args:
        headers (dict): 请求头
        session (requests.Session): 会话
        query_text (str): 搜索关键词
        pageNumber (int, optional): 页码. Defaults to 1.

    Returns:
        records: 文章记录列表
        if page_number == 1: 返回文章列表，总文章数，总页数
    """
    url = 'https://ieeexplore.ieee.org/rest/search'
    data = {
        "newsearch": True, 
        "queryText": query_text, 
        "highlight": True, 
        "returnType": "SEARCH", 
        "matchPubs": True,
        "pageNumber": str(page_number),
        "rowsPerPage": "100",
        "returnFacets": ["ALL"]
    }
    logger.info(f'thread {thread_id}:Search {query_text} {page_number}')
    res = request(headers, session, url, params=None, data=data, thread_id=thread_id)
    if res is None:
        logger.error(f"thread {thread_id}:Search {query_text} {page_number} failed")
        return None
    res_json = res.json()
    records = res_json.get('records',[])

    if page_number == 1:
        total_pages = res_json['totalPages']
        total_records = res_json['totalRecords']
        return records, total_records, total_pages

    return records

def get_search_res(headers, session, recordCfgf:str, keyword:str=None, thread_id=0):
    """
    从搜索结果中获取文章信息,并保存到csv文件中
    在单线程下工作,多线程下每个线程用不同的keyword
    Args:
        headers (dict): 请求头
        session (requests.Session): 会话
        recordCfgf (str): .json文件,用于统计搜索结果
        keyword (str): 搜索关键词
    """
    csvHeader = True
    page, lastindex = 1, -1
    base_url = 'https://ieeexplore.ieee.org'
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
            records, totalRecords, max_page = search(headers,session, query_text=keyword, page_number=page, thread_id=thread_id)
            if totalRecords == 0:
                logger.warning(f'thread {thread_id}:We were unable to find results for {keyword}')
                break
            logger.info (f'thread {thread_id}:Key word: \"{keyword}\" found {totalRecords} results in {max_page} pages')
            # save recordCfg
            recordCfg['max_page'] = max_page
            recordCfg['total_records'] = totalRecords
            saveJson(recordCfgf, recordCfg)
        else:
            records = search(headers, session, query_text=keyword, page_number=page, thread_id=thread_id)
        # save csv
        for index,record in enumerate(records):
            if index <= lastindex:
                continue
            articleTitle = record['articleTitle']
            doi = record.get('doi')
            if record.get('pdfLink') is None:
                continue
            pdfLink = base_url + record['pdfLink']
            # logger.info(f'thread {thread_id}:Collecting Page {page} Index {index}: {articleTitle}')
            result = {'Page':page, 'Index':index, 'Title':articleTitle, 'DOI':doi, 'PDFLink':pdfLink, 'Downloaded':'0'}
            df = pd.DataFrame(result,index=[0])
            df.to_csv(recordf, mode='a', index=False, header=csvHeader, encoding='utf_8_sig')
            csvHeader = False
        page += 1
        lastindex = -1
    logger.info(f'thread {thread_id}:Get all {keyword} results')