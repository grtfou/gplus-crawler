#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20140907
#  @date
#  @brief         Photo downloader

import os
import contextlib
import urllib2

class PicCrawler():
    stop_download = False

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
    #  @brief       Main function by download photo
    #  @param       (Integer) uid
    #               (Tuple) [0]: (string) date
    #                       [1]: (string) photo urls
    #
    def get_pic(self, uid, photo_list):
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