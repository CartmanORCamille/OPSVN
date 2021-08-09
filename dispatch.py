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
from multiprocessing import Queue
from multiprocessing import Process
from threading import Thread

from win32gui import FillRect
from scripts.svn.SVNCheck import SVNMoudle
from scripts.windows.windows import BaseWindowsControl, GrabFocus, ProcessMonitoring, FindTheFile
from scripts.windows.contact import FEISHU
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.dateAnalysis.abacus import FPSAbacus, VRAMAbacus, CrashAbacus, DataAbacus
from scripts.dataMining.miner import PerfMon
from scripts.game.update import Update
from scripts.game.gameControl import GameControl, DEBUGGAMECONTROL


PRETTYPRINT = PrettyPrint()


class OPSVN():
    def __init__(self, *args, **kwargs) -> None:
        self.logName = '{}.log'.format(time.strftime('%S_%M_%H_%d_%m_%Y'))
        self.ghost = 0
        self._checkCaseExists()
        # log使用方法：self.logObj.logHandler()
        self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
        self.SVNObj = SVNMoudle(logName=self.logName)
        self.feishu = FEISHU(logName=self.logName)
        # self.gameControl = GameControl(logName=self.logName)
        self.queue = Queue()
        
        self.logObj.logHandler().info('Initialize all class instance.')

        # 线程信号
        self.grabFocusFlag = threading.Event()

        # 读取版本文件信息
        with open(r'.\config\version.json', 'r', encoding='utf-8') as f:
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

    def grabFocusThread(self, version) -> None:
        while 1:
            self.grabFocusFlag.wait()
            grabObj = GrabFocus(logName=self.logName)
            result = grabObj.dispatch(version)
            if result == 'Ghost':
                # 未响应
                self.ghost += 1
            else:
                self.ghost = 0
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
            self.logObj.logHandler().warning('case.json not found, check if the original file exists.')
            originalFile = 'case_ALPHA_'
            exists = [i for i in os.listdir(r'.\config') if i.startswith(originalFile)]
            if exists:
                self.logObj.logHandler().info('Found case.json(original), start to rename the file.')
                PRETTYPRINT.pPrint('发现case.json(original)，开始重命名文件')
                originalFilePath = os.path.join(r'.\config', exists[0])
                os.rename(originalFilePath, r'.\config\case.json')
                self.logObj.logHandler().info('The name has been changed, the original file name: {}, the current file name: {}.'.format(exists, 'case.json'))
            else:
                PRETTYPRINT.pPrint('未发现 case.json/(original) 文件', 'ERROR', bold=True)
                self.logObj.logHandler().error('[P1] No case.json/(original) file found.')
                raise FileNotFoundError('未发现 case.json/(original) 文件')
        PRETTYPRINT.pPrint('发现 case.json 文件')

    def _checkGameIsReady(self):
        # 检查缓存文件
        # 检查游戏是否准备好
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

    def _makeId(self) -> str:
        """生成标识符

        Returns:
            标识符: version_时间戳
        """
        idVersion = self.version.get('OPSVN').get('version')
        uid = '{}_{}'.format(idVersion, str(time.time()).replace('.', ''))
        return uid

    def _createNewThread(self, func, name, *args, **kwargs) -> Thread:
        t = Thread(target=func, name=name)
        self.logObj.logHandler().info('dispatch.py - Child thread object has been generated: {}, child process name: {}'.format(t, name))
        return t

    def _createNewProcess(self, func, name, *args, **kwargs) -> Process:
        p = Process(target=func, name=name)
        self.logObj.logHandler().info('dispatch.py - Child process object has been generated: {}, child process name: {}'.format(p, name))
        return p

    def dispatch(self):
        # 读取配置文件
        self.logObj.logHandler().info('Reading case.json.')
        caseInfo = self._readCase()
        
        # 更新 lua script 初始化
        self.logObj.logHandler().info('Start checking lua script.')
        updateObj = Update(logName=self.logName)
        updateObj.dispatch(caseInfo.get('GamePlay'), caseInfo.get('InMap'))

        # 获取版本
        uid = caseInfo.get('uid')
        self.logObj.logHandler().info('Ready to find and record the SVN version, case uid: {}.'.format(uid))
        self.SVNObj.updateCheck(uid)
        self.logObj.logHandler().info('Obtained SVN version.')

        # 读取版本
        self.logObj.logHandler().info('Reading version.json.')
        fileRealVersionInfo = self._readCache(r'.\caches\FileRealVersion.json')
        # uid验证
        if fileRealVersionInfo.get('uid') != uid:
            self.logObj.logHandler().error('[P3] The uid comparison is invalid, the data may not be obtained successfully')
            raise LookupError('uid对比失效，可能数据未获取成功')

        versionList = fileRealVersionInfo.get('FileRealVersion')
        if not versionList:
            self.logObj.logHandler().error('[P2] SVN version not obtained.')
            raise ValueError('未获取到版本')

        # 二分切割
        testResult = self.updateStrategyWithDichotomy(versionList)
        self.logObj.logHandler().info('Dichotomizing is completed -> VP: {}, sniperBefore: {}, sniperAfter: {}'.format(*testResult))
        while 1:
            vp, sniperBefore, sniperAfter = testResult
            # 删除 result 文件
            rootDataPath = os.path.join('.', 'caches', 'comprehensiveInspection', uid)
            if os.path.exists(rootDataPath):
                [os.remove(os.path.join(rootDataPath, file)) for file in os.listdir(rootDataPath) if file.endswith('done') or file.endswith('scanned')]

            # 前部数据有问题，提交前部数据 / 前部数据无问题，提交后部数据
            # 开始更新 - 前部最后一个版本
            nowVersion = sniperBefore[-1]
            self.logObj.logHandler().info('Ready to update: {}'.format(nowVersion))
            self.SVNObj.update(version=nowVersion)
            
            # 创建版本文件夹
            versionPath = os.path.join(rootDataPath, nowVersion)
            BaseWindowsControl.whereIsTheDir(versionPath, True)

            '''主机控制'''
            # 开程序
            self.logObj.logHandler().info('Ready to start client.')
            PRETTYPRINT.pPrint('尝试启动游戏')
            processName, cwd = caseInfo.get('Path').get('Jx3'), caseInfo.get('Path').get('Jx3BVTWorkPath')
            BaseWindowsControl.consoleExecutionWithPopen(processName, cwd)

            # 识别进程是否启动
            startingCrash = False
            startupStatus = None
            loadingFlag = 0
            while 1:
                if loadingFlag == 60:
                    startingCrash = True
                    PRETTYPRINT.pPrint('进度条等待时间过长，可能不Clinet有问题，进入下一轮配置路径更新')
                    self.logObj.logHandler().info('The waiting time of the progress bar is too long, there may not be a problem with Clinet, enter the next round of configuration path update.')
                    # 截图
                    BaseWindowsControl.activationWindow(None, '剑侠情缘网络版叁_LoadingClass')
                    BaseWindowsControl.screenshots(os.path.join(versionPath, 'LoadingTimeout.jpg'))
                    BaseWindowsControl.killProcess('JX3ClientX64.exe')
                    break
                self.logObj.logHandler().info('Wait for the client process to exist.')
                PRETTYPRINT.pPrint('等待进入游戏中')
                loadingFlag += 1
                processMonitoringObj = ProcessMonitoring(logName=self.logName)
                startupStatus = processMonitoringObj.dispatch(version=nowVersion)
                
                if startupStatus and loadingFlag >= 3:
                    
                    if startupStatus == 'StartingCrash':
                    # 启动时宕机
                        startingCrash = True
                        BaseWindowsControl.killProcess('DumpReport64.exe')
                        PRETTYPRINT.pPrint('启动时宕机 - 结束宕机窗口进程')
                        self.logObj.logHandler().info('Staring Crash, End the downtime window process')
                        break
                    elif startupStatus:
                        self.logObj.logHandler().info('Client process exists.')
                        break
                    else:
                        PRETTYPRINT.pPrint('可能是异常的 startupStatus 返回值: {}'.format(startupStatus))
                        PRETTYPRINT.pPrint('dispatch 进程扫描 startupStatus 反馈 - 未识别到"加载中窗口"， "客户端窗口"，"宕机窗口"')
                        self.logObj.logHandler().info('Process scanning-"Loading window", "Client window", "Down window" are not recognized.')
                        continue
                    
                time.sleep(2)
            self.logObj.logHandler().info('startingCrash: {}'.format(startingCrash))
            if startingCrash is False:
                # 启动焦点监控 -> 保持暂停状态
                self.logObj.logHandler().info('Start focus monitoring: pause.')
                Thread(target=self.grabFocusThread, name='grabFocus', args=(nowVersion, )).start()
                # 启动时不宕机
                # 打开焦点监控  
                PRETTYPRINT.pPrint('启动焦点监控线程')
                time.sleep(2)
                self.logObj.logHandler().info('Start focus monitoring: Start.')
                self.grabFocusFlag.set()

                '''游戏内操作，打开游戏后就自动调用searchpanel，dispatch.py只做等待'''
                
                '''数据采集'''
                self.logObj.logHandler().info('Initialize the perfmon module.')
                PRETTYPRINT.pPrint('初始化 PerfMon 模块')
                recordTime = caseInfo.get('RecordTime')
                perfmonMiner = PerfMon(logName=self.logName, queue=self.queue)
                filePath = perfmonMiner.dispatch(uid, nowVersion, processMonitoringObj.dispatch(isPid=1), recordTime=None)
                self.logObj.logHandler().info('Game data has been cleaned.')

                # 暂停焦点监控
                self.logObj.logHandler().info('Start focus monitoring: pause.')
                PRETTYPRINT.pPrint('暂停焦点监控进程')
                self.grabFocusFlag.clear()

                '''数据分析'''
                analysisMode, machineGPU = caseInfo.get('DefectBehavior'), caseInfo.get('Machine').get('GPU')
                if analysisMode != 'crash':
                    # FPS AND VRAM
                    # 主数据分析 -> 决定性结论
                    mainAbacus = self.dataAbacusTable.get(analysisMode)(filePath, machineGPU, logName=self.logName)
                    PRETTYPRINT.pPrint('主要数据分析 -> CHECK: {}, GPU: {}'.format(mainAbacus, machineGPU))
                    self.logObj.logHandler().info('Main data analysis -> CHECK: {}, GPU: {}.'.format(mainAbacus, machineGPU))
                    mainDataResult, mainData = mainAbacus.dispatch()
                    self.logObj.logHandler().info('Main data analysis conclusion: {}, value: {}'.format(mainDataResult, mainData))

                    # 次要数据分析
                    secondaryAbacus = self.dataAbacusTable.get('FPS')(filePath, machineGPU, logName=self.logName) if analysisMode == 'VRAM' else self.dataAbacusTable.get('RAM')(filePath, machineGPU, logName=self.logName)
                    PRETTYPRINT.pPrint('次要数据分析 -> CHECK: {}, GPU: {}'.format(secondaryAbacus, machineGPU))
                    self.logObj.logHandler().info('Secondary data analysis -> CHECK: {}, GPU: {}.'.format(secondaryAbacus, machineGPU))
                    secondaryDataResult, secondaryData = secondaryAbacus.dispatch()
                    self.logObj.logHandler().info('Conclusion of secondary data analysis: {}, value: {}'.format(secondaryDataResult, secondaryData))
                else:
                    # crash
                    crashAbacus = self.dataAbacusTable.get(analysisMode)(logName=self.logName)
                    mainDataResult = crashAbacus.dispatch()
                
                '''判断采用哪个版本列表'''
                # dataResult 数据分析结果
                # dataResult == 0 -> 前部数据有问题，提交前部数据
                # dataResult == 1 -> 前部数据无问题，提交后部数据
                PRETTYPRINT.pPrint('可疑版本疑似存在前部数据') if not mainDataResult else PRETTYPRINT.pPrint('可疑版本疑似存在后部数据')

                # 信息记录
                resultVersionFile = 'result_{}.json'.format(nowVersion)
                with open('.\\caches\\{}'.format(resultVersionFile), 'w', encoding='utf-8') as f:
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
                    elif analysisMode == 'VRAM':
                        resultData['FPS'] = secondaryData
                        resultData['VRAM'] = mainData
                    self.logObj.logHandler().info('Saved file: {}, Comprehensive data value -> FPS: {}, VRAM: {}'.format(resultVersionFile, resultData['FPS'], resultData['VRAM']))
                    json.dump(resultData, f, indent=4)

                testResult = self.updateStrategyWithDichotomy(sniperBefore) if not mainDataResult else self.updateStrategyWithDichotomy(sniperAfter)
                self.logObj.logHandler().info('New testResult: {}'.format(testResult))
                PRETTYPRINT.pPrint('正在通知 FEISHU')
                self.logObj.logHandler().info('Notifying Feishu.')
            else:
                # 删除宕机或者Timeout版本
                sniperBefore = self.removeExceptionVersion(nowVersion, sniperBefore)
                PRETTYPRINT.pPrint('删除版本: {}'.format(nowVersion))
                self.logObj.logHandler().info('[{}] - version deleted: {}'.format(startupStatus, nowVersion))
                # 客户端错误导致的版本规避，代表本次的循环是作废的，合并并重新二分版本列表
                versionList = sniperBefore + sniperAfter
                PRETTYPRINT.pPrint('合并后新版本集: {}'.format(versionList))
                self.logObj.logHandler().info('New version set after merging: {}'.format(versionList))
                testResult = self.updateStrategyWithDichotomy(versionList)
                self.logObj.logHandler().info('New testResult: {}'.format(testResult))
            
            # 后续版本更新
            # if result == 'GamingCrash':
            #     # 游戏内宕机
            #     if caseInfo.get('DefectBehavior') == 'crash':
            #         result = 'HIT (Gaming Crash)'
            #     else:
            #         result = 'MISS (Gaming Crash)'
            #     self.logObj.logHandler().info('Gameing Crash. version: {}'.format(nowVersion))
            #     feishuResultData = self.feishu._drawTheGamingCrashMsg(uid, caseInfo.get('Machine').get('GPU'), nowVersion)
            #     self.logObj.logHandler().info('HIT - Normal notification Feishu (Crash).')
            #     self.feishu.sendMsg(feishuResultData)

            if len(testResult) == 3:
                if not startingCrash:
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
                    if loadingFlag == 20:
                        self.logObj.logHandler().info('Loading timeout version: {}'.format(nowVersion))
                        feishuResultData = self.feishu._drawTheLoadingTimeoutMsg(uid, caseInfo.get('Machine').get('GPU'), nowVersion)
                    else:
                        self.logObj.logHandler().info('Crash when the version starts: {}'.format(nowVersion))
                        feishuResultData = self.feishu._drawTheStartingCrashMsg(uid, caseInfo.get('Machine').get('GPU'), nowVersion)
                    
                self.feishu.sendMsg(feishuResultData)
                self.logObj.logHandler().info('MISS - Normal notification Feishu.')
                continue
            else:
                if startingCrash:
                    PRETTYPRINT.pPrint('没有查到在此版本范围查询到符合要求结果，此判断进入是所有客户端出错（进不去客户端timeout or crash）')
                    self.logObj.logHandler().warning('No results found in this version range are found to meet the requirements. This judgement is that all clients have an error (cannot enter the client timeout or crash).')
                    sys.exit(0)
                else:
                    # 命中版本
                    hitVersion = testResult
                    self.logObj.logHandler().info('Hit the version! current version: {}'.format(hitVersion))
                    # 暂停焦点监控
                    self.logObj.logHandler().info('Start focus monitoring: pause.')
                    PRETTYPRINT.pPrint('暂停焦点监控进程')
                    self.grabFocusFlag.clear()
                    result = 'MIT'
                    '''消息通知'''
                    feishuResultData = self.feishu._drawTheNormalMsg(
                        uid, nowVersion, machineGPU, resultData['FPS'], resultData['VRAM'], caseInfo.get('GamePlay'), analysisMode,
                        result, None, caseInfo.get('Machine').get('Resolution'), True
                    )
                    self.feishu.sendMsg(feishuResultData)
                    self.logObj.logHandler().info('HIT - Normal notification Feishu.')

                    PRETTYPRINT.pPrint('疑似问题版本: {}'.format(hitVersion))  
                    self.logObj.logHandler().info('Suspected problem version: {}'.format(hitVersion))
                    sys.exit(0)
                    


if __name__ == '__main__':
    queue = Queue()
    obj = OPSVN()
    try:
        obj.dispatch()
    except Exception as e:
        raise e
    # print('{}'.format(FPSAbacus(11, 1)))
    # PRETTYPRINT.pPrint('111: {}'.format(FPSAbacus(11, 1)))