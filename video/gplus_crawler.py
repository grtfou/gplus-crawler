#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20130414
#  @date          20131002
#  @version       1.3 - New method for download fast
#                 1.2 - Redesigned web crawler for more performance
#                 1.0 - Implemented for new G+ format (20130530)
#  @brief         Download(backup) Google plus videos
# from __future__ import print_function

import urllib, urllib2
import os
import contextlib
import re
import sys
from collections import OrderedDict

class GplusVideoCrawler:
    stop_download = False

    def __init__(self):
        # inside quote is video key. Outside quote is photo url
        # video regx  (url: http://redirector.googlevideo.com/videoplayback?id)
        self.video_regx = re.compile(r",\[.*\"(http:\/\/redirector.googlevideo.com\/videoplayback\?id\\u003d(.*)\\u0026itag.*)\"\]")
        # get date regx
        self.date_regx = re.compile(r".*,\"([0-9_]+).mp4\",500,,")

        # photo regx
        self.photo_regx = re.compile(r",.*\[\"https:\/\/picasaweb.*\/(.*)#.*\[\"(.*)\"")

    def _get_raw_page(self, uid):
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
                   # 300, 1 代表拿幾筆
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

            # if use LXML
            # myparser = etree.HTMLParser(encoding="utf8")
            # context_tree = etree.HTML(html_context, parser=myparser)
            # parse_result = context_tree.xpath('//script/text()')

            video_list = self.video_regx.findall(html_context)
            date_list = self.date_regx.findall(html_context)
            photo_list = self.photo_regx.findall(html_context)

            ### remove duplicate video and get url of best quality video ###
            urls = {}
            for url in video_list:
                urls[url[1]] = url[0].decode('unicode_escape')
            ###-remove

            video_urls = OrderedDict(zip(date_list, urls.values()))

            # Sort by date
            if not(is_new_first):
                temp_order = video_urls.items()
                temp_order.reverse()
                video_urls = OrderedDict(temp_order)

            return photo_list, video_urls

    ##
    #  @brief       For photo url use. Parser url to format filename
    #  @param       (Tuple) [0] : Date
    #                       [1] : photo url
    #  @return      (String) Url
    #               (String) Filename (format by date)
    #
    def _adjust_url(self, img_url):
        url_seg = img_url[1].split('/')
        url = "%s/d/%s" % ('/'.join(url_seg[:-2]), url_seg[-1])

        try:
            if img_url[0][0] == '1':
                filename = "20{0}".format(img_url[0])[:8]
            else:
                filename = img_url[0][:8]   # ex. 20130101
        except:
            filename = img_url[0]

        return url, filename

    def _report_hook(self, blocknum, blocksize, totalsize):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100: percent = 100
        sys.stdout.write("\r%2d%%" % percent)
        sys.stdout.flush()
        # print "%.2f%%"% percent
        # sys.stdout.write('.{0:.2f}%'.format(percent))

    def main(self, uid, is_new_first):
        photo_list, video_urls = self.get_url_context(uid, is_new_first)

        # # Create folder
        # if not os.path.isdir(uid):
        #     os.mkdir(uid)
        # #-create

        # old_filename = ''
        # count = 1
        # download_type = 'photo'
        # if photo_list:
        #     # Create folder
        #     folder_path = '{0}{1}{2}'.format(uid, os.sep, download_type)
        #     if not os.path.isdir(folder_path):
        #         os.mkdir(folder_path)
        #     #-create

        #     for url in photo_list:
        #         if self.stop_download:
        #             break

        #         download_url, filename = self._adjust_url(url)

        #         print("Downloading: {0}".format(filename))

        #         if filename == old_filename:
        #             new_filename = "{0}_{1}".format(filename, count)
        #             count += 1
        #         else:
        #             new_filename = filename
        #             count = 1

        #         urllib.urlretrieve(download_url, "{0}{1}{2}.jpg".format(folder_path, os.sep, new_filename))
        #         old_filename = filename

        # ############################
        # return
        old_filename = ''
        count = 1
        download_type = 'video'
        if video_urls:
            # Create folder
            folder_path = '{0}{1}{2}'.format(uid, os.sep, download_type)
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
            #-create

            for video_date, download_url in video_urls.iteritems():
                if self.stop_download:
                    break

                filename = video_date.split('_')[0]
                print("Downloading: {0}".format(filename))


                ### if one day has two videos  ###
                if filename == old_filename:
                    new_filename = "{0}_{1}".format(filename, count)
                    count += 1
                else:
                    new_filename = filename
                    count = 1
                ###-if
                old_filename = filename

                ### Avoid download the same video by filename ###
                if os.path.isfile("{0}{1}{2}.3gp".format(folder_path, os.sep, new_filename)):
                    print('File Existence: {0}'.format(new_filename))
                    continue
                ###-avoid

                # Download
                urllib.urlretrieve(download_url, "{0}{1}{2}.3gp".format(folder_path, os.sep, new_filename), self._report_hook)
                print('')

            return '========== Success =========='
        else:
            return 'Bad connection'

### Unit test ###
if __name__ == '__main__':
    my_tester = GplusVideoCrawler()
    #uid = '110216234612751595989'
    #uid = '105835152133357364264'
    print(my_tester.main('111907069956262615426', True))