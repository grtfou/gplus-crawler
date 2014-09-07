# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

from gplus_crawler import GplusPhotoCrawler

if __name__ == '__main__':
    my_exe = GplusPhotoCrawler()
    #id = '110216234612751595989'
    #id = '105835152133357364264'
    my_exe.main('110216234612751595989', '')