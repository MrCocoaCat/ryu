# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 17:17
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : OVSDB_bridge.py

from ryu.lib.ovs import vsctl
from ryu.lib.ovs import bridge

OVSDB_ADDR = 'tcp:127.0.0.1:6640'
ovs_vsctl = vsctl.VSCtl(OVSDB_ADDR)
command = vsctl.VSCtlCommand(command='add-br', args=['s1'])
ovs_vsctl.run_command([command])
#print(command.result)


br = bridge.OVSBridge(CONF=None, datapath_id=None, ovsdb_addr=OVSDB_ADDR, timeout=5, exception=None)
#print(dir(br))
br.br_name = 's1'
#print(br.br_name)
br.add_tunnel_port("vxlan1", "vxlan", "1.1.1.1", local_ip="1.1.1.0", key=1111, ofport=None)