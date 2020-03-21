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
        self.mac_to_port = {}
        self.num = 0

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        # print "begin add flow "
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
        #self.num += 1
        #print "round num: %d" % self.num
        datapath = ev.msg.datapath
        #print "datapath:%x" % datapath.id
        ofproto = datapath.ofproto
        # print "ofproto:"
        # print ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 1, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        #print "EventOFPPacketIn"
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
        #print "ethertype is %x" % eth.ethertype
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.logger.info("packet in %x src:%s dst:%s in_port:%s ", dpid, src, dst, in_port)
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # 否则，设为flood 发送
            out_port = ofproto.OFPP_FLOOD
        # 指定动作
        actions = [parser.OFPActionOutput(out_port)]
        # install a flow to avoid packet_in next time
        # 如果可以获取到out_port的值
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        else:
            # 如果发送flood ，则不写入流表
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            # OFPPacketOut:The controller uses this message to send a packet out throught the switch
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            # 发送至switch
            datapath.send_msg(out)
        self.num += 1
        #print "round num: %d" % self.num


