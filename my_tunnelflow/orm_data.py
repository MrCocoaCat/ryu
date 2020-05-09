# -*- coding: utf-8 -*-
# @Time    : 2020/3/14 13:29
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : tunnelport.py
import json


class HostOvsdb:
    def __init__(self, ip):
        self.ip = ip
        self.ovsdb_addr = 'tcp:%s:6640' % ip
        self.dpid = None
        self.ovsdb_uuid = None
        self.br_name = 'br_tunnel'
        self.tunnel_port_name = None
        self.tunnel_port_id = None


    def get_dic_json(self):
        return json.dumps(self.__dict__)


class TunnelMessage:
    def __init__(self, kwargs):
        self.port_name = kwargs.setdefault('port_name', None)
        self.tunnel_id = int(kwargs.setdefault('tunnel_id', '0'))
        self.remote_ip = kwargs.setdefault('remote_ip', None)
        if not (self.port_name and self.tunnel_id and self.remote_ip):
            raise ValueError()
        # 非必要变量
        self.local_ip = kwargs.setdefault('local_ip', None)
        self.port_id = kwargs.setdefault('port_id', None)
        self.vlan_id = kwargs.setdefault('vlan_id', None)
        self.vlan_Convert = kwargs.setdefault('vlan_Convert', None)

        if self.vlan_id is not None:
            self.vlan_id = int(kwargs.setdefault('vlan_id', None))
            if self.vlan_id > 4095 or self.vlan_Convert < 1:
                raise ValueError()
        if self.vlan_Convert is not None:
            self.vlan_Convert = int(kwargs.setdefault('vlan_Convert', None))
            if self.vlan_Convert > 4095 or self.vlan_Convert < 1:
                raise ValueError()

    def get_dic_json(self):
        return json.dumps(self.__dict__)

    def dict_init(self, **kwargs):
        pass

