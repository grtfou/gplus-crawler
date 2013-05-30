# -*- coding: utf-8 -*-
import urllib
import os
import contextlib

from lxml import etree
from StringIO import StringIO

class GplusPhotoCrawler:
    stop_download = False

    def __init__(self):
        pass

    def _format_url(self, origin_url):
        url_seg = origin_url.split('/')
        url = "{0}/s0/{1}".format('/'.join(url_seg[:-1]), url_seg[-1])
        return url


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

            album_urls = set()

            for rec in root.findall('{http://www.w3.org/2005/Atom}entry'):
                for child in rec.findall(r'.//{http://www.w3.org/2005/Atom}link'):
                    album_link = child.get('href')
                    if 'feed' in album_link:
                        album_urls.add(album_link)

            return album_urls

    def get_image_urls(self, album_urls, id):
        if not os.path.isdir(id):
            os.mkdir(id)

        old_filename = ''
        count = 1
        published_date = None
        download_url = ''

        for url in reversed(sorted(album_urls)):
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
                    for child in rec.findall(r'{http://www.w3.org/2005/Atom}*'):

                        if child.tag == r'{http://www.w3.org/2005/Atom}published':
                            published_date = child.text[:10].replace('-', '')
                        elif child.tag == r'{http://www.w3.org/2005/Atom}content':
                            download_url = self._format_url(child.get('src'))
                        else:
                            continue

                        if download_url and published_date:
                            if published_date == old_filename:
                                published_date = "{0}_{1}".format(published_date, count)
                                count += 1
                            else:
                                old_filename = published_date
                                count = 1

                            urllib.urlretrieve(download_url, "{0}{1}{2}.jpg".format(id, os.sep, published_date))

                            print("Downloading: {0}".format(published_date))
                            published_date = None
                            download_url = ''

    def main(self, id, start_date):
        album_urls = None
        try:
            album_urls = self.get_album_urls(id)
        except:
            return 'Bad connection'

        if not(album_urls):
            return 'Not found any albums'

        try:
            self.get_image_urls(album_urls, id)
        except:
            return 'Bad connection'

        return 'Success'
