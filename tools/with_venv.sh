#!/bin/sh

# vim: tabstop=4 shiftwidth=4 softtabstop=4

# $@ 为所有参数
# dirname $0 定位到该脚本的绝对位置
TOOLS=`dirname $0`
# 在脚本的上一层创建虚拟环境
VENV=$TOOLS/../.venv

source $VENV/bin/activate && $@
