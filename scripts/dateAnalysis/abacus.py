#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/11 11:37:46
@Author  :   Camille
@Version :   1.0
'''


import pandas
import numpy
import json
import os
import time
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class Miner():
    def __init__(self) -> None:
        # pandas分析perfmon数据结果列数
        self.pdFps = 1
        self.pdVMemory = 15
        
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.abacusConfig = config.get('AbacusDictionary')
            self.standardConfig = config.get('Standard')

    def averageData(self, dataSeries: object):
        data = self.toFloat(dataSeries.median(), 2)
        return data

    def maxData(self, dataSeries: object):
        data = self.toFloat(dataSeries.max(), 2)
        return data

    def cleanPerfMonData(self, path) -> list:
        file = pandas.read_table(path,  header=None, sep='\t', engine='python')
        # file -> DataFrame
        file = file.drop(labels=0)
        fpsColumn, virtualMemoryColumn = file[self.pdFps], file[self.pdVMemory]
        # fpsColumn, virtualMemoryColumn -> series
        return (fpsColumn, virtualMemoryColumn)

    def toFloat(self, numpyFloat, decimals):
        if isinstance(numpyFloat, str):
            dataFloat = float(numpyFloat)
            return round(dataFloat, decimals)
        return numpy.around(numpyFloat, decimals=decimals)

    def clean(self, dataNumpyList, model, ci, *args, **kwargs):
        """数据比较大小分析

        Args:
            dataNumpyList (object): numpy array.
            model (str): Configuration model.
            ci (str): Comparison item.

        Raises:
            AttributeError: Exception method attribute.

        Returns:
            bool: true or false, analysis result.
        """
        # 获取标准
        if ci == 'FPS':
            modelStandard = self.standardConfig.get('FPS').get(model)
        elif ci == 'VRAM':
            modelStandard = self.standardConfig.get('VRAM').get(model)
        else:
            PRETTYPRINT.pPrint('传参错误, 异常method属性', 'ERROR', bold=True)
            raise AttributeError('异常method属性.')

        # 获取传入数据平均值和最大值
        avg = self.toFloat(int(self.averageData(dataNumpyList) / 1024), 2)
        max = self.toFloat(int(self.maxData(dataNumpyList) / 1024), 2)

        PRETTYPRINT.pPrint('分析结果 -> 平均值(AVG): {} MB, 最大值(MAX): {} MB'.format(avg, max))
        if avg > modelStandard:
            # 内存超标
            difference = avg - modelStandard
            PRETTYPRINT.pPrint(
                '存在内存超标缺陷, 标准(STANDARD): {} MB, 实际平均(AVG): {} MB, 超标: {} MB'.format(modelStandard, avg, difference),
                'WARING',
                bold=True
            )
            return False
        else:
            PRETTYPRINT.pPrint('不存在内存超标缺陷')
            return True
        

class VRAMMiner(Miner):
    def __init__(self, dataFilePath, model) -> None:
        super().__init__()
        # 获取内存标准
        self.VRAMStandard = self.standardConfig.get('VRAM')
        self.dataFilePath = dataFilePath
        self.model = model

    def liquidation(self, *args, **kwargs):
        PRETTYPRINT.pPrint('开始分析 - 虚拟内存')
        VRAMNumpyList = self.cleanPerfMonData(self.dataFilePath)[1]
        result = self.clean(VRAMNumpyList, self.model, 'VRAM')
        return result
        

class FPSMiner(Miner):
    def __init__(self, dataFilePath, model) -> None:
        super().__init__()
        # 获取FPS标准
        self.VRAMStandard = self.standardConfig.get('FPS')
        self.dataFilePath = dataFilePath
        self.model = model

    def liquidation(self, *args, **kwargs):
        PRETTYPRINT.pPrint('开始分析 - FPS')
        FPSNumpyList = self.cleanPerfMonData(self.dataFilePath)[1]
        result = self.clean(FPSNumpyList, self.model, 'FPS')
        return result


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
    pass
