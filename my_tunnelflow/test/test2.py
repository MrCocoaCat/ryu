# -*- coding: utf-8 -*-
# @Time    : 2020/4/15 10:26
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : test2.py

from ryu.lib.ovs import vsctl
from ryu.lib.ovs import bridge
from oslo_config import cfg

from my_tunnelflow.orm_data import HostOvsdb
from my_tunnelflow.orm_data import TunnelMessage
from my_tunnelflow.global_data import ip_host_ovsdb_dict
from my_tunnelflow.global_data import tunnel_message_dict

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



host_ovsdb = HostOvsdb('192.168.125.149')
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