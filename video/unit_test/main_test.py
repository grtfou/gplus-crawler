# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

from gplus_crawler import GplusVideoCrawler

if __name__ == '__main__':
    my_exe = GplusVideoCrawler()
    #id = '115975634910643785199'
    my_exe.main('111907069956262615426', False, '')