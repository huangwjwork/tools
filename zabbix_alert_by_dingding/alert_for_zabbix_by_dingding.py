#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# github: https://github.com/huangwjwork
# file: alert_for_zabbix_by_dingding.py
# time: 2018/5/11 14:31
'''
本程序由huangwjwork开发,一切最终解释权归于huangwjwork.
本程序为开源,只用于技术交流,只供开发者参考与学习.
不得用于违反法律以及未经许可不得用于商业.保留其追责权利.
本程序不涉及任何违法敏感因素,如有人拿程序改造成违法工具,将与本程序开发者无关.
勇于开源,请勿滥用.内部学习交流,请勿传播.违反者造成相关法律事故,自行承担刑事责任.
'''
import sys
import getopt
import requests
import json
import traceback
try:
    opts,args = getopt.getopt(sys.argv[1:],shortopts='',longopts=['webhook_url=','webhook_title=','alert_message='])
    for opt,value in opts:
        if opt == '--webhook_url':
            webhook_url = value
        elif opt == '--webhook_title':
            webhook_title = value
        elif opt == '--alert_message':
            alert_message = value
    webhook_header = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }
    webhook_message = {
            "msgtype": "markdown",
            "markdown": {
                "title": webhook_title,
                "text": alert_message
            }
        }
    sendData = json.dumps(webhook_message,indent=1)
    requests.post(url=webhook_url,headers=webhook_header,data=sendData)
except:
    traceback.print_exc(file=open('alert_zabbix_dingding.log','w+'))
