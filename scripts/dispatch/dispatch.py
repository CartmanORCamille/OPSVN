#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/10 11:15:36
@Author  :   Camille
@Version :   1.0
'''


import time
import random
import json
import sys
sys.path.append('..\..')
from scripts.svn.SVNCheck import SVNMoudle
from scripts.windows.windows import BaseWindowsControl
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.dateAnalysis.abacus import DataAbacus


PRETTYPRINT = PrettyPrint()


class OpSVN():
    def __init__(self) -> None:
        self.SVNObj = SVNMoudle()
        with open(r'..\..\config\version.json') as f:
            self.version = json.load(f)

    def makeId(self) -> str:
        """生成标识符

        Returns:
            标识符: version_时间戳
        """
        idVersion = self.version.get('OPSVN').get('version')
        uid = '{}_{}'.format(idVersion, str(time.time()).replace('.', ''))
        return uid

    def readCache(self, cacheName):
        with open('{}'.format(cacheName), 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache

    def updateStrategyWithDichotomy(self, versions):
        # 二分法更新策略
        PRETTYPRINT.pPrint('更新策略 - 二分查找法')
        if len(versions) == 1:
            PRETTYPRINT.pPrint('发现疑似异常版本 -> {}'.format(versions[0]))
            return versions[0]

        versionPosition = int(len(versions) / 2)
        sniperBefore, sniperAfter = versions[:versionPosition], versions[versionPosition:]
        PRETTYPRINT.pPrint('版本列表二分切割前部: {}'.format(sniperBefore))
        PRETTYPRINT.pPrint('版本列表二分切割后部: {}'.format(sniperAfter))
        return (versionPosition, sniperBefore, sniperAfter)

    def dispatch(self):
        # 获取版本
        uid = self.makeId()
        self.SVNObj.updateCheck(uid)
        # 读取版本
        versionInfo = self.readCache(r'..\..\caches\FileRealVersion.json')
        versionList = versionInfo.get('FileRealVersion')
        # 二分切割
        vp, sniperBefore, sniperAfter = self.updateStrategyWithDichotomy(versionList)
        while 1:
            # 前部数据有问题，提交前部数据 / 前部数据无问题，提交后部数据
            # 开始更新 - 前部最后一个版本
            self.SVNObj.update(version=sniperBefore[-1])
            
            # 主机控制

            # 游戏内操作

            # 数据采集

            # 数据分析
            dataResult = DataAbacus.testResult()

            # 判断采用哪个版本列表
            # dataResult == 0 -> 前部数据有问题，提交前部数据
            # dataResult == 1 -> 前部数据无问题，提交后部数据
            try:
                suspiciousVersionList = []
                PRETTYPRINT.pPrint('可疑版本疑似存在前部数据') if not dataResult else PRETTYPRINT.pPrint('可疑版本疑似存在后部数据')
                suspiciousVersionList.append(sniperBefore) if not dataResult else suspiciousVersionList.append(sniperAfter)
                vp, sniperBefore, sniperAfter = self.updateStrategyWithDichotomy(suspiciousVersionList[0])
                continue
            except:
                # 命中版本
                hitVersion = suspiciousVersionList[0][0]
                break

        PRETTYPRINT.pPrint('疑似问题版本: {}'.format(hitVersion))



if __name__ == '__main__':
    obj = OpSVN()
    obj.dispatch()