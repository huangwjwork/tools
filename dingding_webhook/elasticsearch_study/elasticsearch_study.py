#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# mail: huangwjwork@gmail.com
# blog: http://blog.csdn.net/u010871982
# file: elasticsearch_study.py
# time: 2018/4/9 21:06

import json
from pyelasticsearch import ElasticSearch
es_connect = ElasticSearch('http://172.16.13.11:9200')
with open('search.json','w') as search_json:
    search_json.write(json.dumps(es_connect.search('_id: qWqbqmIBfMfrd5zjdzB_'),indent=1))
