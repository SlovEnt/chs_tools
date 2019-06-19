# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/2 21:54'

from bs4 import BeautifulSoup
from global_function import get_html_all_content_proxy
from collections import OrderedDict
import time

# 从数据库获取代理

class Chs_Proxy(object):

    def __init__(self, mysqlExe):
        self.mysqlExe = mysqlExe

    def verifi_proxy_webmasterhome(self, proxyInfoDict):
        verifiUrl = "http://ip.webmasterhome.cn/"
        rtnHtmlContent = get_html_all_content_proxy(verifiUrl, "本机IP地址", "UTF-8", proxyInfoDict)
        # print(rtnHtmlContent)
        if "本机IP地址" in rtnHtmlContent:
            soup = BeautifulSoup(rtnHtmlContent, 'html.parser')
            localIpaddress = soup.find_all(name="span", attrs={"id": "ipaddr"})[0].text
            localIpaddress = localIpaddress.replace("本机IP地址：", "")
            localIpaddress = localIpaddress.replace("IP物理地址：请点击IP查看 ↑", "")
        else:
            localIpaddress = "127.0.0.1"

        if proxyInfoDict["ip"] == localIpaddress:
            return True
        else:
            return localIpaddress

    def verifi_proxy_ipip(self, proxyInfoDict):
        verifiUrl = "https://www.ipip.net/ip.html"
        rtnHtmlContent = get_html_all_content_proxy(verifiUrl, 'name="ip"', "UTF-8", proxyInfoDict)

        # print("----------------------{0}\n----------------------".format(rtnHtmlContent))

        if 'name="ip"' in rtnHtmlContent:
            soup = BeautifulSoup(rtnHtmlContent, 'html.parser')
            localIpaddress = soup.find_all(name="input")[0]["value"]
        else:
            localIpaddress = "127.0.0.1"

        if proxyInfoDict["ip"] == localIpaddress:
            return True
        else:
            return localIpaddress

    def verifi_proxy_icanhazip(self, proxyInfoDict):
        verifiUrl = "http://icanhazip.com/"

        rtnHtmlContent = get_html_all_content_proxy(verifiUrl, 'controls', "UTF-8", proxyInfoDict)

        print("-----------beg-----------\n{0}\n---------end-------------".format(rtnHtmlContent))

        if '.' in rtnHtmlContent:
            soup = BeautifulSoup(rtnHtmlContent, 'html.parser')
            localIpaddress = soup.find_all(name="pre")[0].text
        else:
            localIpaddress = "127.0.0.1"

        if proxyInfoDict["ip"] == localIpaddress:
            return True
        else:
            return localIpaddress

    def get_proxy_list(self):
        try:
            rtnDate = []
            sqlStr = "select ip, `port`, type, country, addr, weights, is_ok from proxy_list where is_ok='Y' ORDER BY weights"
            rtnDate = self.mysqlExe.query(sqlStr)
            return rtnDate
        except Exception as e:
            print(e)
            return False

    def update_proxy_weights(self, proxyInfoDict):
        try:
            sqlStr = "update proxy_list set weights=weights+1 where ip='{0}' and port='{1}' and type='{2}'".format(
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
                proxyInfoDict["type"],
            )
            self.mysqlExe.execute(sqlStr)
            return True
        except Exception as e:
            print(e)
            return False

    def insert_proxy_info(self, proxyInfoDict):
        try:
            sqlStr = "INSERT INTO `v2PySql`.`proxy_list` (`country`, `ip`, `port`, `addr`, `type`,  `weights`, `is_ok`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '0', 'Y');".format(
                proxyInfoDict["country"],
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
                proxyInfoDict["addr"],
                proxyInfoDict["type"],
            )
            self.mysqlExe.execute(sqlStr)
            return True
        except Exception as e:
            print(e)
            return False

    def select_proxy(self, proxyInfoDict):
        try:
            rtnDate = []
            sqlStr = "SELECT * FROM proxy_list WHERE ip='{0}' AND port='{1}' AND type='{2}'".format(
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
                proxyInfoDict["type"],
            )
            rtnDate = self.mysqlExe.query(sqlStr)
            return rtnDate
        except Exception as e:
            print(e)
            return False

    def generate_db_proxy_list_dict(self):
        proxyInfoDict = OrderedDict()
        proxyInfoDict["ip"] = " "
        proxyInfoDict["port"] = " "
        proxyInfoDict["type"] = " "
        proxyInfoDict["country"] = " "
        proxyInfoDict["addr"] = " "
        proxyInfoDict["weights"] = 0
        proxyInfoDict["is_ok"] = "Y"
        return proxyInfoDict

    def print_verifi_results(self, proxyInfoDict, resultsStr):
        pass
