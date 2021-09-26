#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/07/22 11:39:25
@Author  :   Camille
@Version :   1.0
'''


import sys
import time
import threading
import json
import os
import sys
from typing import Tuple
sys.path.append(os.getcwd())
from multiprocessing import Queue
from multiprocessing import Process
from threading import Thread
from scripts.svn.SVNCheck import SVNMoudle
from scripts.windows.windows import BaseWindowsControl, GrabFocus, ProcessMonitoring, FindTheFile
from scripts.windows.contact import FEISHU
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.dataAnalysis.abacus import FPSAbacus, VRAMAbacus, CrashAbacus, DataAbacus
from scripts.dataMining.miner import PerfMon
from scripts.game.update import Update


PRETTYPRINT = PrettyPrint()


class OPSVN():
    def __init__(self, *args, **kwargs) -> None:
        self.logName = '{}.log'.format(time.strftime('%S_%M_%H_%d_%m_%Y'))
        self.ghost, self.gamingCrash, self.grabFocusExitFlag, self.processMonitorExitFlag = 0, 0, False, False
        self.processMonitoringObj = ProcessMonitoring(logName=self.logName)

        # log使用方法：self.logObj.logHandler()
        self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
        self.SVNObj = SVNMoudle(logName=self.logName)
        self.feishu = FEISHU(logName=self.logName)
        self._checkCaseExists()
        self.queue = Queue()
        
        self.logObj.logHandler().info('Initialize all class instance.')

        # 线程信号
        self.grabFocusFlag = threading.Event()

        # 读取版本文件信息
        with open(r'..\config\version.json', 'r', encoding='utf-8') as f:
            self.version = json.load(f)
        self.logObj.logHandler().info('OPSVN version info -> version: {}'.format(self.version.get('OPSVN').get('version')))

        self.logObj.logHandler().info('Thread signal creation.')
        # 数据分析表
        self.dataAbacusTable = {
            'FPS': FPSAbacus,
            'RAM': VRAMAbacus,
            'crash': CrashAbacus,
        }
        self.logObj.logHandler().info('End of dispatch.py __init__ function.')

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

    def removeExceptionVersion(self, nowVersion: str, versionList: list) -> list:
        if nowVersion in versionList:
            versionList.remove(nowVersion)
        else:
            self.logObj.logHandler().error('[P0] Delete the downtime version error, check whether the version exists in sniperBefore.')
            raise ValueError('删除宕机版本失误，检查版本是否存在于 sniperBefore')
        return versionList

    def grabFocusThread(self, version, uid) -> None:
        while 1:
            self.grabFocusFlag.wait()
            grabObj = GrabFocus(logName=self.logName)
            result = grabObj.dispatch(version, uid)
            if result == 'Ghost':
                # 未响应
                self.ghost += 1
            elif result == 1400:
                # 无效句柄
                continue
            elif result == 'GamingCrash':
                # 进入游戏后宕机
                PRETTYPRINT.pPrint('Gaming is crash now!')
                self.logObj.logHandler().info('Gaming is crash now! self.gamingCrash = 1.')
                self.gamingCrash = 1
                break
            else:
                self.ghost = 0
            time.sleep(2)

    def processMonitor(self, method, versionPath, nowVersion, *args, **kwargs):
        self.startingCrash = False
        self.startupStatus = None
        self.processLoadingFlag = 0
        self.progressBarLoadingFlag = 0
        while 1:
            if self.processMonitorExitFlag:
                self.processMonitorExitFlag = False
                break
            PRETTYPRINT.pPrint('processLoadingFlag: {}, self.progressBarLoadingFlag: {}'.format(self.processLoadingFlag, self.progressBarLoadingFlag))
            self.logObj.logHandler().info('processLoadingFlag: {}, self.progressBarLoadingFlag: {}'.format(self.processLoadingFlag, self.progressBarLoadingFlag))

            if self.processLoadingFlag == 60 or self.progressBarLoadingFlag == 60:
                self.startingCrash = True
                PRETTYPRINT.pPrint('进度条等待时间过长，可能Clinet有问题，进入下一轮配置路径更新')
                self.logObj.logHandler().info('The waiting time of the progress bar is too long, there may not be a problem with Clinet, enter the next round of configuration path update.')
                # 截图
                BaseWindowsControl.activationWindow(None, '剑侠情缘网络版叁_LoadingClass')
                BaseWindowsControl.screenshots(os.path.join(versionPath, 'LoadingTimeout.jpg'))
                BaseWindowsControl.killProcess('JX3ClientX64.exe')
                break

            ''' 进度条识别 '''
            if method == 'loading':
                self.logObj.logHandler().info('Wait for the client process to exist.')
                PRETTYPRINT.pPrint('等待进入游戏中')
                self.startupStatus = self.processMonitoringObj.dispatch(version=nowVersion)
                if self.startupStatus == 'loading':
                    PRETTYPRINT.pPrint('进度条加载中')
                    self.progressBarLoadingFlag += 1
                    time.sleep(1)
                    continue
                self.processLoadingFlag += 1
            
            ''' 进程识别 '''
            if method == 'gamingCrash' or self.startupStatus and self.processLoadingFlag >= 3: 
                if isinstance(self.startupStatus, tuple):
                    # 宕机
                    self.startingCrash = True
                    BaseWindowsControl.killProcess('DumpReport64.exe')
                    PRETTYPRINT.pPrint('启动时宕机 - 结束宕机窗口进程')
                    self.logObj.logHandler().info('Staring Crash, End the downtime window process')
                    break
                elif self.startupStatus:
                    # 进入游戏
                    self.logObj.logHandler().info('Client process exists.')
                    break
                else:
                    PRETTYPRINT.pPrint('可能是异常的 self.startupStatus 返回值: {}'.format(self.startupStatus))
                    PRETTYPRINT.pPrint('dispatch 进程扫描 self.startupStatus 反馈 - 未识别到"加载中窗口"， "客户端窗口"，"宕机窗口"')
                    self.logObj.logHandler().info('Process scanning-"Loading window", "Client window", "Down window" are not recognized.')
                    continue
                
            time.sleep(2)
        self.logObj.logHandler().info('self.startingCrash: {}'.format(self.startingCrash))

    def gamingCrashEvent(self):
        # 游戏宕机处理方法
        PRETTYPRINT.pPrint('游戏宕机事件触发')
        self.logObj.logHandler().info('Game crash event triggered.')
        # 待补充

    def _readCache(self, cacheName) -> dict:
        with open('{}'.format(cacheName), 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache

    def _readConfig(self) -> dict:
        with open(r'..\config\config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    def _readCase(self) -> dict:
        # 检查case是否存在
        with open(r'..\config\case.json', 'r', encoding='utf-8') as f:
            case = json.load(f)
        return case

    def _checkCaseExists(self):
        if not os.path.isfile(r'..\config\case.json'):
            # 检查case原始文件是否存在
            PRETTYPRINT.pPrint('case.json 未发现', 'WARING', bold=True)
            self.logObj.logHandler().warning('case.json not found, check if the original file exists.')
            originalFile = 'case_ALPHA_'
            exists = [i for i in os.listdir(r'..\config') if i.startswith(originalFile)]
            if exists:
                self.logObj.logHandler().info('Found case.json(original), start to rename the file.')
                PRETTYPRINT.pPrint('发现case.json(original)，开始重命名文件')
                originalFilePath = os.path.join(r'..\config', exists[0])
                os.rename(originalFilePath, r'..\config\case.json')
                self.logObj.logHandler().info('The name has been changed, the original file name: {}, the current file name: {}.'.format(exists, 'case.json'))
            else:
                PRETTYPRINT.pPrint('未发现 case.json/(original) 文件', 'ERROR', bold=True)
                self.logObj.logHandler().error('[P1] No case.json/(original) file found.')
                raise FileNotFoundError('未发现 case.json/(original) 文件')
        PRETTYPRINT.pPrint('发现 case.json 文件')

    def _checkGameIsReady(self):
        # 检查缓存文件
        # 检查游戏是否准备好
        if os.path.exists(r'..\caches\GameStatus.json'):
            PRETTYPRINT.pPrint('识别到 GameStatus.json ')
            with open(r'..\caches\GameStatus.json', 'r', encoding='utf-8') as f:
                status = json.load(f)
                if status.get('orReady'):
                    PRETTYPRINT.pPrint('游戏已就绪，可以采集数据')
                    return True
        else:
            PRETTYPRINT.pPrint('未识别到 GameStatus.json ，等待中')
            return False

    def _makeId(self) -> str:
        """生成标识符

        Returns:
            标识符: version_时间戳
        """
        idVersion = self.version.get('OPSVN').get('version')
        uid = '{}_{}'.format(idVersion, str(time.time()).replace('.', ''))
        return uid

    def _createNewThread(self, func, name, *args, **kwargs) -> Thread:
        t = Thread(target=func, name=name, args=(*args, ))
        self.logObj.logHandler().info('dispatch.py - Child thread object has been generated: {}, child process name: {}'.format(t, name))
        return t

    def _createNewProcess(self, func, name, *args, **kwargs) -> Process:
        p = Process(target=func, name=name)
        self.logObj.logHandler().info('dispatch.py - Child process object has been generated: {}, child process name: {}'.format(p, name))
        return p
    
    def _getLogName(self):
        return self.logObj

    def _stopGrabFocusThread(self):
        self.grabFocusExitFlag = True

    def _stopProcessMonitorThread(self):
        self.processMonitorExitFlag = True

    def dispatch(self):
        # 读取配置文件
        self.logObj.logHandler().info('Reading case.json.')
        caseInfo = self._readCase()

        # 获取版本
        uid = caseInfo.get('uid')
        self.logObj.logHandler().info('Ready to find and record the SVN version, case uid: {}.'.format(uid))
        self.SVNObj.updateCheck(uid)
        self.logObj.logHandler().info('Obtained SVN version.')

        # 读取版本
        self.logObj.logHandler().info('Reading version.json.')
        fileRealVersionInfo = self._readCache(r'..\caches\FileRealVersion.json')
        # uid验证
        if fileRealVersionInfo.get('uid') != uid:
            self.logObj.logHandler().error('[P3] The uid comparison is invalid, the data may not be obtained successfully')
            raise LookupError('uid对比失效，可能数据未获取成功')

        versionList = fileRealVersionInfo.get('FileRealVersion')
        if not versionList:
            self.logObj.logHandler().error('[P2] SVN version not obtained.')
            raise ValueError('未获取到版本')

        # 去除宕机版本
        # with open('', 'r', encoding='utf-8') as f:
        #     crashVersons = f.read()

        rootDataPath = os.path.join('..', 'caches', 'usuallyData', uid)
        BaseWindowsControl.whereIsTheDir(rootDataPath, True)

        # 更新 lua script 初始化
        self.logObj.logHandler().info('Start checking lua script.')
        updateObj = Update(logName=self.logName)
        updateObj.dispatch(rootDataPath, caseInfo.get('InMap'))

        # 二分切割
        testResult = self.updateStrategyWithDichotomy(versionList)
        self.logObj.logHandler().info('Dichotomizing is completed -> VP: {}, sniperBefore: {}, sniperAfter: {}'.format(*testResult))
        while 1:
            if len(testResult) == 3:
                vp, sniperBefore, sniperAfter = testResult
                nowVersion = sniperBefore[-1]
            else:
                nowVersion = testResult
            # 删除 result 文件
            if os.path.exists(rootDataPath):
                [os.remove(os.path.join(rootDataPath, file)) for file in os.listdir(rootDataPath) if file.endswith('done') or file.endswith('scanned')]

            # 前部数据有问题，提交前部数据 / 前部数据无问题，提交后部数据
            # 开始更新 - 前部最后一个版本
            self.logObj.logHandler().info('Ready to update: {}'.format(nowVersion))
            self.SVNObj.update(version=nowVersion)
            
            # 创建子版本文件夹
            versionPath = os.path.join(rootDataPath, nowVersion)
            BaseWindowsControl.whereIsTheDir(versionPath, True)

            '''主机控制'''
            # 开程序
            self.logObj.logHandler().info('Ready to start client.')
            PRETTYPRINT.pPrint('尝试启动游戏')
            processName, cwd = caseInfo.get('Path').get('Jx3'), caseInfo.get('Path').get('Jx3BVTWorkPath')
            BaseWindowsControl.consoleExecutionWithPopen(processName, cwd)

            # 识别进程是否启动
            loadingWaitingProcessBarThread = self._createNewThread(self.processMonitor, 'loadingWaitingProcessBarThread', 'loading', versionPath, nowVersion, )
            loadingWaitingProcessBarThread.start()
            loadingWaitingProcessBarThread.join()

            if self.startingCrash is False:
                # 代码逻辑走到这里一定是要保证已经打开了游戏客户端
                # 启动焦点监控 -> 保持暂停状态
                self.logObj.logHandler().info('Start focus monitoring: pause.')
                geabFocusThreadObj = Thread(target=self.grabFocusThread, name='grabFocusThread', args=(nowVersion, uid))
                geabFocusThreadObj.start()
                # 启动时不宕机
                # 打开焦点监控  
                PRETTYPRINT.pPrint('启动焦点监控线程')
                time.sleep(2)
                self.logObj.logHandler().info('Start focus monitoring: Start.')
                self.grabFocusFlag.set()

                '''游戏内操作，打开游戏后就自动调用searchpanel，dispatch.py只做等待'''
                
                '''数据采集'''
                if not self.gamingCrash:
                    self.logObj.logHandler().info('Initialize the perfmon module.')
                    PRETTYPRINT.pPrint('初始化 PerfMon 模块')
                    recordTime = caseInfo.get('RecordTime')
                    perfmonMiner = PerfMon(logName=self.logName, queue=self.queue)
                    filePath = perfmonMiner.dispatch(uid, nowVersion, self.processMonitoringObj.dispatch(isPid=1), recordTime=None, grabFocusFlag=self.grabFocusFlag)
                    self.logObj.logHandler().info('Game data has been cleaned.')
                else:
                    # 在采集数据之前就宕机了
                    self.gamingCrashEvent()

                '''数据分析'''
                analysisMode, machineGPU = caseInfo.get('DefectBehavior'), caseInfo.get('Machine').get('GPU')
                self.logObj.logHandler().info('analysisMode: {} machineGPU: {}'.format(analysisMode, machineGPU))
                if analysisMode != 'crash':
                    # FPS AND VRAM
                    mainAbacus = self.dataAbacusTable.get(analysisMode)(filePath, machineGPU, logName=self.logName)
                    PRETTYPRINT.pPrint('主要数据分析 -> CHECK: {}, GPU: {}'.format(mainAbacus, machineGPU))
                    self.logObj.logHandler().info('Main data analysis -> CHECK: {}, GPU: {}.'.format(mainAbacus, machineGPU))
                    mainDataResult, mainData = mainAbacus.dispatch()
                    self.logObj.logHandler().info('Main data analysis conclusion: {}, value: {}'.format(mainDataResult, mainData))

                    secondaryDataResult, secondaryData = '', ''
                else:
                    # crash
                    mainData = 'crash'
                    crashAbacus = self.dataAbacusTable.get(analysisMode)(logName=self.logName)
                    mainDataResult = crashAbacus.dispatch()
                
                # mainDataResult is bool, mainData is int or 'crash'
                self.logObj.logHandler().info('mainDataResult: {}, mainData: {}'.format(mainDataResult, mainData))

                # 信息记录
                resultVersionFile = 'result_{}.json'.format(nowVersion)
                with open('..\\caches\\usuallyData\\{}\\{}'.format(uid, resultVersionFile), 'w', encoding='utf-8') as f:
                    # 记录数据
                    resultData = {
                        'uid': uid,
                        'version': nowVersion,
                        'DefactBehavior': analysisMode,
                        'FPS': None,
                        'VRAM': None,
                    }
                    if analysisMode == 'FPS':
                        resultData['FPS'] = mainData
                        resultData['VRAM'] = secondaryData
                    elif analysisMode == 'RAM':
                        resultData['FPS'] = secondaryData
                        resultData['VRAM'] = mainData
                    self.logObj.logHandler().info('Saved file: {}, Comprehensive data value -> FPS: {}, VRAM: {}'.format(resultVersionFile, resultData['FPS'], resultData['VRAM']))
                    json.dump(resultData, f, indent=4)

                PRETTYPRINT.pPrint('正在通知 FEISHU')
                self.logObj.logHandler().info('Notifying Feishu.')

            else:
                ''' 不正常的状态 '''
                # 删除宕机或者Timeout版本
                sniperBefore = self.removeExceptionVersion(nowVersion, sniperBefore)
                PRETTYPRINT.pPrint('删除版本: {}'.format(nowVersion))
                self.logObj.logHandler().info('[{}] - version deleted: {}'.format(self.startupStatus, nowVersion))
                # 客户端错误导致的版本规避，代表本次的循环是作废的，合并并重新二分版本列表
                versionList = sniperBefore + sniperAfter
                PRETTYPRINT.pPrint('合并后新版本集: {}'.format(versionList))
                self.logObj.logHandler().info('New version set after merging: {}'.format(versionList))
                testResult = self.updateStrategyWithDichotomy(versionList)
                self.logObj.logHandler().info('New testResult: {}'.format(testResult))

            if len(testResult) == 3:
                if not self.startingCrash:
                    # 正常流程 - 未定位到版本
                    self.logObj.logHandler().info('Suspicious version missed. current version: {}'.format(nowVersion))
                    self.logObj.logHandler().info('Data results of the next round of dichotomy -> sniperBefore: {}, sniperAfter: {}'.format(sniperBefore, sniperAfter))
                    result = 'MISS'
                    '''消息通知'''
                    feishuResultData = self.feishu._drawTheNormalMsg(
                        uid, nowVersion, machineGPU, resultData['FPS'], resultData['VRAM'], caseInfo.get('GamePlay'), analysisMode,
                        result, None, caseInfo.get('Machine').get('Resolution'), 
                    )
                else:
                    if self.progressBarLoadingFlag >= 20:
                        self.logObj.logHandler().info('Loading timeout version: {}'.format(nowVersion))
                        feishuResultData = self.feishu._drawTheLoadingTimeoutMsg(uid, caseInfo.get('Machine').get('GPU'), nowVersion)
                    else:
                        self.logObj.logHandler().info('Crash when the version starts: {}'.format(nowVersion))
                        feishuResultData = self.feishu._drawTheself.startingCrashMsg(uid, caseInfo.get('Machine').get('GPU'), nowVersion)
                    
                self.feishu.sendMsg(feishuResultData)
                self.logObj.logHandler().info('MISS - Normal notification Feishu.')

                '''判断采用哪个版本列表'''
                # dataResult 数据分析结果
                # dataResult == 0 -> 前部数据有问题，提交前部数据
                # dataResult == 1 -> 前部数据无问题，提交后部数据
                if not self.startingCrash:
                    # 正常更新
                    PRETTYPRINT.pPrint('可疑版本疑似存在前部数据') if not mainDataResult else PRETTYPRINT.pPrint('可疑版本疑似存在后部数据')
                    testResult = self.updateStrategyWithDichotomy(sniperBefore) if not mainDataResult else self.updateStrategyWithDichotomy(sniperAfter)
                    self.logObj.logHandler().info('New testResult: {}'.format(testResult))
                continue
            else:
                # 只剩一个版本
                if self.startingCrash:
                    PRETTYPRINT.pPrint('没有查到在此版本范围查询到符合要求结果，此判断进入是所有客户端出错（进不去客户端timeout or crash）')
                    self.logObj.logHandler().warning('No results found in this version range are found to meet the requirements. This judgement is that all clients have an error (cannot enter the client timeout or crash).')
                    sys.exit(0)
                else:
                    # 命中版本
                    if not mainDataResult:
                        hitVersion = testResult
                        self.logObj.logHandler().info('Hit the version! current version: {}'.format(hitVersion))
                        # 暂停焦点监控
                        self.logObj.logHandler().info('Start focus monitoring: stop.')
                        PRETTYPRINT.pPrint('停止焦点监控进程')
                        self._stopGrabFocusThread()
                        result = 'MIT'
                        '''消息通知'''
                        feishuResultData = self.feishu._drawTheNormalMsg(
                            uid, hitVersion, machineGPU, resultData['FPS'], resultData['VRAM'], caseInfo.get('GamePlay'), analysisMode,
                            result, None, caseInfo.get('Machine').get('Resolution'), True
                        )
                        self.feishu.sendMsg(feishuResultData)
                        self.logObj.logHandler().info('HIT - Normal notification Feishu.')

                        PRETTYPRINT.pPrint('疑似问题版本: {}'.format(hitVersion))  
                        self.logObj.logHandler().info('Suspected problem version: {}'.format(hitVersion))
                        sys.exit(0)
                    else:
                        PRETTYPRINT.pPrint('没有查到在此版本范围查询到符合要求结果')
                        self.logObj.logHandler().warning('No results found in this version range.')
                        feishuResultData = self.feishu._drawTheNotFoundMsg(uid, nowVersion)
                        self.feishu.sendMsg(feishuResultData)
                        self.logObj.logHandler().info('NOT FOUND - Normal notification Feishu.')
                        sys.exit(0)


if __name__ == '__main__':
    queue = Queue()
    obj = OPSVN()
    try:
        logObj = obj._getLogName()
        obj.dispatch()
    except Exception as e:
        logObj.logHandler().error('[P0] {} - {}'.format(e, e.__traceback__.tb_lineno))
        raise e