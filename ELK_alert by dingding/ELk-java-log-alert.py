#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# github: https://github.com/huangwjwork
# file: ELk-java-log-alert.py
# time: 2018/4/17 23:31
'''
本程序由huangwjwork开发,一切最终解释权归于huangwjwork.
本程序为开源,只用于技术交流,只供开发者参考与学习.
不得用于违反法律以及未经许可不得用于商业.保留其追责权利.
本程序不涉及任何违法敏感因素,如有人拿程序改造成违法工具,将与本程序开发者无关.
勇于开源,请勿滥用.内部学习交流,请勿传播.违反者造成相关法律事故,自行承担刑事责任.
'''

from elasticsearch import Elasticsearch
import json
import requests

# http代理
proxies = {
    "http" : "http://x.x.x.x:3128",
    "https" : "http://x.x.x.x:3128"
}

# 钉钉自定义机器人webhook_url
dingding_webhook_URL = "自己的钉钉webhook URL"
# ES查询语句：查出最近十五分钟匹配到grok语句，并且主机名字段包含“xixin-had-”，log_level不为INFO的日志
query_DSL_javalog = {
  "query": {
    "bool":{
      "must":[{
      "range":{
        "@timestamp":{
          "gte":"now-1d",
          "lte":"now" }
      }
      },
      {"match_phrase":{
        "beat.hostname":"xixin-had-"}
      }],
      "must_not": [
        {"match_phrase": {
          "log_level": "INFO"
        }
        },
        {"match_phrase": {
          "tags": "_grokparsefailure"
        }}
        ]
  }
}
}
# 连接ELK
es_URL = "http://x.x.x.x:9200"
elastic_connect = Elasticsearch(es_URL)

# 定义消息推送钉钉的函数
def WARNING_PUSH(warning_hit):
    # 钉钉API请求头
    webhook_header = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    # 告警Markdown
    webhook_alert_message_platform = '''
# 状态： {log_level}告警
**主机名：** {hostname}  
**告警模块：** {tag}  
**日志时间：** {log_time}   
**日志等级：** {log_level}  
**日志内容：** {log_message}
'''.format(tag=warning_hit['_source']['tags'][0],hostname=warning_hit['_source']['beat']['hostname'],
               log_time=warning_hit['_source']['log_time'],log_level=warning_hit['_source']['log_level'],
               log_message=warning_hit['_source']['log_message'])
    # body
    webhook_message = {
        "msgtype": "markdown",
        "markdown": {
            "title": '告警: '+warning_hit['_source']['tags'][0] + warning_hit['_source']['log_level'],
            "text": webhook_alert_message_platform
        }
    }
    sendData = json.dumps(webhook_message,indent=1)
    requests.post(dingding_webhook_URL, data=sendData, headers=webhook_header, proxies=proxies)
    # requests.post(dingding_webhook_URL,json=webhook_message,proxies=proxies)


def RESOLVED_PUSH(resolved_hit):
    webhook_header = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    webhook_resolved_message_platform = '''
# 状态： {log_level}恢复
**主机名：** {hostname}  
**恢复模块：** {tag}  
**日志时间：** {log_time}   
**日志等级：** {log_level}  
'''.format(tag=resolved_hit['_source']['tags'][0],hostname=resolved_hit['_source']['beat']['hostname'],
               log_time=resolved_hit['_source']['log_time'],log_level=resolved_hit['_source']['log_level'])
    webhook_message = {
        "msgtype": "markdown",
        "markdown": {
            "title": '恢复: '+resolved_hit['_source']['tags'][0] + resolved_hit['_source']['log_level'],
            "text": webhook_resolved_message_platform
        }
    }
    sendData = json.dumps(webhook_message,indent=1)
    requests.post(dingding_webhook_URL, data=sendData, headers=webhook_header, proxies=proxies)

# 更新告警信息，并post到elasticsearch
def ALERT_UPDATE(doc_name,timestamp,trigger_status):
    alert_body ={
        "last_warning_time": timestamp,
        "trigger_status": trigger_status
    }
    requests.post(url=es_URL+'/wyny_elk/alert/'+doc_name,json=alert_body)


'''
告警策略：
doc_name格式为主机名_模块_日志等级
检查elasticsearch中是否存在该项目的告警信息
    如果告警信息不存在，则该告警项目之前不存在，写入该告警信息至ES，并抛出告警
    如果告警信息存在，则判定该告警的状态
        若本就是WARNING状态，则更新告警信息
        若是RESOLVED状态，则更新告警信息，并抛出告警
'''
def FUNC_ALERT(hit):
    doc_name = hit['_source']['beat']['hostname'] + '_' + hit['_source']['tags'][0] + '_' + hit['_source']['log_level']
    # 如果ES中不存在该条告警项，发出告警日志
    timestamp = hit['_source']['@timestamp']
    if elastic_connect.exists(index='wyny_elk',doc_type='alert',id=doc_name) is False:
        body = {
            "last_warning_time": timestamp,
            "trigger_status": "warning"
        }
        elastic_connect.create(index='wyny_elk',doc_type='alert',id=doc_name,body=body)
        WARNING_PUSH(warning_hit=hit)
    else:
        trigger_info = elastic_connect.get(index='wyny_elk',doc_type='alert',id=doc_name)
        trigger_status = trigger_info['_source']['trigger_status']
        if trigger_status == 'resolved' :
            ALERT_UPDATE(doc_name=doc_name,timestamp=timestamp,trigger_status='warning')
            WARNING_PUSH(warning_hit=hit)
        elif trigger_status == 'warning' :
            ALERT_UPDATE(doc_name=doc_name, timestamp=timestamp, trigger_status='warning')


# 初始化相应的index,type
if elastic_connect.exists(index='wyny_elk',doc_type='alert',id='init_alert') is False:
    elastic_connect.create(index='wyny_elk',doc_type='alert',id='init_alert',body={})
# 滚动查询匹配quert_body的错误日志
elastic_search = elastic_connect.search(scroll='1m',body=query_DSL_javalog)
total_hits = elastic_search['hits']['total']
print(total_hits)
elastic_scroll_id = elastic_search['_scroll_id']
# 遍历所有的ERROR日志
for hit in elastic_search['hits']['hits']:
    # 匹配告警策略
    FUNC_ALERT(hit=hit)
# 遍历剩余告警（search只能查询到前十条）
elastic_scroll = elastic_connect.scroll(scroll_id=elastic_scroll_id,scroll='1m')
elastic_scroll_hits = len(elastic_scroll['hits']['hits'])
while elastic_scroll_hits > 0 :
    for hit in elastic_scroll['hits']['hits']:
        FUNC_ALERT(hit=hit)
        elastic_scroll = elastic_connect.scroll(scroll_id=elastic_scroll_id, scroll='1m')
        elastic_scroll_hits = len(elastic_scroll['hits']['hits'])