#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# file: alert_for_ELK.py
# time: 2018/4/9 21:39

from elasticsearch import Elasticsearch
import time
import datetime
import json
import requests
# dingding
time1 = time.time()
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=45f4b695b1dbe35998626e9083ca8b212d475943259273a699127f1cc76edadb"

webhook_header = {
    "Content-Type": "application/json",
    "charset": "utf-8"
    }

message_platform='''
# ELK日志告警
hostname: **{hostname}**
log_level: **ERROR**
from: **huangwj**

'''.format(hostname="hadoop")


webhook_message = {
"msgtype": "markdown",
"markdown": {
    "title":"markdown测试",
    "text":message_platform
}
}

# sendData = json.dumps(webhook_message,indent=1)
# requests.post(webhook_url,data=sendData,headers=webhook_header)



elastic_client = Elasticsearch(hosts='172.16.13.11:9200')


query_json = {
  "query": {
    "bool": {
      "must": [
        { "match": { "nginx.access.method":"GET"}},
        { "match": { "nginx.access.remote_ip": "172.16.8.241" }}
      ],
        "filter": [
            {"range": {"@timestamp": {
                "gte":"now-1d",
                "lte": "now"}}}
        ]
    }
  }
}

query_json_test = {
  "query": {
    "bool": {

        "filter": [
            {"range": {"@timestamp": {
                "gte":"now-1d",
                "lte": "now"}}}
        ]
    }
  }
}
# query_string = "nginx.access.remote_ip:172.16.8.241 AND nginx.access.remote_ip:172.16.8.241"
search_number = elastic_client.count(body=query_json_test)
print(search_number['count'])
elasticsearch_scroll_info = elastic_client.search(scroll='1m',body=query_json_test)
scroll_id = elasticsearch_scroll_info['_scroll_id']
print(scroll_id)
scroll_size = elasticsearch_scroll_info['hits']['total']
print(scroll_size)
while scroll_size > 0:
    print("scrolling...")
    elasticsearch_scroll = elastic_client.scroll(scroll_id=scroll_id,scroll='1m')
    scroll_id = elasticsearch_scroll['_scroll_id']
    print(scroll_id)
    scroll_size = len(elasticsearch_scroll['hits']['hits'])
    print("scroll_size:"+str(scroll_size))
    for  hit in elasticsearch_scroll['hits']['hits']:
        print(hit['_id'])


# quert_string = 'nginx.access.method:GET AND nginx.access.remote_ip:172.16.8.241'

# elastic_response = elastic_client.search(body=query_json,size=search_number)
#
# with open('search.json',mode='w') as aaa:
#     aaa.write(json.dumps(elastic_response,indent=1))
time2=time.time()
print(time2-time1)




