#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# time: 2019/6/26

from kubernetes import client, config
from elasticsearch import Elasticsearch
import json
import time
import datetime
import os
import traceback


# 获取namespace内的所有deployment
def get_app(kube_config_path):
    config.load_kube_config(kube_config_path)
    ExV1beta = client.ExtensionsV1beta1Api()
    deployment_all = ExV1beta.list_deployment_for_all_namespaces(
        field_selector='metadata.namespace=test')
    namespace_test_app = []
    for i in deployment_all.items:
        namespace_test_app.append(i.metadata.labels['app'])
    return namespace_test_app


def get_esdata(app_list, log_path='./', es_api='http://10.16.17.40:9200'):
    gte = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    while True:
        try:
            es_connect = Elasticsearch(es_api)
            lte = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            for i in app_list:
                log_filename = i + '.log'
                query_DSL = {
                    "query": {
                        "bool": {
                            "must": [{
                                "match_phrase": {
                                    "kubernetes.labels.app": i
                                }
                            }, {
                                "range": {
                                    "@timestamp": {
                                        "gte": gte,
                                        "lte": lte
                                    }
                                }
                            }]
                        }
                    }
                }
                elastic_search = es_connect.search(scroll='1m',
                                                   size=100,
                                                   body=query_DSL)
                elastic_scroll_id = elastic_search['_scroll_id']
                for i in elastic_search['hits']['hits']:
                    with open(os.path.join(log_path, log_filename), 'a') as f:
                        f.write(i['_source']['message'] + '\n')
                    elastic_scroll = es_connect.scroll(
                        scroll_id=elastic_scroll_id, scroll='1m')
                    elastic_scroll_id = elastic_scroll['_scroll_id']
                    while len(elastic_scroll['hits']['hits']) > 0:
                        for i in elastic_scroll['hits']['hits']:
                            with open(os.path.join(log_path, log_filename),
                                      'a') as f:
                                f.write(i['_source']['message'] + '\n')
                        elastic_scroll = es_connect.scroll(
                            scroll_id=elastic_scroll_id, scroll='1m')
            time.sleep(2)
            gte = lte
        except Exception:
            with open('./logs/k8s日志持久化.log', 'a') as f:
                traceback.print_exc(file=f)


app_list = get_app(kube_config_path='config')
# print(app_list)
get_esdata(log_path='logs', app_list=app_list)
