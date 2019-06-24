# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/28 21:36'
__version__ = '1.1'


import datetime
import re
import os
import time
import paramiko
from openpyxl import load_workbook
from random import Random

def get_now_date(dateFormat):

    nowDate = datetime.now()
    Y = nowDate.strftime("%Y")
    M = nowDate.strftime("%m")
    D = nowDate.strftime("%d")

    if dateFormat == "y-m-d" or dateFormat == "Y-M-D":
        strDate = str(Y)+"-"+str(int(M))+"-"+str(int(D))
    elif dateFormat == "yyyy-mm-dd" or dateFormat == "YYYY-MM-DD":
        strDate = str(Y)+"-"+str(M)+"-"+str(D)
    elif dateFormat == "yyyymmdd" or dateFormat == "YYYYMMDD":
        strDate = str(Y)+str(M)+str(D)
    elif dateFormat == "yyyymmdd_HHMMSS" or dateFormat == "YYYYMMDD_HHMMSS":
        strDate = nowDate.strftime("%Y%m%d_%H%M%S")
    else:
        return 'Get_Now_Date("%s"),入参无效' % dateFormat

    return strDate

def dict2list(dic:dict):
    ''' 将字典转化为列表 '''
    keys = dic.keys()
    vals = dic.values()
    lst = [(key, val) for key, val in zip(keys, vals)]
    return lst

def comp_multiline_text(multStr):
    ''' 压缩多行文本代码，主要用于多行SQL压缩为一行 '''
    line = multStr.splitlines()
    ''' 如果行数不仅仅只为一行，则进行多行处理模式 '''
    if len(line) != 1 :
        newSql = ""
        for x in line:
            newSql = newSql + " " + x.lstrip()
            newSql = re.sub(r'\s{2,}',' ',newSql)
        return newSql.lstrip().rstrip()
    else:
        ''' 单行只需要去除前后空格即可 '''
        return multStr.lstrip().rstrip()

def get_trading_day():
    # 获取交易日,通过组策略下发的文本文件
    todayYMD = time.strftime("%Y%m%d", time.localtime())  # YYYYMMDD
    tradeDayFile = r"C:\Windows\HolidayList.txt"
    fileRdade = open(tradeDayFile)
    line = fileRdade.readline()
    while line:
        strFlag = line.split(" ")
        if todayYMD == strFlag[0] and int(strFlag[1]) == 2:
            return False
        line = fileRdade.readline()
    fileRdade.close()
    return True

def get_last_trading_day(dfDay):
    # 获取交易日,通过组策略下发的文本文件取上一个交易日

    nowDay = datetime.datetime.now()

    deltaDayNum = int(dfDay)

    ''' 日历由域控下发，不在域控的机器需要手工拷贝文件到该目录 '''
    tradeDayFile = r"C:\Windows\HolidayList.txt"
    fileRdade = open(tradeDayFile)

    dayFlagArr = []
    for line in fileRdade.readlines():
        ''' 合并字典日期和节假日标志，保持为无空格字符串用于匹配比对 '''
        dayFlag = line.strip("\n").replace(" ", "")
        dayFlagArr.append(dayFlag)

    while True :

        ''' 日期计算 得出指定的上一个交易日 '''
        deltaDay = datetime.timedelta(days=deltaDayNum)
        lastTradeDay = nowDay - deltaDay
        lastTradeDayX = lastTradeDay.strftime('%Y%m%d')
        lastTradeDay = "%s1" % lastTradeDay.strftime('%Y%m%d') # YYYYMMDDF F=标志（1或2）

        if lastTradeDay in dayFlagArr:
            ''' 如果计算出的交易日加标识包含在数组内，则认为当前日期为交易日 '''
            return lastTradeDayX
        elif deltaDayNum > 365 :
            ''' 如果循环日期超过365次，不可能会出现连续放假365天的可能，则基本认为是交易日历有问题 '''
            return False

        ''' 如果是非交易日，则计数累计加1 取再上一天 '''
        deltaDayNum = deltaDayNum + 1

    return False

def print_dict_item(dict,dictName="x"):
    for key, value in dict.items():
        print ("""{2}["{0}"] = {1}""".format(key, value, dictName))
    print()
    time.sleep(0.5)

def get_linux_env_nls_lang(sshCmd):
    '''取Oracle用户下的字符集编码'''
    '''需要实例化sshCmd'''
    strCMD = "cat ~/.bash_profile |grep NLS_LANG"
    stdin, stdout, stderr = sshCmd.exec_command(strCMD)
    for std in stdout.readlines():
        if "#" not in std.strip("\n"):
            dataReg = re.compile(r"""export NLS_LANG=["|'](.+?)['|"]""")
            rawDatas = dataReg.findall(std.strip("\n"))
            if len(rawDatas) == 1:
                return rawDatas[0]
    return False

def get_exclude_list(xlsFile,xlsSheetName):
    # 读取Excek文件
    xlsWBook = load_workbook(xlsFile)
    xlsWSheet = xlsWBook.get_sheet_by_name(xlsSheetName)
    startRow = 2  # 起始行号
    xlsRowList = []

    colCnt = len(list(xlsWSheet.columns))
    rowCnt = len(list(xlsWSheet.rows))
    xlsWSheet = list(xlsWSheet.rows)

    xSn = 0
    for rowv in range(1, rowCnt):
        xSn = xSn + 1
        colDict={}
        for colv in range(0, colCnt):
            if xlsWSheet[rowv][colv].value == None:
                valueX = ""
            else:
                valueX = xlsWSheet[rowv][colv].value

                # 如果Excel里的变量为字符型，则去前后空格，减免出错几率
                if isinstance(valueX,str) == True:
                    valueX = valueX.strip()

            colDict[xlsWSheet[0][colv].value] = valueX
            colDict["xSn"] = xSn
        if int(colDict["处理标志"][0]) == 0:
            xlsRowList.append(colDict)

    return xlsRowList

def get_ssh_hander(hostIP, userName, userPasswd):
    sshCmd = paramiko.SSHClient()
    sshCmd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshCmd.connect(hostIP, 22, userName, userPasswd)
    return sshCmd

def Net_RemtePath_IsAccess(remoteNetPath, remoteHostUser, remoteHostUserPasswd):

    strCmd = r"net use %s %s /user:%s" % (remoteNetPath, remoteHostUserPasswd, remoteHostUser)

    try:
        from subprocess import PIPE, Popen
        cmdHandle = Popen(strCmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = cmdHandle.communicate()
        strOutMsg = out.decode("gb2312")
        strErrMsg = err.decode("gb2312")
        if strOutMsg:
            rtnCmdMsg = strOutMsg
        else:
            rtnCmdMsg = strErrMsg

        rtnCmdMsgLine = ""
        for line in rtnCmdMsg:
            rtnCmdMsgLine += line.strip()

        if "1219" in rtnCmdMsgLine or strOutMsg:
            # 尝试文件是否可以进行读写操作
            import uuid
            wirteFlagFile = "%s\%s" % (remoteNetPath,str(uuid.uuid4()))
            with open(wirteFlagFile, "w") as testFile:
                pass
            os.remove(wirteFlagFile)
            return True
        else:
            return rtnCmdMsgLine

    except Exception as e:
        return e

def Get_Random_Str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz013456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str
