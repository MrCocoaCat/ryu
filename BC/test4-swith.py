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
        self.mac_to_port = {"0x1741f4aa82eef": {" 741f-4aa8-2f1f": 8,
                                                "741f-4aa8-2f20": 9},
                            "0x148bd3d3ad316": {}
                            }
        self.num = 0
        self.switchDic = {"0x1741f4aa82eef": "192.168.125.47",
                          "0x148bd3d3ad316": "192.168.125.43",
                          "0x148bd3d3abf96": "192.168.125.45"}

    def list_add_flow(self, add_list):
        for i in add_list:
            self.add_flow(i[0], i[1], i[2], i[3])

    def list_del_flow(self, add_list):
        for i in add_list:
            self.del_flow(i[0], i[1], i[2], i[3])

    def add_flow(self, datapath, priority, match, actions):
        print "begin add flow ..."
        print match
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=inst)
        #print mod
        datapath.send_msg(mod)

    def del_flow(self, datapath, priority, match, actions):
        print "begin del flow ..."
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
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
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        datapath_id = hex(datapath.id)
        print "datapath id :%x switch IP:%s" % (datapath.id, self.switchDic[datapath_id])
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        if "192.168.125.47" == self.switchDic[datapath_id]:
            print "192.168.125.47"
            flow_list2 = []

            # 9为125服务器，14为大交换机端口
            match3 = parser.OFPMatch(in_port=14)
            actions3 = [parser.OFPActionOutput(9)]
            match4 = parser.OFPMatch(in_port=9)
            actions4 = [parser.OFPActionOutput(14)]

            # 11监听服务器，192.168.125.123的enp4s0f1网卡
            # 12为镜像交换机的镜像端口
            match5 = parser.OFPMatch(in_port=11)
            actions5 = [parser.OFPActionOutput(12)]
            match6 = parser.OFPMatch(in_port=12)
            actions6 = [parser.OFPActionOutput(11)]

            flow_list2.append((datapath, 5, match3, actions3))
            flow_list2.append((datapath, 5, match4, actions4))
            flow_list2.append((datapath, 5, match5, actions5))
            flow_list2.append((datapath, 5, match6, actions6))
            #self.list_add_flow(flow_list2)
            self.list_del_flow(flow_list2)

            # 8 级联 ，13 为镜像交换机端口
            match10 = parser.OFPMatch(in_port=13)
            actions10 = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                                ofproto.OFPCML_NO_BUFFER)]

            #self.add_flow(datapath, 10, match10, actions10)
            self.del_flow(datapath, 10, match10, actions10)

        elif "192.168.125.43" == self.switchDic[datapath_id]:
            # 29 为119服务器，33为小交换机
            # 25 26 为iptable口，192.168.125.161 实现iptable
            print "192.168.125.43"
            flow_list1 = []

            match1 = parser.OFPMatch(in_port=29)
            actions1 = [parser.OFPActionOutput(33)]
            match2 = parser.OFPMatch(in_port=33)
            actions2 = [parser.OFPActionOutput(29)]

            # 34为小交换机，27 为路由器
            match3 = parser.OFPMatch(in_port=34)
            actions3 = [parser.OFPActionOutput(27)]
            match4 = parser.OFPMatch(in_port=27)
            actions4 = [parser.OFPActionOutput(34)]

            # 在iptable 之间加入路由器
            # 28 为路由 25为iptable
            match7 = parser.OFPMatch(in_port=28)
            actions7 = [parser.OFPActionOutput(25)]
            match8 = parser.OFPMatch(in_port=25)
            actions8 = [parser.OFPActionOutput(28)]

            flow_list1.append((datapath, 5, match1, actions1))
            flow_list1.append((datapath, 5, match2, actions2))
            flow_list1.append((datapath, 5, match3, actions3))
            flow_list1.append((datapath, 5, match4, actions4))
            flow_list1.append((datapath, 5, match7, actions7))
            flow_list1.append((datapath, 5, match8, actions8))
            #self.list_add_flow(flow_list1)
            self.list_del_flow(flow_list1)

            # 26 为iptable ，上发至控制器
            match10 = parser.OFPMatch(in_port=26)
            actions10 = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            #self.add_flow(datapath, 10, match10, actions10)
            self.del_flow(datapath, 10, match10, actions10)

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
        in_port = msg.match['in_port']
        datapath_id = hex(datapath.id)
        if "192.168.125.47" == self.switchDic[datapath_id]:
            if in_port == "13":
                pass

        elif "192.168.125.43" == self.switchDic[datapath_id]:
            if in_port == "26":
                pass

        else:
            print in_port

