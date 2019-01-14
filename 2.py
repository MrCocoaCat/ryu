# -*- coding: utf-8 -*-
# @Time    : 2019/1/9 14:08
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : 2.py

import inspect


class Fa(object):
    def __init__(self):
        a = 1

    def f(self):
        print "ddd"

    def close(self):
        print "ddd"


b = inspect.getmembers(Fa)
print b
c = getattr(Fa, "a", None)
print c

c = []
d = [1]
if not d:
    print 123