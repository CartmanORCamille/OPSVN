#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/10 11:15:36
@Author  :   Camille
@Version :   1.0
'''


import time
import threading
import json
from scripts.svn.SVNCheck import SVNMoudle
from scripts.windows.windows import BaseWindowsControl, GrabFocus, ProcessMonitoring
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.dateAnalysis.abacus import DataAbacus


PRETTYPRINT = PrettyPrint()


class OpSVN():
    def __init__(self) -> None:
        self.SVNObj = SVNMoudle()
        # 线程信号
        self.grabFocusFlag = threading.Event()
        with open(r'.\config\version.json') as f:
            self.version = json.load(f)

    def makeId(self) -> str:
        """生成标识符

        Returns:
            标识符: version_时间戳
        """
        idVersion = self.version.get('OPSVN').get('version')
        uid = '{}_{}'.format(idVersion, str(time.time()).replace('.', ''))
        return uid

    def readCache(self, cacheName) -> dict:
        with open('{}'.format(cacheName), 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache

    def readConfig(self) -> dict:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    def readCase(self) -> dict:
        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            case = json.load(f)
        return case

    def updateStrategyWithDichotomy(self, versions) -> tuple:
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

    def grabFocusThread(self) -> None:
        while 1:
            self.grabFocusFlag.wait()
            GrabFocus.dispatch()
            time.sleep(2)

    def dispatch(self):
        # 启动焦点监控 -> 保持暂停状态
        threading.Thread(target=self.grabFocusThread, name='grabFocus').start()

        # 获取版本
        uid = self.makeId()
        self.SVNObj.updateCheck(uid)
        # 读取版本
        configInfo = self.readConfig()
        caseInfo = self.readCase()
        versionInfo = self.readCache(r'.\caches\FileRealVersion.json')
        # uid验证
        if versionInfo.get('uid') != uid:
            raise LookupError('uid对比失效，可能数据未获取成功')

        versionList = versionInfo.get('FileRealVersion')
        if not versionList:
            raise ValueError('未获取到版本')

        # 二分切割
        vp, sniperBefore, sniperAfter = self.updateStrategyWithDichotomy(versionList)
        while 1:
            # 前部数据有问题，提交前部数据 / 前部数据无问题，提交后部数据
            # 开始更新 - 前部最后一个版本
            self.SVNObj.update(version=sniperBefore[-1])
            
            '''主机控制'''
            # 开程序
            PRETTYPRINT.pPrint('尝试启动游戏')
            BaseWindowsControl.consoleExecutionWithPopen(caseInfo.get('Path').get('Jx3Remake'), caseInfo.get('Path').get('Jx3BVTWorkPath'))

            # 识别进程是否启动
            while 1:
                PRETTYPRINT.pPrint('等待进程启动中')
                result = ProcessMonitoring.dispatch()
                if result:
                    break
                time.sleep(2)

            # 打开焦点监控  
            PRETTYPRINT.pPrint('启动焦点监控线程')
            time.sleep(2)
            self.grabFocusFlag.set()

            '''游戏内操作'''
            '''数据采集'''
            time.sleep(30)

            '''数据分析'''
            dataResult = DataAbacus.testResult()

            '''判断采用哪个版本列表'''
            # dataResult == 0 -> 前部数据有问题，提交前部数据
            # dataResult == 1 -> 前部数据无问题，提交后部数据
            PRETTYPRINT.pPrint('可疑版本疑似存在前部数据') if not dataResult else PRETTYPRINT.pPrint('可疑版本疑似存在后部数据')

            testResult = self.updateStrategyWithDichotomy(sniperBefore) if not dataResult else self.updateStrategyWithDichotomy(sniperAfter)
            if len(testResult) == 3:
                vp, sniperBefore, sniperAfter = testResult
                # 关闭游戏
                processName = 'JX3ClientX64.exe'
                PRETTYPRINT.pPrint('尝试结束游戏')
                BaseWindowsControl.killProcess(processName)

                # 暂停焦点监控
                PRETTYPRINT.pPrint('暂停焦点监控进程')
                self.grabFocusFlag.clear()
                continue
            else:
                # 命中版本
                hitVersion = testResult
                # 暂停焦点监控
                PRETTYPRINT.pPrint('暂停焦点监控进程')
                self.grabFocusFlag.clear()
                break

        PRETTYPRINT.pPrint('疑似问题版本: {}'.format(hitVersion))
        



if __name__ == '__main__':
    obj = OpSVN()
    obj.dispatch()