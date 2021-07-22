#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/21 14:51:24
@Author  :   Camille
@Version :   1.0
'''


import time
import os
import json
import random
from multiprocessing import Process
from multiprocessing.context import ProcessError
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class PerfMon():
    def __init__(self, *args, **kwargs) -> None:
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')

        self.processMonitoringObj = ProcessMonitoring(logName=logName)
        self.logObj.logHandler().info('Initialize Perfmon(miner) class instance.')

    def command(self, uid, version, pid, *args, **kwargs):
        # use PerfMon2.x
        resultDirPath = os.path.join('..', '..', 'caches', 'memoryLeak', uid, version)
        resultDirPathExists = BaseWindowsControl.whereIsTheDir(os.path.join(
            '.', 'caches', 'memoryLeak', uid, version
        ), True)
        if resultDirPathExists:
            if not os.path.isdir(resultDirPath):
                self.logObj.logHandler().warning('Client survival time is over, try to end the game.')
                os.makedirs(resultDirPath)
                self.logObj.logHandler().info('PerfMon data staging folder has been created -> {}'.format(resultDirPath))
            baseCommand = 'PerfMon3 --perf_id={} --perf_d3d11hook --perf_logicFPShook --perf_sockethook --perf_dir="{}"'.format(pid, resultDirPath)
            
            return baseCommand
        else:
            self.logObj.logHandler().error('[P0] PerfMon data staging folder does not exist (the function (whereIsTheDir) may be defective).')
            raise FileNotFoundError('路径不存在')

    def _perfMonProcess(self, command):
        p = Process(target=self.runPerfMon, name='PerfMon', args=(command, ))
        self.logObj.logHandler().info('miner.py - Child process object has been generated: {}, child process name: {}'.format(p, 'Perfmon'))
        return p

    def runPerfMon(self, command):
        subResult = BaseWindowsControl.consoleExecutionWithPopen(command, cwd=r'.\tools\PerfMon_3.0')
        subResult.communicate()
        self.logObj.logHandler().info('Start PerfMon.')

    def dispatch(self, uid, version, pid, recordTime=None):
        if not recordTime:
            recordTime = 999999
        self.logObj.logHandler().info('PerfMon record time: {}'.format(recordTime))
        shutdownTime = time.time() + recordTime
        self.logObj.logHandler().info('PerfMon shutdown time: {}'.format(shutdownTime))
        command = self.command(uid, version, pid)
        self.logObj.logHandler().info('PerfMon command: {}'.format(command))
        processObj = self._perfMonProcess(command)
        PRETTYPRINT.pPrint('开始采集，Start -> PerfMon')
        processObj.start()
        
        while 1:
            # 计时
            nowTime = time.time()
            # 检查游戏进程是否存在
            exists = self.processMonitoringObj.dispatch()
            self.logObj.logHandler().info('Game exists: {}'.format(exists))
            if not processObj.is_alive():
                self.logObj.logHandler().error('PerfMon exits for unknown reasons, URGENT level error, need to be checked immediately.')
                self.logObj.logHandler().error('PerfMon exits for unknown reasons, check the PerfMon operating environment and commands.')
                PRETTYPRINT.pPrint('PerfMon未知原因退出，URGENT级错误，需要立即核查', level='ERROR', bold=True)
            if not exists and processObj.is_alive() or shutdownTime <= nowTime:
                PRETTYPRINT.pPrint('结束采集，kill -> PerfMon')
                processObj.terminate()
                self.logObj.logHandler().warning('PerfMon ends the collection.')
                break
            time.sleep(1)

        PRETTYPRINT.pPrint('清洗数据文件')
        self.logObj.logHandler().info('Clean data files.')
        for path, isDir, isFile in os.walk(os.path.join('.', 'caches', 'memoryLeak', uid, version)):
            if isFile:
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
                        os.rename(oldFile, newFile)
                        self.logObj.logHandler().info('Data file name changed successfully.')
                        break
                    except PermissionError as e:
                        PRETTYPRINT.pPrint('PERMISSIONERROR(已知错误) -> 循环等待，错误信息: {}'.format(e))
                        self.logObj.logHandler().error('[P3] Data file name failed to be replaced, PERMISSIONERROR (known error) -> cyclic waiting, error message.')
                        time.sleep(1)
                        continue
                    
                PRETTYPRINT.pPrint('数据已反馈')
                self.logObj.logHandler().info('Data has been fed back')
                return newFile
        
        return 1


if __name__ == '__main__':
    # perfmonMiner = PerfMon()
    # uid = 'ALPHA_16239165704530177'
    # filePath = perfmonMiner.dispatch(uid, '940902')
    # perfmonMiner.command(uid, '123')
    pass