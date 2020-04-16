# -*- coding: utf-8 -*-
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import WSGIApplication
from my_tunnelflow.rest_controller import RestController
from ryu.base import app_manager

simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'


# 交换机程序，继承于SimpleSwitch13
class SimpleSwitchRest13(app_manager.RyuApp):

    # 类别变量CONTEXT 是用來制定Ryu 中所使用的WSGI 网页服务器所对应的类别。
    # 因此可以透過wsgi Key 來取得WSGI 網頁伺服器的實體。
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
        self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(RestController, {simple_switch_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        # switches字典，存放datapath.id:datapath
        self.switches[datapath.id] = datapath

