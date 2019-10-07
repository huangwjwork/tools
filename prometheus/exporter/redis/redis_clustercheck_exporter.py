#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj

import sys
sys.path.append('/usr/local/python3/lib/python3.6/site-packages')
from prometheus_client import start_http_server, Gauge
from rediscluster import StrictRedisCluster
import os
import time


startup_nodes = [{'host': '10.16.200.12', 'port': '7001'}, {'host': '10.16.200.12', 'port': '7002'},
                 {'host': '10.16.200.13', 'port': '7003'}, {'host': '10.16.200.13', 'port': '7004'},
                 {'host': '10.16.200.14', 'port': '7005'}, {'host': '10.16.200.14', 'port': '7006'}]

# startup_nodes_dev = [{'host': '172.16.11.46', 'port': '7001'}, {'host': '172.16.11.46', 'port': '7002'},
#                      {'host': '172.16.11.46', 'port': '7003'}, {'host': '172.16.11.46', 'port': '7004'},
#                      {'host': '172.16.11.46', 'port': '7005'}, {'host': '172.16.11.46', 'port': '7006'}]

redis_password = 'wynyredis'


def get_hostname():
    # 获取主机名
    hostname_cmd = os.popen('hostname')
    a = hostname_cmd.read().strip('\n')
    hostname_cmd.close()
    return a


redis_node_stat = Gauge('redis_node_status', 'redis节点状态，1为正常，0为异常', ['host', 'port', 'role','hostname'])
redis_masternode_slavestat = Gauge('redis_master_stat',
                                   'redis master节点的slave节点状态，1为正常，0代表没有slave节点或slave节点与master节点在同一host',
                                   ['host', 'port','hostname'])


def redis_cluster_check():
    rc = StrictRedisCluster(startup_nodes=startup_nodes, password=redis_password, readonly_mode=True)
    cluster_nodes = rc.cluster_nodes()
    for i in cluster_nodes:
        if i['link-state'] == 'connected':
            link_state = 1
        else:
            link_state = 0
        if 'master' in i['flags']:
            redis_node_stat.labels(host=i['host'], port=i['port'], role='master',hostname=hostname).set(link_state)
            slave_stat = 0
            for j in cluster_nodes:
                if i['id'] == j['master'] and i['host'] != j['host']:
                    slave_stat = 1
                else:
                    pass
                redis_masternode_slavestat.labels(host=i['host'], port=i['port'],hostname=hostname).set(slave_stat)
        else:
            redis_node_stat.labels(host=i['host'], port=i['port'], role='slave',hostname=hostname).set(link_state)


if __name__ == '__main__':
    # 在10000端口启动exporter
    hostname = get_hostname()
    start_http_server(10001)
    # 死循环，每15秒检查一次
    while True:
        redis_cluster_check()
        time.sleep(15)
