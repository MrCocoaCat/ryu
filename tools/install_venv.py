# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4


"""
Installation script for Quantum's development virtualenv
"""

import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
VENV = os.path.join(ROOT, '.venv')

# 相关需求项的列表
PIP_REQUIRES = os.path.join(ROOT, 'tools', 'pip-requires')
OPTIONAL_REQUIRES = os.path.join(ROOT, 'tools', 'optional-requires')
TEST_REQUIRES = os.path.join(ROOT, 'tools', 'test-requires')

PY_VERSION = "python%s.%s" % (sys.version_info[0], sys.version_info[1])

VENV_EXISTS = bool(os.path.exists(VENV))

def die(message, *args):
    print >> sys.stderr, message % args
    sys.exit(1)

# 执行系统命令函数
def run_command(cmd, redirect_output=True, check_exit_code=True):
    """
    Runs a command in an out-of-process shell, returning the
    output of that command.  Working directory is ROOT.
    """
    # subprocess模块用于产生子进程
    # 如果参数为redirect_output ，则创建PIPE
    if redirect_output:
        stdout = subprocess.PIPE
    else:
        stdout = None
    # cwd 参数指定子进程的执行目录为ROOT，执行cwd 函数
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=stdout)
    # 如果子进程输出了大量数据到stdout或者stderr的管道，并达到了系统pipe的缓存大小的话，
    # 子进程会等待父进程读取管道，而父进程此时正wait着的话，将会产生死锁。
    # 使用communicate() 返回值为 (stdoutdata , stderrdata )
    output = proc.communicate()[0]
    if check_exit_code and proc.returncode != 0:
        # 程序不返回0，则失败
        raise Exception('Command "%s" failed.\n%s' % (' '.join(cmd), output))
    return output


HAS_EASY_INSTALL = bool(run_command(['which', 'easy_install'],
                                    check_exit_code=False).strip())

# 执行which 指令，strip为去除首位字符串
# which指令会在环境变量$PATH设置的目录里查找符合条件的文件。
#  如果没有无，则标准输出stdoutdata-返回空，错误输出stderrdata-相应提示
HAS_VIRTUALENV = bool(run_command(['which', 'virtualenv'],
                                    check_exit_code=False).strip())


def check_dependencies():
    """Make sure virtualenv is in the path."""

    if not HAS_VIRTUALENV:
        raise Exception('Virtualenv not found. ' + \
                         'Try installing python-virtualenv')
    print 'done.'


def create_virtualenv(venv=VENV, install_pip=False):
    """Creates the virtual environment and installs PIP only into the
    virtual environment
    """
    print 'Creating venv...',

    install = ['virtualenv', '-q', venv]
    run_command(install)

    print 'done.'
    print 'Installing pip in virtualenv...',
    if install_pip and \
            not run_command(['tools/with_venv.sh', 'easy_install',
                             'pip>1.0']):
        die("Failed to install pip.")
    # 调用with_venv.sh 脚本启动venv
    # die 函数为输出为stderr
    print 'done.'


def install_dependencies(venv=VENV):
    print 'Installing dependencies with pip (this can take a while)...'
    run_command(['tools/with_venv.sh', 'pip', 'install', '-r',
                 PIP_REQUIRES], redirect_output=False)
    run_command(['tools/with_venv.sh', 'pip', 'install', '-r',
                 OPTIONAL_REQUIRES], redirect_output=False)
    run_command(['tools/with_venv.sh', 'pip', 'install', '-r',
                 TEST_REQUIRES], redirect_output=False)

    # Tell the virtual env how to "import quantum"
    pthfile = os.path.join(venv, "lib", PY_VERSION, "site-packages",
                                 "quantum.pth")
    f = open(pthfile, 'w')
    f.write("%s\n" % ROOT)


def print_help():
    help = """
 Quantum development environment setup is complete.

 Quantum development uses virtualenv to track and manage Python dependencies
 while in development and testing.

 To activate the Quantum virtualenv for the extent of your current shell
 session you can run:

 $ source .venv/bin/activate

 Or, if you prefer, you can run commands in the virtualenv on a case by case
 basis by running:

 $ tools/with_venv.sh <your command>

 Also, make test will automatically use the virtualenv.
    """
    print help


def main(argv):
    check_dependencies()
    create_virtualenv()
    install_dependencies()
    print_help()

if __name__ == '__main__':
    main(sys.argv)
