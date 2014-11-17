#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20140916
#  @date
#  @version       0.1 (140916)
#  @brief         Test crawler main function

import sys
sys.path.append('..')

from gplus_crawler import GplusCrawler

if __name__ == '__main__':
    my_exe = GplusCrawler()
    user_id = '115975634910643785199'

    d_type = sys.argv[1]

    if d_type in ('video', 'photo'):
        my_exe.main(user_id, d_type)
    else:
        print("Usage: python test_main <video/photo>")