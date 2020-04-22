# -*- coding: utf-8 -*-
# @Time    : 2020/3/26 16:43
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : test.py
# -*- coding: utf-8 -*-
# @Time    : 2020/3/21 13:06
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com

from requests import put, get
import json
import os
import socket

this_ns_ip = None
remote_ip = None


def clean():
    os.system('ovs-vsctl −−if−exists del-br br-tunnel ')
    os.system('ip netns del ns1')


def add_port():
    os.system('ovs-vsctl add-port br-tunnel p1 -- set Interface p1 type=internal')
    os.system('ip netns add ns1')
    os.system('ip link set p1 netns ns1')
    os.system('ip netns exec ns1 ip addr add %s dev p1' % this_ns_ip)


def test_ping():
    os.system('ip netns exec ns1 ping %s' % remote_ns_ip)


if __name__ == '__main__':
    clean()
    # 获取计算机名称
    hostname = socket.gethostname()

    if hostname == 'test1':
        this_ns_ip = '10.0.0.10/24'
        remote_ns_ip = '10.0.0.20/24'
        remote_ip = '192.168.83.138'
    elif hostname == 'test2':
        this_ns_ip = '10.0.0.20/24'
        remote_ns_ip = '10.0.0.10/24'
        remote_ip = '192.168.83.137'
    else:
        exit(0)

    ret = put('http://192.168.83.132:8080/tunnel/')
    add_port()
    ret2 = put('http://192.168.83.132:8080/tunnel/p1', data=json.dumps({
        'port_name': 'p1',
        'tunnel_id': 89,
        'remote_ip': remote_ip,

        'port_id': None,
        'vlan_id': None,
        'vlan_convert': None,
        'local_ip': None,
    }))
    print(ret2)
