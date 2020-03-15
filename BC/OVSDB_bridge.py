# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 17:17
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : OVSDB_bridge.py

from ryu.lib.ovs import vsctl
from ryu.lib.ovs import bridge
from oslo_config import cfg


OVSDB_ADDR = 'tcp:192.168.83.132:6640'
ret = vsctl.valid_ovsdb_addr(OVSDB_ADDR)
ovs_vsctl = vsctl.VSCtl(OVSDB_ADDR)
command1 = vsctl.VSCtlCommand(command='br-exists', args=['br0'])
#command2 = vsctl.VSCtlCommand(command='add-br', args=['test111'], options='--may-exist')

ovs_vsctl.run_command([command1])
print(command1.result)

#ovs_vsctl.run_command([command2])
#print(command2.result)
# print(command3.result)

opts = [
    cfg.StrOpt('switch', default='ovs',
               help='test switch [ovs|cpqd]'),
    cfg.StrOpt('protocols', default='OpenFlow13',
               help='"protocols" option for ovs-vsctl (e.g. OpenFlow13)'),
    cfg.IntOpt('ovsdb_timeout', default=5,
               help=' timeout ')
]
conf = cfg.ConfigOpts()
conf.register_cli_opts(opts)
print(conf.protocols)


br = bridge.OVSBridge(CONF=conf, datapath_id=None, ovsdb_addr=OVSDB_ADDR)
br.br_name = 's1'
ret = br.get_datapath_id()
print(ret)

exit(0)

br.br_name = 's1'
# print(br.br_name)

br.add_tunnel_port("vxlan1", "vxlan", "1.1.1.1", local_ip="1.1.1.0", key=1111, ofport=None)


