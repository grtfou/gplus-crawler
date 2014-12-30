#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @date          20141118
import configure
from setuptools import setup, find_packages

# base = None
# if sys.platform == "win32":
    # base = "Win32GUI"

setup(name='gplus_crawler',
      version=configure.VERSION,
      url='https://github.com/grtfou/gplus_crawler',
      description='Download google plus pictures and videos in message',
      license='MIT License',
      install_requires=open('requirements.txt').read().splitlines(),
      author='grtfou',
      packages=find_packages(),
)
