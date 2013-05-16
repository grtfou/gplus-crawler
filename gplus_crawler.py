# -*- coding: utf-8 -*-
import urllib
import re
import os
import datetime
import contextlib

from lxml import etree

class gplus_photo_crawler:
    stop_download = False

    def __init__(self):
        # 1st is date. 2nd is photo url
        self.url_regx = re.compile(r",.*\[\"https:\/\/picasaweb.*\/(.*)#.*\[\"(.*)\"")

    def _adjust_url(self, img_url):
        url_seg = img_url[1].split('/')
        url = "%s/d/%s" % ('/'.join(url_seg[:-2]), url_seg[-1])

        if img_url[0][0] == '1':
            filename = "20{0}".format(img_url[0])[:8]
        else:
            filename = img_url[0][:8]   # ex. 20130101

        return url, filename

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

                for node in parse_result:
                    if node.find("key: '126'") != -1:
                        photo = self.url_regx.findall(node.encode('utf8'))
                        return photo

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

                # try:
                    # if datetime.datetime.strptime(filename, "%Y%m%d") < datetime.datetime.strptime(start_date.isoformat(), "%Y-%m-%d"):
                        # break
                # except:
                    # pass

                print("Downloading: {0}".format(filename))

                if filename == old_filename:
                    new_filename = "{0}_{1}".format(filename, count)
                    count+=1
                else:
                    new_filename = filename
                    count = 1

                urllib.urlretrieve(download_url, "{0}{1}{2}.jpg".format(id, os.sep, new_filename))
                old_filename = filename

            return 'Success'
        else:
            print('Bad connection')

            return ''

# if __name__ == '__main__':
    # my_exe = gplus_photo_crawler()
    # my_exe.main('110216234612751595989', '')