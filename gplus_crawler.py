#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20130414
#  @date          20131002
#  @version       1.3 - New method for download fast
#                 1.2 - Redesigned web crawler for more performance
#                 1.0 - Implemented for new G+ format (20130530)
#  @brief         Download(backup) Google plus videos
# from __future__ import print_function

import urllib
import urllib2
import contextlib
import os
import re
import sys
from collections import OrderedDict

class GplusVideoCrawler(object):
    stop_download = False

    def __init__(self):
        # inside quote is video key. Outside quote is photo url
        # video regx  (url: http://redirector.googlevideo.com/videoplayback?id)
        self.video_regx = re.compile(r",\[.*\"(http:\/\/redirector.googlevideo.com\/videoplayback\?id\\u003d(.*)\\u0026itag.*)\"\]")
        # get date regx
        # self.date_regx = re.compile(r".*,\"([0-9_]+).mp4\",500,,")
        self.date_regx = re.compile(r".*,\[1,\"http.*\/([0-9_]+).mp4")

        # photo regx
        self.photo_regx = re.compile(r",.*\[\"https:\/\/picasaweb.*\/(.*)#.*\[\"(.*)\"")

    ##
    #  @brief       Arrage request for get raw html page
    #  @param       (String) uid
    #  @return      (Object) network request
    #
    def _get_raw_page(self, uid):
        url = 'https://plus.google.com/u/0/photos/{0}/albums/posts'.format(uid)
        url = 'https://plus.google.com/u/0/_/photos/pc/read/?soc-app=2'

        headers = {
         'User-Agent':'Mozilla/5.0 (Windows NT 6.1) Gecko/20091201 Firefox/3.5.6 Chrome/16.0.912.77 Safari/535.7'
        }

        url_param = {
                '_reqid': '',
                'avw': 'phst:31',
                'cid': '0',
                'f.sid': '',
                'ozv': 'es_oz_20130915.11_p1',
                'rt': 'j',
                'soc-app': '2',
                'soc-platform': '1',
                'f.req': ('[["posts",null,null,"synthetic:posts:{0}",3,"{0}",null],[1500,1,null],""]'.format(uid))
                   # 沒有 KQryPrNyAAAAMWJDNePFPcZROABBIfsNccU9xlFNAACAP1CUqBtaLXNoYTE6NDE5MmQ2NDVjZTU2NGI5MzZiMTg5ZGUzN2MzYzg5Nzg0NDgzYmI1OYgB55OF8_YnqQHFPcZRAAAAALEBOMMGAAAAAAC6AQd1cGRhdGVz
                   # 也能抓，不過只有最一開始的那一頁
        }
        req = urllib2.Request(
                url = url,
                data = urllib.urlencode(url_param),
                headers = headers
        )

        return req

    ##
    #  @brief       Get urls by raw of html page
    #  @param       (String) uid
    #               (Boolean) For download video use. Can download lastest video first.
    #  @return      (Tuple) photo list
    #               (OrderedDict) video list
    #
    def _get_url_context(self, uid, is_new_first):
        page_req = self._get_raw_page(uid)

        with contextlib.closing(urllib2.urlopen(page_req)) as web_page:
            if web_page.getcode() != 200:
                web_page.close()
                return None, None

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

    ##
    #  @brief       For video download have download progress bar
    #  @param       (Integer) number of block
    #               (Integer) size of block
    #               (Integer) total size
    #
    def _report_hook(self, blocknum, blocksize, totalsize):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100: percent = 100
        sys.stdout.write("\r%2d%%" % percent)
        sys.stdout.flush()

    ##
    #  @brief       Main function by download photo
    #  @param       (Integer) uid
    #               (Tuple) [0]: (string) date
    #                       [1]: (string) photo urls
    #
    def _photo_download(self, uid, photo_list):
        old_filename = ''
        count = 1
        if photo_list:
            # Create folder
            folder_path = '{0}{1}{2}'.format(uid, os.sep, 'photo')
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
            #-create

            for url in photo_list:
                if self.stop_download:
                    break

                download_url, filename = self._adjust_url(url)

                print("Downloading: {0}".format(filename))

                if filename == old_filename:
                    new_filename = "{0}_{1}".format(filename, count)
                    count += 1
                else:
                    new_filename = filename
                    count = 1

                old_filename = filename
                ### Avoid download the same video by filename ###
                if os.path.isfile("{0}{1}{2}.jpg".format(folder_path, os.sep, new_filename)):
                    print('File Existence: {0}'.format(new_filename))
                    continue
                ###-avoid

                # urllib.urlretrieve(download_url, "{0}{1}{2}.jpg".format(folder_path, os.sep, new_filename))
                ### Download ###
                path = "{0}{1}{2}.jpg".format(folder_path, os.sep, new_filename)
                with contextlib.closing(urllib2.urlopen(download_url)) as response:
                    if response.getcode() == 200:
                        with open(path, 'wb') as o_f:
                            o_f.write(response.read())
                ###-download

            return 1
        else:
            return 0

    ##
    #  @brief       Main function by download video
    #  @param       (Integer) uid
    #               (OrderedDict) key:   (string) video key
    #                             value: (string) video url
    #
    def _video_download(self, uid, video_urls):
        old_filename = ''
        count = 1
        if video_urls:
            # Create folder
            folder_path = '{0}{1}{2}'.format(uid, os.sep, 'video')
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

            return 1
        else:
            return 0

    ##
    #  @brief       Main function
    #  @param       (Integer) user id
    #               (String) photo / video by download
    #               (Boolean) For download video use. Can download lastest video first.
    #
    def main(self, uid, d_type='photo', is_new_first=True):
        photo_list, video_urls = self._get_url_context(uid, is_new_first)

        # Create folder
        if not os.path.isdir(uid):
            os.mkdir(uid)

        status = 0
        # photo
        if d_type == 'photo':
            status = self._photo_download(uid, photo_list)

        # video
        if d_type == 'video':
            status = self._video_download(uid, video_urls)

        if status == 1:
            return '========== Success =========='

        return 'Connection fail'

### Unit test ###
if __name__ == '__main__':
    my_tester = GplusVideoCrawler()
    #uid = '110216234612751595989'
    #uid = '105835152133357364264'
    print(my_tester.main('111907069956262615426', 'video', False))