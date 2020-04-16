# -*- coding: utf-8 -*-
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


# 继承ryu.base.app_manager.RyuApp
class SimpleSwitch13(app_manager.RyuApp):
    # 指定openflow版本
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Instruction 规定对符合match时，所进行的指令
        # OFPInstructionGotoTable
        # OFPInstructionWriteMetadata:寫入Metadata 以做為下一個table 所需的參考資料。
        # OFPInstructionActions:在目前的action set中寫入新的action，如果有相同的则覆盖
        # OFPInstructionMeter:指定該封包到所定義的meter table。
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        # APPLY_ACTIONS为立即为报文执行指令
        if buffer_id:
            # 消息类别为OFPFlowMod，instructions为指令
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
            # 发送至switch
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # ryu.controller.handler.set_ev_cls 最为其修飾函數
        # CONFIG_DISPATCHER状态：接收SwitchFeatures 訊息
        # ev.mag 存储消息类别实例，ryu.ofproto.ofproto_v1_3_parser.OFPSwitchFeatures
        # datapath 类存储讯息相关事件 ryu.controller.controller.Datapath
        datapath = ev.msg.datapath
        #print("{:0>16x}".format(datapath.id))
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        # 封包
        # 當封包沒有match 任何一個普通Flow Entry 時，則觸發Packet-In。
        match = parser.OFPMatch()
        # OFPActionOutput类是用来指定封包的类
        # 指定为OUTPUT action 类别
        # OFPP_CONTROLLER:轉送到Controller 的Packet-In 訊息
        # OFPP_FLOOD:轉送（Flood）到所有VLAN的物理連接埠，除了來源埠跟已閉鎖的埠
        # 当指定OFPCML_NO_BUFFER时，将全部加入packet-in，
        # 不会暂存在交换机中
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        # 优先级为0
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # PacketIn事件，接收位置目的的封包
        # MAIN_DISPATCHER：一般状态
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        in_port = msg.match['in_port']
        # 获取源地址，目的地址
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        # mac_to_port为类内定义的字典
        # 查找键值，若无想对应的键值，则设置
        # 如果字典中包含有给定键，则返回该键对应的值，否则返回为该键设置的值。
        self.mac_to_port.setdefault(dpid, {})
        # self.logger.info("packet in %x %s %s %s", dpid, src, dst, in_port)
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
        # print self.mac_to_port
        # 如果目的IP 在字典中，获取其值
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # 否则，设为flood发送
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
        # 如果发送flood ，则不写入流表
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        # OFPPacketOut:The controller uses this message to send a packet out throught the switch
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        # 发送至switch
        datapath.send_msg(out)


