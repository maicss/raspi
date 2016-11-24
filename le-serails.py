import sys
from you_get import common
import requests
import time
import random
import pickle
import os

from bs4 import BeautifulSoup as bs


if os.path.isfile('zhenhuan-url-list.txt'):
    with open('zhenhuan-url-list.txt', 'r') as f:
        url_list = pickle.loads(f.read())
        for i in url_list:
            common.output_filename = i["output_filename"]
            common.any_download(i["url"])
            time.sleep(2)
else:

    if len(sys.argv) > 2:
        print('只需要一个url参数')
    try:
        assert isinstance(sys.argv[1], str)
    except (IndexError, AssertionError):
        print('请给出第一集的页面地址后重试')
        # print('请给出电视剧的原始提供商的展示页面后重试')
    
    serial_home_url = sys.argv[1]
    
    
    def get_all_video_urls():
        first = requests.get(serial_home_url)
        
        soup = bs(first.text, 'lxml')
        
        script_str = soup.find('script', attrs={"type": "text/javascript"}).text
        params = {
            'cid': int(script_str[script_str.find('cid:') + len('cid:'): script_str.find('pid')].strip()[:-1]),  # 频道ID
            'id': int(script_str[script_str.find('pid:') + len('pid:'): script_str.find('vid')].strip()[:-1]),  # 专辑ID
            'vid': int(script_str[script_str.find('vid:') + len('vid:'): script_str.find('search_word')].strip()[:-1]),
            'platform': 'pc',
            'vip': 0,
            'type': 'episode',
            '_': int(time.time()),
            'callback': 'jQuery' + str(random.random()) + '_' + str(time.time())
        }
        
        # 获取所有剧集的ID
        
        video_id_list_url = 'http://d.api.m.le.com/apipccard/dynamic'
        
        video_id_list_r = requests.get(video_id_list_url, params=params)
        
        video_id_list = video_id_list_r.json()
        
        return video_id_list['data']['episode']['videolist']
    
    with open('zhenhuan-url-list.txt', 'w') as f:
        f.write(pickle.dumps([{"output_filename": i["title"] + ' - ' + i["subTitle"] + '.mp4', "url": i["url"]}
                              for i in get_all_video_urls()]))


