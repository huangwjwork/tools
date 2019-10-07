#!/usr/bin/env python3
# encoding: utf-8
# author: huangwj
# time: 2019/6/3
import sys
sys.path.append('/usr/local/python3/lib/python3.6/site-packages')
import os
import re
import uuid
import time
import psutil
import getopt
from prometheus_client import start_http_server, Summary ,Counter , Gauge

'''
监控文件系统所有挂载点，可读写置0，不可读写置1
'''

def get_hostname():
    # 获取主机名
    hostname_cmd = os.popen('hostname')
    a = hostname_cmd.read().strip('\n')
    hostname_cmd.close()
    return a

# 定义文件系统检查的数据类型为gauge，添加label mountpint
filesystem_readonly_check_metrics = Gauge('filesystem_readonly_check_metrics',
                                          'check the filesystem rw or ro , 0 is rw, 1 is ro', ['mountpoint','alias'])
def filesystem_readonly_check():
    # 获取文件系统的所有挂载点
    mount_info_cmd = os.popen('/bin/mount | awk \'{ print $3}\' | grep -Ev \'docker|kubelet|run|tmpfs|efi|Filesystem|^/proc|^/dev|^/sys|rpc_pipefs$|tmp$\' ')
    mount_info = mount_info_cmd.read()
    mount_info_cmd.close()
    # 正则匹配获得挂载点list
    mount_points = re.findall(r'.+' , mount_info)
    # 通过UUID生成文件名
    filename = 'filesystem_check_' + str(uuid.uuid1())
    # 遍历所有挂载点
    for mount_point in mount_points:
        # 定义写入的文件路径为“挂载点+UUID文件名”
        file_url = os.path.join(mount_point,filename)
        # 尝试写入文件后，读取文件，若文件内容为预定义内容，则认为文件系统读写正常，metric置为0，否则文件系统异常，metric置为1（判定较为粗糙）
        try:
            with open(file_url,'w') as openfile:
                openfile.write('This is the filesystem check.')
            if os.path.exists(file_url) is True:
                with  open(file_url,'r') as openfile:
                    file_content = openfile.read()
                    if file_content == 'This is the filesystem check.':
                        filesystem_readonly_check_metrics.labels(mountpoint=mount_point,alias=hostname).set(0)
                        os.remove(file_url)
                    else:
                        filesystem_readonly_check_metrics.labels(mountpoint=mount_point,alias=hostname).set(1)
        # 检查过程中任何异常均认为检查失败
        except:
            filesystem_readonly_check_metrics.labels(mountpoint=mount_point,alias=hostname).set(1)


# 检查僵尸进程
zombie_process_number = Gauge('zombie_process_number','check the zombie process number',['alias'])
def zombie_process_check():
    try:
        # 僵尸进程数量
        zombie_process_num = 0
        # 获取僵尸进程pid
        zombie_cmd = os.popen('ps -ef | grep defunct | grep -v grep | awk \'{print $2 }\'')
        zombie_pids = zombie_cmd.read()
        zombie_cmd.close()
        # 僵尸进程pid存列表
        zombie_pids = re.findall('\d+', zombie_pids)
        if zombie_pids.__len__() != 0:
            # 遍历僵尸进程，获取僵尸进程状态
            for i in zombie_pids:
                p = psutil.Process(int(i))
                # 若僵尸进程启动时间与当前系统unix时间差大于3600s，则判定为僵尸进程
                if (time.time() - p.create_time()) > 3600:
                    zombie_process_num += 1
                else:
                    pass
        else:
            pass
        zombie_process_number.labels(alias=hostname).set(zombie_process_num)
    except:
        pass

if __name__ == '__main__':
    port = 10000
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['port=', 'help'])
        for opt, arg in opts:
            if opt in ['-h', '--help']:
                print('''
                -h或--help，查看帮助信息
                --port= ，定义exporter端口号，参数类型int，默认10000
        ''')
                sys.exit()
            elif opt == '--port':
                port = int(arg)
    except Exception as e:
        print('输入错误，请输入-h或--help查看帮助信息')
    hostname = get_hostname()
    start_http_server(port)
    # 死循环，每15秒检查一次
    while True:
        filesystem_readonly_check()
        zombie_process_check()
        time.sleep(15)