#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20130414
#  @date          20131001
#  @version       1.2 - Redesigned web crawler for more performance
#                 1.0 - Implemented for new G+ format (20130530)
#  @brief         Download(backup) Google plus videos
# from __future__ import print_function

import urllib, urllib2
import os
import contextlib
import re
import datetime

from collections import OrderedDict

from lxml import etree
from StringIO import StringIO

class GplusVideoCrawler:
    stop_download = False

    def __init__(self):
        # 1st is video key. 2nd is photo url
        # video regx  (url: http://redirector.googlevideo.com/videoplayback?id)
        self.video_regx = re.compile(r",\[.*\"(http:\/\/redirector.googlevideo.com\/videoplayback\?id\\u003d(.*)\\u0026itag.*)\"\]")

    def _get_raw_page(self, uid):
        #uid = '110216234612751595989'
        #uid = '105835152133357364264'
        url = 'https://plus.google.com/u/0/photos/{0}/albums/posts'.format(uid)
        url = 'https://plus.google.com/u/0/_/photos/pc/read/?soc-app=2'

        headers = {
         'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }

        url_param = {
                '_reqid': '',    # 會隨著新的page down而變，例： 1381406，但空字串也能過
                'avw': 'phst:31',
                'cid': '0',
                'f.sid': '',   # 依成員不同，可以從原始碼的  var OZ_afsid =  拿到，固定的。但空值也能過
                'ozv': 'es_oz_20130915.11_p1',  #固定的，但空值也能過
                'rt': 'j',
                'soc-app': '2',
                'soc-platform': '1',
                'f.req': ('[["posts",null,null,"synthetic:posts:{0}",3,"{0}",null],[100,1,null],""]'.format(uid))
                   # 300, 1 代表拿幾筆  哈哈 ，爽
                   # 有兩個成員編號，改後面那個可以拿到該成員的，改前面的好像沒用。
                   # 包在編號中間的那個3，只能是3，其它值會error
                   # 沒有 KdfhXsCrAAAAMUJEiTfmsYNROABBsbIb6-axg1FNAACAP1DBwAtaLXNoYTE6OGZlNTYzNGNhZWRkOGEyYTQ4ZDA0NTM0ZWI0ZmZhYjAyOGU0OGUyZIgBzti70-YnqQHmsYNRAAAAALEBN7QCAAAAAAC6AQd1cGRhdGVz
                   # 也能抓，不過只有最一開始的那一頁
        }
        req = urllib2.Request(
                url = url,
                data = urllib.urlencode(url_param),
                headers = headers
        )

        return req

    def get_url_context(self, uid, is_new_first):
        page_req = self._get_raw_page(uid)

        with contextlib.closing(urllib2.urlopen(page_req)) as web_page:
            if web_page.getcode() != 200:
                web_page.close()
                return None

            html_context = web_page.read()
            web_page.close()

            # myparser = etree.HTMLParser(encoding="utf8")
            # context_tree = etree.HTML(html_context, parser=myparser)
            # parse_result = context_tree.xpath('//script/text()')


            url_list = self.video_regx.findall(html_context)

            ### remove duplicate video and get url of best quality video ###
            urls = {}
            for url in url_list:
                urls[url[1]] = url[0].decode('unicode_escape')
            ###-remove

            return urls.values()

            # video = OrderedDict(zip([key[1] for key in url], [key[0] for key in url]))

            # if not(is_new_first):
            #     temp_order = video.items()
            #     temp_order.reverse()
            #     video = OrderedDict(temp_order)

            # return video.values()

    def main(self, uid, is_new_first):
        urls = self.get_url_context(uid, is_new_first)
        if urls:
            # Create folder
            if not os.path.isdir(uid):
                os.mkdir(uid)

            old_filename = ''
            count = 1


            for url in urls:
                if self.stop_download:
                    break

                download_url, filename = url, 'video'

                # if datetime.datetime.strptime(filename, "%Y%m%d") < datetime.datetime.strptime(start_date.isoformat(), "%Y-%m-%d"):
                    # break

                print("Downloading: {0}".format(filename))

                if filename == old_filename:
                    new_filename = "{0}_{1}".format(filename, count)
                    count+=1
                else:
                    new_filename = filename
                    count = 1

                if os.path.isfile("{0}{1}{2}.3gp".format(uid, os.sep, new_filename)):
                    print('File Existence')
                    old_filename = filename
                    continue

                urllib.urlretrieve(download_url, "{0}{1}{2}.3gp".format(uid, os.sep, new_filename))
                old_filename = filename

            return '========== Success =========='
        else:
            return 'Bad connection'

if __name__ == '__main__':
    my_tester = GplusVideoCrawler()
    my_tester.main('111907069956262615426', True)