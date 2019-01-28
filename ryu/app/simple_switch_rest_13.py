# -*- coding: utf-8 -*-
# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import Response
from ryu.app.wsgi import route
from ryu.app.wsgi import WSGIApplication
from ryu.lib import dpid as dpid_lib

simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'


# 交换机程序，继承于SimpleSwitch13
class SimpleSwitchRest13(simple_switch_13.SimpleSwitch13):

    # 类别变量CONTEXT 是用來制定Ryu 中所使用的WSGI 网页服务器所对应的类别。
    # 因此可以透過wsgi Key 來取得WSGI 網頁伺服器的實體。
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
        self.switches = {}
        wsgi = kwargs['wsgi']
        # 注册
        wsgi.register(SimpleSwitchController, {simple_switch_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(SimpleSwitchRest13, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        # switches字典，存放datapath.id:datapath
        self.switches[datapath.id] = datapath
        # mac_to_port 字典，存放datapath.id:
        self.mac_to_port.setdefault(datapath.id, {})
        print self.mac_to_port
        #print "%d " % datapath.id

    def set_mac_to_port(self, dpid, entry):
        # 获取到这个交换机的字典，其存放mac:port 键值对
        mac_table = self.mac_to_port.setdefault(dpid, {})
        datapath = self.switches.get(dpid)

        # entry 是传入的字典参数
        entry_port = entry['port']
        entry_mac = entry['mac']

        if datapath is not None:
            parser = datapath.ofproto_parser
            # values() 获取字典的value
            if entry_port not in mac_table.values():
                #  获取字典的每一个元素
                for mac, port in mac_table.items():

                    # from known device to new device
                    actions = [parser.OFPActionOutput(entry_port)]
                    # 封包
                    match = parser.OFPMatch(in_port=port, eth_dst=entry_mac)
                    self.add_flow(datapath, 1, match, actions)

                    # from new device to known device
                    actions = [parser.OFPActionOutput(port)]
                    match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
                    self.add_flow(datapath, 1, match, actions)

                mac_table.update({entry_mac: entry_port})
        return mac_table


# 连接控制器
class SimpleSwitchController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(SimpleSwitchController, self).__init__(req, link, data, **config)
        self.simple_switch_app = data[simple_switch_instance_name]

    @route('simpleswitch', '/simpleswitch/mactable/{dpid}', methods=['GET'],
           requirements={'dpid': dpid_lib.DPID_PATTERN})
    def list_mac_table(self, req, **kwargs):
        #  返回列表
        simple_switch = self.simple_switch_app
        dpid = dpid_lib.str_to_dpid(kwargs['dpid'])

        if dpid not in simple_switch.mac_to_port:
            return Response(status=404)

        mac_table = simple_switch.mac_to_port.get(dpid, {})
        # 将python 类型转换为json 类型
        body = json.dumps(mac_table)
        return Response(content_type='application/json', body=body)

    @route('simpleswitch', '/simpleswitch/mactable/{dpid}', methods=['PUT'],
           requirements={'dpid': dpid_lib.DPID_PATTERN})
    def put_mac_table(self, req, **kwargs):

        simple_switch = self.simple_switch_app
        # 将字符串转换为16进制int
        dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
        try:
            new_entry = req.json if req.body else {}
        except ValueError:
            raise Response(status=400)

        if dpid not in simple_switch.mac_to_port:
            return Response(status=404)

        try:
            # 调用set_mac_to_port 函数
            mac_table = simple_switch.set_mac_to_port(dpid, new_entry)
            body = json.dumps(mac_table)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)
