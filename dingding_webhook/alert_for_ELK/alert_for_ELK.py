#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# file: alert_for_ELK.py
# time: 2018/4/9 21:39

from pyelasticsearch import ElasticSearch
import requests
import json

# elasticsearch
es_connect = ElasticSearch('http://172.16.13.11:9200')
alert_message = es_connect.search('_id: qWqbqmIBfMfrd5zjdzB_')

print(json.dumps(alert_message['hits']['hits'][0]['_source']['nginx'],indent=1))

# dingding
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=45f4b695b1dbe35998626e9083ca8b212d475943259273a699127f1cc76edadb"

webhook_header = {
    "Content-Type": "application/json",
    "charset": "utf-8"
    }

webhook_message = {
"msgtype": "text",
"text": {
    "content":alert_message['hits']['hits'][0]['_source']['nginx']}
}

sendData = json.dumps(webhook_message,indent=1)
requests.post(webhook_url,data=sendData,headers=webhook_header)



