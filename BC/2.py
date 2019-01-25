# -*- coding: utf-8 -*-
# @Time    : 2019/1/9 14:08
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : 2.py

import inspect

class a:
    a=1

b=inspect.getmembers(a)
print b