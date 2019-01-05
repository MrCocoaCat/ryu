# -*- coding: UTF-8 -*-

import importlib
import logging
import os
import sys

import six


LOG = logging.getLogger('ryu.utils')


def load_source(name, pathname):
    """
    This function provides the backward compatibility for 'imp.load_source'
    in Python 2.

    :param name: Name used to create or access a module object.
    :param pathname: Path pointing to the source file.
    :return: Loaded and initialized module.
    """
    if six.PY2:
        import imp
        return imp.load_source(name, pathname)
    else:
        loader = importlib.machinery.SourceFileLoader(name, pathname)
        return loader.load_module(name)


def chop_py_suffix(p):
    # 该函数将所有py结尾均切割
    for suf in ['.py', '.pyc', '.pyo']:
        # str.endswith 函数判断是否已指定字符结尾
        if p.endswith(suf):
            #  切片
            return p[:-len(suf)]
    return p


def _likely_same(a, b):
    try:
        # Samefile not availible on windows
        if sys.platform == 'win32':
            if os.stat(a) == os.stat(b):
                return True
        else:
            if os.path.samefile(a, b):
                return True
    except OSError:
        # m.__file__ is not always accessible.  eg. egg
        return False
    if chop_py_suffix(a) == chop_py_suffix(b):
        return True
    return False


def _find_loaded_module(modpath):
    # copy() to avoid RuntimeError: dictionary changed size during iteration
    for k, m in sys.modules.copy().items():
        if k == '__main__':
            continue
        if not hasattr(m, '__file__'):
            continue
        if _likely_same(m.__file__, modpath):
            return m
    return None


def _import_module_file(path):

    abspath = os.path.abspath(path)
    # Backup original sys.path before appending path to file
    # sys.path 当前python 搜索路径模块
    original_path = list(sys.path)
    # 添加当前路径
    sys.path.append(os.path.dirname(abspath))
    # os.path.basename 返回最后一个元素，通常为文件名
    # 自定义chop_py_suffix函数，用于去除后缀名
    modname = chop_py_suffix(os.path.basename(abspath))
    try:
        return load_source(modname, abspath)
    finally:
        # Restore original sys.path
        sys.path = original_path


def import_module(modname):
    if os.path.exists(modname):
        try:
            # Try to import module since 'modname' is a valid path to a file
            # e.g.) modname = './path/to/module/name.py'
            return _import_module_file(modname)
        except SyntaxError:
            # The file didn't parse as valid Python code, try
            # importing module assuming 'modname' is a Python module name
            # e.g.) modname = 'path.to.module.name'
            return importlib.import_module(modname)
    else:
        # Import module assuming 'modname' is a Python module name
        # e.g.) modname = 'path.to.module.name'
        return importlib.import_module(modname)


def round_up(x, y):
    return ((x + y - 1) // y) * y


def hex_array(data):
    """
    Convert six.binary_type or bytearray into array of hexes to be printed.
    """
    # convert data into bytearray explicitly
    return ' '.join('0x%02x' % byte for byte in bytearray(data))


def binary_str(data):
    """
    Convert six.binary_type or bytearray into str to be printed.
    """
    # convert data into bytearray explicitly
    return ''.join('\\x%02x' % byte for byte in bytearray(data))
