#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/21 14:51:24
@Author  :   Camille
@Version :   1.0
'''


import shutil
import time
import os
import sys
sys.path.append(os.getcwd())
from multiprocessing import Process
from multiprocessing.context import ProcessError
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.game.gameControl import GameControl


PRETTYPRINT = PrettyPrint()


class PerfMon():
    def __init__(self, queue, *args, **kwargs) -> None:
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')

        self.queue = queue
        self.processMonitoringObj = ProcessMonitoring(logName=logName)
        self.gameControl = GameControl(queue=self.queue, logName=logName)
        self.logObj.logHandler().info('Initialize Perfmon(miner) class instance.')

    def command(self, uid, version, pid, *args, **kwargs):
        # use PerfMon3.x
        # perfmon命令路径
        path = os.path.join('..', 'caches', 'usuallyData', uid, version)
        resultDirPath = os.path.join('..', path)
        # OPSVN路径
        resultDirPathExists = BaseWindowsControl.whereIsTheDir(path, True)
        self.logObj.logHandler().info('resultDirPathExists: {}'.format(resultDirPathExists))
        residualData = os.listdir(path)
        self.logObj.logHandler().info('residualData: {}'.format(residualData))
        if residualData:
            for i in residualData:
                if not os.path.isdir(os.path.join(path, i)):
                    # 文件
                    shutil.rmtree(path)
                else:
                    # 文件夹
                    shutil.rmtree(os.path.join(path, i))
                PRETTYPRINT.pPrint('{} - 已删除残留文件：{}'.format(path, i))
                self.logObj.logHandler().info('{} - Remaining data has been deleted: {}'.format(resultDirPath, i))
        baseCommand = 'PerfMon3 --perf_id={} --perf_d3d11hook --perf_logicFPShook --perf_sockethook --perf_dir="{}"'.format(pid, resultDirPath)
        return baseCommand

    def dispatch(self, uid, version, pid, recordTime=None, stopGrabFocusFlag:object=None, *args, **kwargs) -> str:
        dataPath = os.path.join('..', 'caches', 'usuallyData', uid)
         # 启动SearchPanel进度文件监控
        self.logObj.logHandler().info('Start autoMonitorControl monitoring: pause.')
        self.gameControl.dispatch(dataPath)

        # 打开标识文件监控
        PRETTYPRINT.pPrint('打开标识文件监控')
        self.logObj.logHandler().info('Start game control monitoring dispatch thread: Start.')
        self.gameControl._startAutoMonitorControlFlag()

        count = 0
        while 1:
            # 等待识别到 start.result 标识进度文件
            PRETTYPRINT.pPrint('等待 lua case(SearchPanel) 加载，等待 start.result 生成')
            self.logObj.logHandler().info('Wait for lua case(SearchPanel) to load. Wait for start.result to be generated.')
            if self.queue.get() == 'start':
                PRETTYPRINT.pPrint('SearchPanel 就绪，准备启动 PerfMon')
                self.logObj.logHandler().info('SearchPanel is ready, ready to start PerfMon.')
                break
            count += 1
            time.sleep(1)

        if not recordTime:
            recordTime = 999999
        self.logObj.logHandler().info('PerfMon record time: {}'.format(recordTime))
        shutdownTime = time.time() + recordTime
        self.logObj.logHandler().info('PerfMon shutdown time: {}'.format(shutdownTime))
        command = self.command(uid, version, pid)
        self.logObj.logHandler().info('PerfMon command: {}'.format(command))
        subResult = BaseWindowsControl.consoleExecutionWithPopen(command, cwd=r'..\tools\PerfMon_3.0')
        PRETTYPRINT.pPrint('开始采集，Start -> PerfMon')
        self.logObj.logHandler().info('Start -> PerfMon')
        
        while 1:
            # 计时
            nowTime = time.time()
            # 检查游戏进程是否存在
            clientProcessExists = self.processMonitoringObj.dispatch()
            if not subResult.poll():
                PRETTYPRINT.pPrint('正常采集数据中')
                self.logObj.logHandler().info('Collecting data normally, Game exists: {}'.format(clientProcessExists))
            if not clientProcessExists or shutdownTime <= nowTime:
                # 获取宕机弹窗在不在
                crashDumpExists = self.processMonitoringObj.dispatch('DumpReport64.exe', True)
                if crashDumpExists:
                    # 宕机，非正常运行
                    break
                PRETTYPRINT.pPrint('结束采集，kill -> PerfMon')
                subResult.terminate()
                self.logObj.logHandler().warning('PerfMon ends the collection.')
                # 暂停标识文件监控
                PRETTYPRINT.pPrint('暂停标识文件监控')
                self.gameControl._stopAutoMonitorControlFlag()
                break
            if subResult.poll() == 2:
                self.logObj.logHandler().error('[P0] PerfMon exits for unknown reasons, URGENT level error, need to be checked immediately.')
                self.logObj.logHandler().error('[P0] PerfMon exits for unknown reasons, check the PerfMon operating environment and commands.')
                PRETTYPRINT.pPrint('[P0] PerfMon未知原因退出，URGENT级错误，需要立即核查', level='ERROR', bold=True)
            time.sleep(1)

        if not crashDumpExists:
            # 通知已经采集完成
            # 暂停焦点监控
            self.logObj.logHandler().info('Start focus monitoring: pause.')
            PRETTYPRINT.pPrint('暂停焦点监控进程')
            stopGrabFocusFlag()
            
            PRETTYPRINT.pPrint('清洗数据文件')
            self.logObj.logHandler().info('Clean data files.')
            for path, isDir, isFile in os.walk(os.path.join(dataPath, version)):
                if isFile and isFile[0] == 'sys_summary.tab':
                    self.logObj.logHandler().info('Data file found.')
                    oldFile, newFile = os.path.join(path, isFile[0]), os.path.join(path, '{}.{}'.format(version, 'tab'))
                    PRETTYPRINT.pPrint('数据文件名更换: {} -> {}'.format(oldFile, newFile))
                    self.logObj.logHandler().info('Data file name replacement: {} -> {}'.format(oldFile, newFile))
                    # 等待写入
                    PRETTYPRINT.pPrint('数据写入中')
                    wait = 10
                    self.logObj.logHandler().info('Waiting time during data writing (seconds): {}'.format(wait))
                    time.sleep(wait)
                    while 1:
                        try:
                            if isinstance(subResult.poll(), int):
                                # 数字意味着已经退出
                                os.rename(oldFile, newFile)
                                self.logObj.logHandler().info('Data file name changed successfully.')
                                print(subResult, subResult.poll())
                                break
                            print(subResult, subResult.poll())
                        except PermissionError as e:
                            PRETTYPRINT.pPrint('PERMISSIONERROR(已知错误) -> 循环等待，错误信息: {}'.format(e))
                            self.logObj.logHandler().error('[P3] Data file name failed to be replaced, PERMISSIONERROR (known error) -> cyclic waiting, error message.')
                            time.sleep(1)
                            continue
                        time.sleep(1)
                    
                    PRETTYPRINT.pPrint('数据已反馈')
                    self.logObj.logHandler().info('Data has been fed back')
            
                    return newFile
                
            PRETTYPRINT.pPrint('The perform data file was not found', 'ERROR', bold=True)
            self.logObj.logHandler().error('[P0] The perform data file was not found')
            raise FileNotFoundError('未找到文件')
        else:
            # 宕机
            return False


if __name__ == '__main__':
    pass