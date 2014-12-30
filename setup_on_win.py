#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @date          20141230 - Bug fixing for building execution file
"""
Setup file
"""

from cx_Freeze import setup, Executable
import requests.certs

import configure

# base = None
# if sys.platform == "win32":
    # base = "Win32GUI"

copyDependentFiles = True
silent = True

INCLUDES = ["encodings.utf_8", "encodings.ascii",
            "os", "re", "sys", "threading",
            "contextlib", "logging", "requests", "wx"]

setup(name='gplus_crawler',
      version=configure.VERSION,
      options={
        "build_exe":{
            "includes": INCLUDES,
            "include_msvcr": True,
            "include_files":[(requests.certs.where(), 'cacert.pem')],
        },
      },
      executables=[Executable('start_ui.py')],
)
