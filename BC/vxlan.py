# -*- coding: utf-8 -*-
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import ryu.app.ofctl.api
from ryu.utils import hex_array

# 继承ryu.base.app_manager.RyuApp
class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)

        self.sw1 = range(25, 36)
        self.sw2 = range(7, 15)

        self._ETH_TYPE_DIC = {0x0800: "TH_TYPE_IP",
                              0x0806: "ETH_TYPE_ARP",
                              0x6558: "ETH_TYPE_TEB",
                              0x8100: "ETH_TYPE_8021Q",
                              0x86dd: "ETH_TYPE_IPV6",
                              0x8809: "ETH_TYPE_SLOW",
                              0x8847: "ETH_TYPE_MPLS",
                              0x88a8: "ETH_TYPE_8021AD",
                              0x88cc: "ETH_TYPE_LLDP",
                              0x88e7: "ETH_TYPE_8021AH",
                              0x05dc: "ETH_TYPE_IEEE802_3",
                              0x8902: "ETH_TYPE_CFM"}
        self.switchDic = {"0x148bd3d3ad316": "43-instance1",
                          "0x1741f4aa82eef": "192.168.125.47",
                          "0x248bd3d3ad316": "43-instance2"
                          }
        self.dataPathDic = {}

    @staticmethod
    def add_flow(datapath, priority, match, actions):
        print "begin add flow "
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)

    @staticmethod
    def clean_flow(datapath, in_port_list):
        print "begin clean flow ..."
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        priority = 5
        for in_port in in_port_list:
            match = parser.OFPMatch(in_port=in_port)
            mod = parser.OFPFlowMod(datapath,
                                    cookie=0,
                                    cookie_mask=0,
                                    table_id=0,
                                    command=ofproto.OFPFC_DELETE,
                                    idle_timeout=0,
                                    hard_timeout=0,
                                    priority=priority,
                                    buffer_id=ofproto.OFP_NO_BUFFER,
                                    out_port=ofproto.OFPP_ANY,
                                    out_group=ofproto.OFPG_ANY,
                                    flags=0,
                                    match=match)
            datapath.send_msg(mod)

    def vxlan(self, datapath):
        print("vxlan")
        pass
        # self.clean_flow(datapath, self.sw1)
        # parser = datapath.ofproto_parser
        # match1 = parser.OFPMatch(in_port=18, arp_sha="52:54:00:68:46:03", vlan_vid=600)
        # #actions1 = [parser.OFPActionOutput(33)]
        # actions1 = [parser.OFPActionPopVlan()]
        # self.add_flow(datapath, 5, match1, actions1)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        datapath_id = hex(datapath.id)
        self.dataPathDic.setdefault(datapath_id, datapath)
        print "datapath id :%x switch IP:%s" % (datapath.id, self.switchDic[datapath_id])
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        if "43-instance2" == self.switchDic[datapath_id]:
            self.vxlan(datapath)


    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        if msg.reason == ofp.OFPPR_ADD:
            reason = 'ADD'
        elif msg.reason == ofp.OFPPR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofp.OFPPR_MODIFY:
            reason = 'MODIFY'
        else:
            reason = 'unknown'
        print('OFPPortStatus received: reason=%s desc=%s', reason, msg.desc)


    @set_ev_cls(ofp_event.EventOFPErrorMsg,[ CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
        print('OFPErrorMsg received: type=0x%02x code=0x%02x '
                'message=%s', msg.type, msg.code, hex_array(msg.data))

