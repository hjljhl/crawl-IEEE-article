from crawl import *


# get_search_res(headers, session, 'lna.json', 'low noise amplifier', pageSize=3)
# batch_download(headers, session, 'lna.json', start_id=4)

get_search_res(headers, session, 'opa.json', 'operational amplifier', pageSize=100)
