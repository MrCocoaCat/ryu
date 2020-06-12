# -*-coding:utf-8-*-
import pymysql
from DBUtils.PooledDB import PooledDB


class DB(object):
    """docstring for DbConnection"""
    __pool = None

    def __init__(self):
        self.pool = DB.__get_conn_pool()

    @staticmethod
    def __get_conn_pool():
        if DB.__pool is None:
            try:
                DB.__pool = PooledDB(creator=pymysql,
                                     host='192.168.125.183',
                                     port=3307,
                                     user='root',
                                     passwd='iiecas',
                                     db='tunnel',
                                     charset='utf8',
                                     maxconnections=10240)
            except Exception as e:
                print("%s : %s" % (Exception, e))
        return DB.__pool

    def _get_connection(self):
        conn = self.pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def _close_connection(self, conn, cursor):
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    def query_sql(self, sql, params=None):
        conn, cursor = self._get_connection()
        try:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            self._close_connection(conn, cursor)
        except Exception as e:
            self._close_connection(conn, cursor)
            print(str(e))
            raise Exception("database execute error")
        return result

    def execute_sql(self, sql, params=None):
        conn, cursor = self._get_connection()
        try:
            cursor.execute(sql, params)
            result = cursor.lastrowid
            conn.commit()
            self._close_connection(conn, cursor)
        except Exception as e:
            conn.rollback()
            self._close_connection(conn, cursor)
            print(str(e))
            raise Exception("database commit error")
        return result

    def update_sql(self, sql, params=None):
        conn, cursor = self._get_connection()
        try:
            result = cursor.execute(sql, params)
            conn.commit()
            self._close_connection(conn, cursor)
        except Exception as e:
            conn.rollback()
            self._close_connection(conn, cursor)
            print(str(e))
            raise Exception("database commit error")
        return result
