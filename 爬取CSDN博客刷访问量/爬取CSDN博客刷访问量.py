#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# file: 爬取CSDN博客刷访问量.py
# time: 2018/3/1 15:16




'''
刷来玩玩  刷之前3887 打算刷1W试试 哈哈哈
'''


import requests
import bs4
import time

for times in range(0,200):
    csdn_blog_index = "http://blog.csdn.net/u010871982"
    csdn_blog_index_requests = requests.get(csdn_blog_index)
    csdn_blog_index_bs4 = bs4.BeautifulSoup(csdn_blog_index_requests.text)
    csdn_blog_url = csdn_blog_index_bs4.select('li[class="blog-unit"] > a[target="_blank"] ')
    for i in range(0,len(csdn_blog_url)):
        blog_request = requests.get(csdn_blog_url[i].get('href'))
    num_div = csdn_blog_index_bs4.select('div[class="gradeAndbadge gradewidths"]')
    print(num_div[0].get('title'))
    time.sleep(10)