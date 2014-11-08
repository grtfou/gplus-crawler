#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20130414
#  @date          20141108 - import Requests for fixing ssl bug issue.
'''
Download photo or videos from google plus
'''

import urllib
import urllib2
import contextlib
import os
import re
import sys
import logging
import requests

''' Test debug code
import ssl
import httplib
from functools import partial
class fake_ssl:
    wrap_socket = partial(ssl.wrap_socket, ssl_version=ssl.PROTOCOL_SSLv3)

httplib.ssl = fake_ssl
'''

logging.basicConfig(level=logging.DEBUG, filename='debug.log')

class GplusCrawler(object):
    stop_download = False

    def __init__(self):
        ### video regex ###
        # (url: http://redirector.googlevideo.com/videoplayback?id)
        # g+ source code
        regx_txt = r".*(https://redirector\.googlevideo\.com.*)\"\]$"
        self.video_regx = re.compile(regx_txt)

        regx_txt = r".*(20[0-9]{1}[0-9]{1}/[0-1][0-9]/[0-3][0-9]).*"
        self.date_regx = re.compile(regx_txt)

        ### photo regex ###
        # old regex
        regx_txt = r"^,.*https://picasaweb.google.com/[0-9]*/([0-9]*)#.*\[\"(https://.*)\".*\]$"
        self.photo_regx = re.compile(regx_txt)

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
        }
        req = urllib2.Request(
                url = url,
                data = urllib.urlencode(url_param),
                headers = headers
        )

        return req

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

    def _download(self, url, filename):
        # urllib.urlretrieve(url, filename, self._report_hook)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as o_file:
                for chunk in r.iter_content(1024):
                    o_file.write(chunk)
        else:
            print('Visit website fail')


    ##
    #  @brief       Get urls by raw html and download
    #  @param       (String) uid
    #               (String) download photo or video
    #
    def _get_url_context(self, uid, d_type):
        page_req = self._get_raw_page(uid)

        with contextlib.closing(urllib2.urlopen(page_req)) as web_page:
            if web_page.getcode() != 200:
                web_page.close()
                return None, None

            date_list = ""
            video_list = ""
            count = 1
            old_filename = ""

            for line in web_page:
                line = line.strip()

                ### photo or video ###
                if d_type == "video":
                    new_video = self.video_regx.match(line)
                    new_date = self.date_regx.match(line)

                    if new_video:
                        video_list = new_video

                    if new_date:
                        date_list = new_date


                    if date_list and video_list and line == ']':
                        filename = date_list.group(1).replace('/','-') + ".mp4"
                        video_url = video_list.group(1).replace('\u003d', '=').replace('\u0026', '&')
                        print(filename)
                        filename = '{0}{1}video{1}{2}'.format(uid, os.sep, filename)

                        self._download(video_url, filename)

                        video_list = ""
                        date_list = ""
                        print("\n")
                elif d_type == "photo":
                    new_photo = self.photo_regx.match(line)
                    if new_photo:
                        filename = ""
                        if len(new_photo.group(1)) > 8:
                            filename = new_photo.group(1)[:8] + "-" + new_photo.group(1)[8:]
                        else:
                            filename = new_photo.group(1)

                        print(filename)
                        if filename == old_filename:
                            filename += "_{}".format(count)
                            count += 1
                        else:
                            count = 1
                            old_filename = filename

                        filename = '{0}{1}photo{1}{2}'.format(uid, os.sep, filename)
                        photo_url = new_photo.group(2)
                        # urllib.urlretrieve(photo_url, filename + ".jpg", self._report_hook)
                        self._download(photo_url, filename + ".jpg")

                        print("\n")
            ###-

                if self.stop_download:
                    self.stop_download = False
                    break

    ##
    #  @brief       Main function
    #  @param       (Integer) user id
    #               (String) photo / video
    #  @return      (String) program status
    #
    def main(self, uid, d_type='photo'):
        # Create folder
        if not os.path.isdir(uid):
            os.mkdir(uid)

        video_path = '{}{}video'.format(uid, os.sep)
        if not os.path.isdir(video_path):
            os.mkdir(video_path)
        pic_path = '{}{}photo'.format(uid, os.sep)
        if not os.path.isdir(pic_path):
            os.mkdir(pic_path)
        ###-

        try:
            self._get_url_context(uid, d_type)
            return '========== Success =========='
        except:
            logging.exception("Error !! Error:{}, {}".format(str(uid), d_type))
            return 'Connection Fail'
