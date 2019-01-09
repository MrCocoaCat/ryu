# -*- coding: utf-8 -*-
# @Time    : 2019/1/9 14:08
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : 2.py

import inspect

class a(object):
    a = 1

    def f(self):
        print "ddd"

    def close(self):
        print "ddd"

b = inspect.getmembers(a)
print b
c = getattr(a, "a", None)
print c
