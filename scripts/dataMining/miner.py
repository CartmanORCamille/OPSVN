#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/21 14:51:24
@Author  :   Camille
@Version :   1.0
'''


import pandas
import numpy
import os
import json
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class Miner():
    def __init__(self) -> None:
        # pandas分析perfmon数据结果列数
        self.pdFps = 1
        self.pdVMemory = 15
        
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.abacusConfig = json.load(f).get('AbacusDictionary')

    def averageData(self, dataSeries: object):
        data = self.numpyToFloat(dataSeries.median(), 2)
        return data

    def maxData(self, dataSeries: object):
        data = self.numpyToFloat(dataSeries.max(), 2)
        return data

    def cleanPerfMonData(self, path) -> list:
        file = pandas.read_table(path,  header=None, sep='\t', engine='python')
        # file -> DataFrame
        file = file.drop(labels=0)
        fpsColumn, virtualMemoryColumn = file[self.pdFps], file[self.pdVMemory]
        # fpsColumn, virtualMemoryColumn -> series
        return fpsColumn, virtualMemoryColumn

    def numpyToFloat(self, numpyFloat, decimals):
        if isinstance(numpyFloat, str):
            numpyFloat = float(numpyFloat)
            return round(numpyFloat, decimals)
        return numpy.around(numpyFloat, decimals=decimals)

class VRAMMiner(Miner):
    pass


class FPSMiner(Miner):
    pass


class CrashMiner(Miner):
    '''
        1. 截图
        2. 查找进程
    '''
    def __init__(self) -> None:
        super().__init__()

    def dispatch(self, version) -> bool:
        # 获取标识符
        with open(r'.\caches\FileRealVersion.json', 'r', encoding='utf-8') as f:
            uid = json.load(f).get('uid')

        # 保存数据文件夹目录
        savePath = '.\caches\crashCertificate\{}'.format(uid)
        BaseWindowsControl.whereIsTheDir(savePath, 1)
        if savePath:
            # 截图 -> 捕捉可能出现的宕机界面
            imgSavePath = os.path.join(savePath, '{}_{}.jpg'.format(uid, version))
            PrettyPrint.pPrint('已截图当前显示器内容')
            BaseWindowsControl.screenshots(imgSavePath)
            # 查找进程
            crashProcess = self.abacusConfig.get('crashProcess')
            if ProcessMonitoring.dispatch(crashProcess):
                PRETTYPRINT.pPrint('已识别宕机进程')
                return True
            else:
                PRETTYPRINT.pPrint('宕机进程不存在，可能是宕机进程未加载或未出现宕机情况')
                return False


if __name__ == '__main__':
    obj = Miner()
    path = r'.\caches\crashCertificate\test.tab'
    # fileObject = pandas.read_table(r'.\caches\crashCertificate\test.tab', header=None, sep='\t', engine='python')
    # fileObject = fileObject.drop(labels=0)
    fps, vram = obj.cleanPerfMonData(path)
    fpsAvg, fpsMax = obj.averageData(fps), obj.maxData(fps)
    print(fpsAvg, fpsMax)