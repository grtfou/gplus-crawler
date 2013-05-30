#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20130414
#  @date          20130530
#  @brief         Download(backup) Google plus videos
from __future__ import print_function

import urllib
import os
import contextlib

from lxml import etree
from StringIO import StringIO

class GplusVideoCrawler:
    stop_download = False

    def __init__(self):
        pass

    def _get_url_data(self, url):
        with contextlib.closing(urllib.urlopen(url)) as web_page:
            if web_page.getcode() != 200:
                web_page.close()
                return None

            html_context = web_page.read()
            web_page.close()

        return html_context

    """
    @desc   Get all album urls
    """
    def get_album_urls(self, id):
        url = 'https://picasaweb.google.com/data/feed/api/user/{0}'.format(id)

        html_context = self._get_url_data(url)
        if not(html_context):
            raise

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
    @desc   Traveled all album and download all videos
    """
    def get_image_urls(self, album_urls, id):
        if not os.path.isdir(id):
            os.mkdir(id)

        download_url = ''
        previous_date = ''
        published_date = None
        count = 1

        for url in album_urls:
            print('.', end='')
            if self.stop_download:
                break

            html_context = self._get_url_data(url)
            if not(html_context):
                raise

            myparser = etree.XMLParser(ns_clean=True, encoding="utf8")
            context_tree = etree.parse(StringIO(html_context), parser=myparser)
            root = context_tree.getroot()

            pattern = "{http://www.w3.org/2005/Atom}entry//"
            group_pattern = "{http://search.yahoo.com/mrss/}content[last()]"

            for rec in root.findall(pattern):
                if rec.tag == r'{http://www.w3.org/2005/Atom}published':    # date
                    published_date = rec.text[:10].replace('-', '')
                elif rec.tag == r'{http://search.yahoo.com/mrss/}group':    # video level
                    for v_url in rec.findall(group_pattern):
                        download_url = v_url.get('url')

                        if 'googlevideo' not in download_url:
                            published_date = None
                            download_url = ''
                            break

                        # Test url is vaild
                        v_page = self._get_url_data(download_url)
                        if not(v_page):
                            published_date = None
                            download_url = ''
                            break

                else:
                    continue


                # Download
                if download_url and published_date:
                    if published_date == previous_date:
                        published_date = "{0}_{1}".format(published_date, count)
                        count += 1
                    else:
                        previous_date = published_date
                        count = 1

                    print("\nDownloading: {0}".format(published_date))
                    # Is file exist and skip
                    if os.path.isfile("{0}{1}{2}.mp4".format(id, os.sep, published_date)):
                        print('File Existence')

                    else:
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
