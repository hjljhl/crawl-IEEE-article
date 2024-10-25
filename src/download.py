from basic import *

def download(headers, session, url:str, articleTitle:str, save_dir:str,thread_id=0):
    """
    下载指定url下的pdf(由于JavaScript的原因,无法直接获取pdf的url
    需要先获取pdf的网页,再从网页中获取pdf的url,再下载pdf)

    Args:
        headers (dict): 请求头
        session (requests.Session): 会话
        url (str): pdf的url
        articleTitle (str): 文章标题
        save_path (str): 保存路径
        thread_id (int, optional): 线程id. Defaults to 0.
    """
    # download pdf
    pdfName = re.sub(r'[\\/|:*?"<>{}$]','',articleTitle) + '.pdf'
    path = '/'.join([save_dir, pdfName])
    # path = '/'.join(["G:/", save_dir, pdfName])
    # get pdf link
    logger.info(f'thread {thread_id}:Getting {articleTitle} pdf link')
    res = request(headers, session, url, thread_id=thread_id)
    if res is None:
        logger.error(f'thread {thread_id}:Failed to get {articleTitle} pdf link')
        return False
    html = etree.HTML(res.text)
    if len(html.xpath('//iframe[@src and @frameborder]')) == 0:
        print(html.text)
    else:
        pdf_link = html.xpath('//iframe[@src and @frameborder]/@src')[0]

    # download pdf
    logger.info(f'thread {thread_id}:Downloading {articleTitle} pdf')
    pdf = request(headers, session, pdf_link, thread_id=thread_id)
    if pdf is None:
        logger.error(f'thread {thread_id}:Failed to download {articleTitle} pdf')
        return False
    if pdf.headers['Content-Type'] == 'application/pdf':
        with open(path,'wb') as f:
            f.write(pdf.content)
        return True
    
def batch_download(headers, session, recordCfgf:str, start_id=0, thread_id=0):
    """
    从recordCfgf中读取记录csv文件,指定下载的起始id,依次下载pdf
    下载后将记录csv文件中的Downloaded字段置为1

    Args:
        headers (dict): 请求头
        session (requests.Session): 会话
        recordCfgf (str): json路径 
        start_id (int, optional): .json文件中下载索引. Defaults to 0.
        thread_id (int, optional): 线程id. Defaults to 0.
    """

    # read recordcfg
    recordCfg = loadJson(recordCfgf)
    recordf = recordCfg['recordf']
    pdfdir = recordCfg['pdfdir']
    if not os.path.exists(pdfdir):
    # if not os.path.exists("G:/"+pdfdir):
        os.mkdir(pdfdir)
        # os.makedirs("G:/"+pdfdir)
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
        logger.info(f'thread {thread_id}:Downloading PDF of Page {oneitem["Page"]} Index {oneitem["Index"]}: {oneitem["Title"]}')
        pdftitle = oneitem["Title"]
        if download(headers, session, pdflink, pdftitle, pdfdir, thread_id=thread_id):
            logger.success(f'thread {thread_id}:PDF download success:{oneitem["Title"]}')
            oneitem['Downloaded'] = '1'
            csvContNew[i] = oneitem
            with open(recordf, 'w', encoding='utf_8_sig',newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csvreader.fieldnames) 
                writer.writeheader()  
                writer.writerows(csvContNew)
            cnt += 1
            logger.success(f'thread {thread_id}:A total of {cnt} papers downloaded')
        else:
            logger.error(f'thread {thread_id}:PDF download failed:{oneitem["Title"]}')
            return False
    logger.success(f'thread {thread_id}:All papers downloaded')