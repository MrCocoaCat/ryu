# -*- coding: utf-8 -*-
# @Time    : 2020/4/15 10:48
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : response_body.py
import json
from webob.response import Response as webob_Response

# 1 返回成功
# 1000 初始化错误

# 1100 添加Tunnel错误
# 1101 未初始化
# 1102 无这个端口


class ResponseTunnelBase(webob_Response):
    """
    Wrapper class for webob.response.Response.

    The behavior of this class is the same as webob.response.Response
    except for setting "charset" to "UTF-8" automatically.
    """

    def __init__(self, num,  status, msg, *args, **kwargs):
        body = json.dumps({'num': num, 'msg': msg})
        super(ResponseTunnelBase, self).__init__(charset="UTF-8",
                                                 body=body,
                                                 content_type='application/json',
                                                 status=status, *args, **kwargs)


class ResponseSuccess(ResponseTunnelBase):
    def __init__(self, msg=''):
        ResponseTunnelBase.__init__(self, num=1, msg=msg, status=201)


# 1000
class ResponseErrorInitBase(ResponseTunnelBase):
    def __init__(self, num=1000, msg='', status=404):
        ms = 'Init Error:'
        ResponseTunnelBase.__init__(self, num=num, msg=ms + msg, status=status)
        print(self.__dict__)

# 1100
class ResponseErrorPortBase(ResponseTunnelBase):
    def __init__(self, num=1100, msg='', status=404):
        ms = 'Tunnel Error:'
        ResponseTunnelBase.__init__(self, num=num, msg=ms + msg, status=status)
        print(self.__dict__)


class ResponseErrorNoInit(ResponseErrorPortBase):
    def __init__(self, msg="No Init ,please init first"):
        ResponseErrorPortBase.__init__(self, num=1101, msg=msg, status=404)


class ResponseErrorNoPort(ResponseErrorPortBase):
    def __init__(self, msg="No this port"):
        ResponseErrorPortBase.__init__(self, num=1102, msg=msg, status=404)
