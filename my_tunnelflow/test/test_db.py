# -*- coding: utf-8 -*-
# @Time    : 2020/5/12 10:15
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : test_db.py
from dao.querydb import QueryDB
from my_tunnelflow.orm_data import *

db = QueryDB()
# t = HostOvsdb('1.2.3.4')
# t.br_name = 'dddddddd'
# t.dpid= 0X1234
# db.update_ovsdb(t)
#
#
# ret = db.get_ovsdb('1.2.3.4')
#
# print(ret)
# print('{:0>16x}'.format(ret.dpid))
a = db.get_tunnel_port('192.168.125.158', 'p1')
print(a)
db.delete_tunnel_port('192.168.125.158', 'p1')