#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: CityNorth
@file: start.py
@time: 2020/11/23 17:30
@desc: 
"""

from scrapy import cmdline
#cmdline.execute("scrapy crawl bw5".split())
cmdline.execute("scrapy crawl Position -o position.json".split())