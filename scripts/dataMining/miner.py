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



class DataAbacus():

    def __init__(self) -> None:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.abacusConfig = json.load(f).get('AbacusDictionary')

    def testResult():
        result = random.randint(0, 1)
        return result


class Perfmon():
    def __init__(self, *args, **kwargs) -> None:
        pass

    def command(self, uid, version, *args, **kwargs):
        # use PerfMon2.x
        resultDirPath = os.path.join('..', '..', 'caches', 'memoryLeak', uid, version)
        if not os.path.isdir(resultDirPath):
            os.makedirs(resultDirPath)
        baseCommand = 'PerfMon --perf_proc="JX3ClientX64.exe" --perf_prefix="JX3_" --perf_dir="{}" --perf_d3dhookdll="d3d11hook.dll"'.format(resultDirPath)
        return baseCommand

    def _perfMonProcess(self, command):
        p = Process(target=self.runPerfMon, name='PerfMon', args=(command, ))
        return p

    def runPerfMon(self, command):
        subResult = BaseWindowsControl.consoleExecutionWithPopen(command, cwd=r'.\tools\PerfMon_2.12')
        error = subResult.read().decode('gbk')
        if error:
            raise IOError(error)

    def dispatch(self, uid, version):
        if not ProcessMonitoring.dispatch():
            raise ProcessError('JX3 进程不存在')

        command = self.command(uid, version)
        processObj = self._perfMonProcess(command)
        PRETTYPRINT.pPrint('开始采集，kill -> PerfMon')
        processObj.start()
        
        while 1:
            # 检查游戏进程是否存在
            exists = ProcessMonitoring.dispatch()
            if not processObj.is_alive():
                PRETTYPRINT.pPrint('PerfMon未知原因退出，URGENT级错误，需要立即核查', level='ERROR', bold=True)
            if not exists and processObj.is_alive():
                PRETTYPRINT.pPrint('结束采集，kill -> PerfMon')
                processObj.terminate()
                break
            time.sleep(1)

        for path, isDir, isFile in os.walk(os.path.join('.', 'caches', 'memoryLeak', uid, version)):
            if isFile:
                oldFile, newFile = os.path.join(path, isFile[0]), os.path.join(path, '{}.{}'.format(version, 'tab'))
                PRETTYPRINT.pPrint('数据文件名更换: {} -> {}'.format(oldFile, newFile))
                # 等待写入
                PRETTYPRINT.pPrint('数据写入中 -> \r')
                BaseWindowsControl.loading(3)
                os.rename(oldFile, newFile)
                PRETTYPRINT.pPrint('数据已反馈')
                return newFile
        
        return 1


if __name__ == '__main__':
    pass