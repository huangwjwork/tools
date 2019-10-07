#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# time: 2019/6/12

import yaml
import consul
import uuid
import sys
import json
import requests


def registry(consul_yaml):
    registryAPI = consul_yaml['registerAPI']
    print('consul地址：' + registryAPI)
    exporter_types = []
    for i in consul_yaml['Exporter-Type']:
        exporter_types.append(i)
    a = 0
    b = ''
    for i in exporter_types:
        b = b + str(a) + '. ' + i + '\n'
        a += 1
    while True:
        user_choice = input('请选择你要注册的服务类型：\n%s\n' % (b))
        if user_choice.isdecimal() == True and int(user_choice) in range(
                0, exporter_types.__len__()):
            exporter_id = str(uuid.uuid1())
            exporter_type = exporter_types[int(user_choice)]
            exporter_ip = input('请输入exporter的IP地址：\n')
            exporter_port = input('请输入exporter的端口：\n')
            global service_name
            exporter_meta = None
            metrics_path = consul_yaml['Exporter-Type'][exporter_types[int(
                user_choice)]]['default_metrics_path']

            if exporter_type == 'node':
                # exporter_alias = input('请输入exporter的tag，可置空：')
                service_name = 'node'
                node_groups = consul_yaml['Exporter-Type']['node']['groups']
                a = 0
                b = ''
                for i in node_groups:
                    b = b + str(a) + '. ' + i + '\n'
                    a += 1
                while True:
                    node_group_choice = input('请选择服务器组：\n%s\n' % (b))
                    if node_group_choice.isdecimal() == True and int(
                            node_group_choice) in range(
                                0, node_groups.__len__()):
                        node_group = node_groups[int(node_group_choice)]
                        node_hostname = input('请输入主机名:\n')
                        exporter_meta = {
                            'group': node_group,
                            'alias': node_hostname
                        }
                        break
                    else:
                        print('输入错误，请重新输入\n')
                        continue
            elif exporter_type in ['microservice', 'middleware', 'monitoring']:
                service_name = input('请输入服务名或应用名：\n')
            elif exporter_type == 'ops-exporter':
                service_name = 'ops-exporter'
            else:
                pass

            exporter_url = 'http://%s:%s%s' % (exporter_ip, int(exporter_port),
                                               metrics_path)
            # print(exporter_url)
            check_tcp = {
                "tcp": "%s:%s" % (exporter_ip, exporter_port),
                "interval": "30s"
            }
            header = {'Content-Type': 'application/json'}
            body = {
                'name': service_name,
                'id': exporter_id,
                'address': exporter_ip,
                'port': int(exporter_port),
                'tags': [exporter_type],
                'meta': exporter_meta,
                'check': check_tcp
            }
            # print(header)
            # print(body)
            # a = requests.put(url=registryAPI, headers=json.loads(json.dumps(header)), data=json.loads(json.dumps(body)))
            # print(a.status_code)
            a = requests.request(method='PUT',
                                 url=registryAPI,
                                 headers=header,
                                 json=body)
            # print(a.content)
            # print(a.status_code)
            print('%s注册成功' % exporter_id)

            break

        else:
            print('服务类型选择错误，请重新选择')


def deregistry(consul_yaml):
    ip = input('请输入要注销的service IP：\n')
    port = input('请输入要注销的service 端口：\n')
    servicelistAPI = consul_yaml['servicelistAPI']
    deregistrerAPI = consul_yaml['deregisterAPI']
    a = requests.request(method='GET', url=servicelistAPI)
    servicelist = a.json()
    for i in servicelist:
        if servicelist[i]['Address'] == ip and str(
                servicelist[i]['Port']) == port:
            requests.request(method='PUT',
                             url=deregistrerAPI + servicelist[i]['ID'],
                             headers={'Content-Type': 'application/json'})
            print('exporterIP:%s exporterPort:%d exporterID:%s 已删除. ' %
                  (servicelist[i]['Address'], servicelist[i]['Port'],
                   servicelist[i]['ID']))


if __name__ == '__main__':
    with open('consul-registry.yaml', 'r') as f:
        consul_yaml = yaml.load(f)
    while True:
        action = input('''
请选择要进行的操作：
1. 注册服务
2. 注销服务
3. 退出\n
        ''')
        if action == '1':
            registry(consul_yaml)
        elif action == '2':
            deregistry(consul_yaml)
        elif action == '3':
            sys.exit()
        else:
            print('输入错误，请重新输入')
