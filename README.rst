Google Plus Image / Video Crawler
===============================

README Last Updated on 2015.11.03

::

    Shutting down Google+ for consumer (personal) accounts on April 2, 2019
    (https://support.google.com/plus/answer/9195133)
    
    So this repo has been archived.


|build|
--------

Introduction
=============
Download Google Plus (Google+) ``Pictures`` and ``Videos`` in messages

* For backup (download) pictures and videos in messages
* The best video quality


Requirements
=============
+ Python == 3.7
+ requests >= 2.21.0
+ wxPython == 4.0.3  (For UI)
+ cx_Freeze == 5.1.1 (For compile to .exe file)


How to Use
==================
* Download it (portable)
    * https://github.com/grtfou/gplus-crawler/releases
* Uncompress 7z file and execute ``start_ui.exe`` to run
* Input Google+ id that you want to backup (download) user into text field
    * ex: 105229500895781124316
* Press ``Go Download!`` button
* If yout want to ``Stop``, press ``Stop`` button


Change log
===========
* ``0.4.2`` (2015-11-03)
    * Fixed: Regex of video url parser
* ``0.4.1`` (2014-12-30)
    * Fixed: connection alive issue
    * Fixed: Service refusing SSLv2 connection
    * Fixed: Building execution file fail by HTTPS certification
    * Enhanced: Support to testing on travis ci
* ``0.4.0`` (2014-09-08)
    * Added: Video date
    * Fixed: Regex bugs
    * Enhanced: Refactored system structure for download efficiency
    * Enhanced: Integrated Video and Pictures crawlers
* ``0.3.0`` (2013-05-30)
    * Fixed: Full crawl fail (Only 1000 messages) by G+ new design
    * Fixed: Refactored system for Google+ change new design
* ``0.2.4`` (2013-05-16)
    * Implemented: Videos full crawler from G+ message
    * Enhanced: Download efficiency
* ``0.1.0`` (2013-03-23)
    * Implemented: Pictures full crawler from G+ message

Licence
========
MIT License

.. |build| image:: https://travis-ci.org/grtfou/gplus-crawler.svg?branch=master
    :target: https://travis-ci.org/grtfou/gplus-crawler
