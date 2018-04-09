#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# file: test dingding webhook.py
# time: 2018/4/9 16:41


import urllib.request
import requests
import json

webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=45f4b695b1dbe35998626e9083ca8b212d475943259273a699127f1cc76edadb"

webhook_header = {
    "Content-Type": "application/json",
    "charset": "utf-8"
    }
webhook_data = {
     "msgtype": "text",
        "text": {
            "content": "huangwj告警测试"
        }
    }

sendData = json.dumps(webhook_data)
requests.post(webhook_url,data=sendData,headers=webhook_header)
