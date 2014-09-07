#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20140907
#  @date
#  @brief         Video downloader
import os
import sys
import urllib2

class VideoCrawler():
    stop_download = False

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
    #  @brief       Main function by download video
    #  @param       (Integer) uid
    #               (OrderedDict) key:   (string) video key
    #                             value: (string) video url
    #
    def get_video(self, uid, video_urls):
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
                if os.path.isfile("{0}{1}{2}.mp4".format(folder_path, os.sep, new_filename)):
                    print('File Existence: {0}'.format(new_filename))
                    continue
                ###-avoid

                # Download
                v_filename = "{0}{1}{2}.mp4".format(folder_path, os.sep, new_filename)
                urllib.urlretrieve(download_url, v_filename, self._report_hook)
                print('')

            return 1
        else:
            return 0