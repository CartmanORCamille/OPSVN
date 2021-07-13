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
import os
from scripts.svn.SVNCheck import SVNMoudle
from scripts.windows.windows import BaseWindowsControl, GrabFocus, ProcessMonitoring
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.dateAnalysis.abacus import FPSAbacus, VRAMAbacus, CrashAbacus
from scripts.dataMining.miner import Perfmon
from scripts.game.update import Update


PRETTYPRINT = PrettyPrint()


class OPSVN():
    def __init__(self) -> None:
        self._checkCaseExists()
        self.SVNObj = SVNMoudle()
        # 线程信号
        self.grabFocusFlag = threading.Event()
        with open(r'.\config\version.json') as f:
            self.version = json.load(f)
        # 数据分析表
        self.dataAbacusTable = {
            'FPS': FPSAbacus,
            'RAM': VRAMAbacus,
            'crash': CrashAbacus,
        }

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
        # 检查case是否存在
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

    def _checkCaseExists(self):
        if not os.path.isfile(r'.\config\case.json'):
            # 检查case原始文件是否存在
            PRETTYPRINT.pPrint('case.json 未发现', 'WARING', bold=True)
            originalFile = 'case_ALPHA_'
            exists = [i for i in os.listdir(r'.\config') if i.startswith(originalFile)]
            if exists:
                PRETTYPRINT.pPrint('发现case.json(original)，开始重命名文件')
                originalFilePath = os.path.join(r'.\config', exists[0])
                os.rename(originalFilePath, r'.\config\case.json')
            else:
                PRETTYPRINT.pPrint('未发现 case.json/(original) 文件', 'ERROR', bold=True)
                raise FileNotFoundError('未发现 case.json/(original) 文件')
        PRETTYPRINT.pPrint('发现 case.json 文件')

    def dispatch(self):
        # 启动焦点监控 -> 保持暂停状态
        threading.Thread(target=self.grabFocusThread, name='grabFocus').start()

        # 读取配置文件
        caseInfo = self.readCase()

        # 更新 lua script 初始化
        updateObj = Update()
        updateObj.dispatch()

        # 获取版本
        uid = caseInfo.get('uid')
        self.SVNObj.updateCheck(uid)
        # 读取版本
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
            time.sleep(30)

            '''数据采集'''
            perfmonMiner = Perfmon()
            filePath = perfmonMiner.dispatch(uid, sniperBefore[-1])

            '''数据分析'''
            analysisMode, machineGPU = caseInfo.get('DefectBehavior'), caseInfo.get('machine').get('GPU')
            abacus = self.dataAbacusTable.get(analysisMode)(filePath, machineGPU)
            dataResult = abacus.dispatch()
            
            '''判断采用哪个版本列表'''
            # dataResult 数据分析结果
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
    obj = OPSVN()
    obj.readCase()