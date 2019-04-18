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
    def clean_flow(datapath):
        print "begin clean flow ..."
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        priority = 5
        match = parser.OFPMatch()
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

        self.clean_flow(datapath)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # 封包
        #match = parser.OFPMatch(vlan_vid=(0x1000 | 600))
        # 动作
        match = parser.OFPMatch(in_port=17)
        actions = [parser.OFPActionOutput(18)]
        #actions = [ parser.OFPActionPushVlan(ethertype=33024, type_=None, len_=None)]

       # actions = [parser.OFPActionPopVlan()]


        # 指令
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        # 更改流表状态信息
        mod = parser.OFPFlowMod(datapath,
                                cookie=0,
                                cookie_mask=0,
                                table_id=0,
                                # 增加流表
                                command=ofproto.OFPFC_ADD,
                                idle_timeout=0,
                                hard_timeout=0,
                                priority=5,
                                buffer_id=ofproto.OFP_NO_BUFFER,
                                out_port=ofproto.OFPP_ANY,
                                out_group=ofproto.OFPG_ANY,
                                flags=0,
                                match=match,
                                instructions=inst)

        #datapath.send_msg(mod)


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
        TypeDct = {"OFPET_HELLO_FAILED" : 0,            # Hello protocol failed.
                   "OFPET_BAD_REQUEST" : 1,              # Request was not understood.
                    "OFPET_BAD_ACTION" : 2,               # Error in action description.
                    "OFPET_BAD_INSTRUCTION": 3,           # Error in instruction list.
                    "OFPET_BAD_MATCH": 4,                 # Error in match.
                  "OFPET_FLOW_MOD_FAILED": 5,           # Problem modifying flow entry.
                  "OFPET_GROUP_MOD_FAILED": 6,          # Problem modifying group entry.
                  "OFPET_PORT_MOD_FAILED":7,           # OFPT_PORT_MOD failed.
                  "OFPET_TABLE_MOD_FAILED": 8,          # Table mod request failed.
                  "OFPET_QUEUE_OP_FAILED": 9,           # Queue operation failed.
                  "OFPET_SWITCH_CONFIG_FAILED": 10,     # Switch config request failed.
                  "OFPET_ROLE_REQUEST_FAILED": 11,      # Controller Role request failed.
                  "OFPET_METER_MOD_FAILED": 12,         # Error in meter.
                  "OFPET_TABLE_FEATURES_FAILED": 13,    # Setting table features failed.
                  "OFPET_EXPERIMENTER" : 0xffff,         # Experimenter error messages.
                  }
        print 'OFPErrorMsg received: type=0x%02x code=0x%02x' % (msg.type, msg.code)

    # pack-in
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        data = msg.data

        in_port = msg.match['in_port']
        pkt = packet.Packet(data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        # eth 为class ethernet 对象
        dst = eth.dst
        src = eth.src
        ethertype = self._ETH_TYPE_DIC.get(eth.ethertype, "UNKNOW_TYPE")
        datapath_id = hex(datapath.id)
        self.logger.info("packet in %s -- ethertype:%s src:%s dst:%s in_port:%s ",
                         datapath_id, ethertype, src, dst, in_port)
