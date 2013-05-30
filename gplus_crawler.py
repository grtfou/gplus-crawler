#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20130323
#  @date          20130530
#  @brief         Download(backup) Google plus images
import urllib
import os
import contextlib

from lxml import etree
from StringIO import StringIO

class GplusPhotoCrawler:
    stop_download = False

    def __init__(self):
        pass

    """
    @desc   Replace download url to new url of full size image
    """
    def _format_url(self, origin_url):
        url_seg = origin_url.split('/')
        url = "{0}/s0/{1}".format('/'.join(url_seg[:-1]), url_seg[-1])
        return url


    """
    @desc   Get all album urls
    """
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

            pattern = "{http://www.w3.org/2005/Atom}entry//{http://www.w3.org/2005/Atom}link"

            for rec in root.findall(pattern):
                if 'feed' in rec.get('href'):
                    album_urls.append(rec.get('href'))

            return album_urls

    """
    @desc   Traveled all album and download all images
    """
    def get_image_urls(self, album_urls, id):
        # Create folder to store images
        if not os.path.isdir(id):
            os.mkdir(id)

        download_url = ''
        previous_date = ''
        published_date = None
        count = 1

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

                pattern = "{http://www.w3.org/2005/Atom}entry//"

                for rec in root.findall(pattern):
                    if rec.tag == r'{http://www.w3.org/2005/Atom}published':    # date
                        published_date = rec.text[:10].replace('-', '')
                    elif rec.tag == r'{http://www.w3.org/2005/Atom}content':    # image url
                        download_url = self._format_url(rec.get('src'))
                    else:
                        continue

                    if download_url and published_date:
                        # Check filename overlap, if TRUE then rename
                        if published_date == previous_date:
                            published_date = "{0}_{1}".format(published_date, count)
                            count += 1
                        else:
                            previous_date = published_date
                            count = 1

                        urllib.urlretrieve(download_url, "{0}{1}{2}.jpg".format(id, os.sep, published_date))

                        print("Downloading: {0}.jpg".format(published_date))
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
