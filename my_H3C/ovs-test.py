# -*- coding: utf-8 -*-
# @Time    : 2019/1/25 16:40
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : ovs-test.py
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

# 继承ryu.base.app_manager.RyuApp
class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        # mac:port 的映射
        self.mac_to_port = {}
        self.num = 0

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        print "begin add flow "
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        # APPLY_ACTIONS为立即为报文执行指令
        if buffer_id:
            # 消息类别为OFPFlowMod，instructions为指令
            mod = parser.OFPFlowMod(datapath=datapath,
                                    buffer_id=buffer_id,
                                    priority=priority,
                                    match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=priority,
                                    match=match,
                                    instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        print "datapath:%x" % datapath.id
        ofproto = datapath.ofproto
        # print "ofproto:"
        # print ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 1, match, actions)
        datapath_id = hex(datapath.id)
        print datapath_id

        if datapath_id == "0x720756b76142":
            # tap1
            match1 = parser.OFPMatch(in_port=3, eth_src="3e:ef:3d:57:84:da")
            actions1 = [parser.OFPActionOutput(4)]
            self.add_flow(datapath, 5, match1, actions1)
            # tap2
            match2 = parser.OFPMatch(in_port=3, eth_src="a2:64:d0:6b:86:df")
            actions2 = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 5, match2, actions2)

            match3 = parser.OFPMatch(in_port=4)
            actions3 = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 5, match3, actions3)
            match4 = parser.OFPMatch(in_port=2)
            action4 = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 5, match4, action4)

        elif datapath_id == "0x12c37da24148":
            # tap1
            match1 = parser.OFPMatch(in_port=1, eth_src="a2:64:d0:6b:86:df")
            actions1 = [parser.OFPActionOutput(7)]
            self.add_flow(datapath, 5, match1, actions1)

            match2 = parser.OFPMatch(in_port=7, eth_src="3e:ef:3d:57:84:da")
            actions2 = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 5, match2, actions2)


            # tap2
            match2 = parser.OFPMatch(in_port=1, eth_src="3e:ef:3d:57:84:da")
            actions2 = [parser.OFPActionOutput(8)]
            self.add_flow(datapath, 5, match2, actions2)

            match3 = parser.OFPMatch(in_port=8, eth_src="a2:64:d0:6b:86:df")
            actions3 = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 5, match3, actions3)





    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        print "EventOFPPacketIn"
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        # ev 为事件

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        # print "in_port:%d" % in_port
        # 获取源地址，目的地址
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        #if eth.ethertype == ether_types.ETH_TYPE_LLDP:
        #   print "ignor packet"
           #return
        if eth.ethertype == 105:
            return
        print "ethertype is %x" % eth.ethertype
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.logger.info("packet in %x src:%s dst:%s in_port:%s ", dpid, src, dst, in_port)
        # learn a mac address to avoid FLOOD next time.
        # mac:port 的映射
        self.mac_to_port[dpid][src] = in_port




