# coding: utf-8
import os
import pickle
import random
import sys
import time

import requests
from bs4 import BeautifulSoup as bs

from you_get import common


def down(urls):
    for i in urls:
        if not i.get('cached'):
            common.output_filename = i["output_filename"]
            try:
                t0 = time.time()
                common.any_download(i["url"], stream_id='1080p')
                print("total: " + str(len(urls)))
                print(" 耗时：" + str(int(time.time() - t0)))
            except Exception:
                print(i["output_filename"] + ' 下载失败')
                with open('le-url-cache', 'rb') as f:
                    f.write(pickle.dumps(urls))
            i['cached'] = True
            time.sleep(2)


if os.path.isfile('le-url-cache'):
    with open('le-url-cache', 'rb') as f:
        url_list = pickle.loads(f.read())
        down(url_list)

else:

    if len(sys.argv) > 3:
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

        script_str = soup.find(
            'script', attrs={"type": "text/javascript"}).text

        params = {
            # 频道ID
            'cid': int(script_str[script_str.find('cid:') + len('cid:'): script_str.find('pid')].strip()[:-1]),
            # 专辑ID

            'id': int(script_str[script_str.find('pid:') + len('pid:'): script_str.find('vid')].strip()[:-1]),

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


    urls = get_all_video_urls()

    pick_urls = [{
                     "output_filename": i["title"] + ' - ' + i["subTitle"] + '.mp4',
                     "url": i["url"]

                 } for i in urls]

    with open('le-url-cache', 'wb') as f:
        f.write(pickle.dumps(pick_urls))

    down(pick_urls)
