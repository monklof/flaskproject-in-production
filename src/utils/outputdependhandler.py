# coding: utf-8
import sys,os
import logging
import datetime
import urllib
from logging.handlers import TimedRotatingFileHandler

def is_stdout_attached_to_terminal():
    '''判断当前进程组是不是前台进程组（主要关注stdout是否被关联到/dev/tty）'''
    try:
        # 如果stdout被绑定到终端设备上，则是前端进程组
        if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
            return True
        else:
            return False
    except OSError: # sys.stdout 未绑定到任何设备
        return False


class OutputDependHandler(object):
    '''根据标准输出目的地选择打印位置
    进程在终端前端运行时，打印至stdout_handler, 否则打印至default_handler
    目的是方便调试。
    '''
    
    def __new__(cls, default_handler, stdout_handler):
        if is_stdout_attached_to_terminal():
            return stdout_handler
        else:
            return default_handler
