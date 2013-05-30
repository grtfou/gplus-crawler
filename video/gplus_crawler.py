# -*- coding: utf-8 -*-
import urllib
import os
import contextlib

from lxml import etree
from StringIO import StringIO

class GplusVideoCrawler:
    stop_download = False

    def __init__(self):
        pass

    def get_album_urls(self, id):
        url = 'https://picasaweb.google.com/data/feed/api/user/{0}'.format(id)

        with contextlib.closing(urllib.urlopen(url)) as web_page:
            if web_page.getcode() != 200:
                web_page.close()
                raise

            html_context = web_page.read()
            web_page.close()

            myparser = etree.XMLParser(ns_clean=True, encoding="utf8")
            context_tree = etree.parse(StringIO(html_context), parser=myparser)
            root = context_tree.getroot()

            album_urls = []

            for rec in root.findall('{http://www.w3.org/2005/Atom}entry'):
                for child in rec.findall(r'.//{http://www.w3.org/2005/Atom}link'):
                    album_link = child.get('href')
                    if 'feed' in album_link:
                        album_urls.append(album_link)

            return album_urls

    def get_image_urls(self, album_urls, id):
        if not os.path.isdir(id):
            os.mkdir(id)

        old_filename = ''
        count = 1
        published_date = None
        download_url = ''

        for url in album_urls:
            if self.stop_download:
                break

            with contextlib.closing(urllib.urlopen(url)) as web_page:
                if web_page.getcode() != 200:
                    web_page.close()
                    raise

                html_context = web_page.read()
                web_page.close()

                myparser = etree.XMLParser(ns_clean=True, encoding="utf8")
                context_tree = etree.parse(StringIO(html_context), parser=myparser)
                root = context_tree.getroot()

                for rec in root:
                    for child in rec:

                        if child.tag == r'{http://www.w3.org/2005/Atom}published':
                            published_date = child.text[:10].replace('-', '')
                        elif child.tag == r'{http://search.yahoo.com/mrss/}group':
                            for abc in child:
                                if abc.tag == '{http://search.yahoo.com/mrss/}content':
                                    if 'googlevideo' in abc.get('url'):
                                        download_url = abc.get('url')

                                        with contextlib.closing(urllib.urlopen(download_url)) as download_page:
                                            if download_page.getcode() != 200:
                                                download_url = ''
                                                break
                        else:
                            continue

                        if download_url and published_date:
                            if published_date == old_filename:
                                published_date = "{0}_{1}".format(published_date, count)
                                count += 1
                            else:
                                old_filename = published_date
                                count = 1

                            # if os.path.isfile("{0}{1}{2}.mp4".format(id, os.sep, new_filename)):
                                # print 'File Existence'
                                # old_filename = filename
                                # continue

                                print("Downloading: {0}".format(published_date))
                                urllib.urlretrieve(download_url, "{0}{1}{2}.mp4".format(id, os.sep, published_date))
                                published_date = None
                                download_url = ''

    def main(self, id, is_new_first, start_date):
        album_urls = None
        try:
            album_urls = self.get_album_urls(id)
        except:
            return 'Bad connection'

        if not(album_urls):
            return 'Not found any albums'

        try:
            if not(is_new_first):
                album_urls = sorted(album_urls)

            self.get_image_urls(album_urls, id)
        except:
            return 'Bad connection'

        return 'Success'

if __name__ == '__main__':
    my_exe = GplusVideoCrawler()
    my_exe.main('111907069956262615426', False, '')