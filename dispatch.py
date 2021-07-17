#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/10 11:15:36
@Author  :   Camille
@Version :   1.0
'''


from multiprocessing.context import ProcessError
import time
import threading
import json
import os
from multiprocessing import Process
from threading import Thread
from scripts.svn.SVNCheck import SVNMoudle
from scripts.windows.windows import BaseWindowsControl, GrabFocus, ProcessMonitoring
from scripts.windows.contact import FEISHU
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.dateAnalysis.abacus import FPSAbacus, VRAMAbacus, CrashAbacus
from scripts.dataMining.miner import PerfMon
from scripts.game.update import Update
from scripts.game.gameControl import debugGameControl


PRETTYPRINT = PrettyPrint()


class OPSVN():
    def __init__(self) -> None:
        self._checkCaseExists()
        self.SVNObj = SVNMoudle()
        self.feishu = FEISHU()
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

    def _readCache(self, cacheName) -> dict:
        with open('{}'.format(cacheName), 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache

    def _readConfig(self) -> dict:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    def _readCase(self) -> dict:
        # 检查case是否存在
        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            case = json.load(f)
        return case

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

    def _checkGameIsReady(self):
        # 检查缓存文件游戏是否准备好
        if os.path.exists(r'.\caches\GameStatus.json'):
            PRETTYPRINT.pPrint('识别到 GameStatus.json ')
            with open(r'.\caches\GameStatus.json', 'r', encoding='utf-8') as f:
                status = json.load(f)
                if status.get('orReady'):
                    PRETTYPRINT.pPrint('游戏已就绪，可以采集数据')
                    return True
        else:
            PRETTYPRINT.pPrint('未识别到 GameStatus.json ，等待中')
            return False

    def _createNewProcess(self, func, name, *args, **kwargs) -> Process:
        p = Process(target=func, name=name)
        return p

    def dispatch(self):
        # 启动焦点监控 -> 保持暂停状态
        threading.Thread(target=self.grabFocusThread, name='grabFocus').start()

        # 读取配置文件
        caseInfo = self._readCase()

        # 更新 lua script 初始化
        updateObj = Update()
        updateObj.dispatch()

        # 获取版本
        uid = caseInfo.get('uid')
        self.SVNObj.updateCheck(uid)
        # 读取版本
        versionInfo = self._readCache(r'.\caches\FileRealVersion.json')
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
            nowVersion = sniperBefore[-1]
            self.SVNObj.update(version=nowVersion)
            
            '''主机控制'''
            # 开程序
            PRETTYPRINT.pPrint('尝试启动游戏')
            processName, cwd = caseInfo.get('Path').get('Jx3Remake'), caseInfo.get('Path').get('Jx3BVTWorkPath')
            BaseWindowsControl.consoleExecutionWithPopen(processName, cwd)

            # 识别进程是否启动
            while 1:
                PRETTYPRINT.pPrint('等待进入游戏中')
                result = ProcessMonitoring.dispatch()
                if result:
                    break
                time.sleep(2)

            # 打开焦点监控  
            PRETTYPRINT.pPrint('启动焦点监控线程')
            time.sleep(2)
            self.grabFocusFlag.set()

            '''游戏内操作'''
            # 需要单独开一个线程去运行游戏控制
            gameControlProcess = self._createNewProcess(debugGameControl, 'debugGameControl')
            gameControlProcess.start()

            '''数据采集'''
            while 1:
                # 等待游戏环境就绪
                gameStatus = self._checkGameIsReady()
                if gameStatus:
                    break
                time.sleep(2)
            PRETTYPRINT.pPrint('初始化 PerfMon 模块')
            recordTime = caseInfo.get('RecordTime')
            perfmonMiner = PerfMon()
            filePath = perfmonMiner.dispatch(uid, nowVersion, recordTime=None)

            # 暂停焦点监控
            PRETTYPRINT.pPrint('暂停焦点监控进程')
            self.grabFocusFlag.clear()

            '''数据分析'''
            # 主数据分析 -> 决定性结论
            analysisMode, machineGPU = caseInfo.get('DefectBehavior'), caseInfo.get('machine').get('GPU')
            mainAbacus = self.dataAbacusTable.get(analysisMode)(filePath, machineGPU)
            PRETTYPRINT.pPrint('主要数据分析 -> CHECK: {}, GPU: {}'.format(mainAbacus, machineGPU))
            mainDataResult = mainAbacus.dispatch()
            # 次要数据分析
            secondaryAbacus = self.dataAbacusTable.get('FPS')(filePath, machineGPU) if analysisMode == 'VRAM' else analysisMode == self.dataAbacusTable.get('RAM')
            PRETTYPRINT.pPrint('次要数据分析 -> CHECK: {}, GPU: {}'.format(secondaryAbacus, machineGPU))
            secondaryDataResult = secondaryAbacus.dispatch()
            
            '''判断采用哪个版本列表'''
            # dataResult 数据分析结果
            # dataResult == 0 -> 前部数据有问题，提交前部数据
            # dataResult == 1 -> 前部数据无问题，提交后部数据
            PRETTYPRINT.pPrint('可疑版本疑似存在前部数据') if not mainDataResult else PRETTYPRINT.pPrint('可疑版本疑似存在后部数据')

            # 信息记录
            with open('.\\caches\\result_{}'.format(nowVersion), 'w', encoding='utf-8') as f:
                # 记录数据
                resultData = {
                    'uid': uid,
                    'version': nowVersion,
                    'DefactBehavior': analysisMode,
                    'FPS': None,
                    'VRAM': None,
                }
                if analysisMode == 'FPS':
                    resultData['FPS'] = mainDataResult
                    resultData['VRAM'] = secondaryDataResult
                elif analysisMode == 'VRAM':
                    resultData['FPS'] = secondaryDataResult
                    resultData['VRAM'] = mainDataResult
                json.dump(resultData, f, indent=4)

            '''消息通知'''
            PRETTYPRINT.pPrint('正在通知 FEISHU')
            feishuResultData = self.feishu.drawTheMsg(uid, nowVersion, machineGPU, resultData['FPS'], resultData['VRAM'], 'stand(DEBUG)', analysisMode)
            self.feishu.sendMsg(feishuResultData)

            testResult = self.updateStrategyWithDichotomy(sniperBefore) if not mainDataResult else self.updateStrategyWithDichotomy(sniperAfter)
            if len(testResult) == 3:
                vp, sniperBefore, sniperAfter = testResult
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
    obj.dispatch()
    # print('{}'.format(FPSAbacus(11, 1)))
    # PRETTYPRINT.pPrint('111: {}'.format(FPSAbacus(11, 1)))