from search import *
from download import *
from loguru import logger
from bug_repair import *

def create_sessions(num_sessions):
    sessions = []
    for _ in range(num_sessions):
        session = requests.Session()
        read_cookie('cookie.txt', session)
        sessions.append(session)
    return sessions

def main_search(headers, session, recordCfgf, keyword, thread_id=0):
    get_search_res(headers, session, recordCfgf, keyword, thread_id)

def main_download(headers, session, recordCfgf, start_id, thread_id=0):
    batch_download(headers, session, recordCfgf, start_id, thread_id)

def read_keywords(filename='keywords.txt'):
    with open(filename, 'r') as f:
        keywords = f.read()
    # 每行，形成列表
    keywords_list = keywords.split('\n')
    return keywords_list

def update_proxy(proxy_num):
    proxy_num += 1
    if proxy_num >= 15:
        proxy_num = 0
    return proxy_num

def main():
    headers = {
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    }
    # keywords.txt中每行为一个搜索关键词
    keywords_list = read_keywords('keywords.txt')
    search_session_num = len(keywords_list)
    search_threads = []
    search_sessions = create_sessions(search_session_num)
    for id, session in enumerate(search_sessions):
        thread = threading.Thread(target=main_search, args=(headers, session, keywords_list[id]+'.json', keywords_list[id], id))
        search_threads.append(thread)
        thread.start()
    for thread in search_threads:
        thread.join()
    for session in search_sessions:
        session.close()
    
    # record pigcha location
    location = record_location(2)
    proxy_num = 0
    # download 
    download_session_num = len(keywords_list)
    download_threads = []
    download_sessions = create_sessions(download_session_num)

    while True:
        download_threads = []
        for id, session in enumerate(download_sessions):
            thread = threading.Thread(target=main_download, args=(headers, session, keywords_list[id]+'.json', 0, id))
            download_threads.append(thread)
            thread.start()
        for thread in download_threads:
            thread.join()

        bug_repair(location,proxy_num)
        proxy_num = update_proxy(proxy_num)

        time.sleep(2)



    # for session in download_sessions:
    #     session.close()
    




    

if __name__ == '__main__':
    logger.add("runtime_{time:YYYY-MM-DD_HH-mm}.log")       # 创建一个文件名为runtime的log文件
    main()