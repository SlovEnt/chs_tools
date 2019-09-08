# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/28 21:26'

# from datetime import datetime
import datetime
import time
import sys

import logging
from logging import handlers


class C_PrintLog(object):
    def __init__(self, logFile=""):
        self.logFile = logFile

    def debug(self, msg=""):
        now = datetime.datetime.now()
        print("\033[1;34mDEBUG INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)
        if self.logFile != "":
            self.logFile.write(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg + "\n")

    def error(self, msg=""):
        now = datetime.datetime.now()
        print("\033[1;31mERROR INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)
        if self.logFile != "":
            self.logFile.write(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg + "\n")

    def warning(self, msg=""):
        now = datetime.datetime.now()
        print("\033[1;31mWarning INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)
        if self.logFile != "":
            self.logFile.write(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg + "\n")

    def tmpinfo(self, msg=""):
        now = datetime.datetime.now()
        # if msg != "":
        #     msg = " " + msg
        print("\033[1;32mTEMP INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)

    def time_remain(self, msg, showMins):
        now = datetime.datetime.now()
        cnt = 0
        while (cnt < showMins):
            cnt += 1
            n = showMins - cnt
            time.sleep(1)
            sys.stdout.write("\r" + "\033[1;34mDEBUG INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m " +  msg %(n) , )
            if  cnt == showMins:
                sys.stdout.write("\n")
            sys.stdout.flush()
            if not n:
                return "完成"


class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,logFile,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        # log.logger.debug('debug')
        # log.logger.info('info')
        # log.logger.warning('警告')
        # log.logger.error('报错')
        # log.logger.critical('严重')
        # Logger('error.log', level='error').logger.error('error')

        fmt = '%(asctime)s - %(levelname)s: %(message)s'
        self.logger = logging.getLogger(logFile)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=logFile,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)


import os
import re
import datetime
import logging

try:
    import codecs
except ImportError:
    codecs = None

class MultiprocessHandler(logging.FileHandler):
    """支持多进程的TimedRotatingFileHandler"""
    def __init__(self,filename, when='D', backupCount=0, encoding=None, delay=False):
        """filename 日志文件名,when 时间间隔的单位,backupCount 保留文件个数
        delay 是否开启 OutSteam缓存
            True 表示开启缓存，OutStream输出到缓存，待缓存区满后，刷新缓存区，并输出缓存数据到文件。
            False表示不缓存，OutStrea直接输出到文件"""
        self.prefix = filename
        self.backupCount = backupCount
        self.when = when.upper()
        # 正则匹配 年-月-日
        self.extMath = r"^\d{4}-\d{2}-\d{2}"

        # S 每秒建立一个新文件
        # M 每分钟建立一个新文件
        # H 每天建立一个新文件
        # D 每天建立一个新文件
        self.when_dict = {
            'S':"%Y-%m-%d-%H-%M-%S",
            'M':"%Y-%m-%d-%H-%M",
            'H':"%Y-%m-%d-%H",
            'D':"%Y-%m-%d"
        }
        #日志文件日期后缀
        self.suffix = self.when_dict.get(when)
        if not self.suffix:
            raise ValueError(u"指定的日期间隔单位无效: %s" % self.when)
        #拼接文件路径 格式化字符串
        self.suffixYMD = datetime.datetime.now().strftime(self.suffix)
        self.filefmt = os.path.join("logs","%s.%s" % (self.prefix, self.suffixYMD))
        #使用当前时间，格式化文件格式化字符串
        self.filePath = self.filefmt
        #获得文件夹路径
        _dir = os.path.dirname(self.filefmt)
        try:
            #如果日志文件夹不存在，则创建文件夹
            if not os.path.exists(_dir):
                os.makedirs(_dir)
        except Exception:
            print ("创建文件夹失败")
            print ("文件夹路径：" + self.filePath)
            pass

        if codecs is None:
            encoding = None

        logging.FileHandler.__init__(self,self.filePath,'a+',encoding,delay)

    def shouldChangeFileToWrite(self):
        """更改日志写入目的写入文件
        :return True 表示已更改，False 表示未更改"""
        #以当前时间获得新日志文件路径
        _filePath = self.filefmt
        #新日志文件日期 不等于 旧日志文件日期，则表示 已经到了日志切分的时候
        #   更换日志写入目的为新日志文件。
        #例如 按 天 （D）来切分日志
        #   当前新日志日期等于旧日志日期，则表示在同一天内，还不到日志切分的时候
        #   当前新日志日期不等于旧日志日期，则表示不在
        #同一天内，进行日志切分，将日志内容写入新日志内。
        if _filePath != self.filePath:
            self.filePath = _filePath
            return True
        return False

    def doChangeFile(self):
        """输出信息到日志文件，并删除多于保留个数的所有日志文件"""
        #日志文件的绝对路径
        self.baseFilename = os.path.abspath(self.filePath)
        #stream == OutStream
        #stream is not None 表示 OutStream中还有未输出完的缓存数据
        if self.stream:
            #flush close 都会刷新缓冲区，flush不会关闭stream，close则关闭stream
            #self.stream.flush()
            self.stream.close()
            #关闭stream后必须重新设置stream为None，否则会造成对已关闭文件进行IO操作。
            self.stream = None
        #delay 为False 表示 不OutStream不缓存数据 直接输出
        #   所有，只需要关闭OutStream即可
        if not self.delay:
            #这个地方如果关闭colse那么就会造成进程往已关闭的文件中写数据，从而造成IO错误
            #delay == False 表示的就是 不缓存直接写入磁盘
            #我们需要重新在打开一次stream
            #self.stream.close()
            self.stream = self._open()
        #删除多于保留个数的所有日志文件
        if self.backupCount > 0:
            print ('删除日志')
            for s in self.getFilesToDelete():
                print (s)
                os.remove(s)

    def getFilesToDelete(self):
        """获得过期需要删除的日志文件"""
        #分离出日志文件夹绝对路径
        #split返回一个元组（absFilePath,fileName)
        #例如：split('I:\ScripPython\char4\mybook\util\logs\mylog.2017-03-19）
        #返回（I:\ScripPython\char4\mybook\util\logs， mylog.2017-03-19）
        # _ 表示占位符，没什么实际意义，
        dirName,_ = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        #self.prefix 为日志文件名 列如：mylog.2017-03-19 中的 mylog
        #加上 点号 . 方便获取点号后面的日期
        prefix = self.prefix + '.'
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                #日期后缀 mylog.2017-03-19 中的 2017-03-19
                suffix = fileName[plen:]
                #匹配符合规则的日志文件，添加到result列表中
                if re.compile(self.extMath).match(suffix):
                    result.append(os.path.join(dirName,fileName))
        result.sort()

        #返回  待删除的日志文件
        #   多于 保留文件个数 backupCount的所有前面的日志文件。
        if len(result) < self.backupCount:
            result = []
        else:
            result = result[:len(result) - self.backupCount]
        return result

    def emit(self, record):
        """发送一个日志记录
        覆盖FileHandler中的emit方法，logging会自动调用此方法"""
        try:
            if self.shouldChangeFileToWrite():
                self.doChangeFile()
            logging.FileHandler.emit(self,record)
        except (KeyboardInterrupt,SystemExit):
            raise
        except:
            self.handleError(record)

def MLogger(filename, level="debug", when="D", backCount=999):

    # 定义日志输出格式
    formattler = '%(asctime)s - line:%(lineno)d - %(levelname)s: %(message)s'
    fmt = logging.Formatter(formattler)

    # 日志级别关系映射
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL
    }

    # 获得logger，默认获得root logger对象
    # 设置logger级别 debug
    # root logger默认的级别是warning级别。
    # 不设置的话 只能发送 >= warning级别的日志
    logger = logging.getLogger()

    if not logger.handlers:

        logger.setLevel(logging.DEBUG)
        # 设置handleer日志处理器，日志具体怎么处理都在日志处理器里面定义
        # SteamHandler 流处理器，输出到控制台,输出方式为stdout
        #   StreamHandler默认输出到sys.stderr
        # 设置handler所处理的日志级别。
        #   只能处理 >= 所设置handler级别的日志
        # 设置日志输出格式
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level_relations.get(level))
        stream_handler.setFormatter(fmt)

        # 使用我们写的多进程版Handler理器，定义日志输出到mylog.log文件内
        #   文件打开方式默认为 a
        #   按分钟进行日志切割
        file_handler = MultiprocessHandler(filename, when, backCount)
        file_handler.setLevel(level_relations.get(level))
        file_handler.setFormatter(fmt)

        # 对logger增加handler日志处理器
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger
