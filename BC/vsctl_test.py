# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 14:24
# @Author  : MrCocoaCat
# @Email   : MrCocoaCat@aliyun.com
# @File    : vsctl_test.py

from ryu.lib.ovs import vsctl


OVSDB_ADDR = 'tcp:127.0.0.1:6640'

# 判断格式是否正确
#
#vsctl.valid_ovsdb_addr(OVSDB_ADDR)

# 绑定网桥
ovs_vsctl = vsctl.VSCtl(OVSDB_ADDR)

# vsctl.VSCtlCommand 类用于定义命令

# Bridge commands.
# 'add-br'
# 'del-br'
# 'list-br'
# 'br-exists'
# 'br-to-vlan'
# 'br-to-parent'
# 'br-set-external-id'
# 'br-get-external-id'

#  添加网桥test，需要一个或三个参数
command = vsctl.VSCtlCommand(command='add-br', args=['test'], options="--may-exist")
command = vsctl.VSCtlCommand(command='add-br', args=['test', 's1', 10], options="--may-exist")

#  删除网桥test
command = vsctl.VSCtlCommand(command='del-br', args=['test'], options=" --if-exists")

# 显示所有网桥
# --fake
# --real
command = vsctl.VSCtlCommand(command='list-br')

# 判断网桥是否存在
command = vsctl.VSCtlCommand(command='br-exists', args=['test'])

# 显示fake 网桥的vlan, 如果是real网桥，则返回0
command = vsctl.VSCtlCommand(command='br-to-vlan', args=['test'])

#  如果是fake 网桥，显示其父类网桥，如果是real 则显示其自身网桥
command = vsctl.VSCtlCommand(command='br-to-parent', args=['test'])


#  如果是fake 网桥，显示其父类网桥，如果是real 则显示其自身网桥
command = vsctl.VSCtlCommand(command='br-to-parent', args=['test'])



# Port. commands
# 'list-ports'
command = vsctl.VSCtlCommand(command='list-ports', args=['s1'])
# 'add-port'
command = vsctl.VSCtlCommand(command='add-port', args=['s1', 'port2'])
# 'add-bond'
# command = vsctl.VSCtlCommand(command='add-port', args=['s1', 'port2'])

# 'del-port'
# command = vsctl.VSCtlCommand(command='del-port', args=['s1', 's1-eth99'])

# 'port-to-br' 显示port2 port所在的网桥
command = vsctl.VSCtlCommand(command='port-to-br', args=['port2'])


# Interface commands.
# 'list-ifaces' 显示网桥内所有的
command = vsctl.VSCtlCommand(command='list-ifaces', args=['s1'])

# 'iface-to-br' 显示属于inter 的网桥信息
command = vsctl.VSCtlCommand(command='list-ifaces', args=['s1'])


# Controller commands.
# 'get-controller' 显示网桥控制器
command = vsctl.VSCtlCommand(command='get-controller', args=['s1'])
# 'del-controller' 删除网桥控制器

# 'set-controller' 设置网桥控制器

# 'get-fail-mode'
# 'del-fail-mode'
# 'set-fail-mode'

# 执行命令
ovs_vsctl.run_command([command])


print(command.result)

