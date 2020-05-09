# -*- coding: utf-8 -*-
# @Time    : 2020/3/21 13:06
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : rest_controller.py

from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import Response
from ryu.app.wsgi import route
from ryu.lib import dpid as dpid_lib
import json
from ryu.lib.ovs import vsctl
from ryu.lib.ovs import bridge
from oslo_config import cfg

from my_tunnelflow.orm_data import HostOvsdb
from my_tunnelflow.orm_data import TunnelMessage
from my_tunnelflow.global_data import ip_host_ovsdb_dict
from my_tunnelflow.global_data import tunnel_message_dict
from my_tunnelflow.response_body import *
simple_switch_instance_name = 'simple_switch_api_app'
# OVSDB_ADDR = 'tcp:127.0.0.1:6640'
# CONTROLLER_ADDR = "tcp:127.0.0.1:6633"


def get_ovsdb_addr(ip, port='6640'):
    return 'tcp:' + ip + ':' + port


opts = [
    cfg.StrOpt('tunnel_bridge', default='ovs',
               help='tunnel_bridge'),
    cfg.StrOpt('tunnel_port', default='tunnel_port',
               help='"protocols" option for ovs-vsctl (e.g. OpenFlow13)'),
    cfg.IntOpt('ovsdb_timeout', default=5,
               help='timeout ')
]
conf = cfg.ConfigOpts()
conf.register_cli_opts(opts)
server_addr = "192.168.125.183"


def add_flow(datapath, priority, match, actions, buffer_id=None):
    print('add flow')
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)]
    if buffer_id:
        mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                priority=priority, match=match,
                                instructions=inst)
    else:
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
    datapath.send_msg(mod)


def del_flow(datapath, priority, match, actions, buffer_id=None):
    print('del flow')
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)]
    mod = parser.OFPFlowMod(datapath=datapath,
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


class RestController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(RestController, self).__init__(req, link, data, **config)
        self.simple_switch_app = data[simple_switch_instance_name]

    def init_bridge(self, remote_addr):
        host_ovsdb = HostOvsdb(remote_addr)
        br = bridge.OVSBridge(CONF=conf,
                              datapath_id=None,
                              ovsdb_addr=host_ovsdb.ovsdb_addr)
        br.br_name = host_ovsdb.br_name
        # TODO:判断是否设置 ovs-vsctl set-manager "ptcp:6640"
        command1 = vsctl.VSCtlCommand(command='br-exists', args=[host_ovsdb.br_name])
        br.run_command([command1])
        if not command1.result:
            command2 = vsctl.VSCtlCommand(command='add-br', args=[host_ovsdb.br_name])
            command3 = vsctl.VSCtlCommand(command='set', args=['Bridge', host_ovsdb.br_name, 'protocols=OpenFlow13'])
            br.run_command([command2])
            br.run_command([command3])
        host_ovsdb.dpid = int(br.get_datapath_id()[0], 16)
        br.set_controller(["tcp:%s:6633" % server_addr])
        if conf.tunnel_port not in br.get_port_name_list():
            br.add_vxlan_port(conf.tunnel_port,
                              remote_ip='flow',
                              local_ip='flow',
                              key='flow')
        host_ovsdb.tunnel_port_id = br.get_ofport(conf.tunnel_port)
        ip_host_ovsdb_dict[host_ovsdb.ip] = host_ovsdb
        return host_ovsdb.br_name

    @route('simpleswitch', '/tunnel/{port}', methods=['GET'])
    def get_port(self, req, **kwargs):
        remote_addr = req.environ['REMOTE_ADDR']
        simple_switch = self.simple_switch_app
        print(req)
        port = kwargs['port']
        host_ovsdb = ip_host_ovsdb_dict.setdefault(remote_addr, None)
        if host_ovsdb is None:
            raise Exception()
        br = bridge.OVSBridge(CONF=conf,
                              datapath_id=host_ovsdb.dpid,
                              ovsdb_addr=host_ovsdb.ovsdb_addr)
        br.init()
        if port not in br.get_port_name_list():
            return Response(content_type='application/json', status=404)
        else:
            t_p = tunnel_message_dict[port]
            return ResponseSuccess(msg=t_p.get_dic_json())

    @route('simpleswitch', '/tunnel/{port}', methods=['PUT'])
    def put_port(self, req, **kwargs):
        simple_switch = self.simple_switch_app
        port = kwargs['port']
        try:
            new_entry = req.json if req.body else {}
            t_mes = TunnelMessage(new_entry)

            remote_addr = req.environ['REMOTE_ADDR']
            # server_name = req.environ['SERVER_NAME']
            host_ovsdb = ip_host_ovsdb_dict.setdefault(remote_addr, None)
            if host_ovsdb is None:
                return ResponseErrorNoInit()
            else:
                br = bridge.OVSBridge(CONF=conf,
                                      datapath_id=host_ovsdb.dpid,
                                      ovsdb_addr=host_ovsdb.ovsdb_addr)
                br.init()
            if port not in br.get_port_name_list():
                return ResponseErrorNoPort()
            t_mes.port_id = br.get_ofport(t_mes.port_name)
            if t_mes.local_ip is None:
                t_mes.local_ip = remote_addr
            tunnel_message_dict[t_mes.port_name] = t_mes
            datapath = simple_switch.switches_datapath.get(host_ovsdb.dpid)
            if datapath is not None:
                parser = datapath.ofproto_parser
                # ofproto = datapath.ofproto
                actions = [parser.NXActionSetTunnel(tun_id=t_mes.tunnel_id),
                           # OFPAT_SET_FIELD
                           parser.OFPActionSetField(tun_ipv4_dst=t_mes.remote_ip),
                           parser.OFPActionSetField(tun_ipv4_src=t_mes.local_ip),
                           parser.OFPActionOutput(host_ovsdb.tunnel_port_id),
                           ]
                match = parser.OFPMatch(in_port=t_mes.port_id)
                add_flow(datapath, 3, match, actions)

                actions2 = [parser.OFPActionOutput(t_mes.port_id)]
                match2 = parser.OFPMatch(in_port=host_ovsdb.tunnel_port_id, tunnel_id=t_mes.tunnel_id)
                add_flow(datapath, 3, match2, actions2)
            else:
                raise Exception("no depapath")
        except Exception as e:
            return ResponseErrorPortBase(msg=str(e))
        else:
            return ResponseSuccess()

    @route('simpleswitch', '/tunnel/{port}', methods=['DELETE'])
    def delete_port(self, req, **kwargs):
        port = kwargs['port']
        remote_addr = req.environ['REMOTE_ADDR']
        server_name = req.environ['SERVER_NAME']
        host_ovsdb = ip_host_ovsdb_dict.setdefault(remote_addr, None)
        if host_ovsdb is None:
            return ResponseErrorNoPort()
        else:
            br = bridge.OVSBridge(CONF=conf,
                                  datapath_id=host_ovsdb.dpid,
                                  ovsdb_addr=host_ovsdb.ovsdb_addr)
            br.init()
        t_mes = tunnel_message_dict.setdefault(port)
        if t_mes is None:
            return ResponseErrorNoPort()
        datapath = self.simple_switch_app.switches_datapath.get(host_ovsdb.dpid)
        if datapath is not None:
            parser = datapath.ofproto_parser
            actions = []
            match1 = parser.OFPMatch(in_port=t_mes.port_id)
            del_flow(datapath, 3, match1, actions)

            match2 = parser.OFPMatch(tunnel_id=t_mes.tunnel_id)
            del_flow(datapath, 3, match2, actions)
        return ResponseSuccess()

    @route('simpleswitch', '/tunnel/', methods=['PUT', 'POST'])
    def init_br(self, req):
        # 添加基础网桥
        remote_addr = req.environ['REMOTE_ADDR']
        try:
            re = self.init_bridge(remote_addr=remote_addr)
        except Exception as e:
            return ResponseErrorInitBase(msg=str(e))
        else:
            return ResponseSuccess(msg=re)

    @route('simpleswitch', '/tunnel/', methods=['GET'])
    def get_init_br(self, req):
        # 添加基础网桥
        remote_addr = req.environ['REMOTE_ADDR']
        host_ovsdb = ip_host_ovsdb_dict.setdefault(remote_addr, None)
        print(host_ovsdb.get_dic_json())
        if host_ovsdb is None:
            return Response(status=404)
        else:
            return ResponseSuccess(msg=host_ovsdb.get_dic_json())
