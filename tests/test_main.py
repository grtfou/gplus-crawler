#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @first_date    20140916
#  @date          20141117 - Edit to unit test format
'''
Test main function for download image
'''

import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gplus_crawler import GplusCrawler

class TestMainFunction(unittest.TestCase):
    def setUp(self):
        self.user_id = '115975634910643785199'

    def tearDown(self):
        self.user_id = None

    def test_video(self):
        main_program = GplusCrawler()
        result = main_program.main(self.user_id, 'video')
        main_program.stop_download = True

        self.assertNotEqual(result, 'Connection Fail')

if __name__ == '__main__':
    unittest.main()
