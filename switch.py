# -*- coding: utf-8 -*-
# @Time    : 2020/5/13 9:34
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : switch.py
# -*- coding: utf-8 -*-
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import WSGIApplication
import os, sys
from ryu.base import app_manager
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from my_tunnelflow.rest_controller import RestController
from my_tunnelflow.global_data import dpid_datapath_dict
from my_tunnelflow.rest_controller import *
simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'


# 交换机程序，继承于SimpleSwitch13
class SimpleSwitchRest13(app_manager.RyuApp):

    # 类别变量CONTEXT 是用來制定Ryu 中所使用的WSGI 网页服务器所对应的类别。
    # 因此可以透過wsgi Key 來取得WSGI 網頁伺服器的實體。
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
        # self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(RestController, {simple_switch_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        # switches字典，存放datapath.id:datapath
        # self.switches[datapath.id] = datapath
        # for k, y in self.switches.items():
        #     print(k, y)
        dpid_datapath_dict[datapath.id] = datapath
        print('begin---dpid_datapath_dict***************************')
        for k, y in dpid_datapath_dict.items():
            print(k, y)
        print('end----dpid_datapath_dict***************************')


