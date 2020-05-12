# -*-coding:utf-8-*-

from my_tunnelflow.dao.dbcon import DB
globala = []
db = DB()
from my_tunnelflow.orm_data import *


class QueryDB(object):

    def __init__(self):
        pass

    # 查询Int型结果，sqlStr查询数据库的结果是一个整数，需要做sql查询结果空值的判断
    def queryint(self, res):
        try:
            if len(res) == 0:
                return 0
            elif len(res) == 1:
                return res
            else:
                return res[0]
        except TypeError:
            return -1

    def get_ovsdb(self, ip):
        sql = "SELECT * from ovsdb where ip = %s"
        res = db.query_sql(sql, ip)
        tmp = HostOvsdb(ip)
        if len(res) == 0:
            return None
        rt = res[0]
        rt['dpid'] = int(rt['dpid'], 16)
        tmp.__dict__ = res[0]
        return tmp

    def update_ovsdb(self, ovsdb):
        sql = "REPLACE INTO ovsdb values(%s,%s,%s,%s,%s,%s)"
        dpid = '{:0>16x}'.format(ovsdb.dpid)
        res = db.update_sql(sql, (ovsdb.IP, ovsdb.ovsdb_addr, dpid, ovsdb.br_name,
                                  ovsdb.tunnel_port_name, ovsdb.tunnel_port_id))
        return res

    def get_tunnel_port(self, ip, port_name):
        sql = "SELECT * FROM tunnel_port WHERE IP=%s AND port_name = %s"

        res = db.query_sql(sql, (ip, port_name))
        if len(res) == 0:
            return None
        tmp = TunnelPort(res[0])
        # print(tmp.__dict__)
        # if len(res) == 0:
        #     return None
        # tmp.__dict__ = res[0]
        return tmp

    def update_tunnel_port(self, tunnel_port):
        sql = "REPLACE INTO tunnel_port values(%s,%s,%s,%s,%s,%s,%s,%s)"
        print(tunnel_port.__dict__)
        res = db.update_sql(sql, (tunnel_port.IP,
                                  tunnel_port.port_name,
                                  tunnel_port.tunnel_id,
                                  tunnel_port.remote_ip,
                                  tunnel_port.local_ip,
                                  tunnel_port.port_id,
                                  tunnel_port.vlan_id,
                                  tunnel_port.vlan_Convert))
        return res
