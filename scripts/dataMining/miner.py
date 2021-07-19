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
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class PerfMon():
    def __init__(self, *args, **kwargs) -> None:
        pass

    def command(self, uid, version, pid, *args, **kwargs):
        # use PerfMon2.x
        resultDirPath = os.path.join('..', '..', 'caches', 'memoryLeak', uid, version)
        resultDirPathExists = BaseWindowsControl.whereIsTheDir(os.path.join(
            '.', 'caches', 'memoryLeak', uid, version
        ), True)
        if resultDirPathExists:
            if not os.path.isdir(resultDirPath):
                os.makedirs(resultDirPath)
            baseCommand = 'PerfMon3 --perf_id={} --perf_d3d11hook --perf_logicFPShook --perf_sockethook --perf_dir="{}"'.format(pid, resultDirPath)
            
            return baseCommand
        else:
            raise FileNotFoundError('路径不存在')

    def _perfMonProcess(self, command):
        p = Process(target=self.runPerfMon, name='PerfMon', args=(command, ))
        return p

    def runPerfMon(self, command):
        subResult = BaseWindowsControl.consoleExecutionWithPopen(command, cwd=r'.\tools\PerfMon_3.0')
        subResult.communicate()

    def dispatch(self, uid, version, pid, recordTime=None):
        if not recordTime:
            recordTime = 999999
        shutdownTime = time.time() + recordTime
        command = self.command(uid, version, pid)
        processObj = self._perfMonProcess(command)
        PRETTYPRINT.pPrint('开始采集，Start -> PerfMon')
        processObj.start()
        
        while 1:
            # 计时
            nowTime = time.time()
            # 检查游戏进程是否存在
            exists = ProcessMonitoring.dispatch()
            if not processObj.is_alive():
                PRETTYPRINT.pPrint('PerfMon未知原因退出，URGENT级错误，需要立即核查', level='ERROR', bold=True)
            if not exists and processObj.is_alive() or shutdownTime <= nowTime:
                PRETTYPRINT.pPrint('结束采集，kill -> PerfMon')
                processObj.terminate()
                break
            time.sleep(1)

        PRETTYPRINT.pPrint('清洗数据文件')
        for path, isDir, isFile in os.walk(os.path.join('.', 'caches', 'memoryLeak', uid, version)):
            if isFile:
                oldFile, newFile = os.path.join(path, isFile[0]), os.path.join(path, '{}.{}'.format(version, 'tab'))
                PRETTYPRINT.pPrint('数据文件名更换: {} -> {}'.format(oldFile, newFile))
                # 等待写入
                PRETTYPRINT.pPrint('数据写入中')
                time.sleep(10)
                while 1:
                    try:
                        os.rename(oldFile, newFile)
                        break
                    except PermissionError as e:
                        PRETTYPRINT.pPrint('PERMISSIONERROR(已知错误) -> 循环等待，错误信息: {}'.format(e))
                        time.sleep(1)
                        continue
                    
                PRETTYPRINT.pPrint('数据已反馈')
                return newFile
        
        return 1


if __name__ == '__main__':
    perfmonMiner = PerfMon()
    uid = 'ALPHA_16239165704530177'
    filePath = perfmonMiner.dispatch(uid, '940902')
    # perfmonMiner.command(uid, '123')