# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 17:17
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : bridge_test.py

from ryu.lib.ovs import bridge

OVSDB_ADDR = 'tcp:127.0.0.1:6640'

br = bridge.OVSBridge(CONF=None, datapath_id=None, ovsdb_addr=OVSDB_ADDR, timeout=5, exception=None)

