#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# file: 1024_image.py
# time: 2018/2/28 23:16

#


import bs4
import requests
import os
import re
download_disk = "d:\\"

# 主页
bt1024_url = "http://1024.917rbb.com/pw/"

# 图片板块主页，可替换其他板块
bt1024_index_url = bt1024_url+"thread.php?fid=16"

# 获取图片板块主页
bt1024_index_page = requests.get(bt1024_index_url)
bt1024_index_bs4 = bs4.BeautifulSoup(bt1024_index_page.text)
# print(bt1024_index_bs4.select('h3 > a[id]'))

# 过滤出 h3标题下 a标签 并具备ID属性的文本
bt1024_index_bs4_url = bt1024_index_bs4.select('h3 > a[id]')
# print(bt1024_index_bs4_url)

# 建立图片页链接空列表
bt1024_imagepage_url = []

# 剔除read.php一类的非图片页面链接
for i in  range(0,len(bt1024_index_bs4_url)):
  if "read.php" not in bt1024_index_bs4_url[i].get('href'):
    # 生成图片页链列表
    bt1024_imagepage_url.append(bt1024_url+bt1024_index_bs4_url[i].get('href'))
# print(bt1024_imagepage_url)
# print(type(bt1024_imagepage_url))

# print(requests.get(bt1024_imagepage_url[0]).text)

os.chdir(os.path.join(download_disk))
if os.path.exists('bt1024') :
  print("图片下载路径"+os.getcwd()+"bt1024")
else :
  os.mkdir('bt1024')

# 遍历所有图片页面
for i in range(0,len(bt1024_imagepage_url)):
  bt1024_imagepage_url_html = requests.get(bt1024_imagepage_url[i])
  bt1024_imagepage_url_html.encoding='utf-8'
  bt1024_imagepage_url_html_bs4 = bs4.BeautifulSoup(bt1024_imagepage_url_html.text)

  # 获取页面title作为目录名
  image_dir = bt1024_imagepage_url_html_bs4.select('title ')
  re_image_dir = re.compile(r'<title>(.*]).*')
  image_dir = re_image_dir.search(str(image_dir[0]))
  print(image_dir.group(1))
  os.chdir(download_disk+"bt1024")
  if not os.path.exists(image_dir.group(1)):
    os.mkdir(image_dir.group(1))
  os.chdir(image_dir.group(1))

  # 获取图片链接并下载
  sex_image_url = bt1024_imagepage_url_html_bs4.select('div[class="tpc_content"] > img')
  # print(sex_image_url)
  for url_list in sex_image_url:
    print(url_list.get('src'))
    re_image_name = re.compile(r'.*/(.*jpg)$')
    image_name = re_image_name.search(url_list.get('src')).group(1)
    print(image_name)
    with open(image_name,'wb') as image_download :
      for trunk in requests.get(url_list.get('src')).iter_content(10000):
        image_download.write(trunk)




