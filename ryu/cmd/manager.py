# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#


import os
import sys

from ryu.lib import hub
hub.patch(thread=False)

from ryu import cfg

import logging
from ryu import log
# 调用log 模块中的early_init_log 函数
log.early_init_log(logging.DEBUG)

from ryu import flags
from ryu import version
from ryu.app import wsgi
from ryu.base.app_manager import AppManager
from ryu.controller import controller
from ryu.topology import switches


CONF = cfg.CONF
CONF.register_cli_opts([
    cfg.ListOpt('app-lists', default=[],
                help='application module name to run'),
    cfg.MultiStrOpt('app', positional=True, default=[],
                    help='application module name to run'),
    cfg.StrOpt('pid-file', default=None, help='pid file name'),
    cfg.BoolOpt('enable-debugger', default=False,
                help='don\'t overwrite Python standard threading library'
                '(use only for debugging)'),
    cfg.StrOpt('user-flags', default=None,
               help='Additional flags file for user applications'),
])


def _parse_user_flags():
    """
    Parses user-flags file and loads it to register user defined options.
    """
    try:
        # sys.argv获取程序参数，.index函数用于获取索引
        idx = list(sys.argv).index('--user-flags')
        # 获取--user-flags 后一个参数
        user_flags_file = sys.argv[idx + 1]
    except (ValueError, IndexError):
        user_flags_file = ''

    if user_flags_file and os.path.isfile(user_flags_file):
        from ryu.utils import _import_module_file
        _import_module_file(user_flags_file)


def main(args=None, prog=None):
    # 加载函数库
    _parse_user_flags()

    # 加载配置文件
    try:
        CONF(args=args, prog=prog,
             project='ryu', version='ryu-manager %s' % version,
             default_config_files=['/usr/local/etc/ryu/ryu.conf'])
    except cfg.ConfigFilesNotFoundError:
        CONF(args=args, prog=prog,
             project='ryu', version='ryu-manager %s' % version)

    log.init_log()
    logger = logging.getLogger(__name__)

    if CONF.enable_debugger:
        msg = 'debugging is available (--enable-debugger option is turned on)'
        logger.info(msg)
    else:
        hub.patch(thread=True)

    if CONF.pid_file:
        with open(CONF.pid_file, 'w') as pid_file:
            pid_file.write(str(os.getpid()))

    app_lists = CONF.app_lists + CONF.app
    # keep old behavior, run ofp if no application is specified.
    # 如果配置文件的列表为空，则加载ryu.controller.ofp_handler
    if not app_lists:
        app_lists = ['ryu.controller.ofp_handler']

    # 创建实例，调用get_instance，实现单例模式
    app_mgr = AppManager.get_instance()
    # 加载app_lists中的app
    app_mgr.load_apps(app_lists)
    # 创建上下文
    contexts = app_mgr.create_contexts()
    services = []
    services.extend(app_mgr.instantiate_apps(**contexts))

    webapp = wsgi.start_service(app_mgr)
    if webapp:
        thr = hub.spawn(webapp)
        # 加入services列表
        services.append(thr)

    try:
        # 对server服务列表遍历wait
        hub.joinall(services)
    except KeyboardInterrupt:
        # KeyboardInterrupt 用户中断执行(通常是输入^C)
        logger.debug("Keyboard Interrupt received. "
                     "Closing RYU application manager...")
    finally:
        app_mgr.close()


if __name__ == "__main__":
    main()
