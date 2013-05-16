# -*- coding: utf-8 -*-
import urllib
import re
import os
import datetime
import contextlib

from collections import OrderedDict

from lxml import etree

class gplus_photo_crawler:
    stop_download = False

    def __init__(self):
        # 1st is date. 2nd is photo url
        #self.url_regx = re.compile(r",\[\"https:\/\/picasaweb.*\/(.*)#.*\[\"(.*)\"")
        #http://redirector.googlevideo.com/videoplayback?id
        self.video_regx = re.compile(r",\[.*\"(http:\/\/redirector.googlevideo.com\/videoplayback\?id\\u003d(.*)\\u0026itag.*)\"\]")

    def _adjust_url(self, img_url):
        return img_url.replace('\u003d', '=').replace('\u0026', '&'), 'video'

    def get_url_context(self, id):
        #id = '110216234612751595989'
        #id = '105835152133357364264'
        url = 'https://plus.google.com/u/0/photos/{0}/albums/posts'.format(id)

        try:
            with contextlib.closing(urllib.urlopen(url)) as web_page:

                if web_page.getcode() != 200:
                    web_page.close()
                    raise

                html_context = web_page.read()
                web_page.close()

                myparser = etree.HTMLParser(encoding="utf8")
                context_tree = etree.HTML(html_context, parser=myparser)

                parse_result = context_tree.xpath('//script/text()')

                video = dict()
                for node in parse_result:
                    if node.find("key: '126'") != -1:
                        url = self.video_regx.findall(node.encode('utf8'))

                        video = OrderedDict(zip([key[1] for key in url], [key[0] for key in url]))

                        temp_order = video.items()
                        temp_order.reverse()
                        video = OrderedDict(temp_order)

                        return video.values()

            return None
        except:
            return None

    def main(self, id, start_date):
        urls = self.get_url_context(id)

        if urls:
            # Create folder
            if not os.path.isdir(id):
                os.mkdir(id)

            old_filename = ''
            count = 1


            for url in urls:
                if self.stop_download:
                    break

                download_url, filename = self._adjust_url(url)

                # if datetime.datetime.strptime(filename, "%Y%m%d") < datetime.datetime.strptime(start_date.isoformat(), "%Y-%m-%d"):
                    # break

                print("Downloading: {0}".format(filename))

                if filename == old_filename:
                    new_filename = "{0}_{1}".format(filename, count)
                    count+=1
                else:
                    new_filename = filename
                    count = 1

                if os.path.isfile("{0}{1}{2}.mp4".format(id, os.sep, new_filename)):
                    print 'File Existence'
                    old_filename = filename
                    continue
                urllib.urlretrieve(download_url, "{0}{1}{2}.mp4".format(id, os.sep, new_filename))
                old_filename = filename

            return '========== Success =========='
        else:
            print('Bad connection')

            return ''

# if __name__ == '__main__':
    # my_exe = gplus_photo_crawler()
    # my_exe.main('102277090985412703374', '')