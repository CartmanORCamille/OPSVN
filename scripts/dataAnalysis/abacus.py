#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/11 11:37:46
@Author  :   Camille
@Version :   1.0
'''

import os
import sys
sys.path.append(os.getcwd())
import pandas
import numpy
import json
import time
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class DataAbacus():
    def __init__(self, *args, **kwargs) -> None:
        self.logName = kwargs.get('logName', None)
        assert self.logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize DataAnacus(abacus) class instance.')

        # pandas分析perfmon数据结果列数
        self.pdFps = 2
        self.pdVMemory = 4
        
        with open(r'..\config\config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.abacusConfig = config.get('AbacusDictionary')
            self.standardConfig = config.get('Standard')

    def __str__(self) -> str:
        return 'BaseAbacus'

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

    def _printVRAMResult(self, avg, max, modelStandard):
        if avg > modelStandard:
            # 内存超标
            difference = avg - modelStandard
            avg = self.toFloat(avg, 2)
            max = self.toFloat(max, 2)
            PRETTYPRINT.pPrint(
                '存在超标缺陷, 标准(STANDARD): {} MB, 实际平均(AVG): {} MB, 超标: {} MB, 最大: {} MB'.format(modelStandard, avg, difference, max),
                'WARING',
                bold=True
            )
            self.logObj.logHandler().info('Existence of over-standard defects, standard (STANDARD): {} MB, actual average (AVG): {} MB, over-standard: {} MB, MAX: {} MB'.format(modelStandard, avg, difference, max))
            return (False, int(avg))
        else:
            PRETTYPRINT.pPrint('不存在内存超标缺陷')
            self.logObj.logHandler().info('There is no memory excess defect.')
            return (True, int(avg))

    def _printFPSResult(self, avg, max, modelStandard):
        if avg < modelStandard:
            avg = self.toFloat(avg, 2)
            max = self.toFloat(max, 2)
            # FPS不达标
            difference = modelStandard - avg
            PRETTYPRINT.pPrint(
                '存在FPS缺陷, 标准(STANDARD): {} frame, 实际平均(AVG): {} frame, 不达标: {} frame, 最大: {} frame'.format(modelStandard, avg, difference, max),
                'WARING',
                bold=True
            )
            self.logObj.logHandler().info('Existence of over-standard defects, standard (STANDARD): {} frame, actual average (AVG): {} frame, over-standard: {} frame, MAX: {} MB'.format(modelStandard, avg, difference, max))
            return (False, int(avg))
        else:
            PRETTYPRINT.pPrint('不存在内存超标缺陷')
            self.logObj.logHandler().info('There is no memory excess defect.')
            return (True, int(avg))

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
        # 获取传入数据平均值和最大值
        avg = int(self.averageData(dataNumpyList))
        max = int(self.maxData(dataNumpyList))

        PRETTYPRINT.pPrint('ci: {}, max: {}, avg: {}'.format(ci, avg, max))
        self.logObj.logHandler().info('ci: {}, max: {}, avg: {}'.format(ci, avg, max))

        # 获取标准并计算
        if ci == 'FPS':
            modelStandard = self.standardConfig.get('FPS').get(model)
            return self._printFPSResult(avg, max, modelStandard)
        elif ci == 'VRAM':
            modelStandard = self.standardConfig.get('VRAM').get(model)
            avg, max = avg / 1024, max / 1024
            return self._printVRAMResult(avg, max, modelStandard)
        else:
            PRETTYPRINT.pPrint('传参错误, 异常method属性', 'ERROR', bold=True)
            self.logObj.logHandler().error('[P3] Pass parameter error, abnormal method attribute')
            raise AttributeError('异常method属性.')
        

class VRAMAbacus(DataAbacus):
    def __init__(self, dataFilePath, model, *args, **kwargs) -> None:
        """虚拟内存分析
            - 虚拟内存

        Args:
            dataFilePath (str): 数据文件路径
            model (str): 测试机机型
        """
        super().__init__(*args, **kwargs)
        # 获取内存标准
        self.VRAMStandard = self.standardConfig.get('VRAM')
        self.dataFilePath = dataFilePath
        self.model = model

    def __str__(self) -> str:
        return 'VRAM'

    def dispatch(self, *args, **kwargs):
        PRETTYPRINT.pPrint('开始分析 - 虚拟内存')
        VRAMNumpyList = self.cleanPerfMonData(self.dataFilePath)[1]
        result = self.clean(VRAMNumpyList, self.model, 'VRAM')
        return result
        

class FPSAbacus(DataAbacus):
    """FPS内存分析

    Args:
        dataFilePath (str): 数据文件路径
        model (str): 测试机机型
    """
    def __init__(self, dataFilePath, model, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # 获取FPS标准
        self.VRAMStandard = self.standardConfig.get('FPS')
        self.dataFilePath = dataFilePath
        self.model = model

    def __str__(self) -> str:
        return 'FPS'

    def dispatch(self, *args, **kwargs):
        PRETTYPRINT.pPrint('开始分析 - FPS')
        FPSNumpyList = self.cleanPerfMonData(self.dataFilePath)[0]
        result = self.clean(FPSNumpyList, self.model, 'FPS')
        return result


class CrashAbacus(DataAbacus):
    '''
        1. 截图
        2. 查找进程
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logName = kwargs.get('logName', None)
        assert self.logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
        self.processMonitoringObj = ProcessMonitoring(logName=self.logName)
        self.logObj.logHandler().info('Initialize CrashAbacus(abacus) class instance.')

    def __str__(self) -> str:
        return 'Crash'

    def dispatch(self, version, startingCheck=False, *args, **kwargs) -> bool:
        # 获取标识符
        with open(r'..\caches\FileRealVersion.json', 'r', encoding='utf-8') as f:
            # uid = ALPHA_xxx
            uid = json.load(f).get('uid')

        # 保存数据文件夹目录
        if not startingCheck:
            savePath = '..\caches\crashCertificate\{}'.format(uid)
        else:
            savePath = os.path.join('.', 'caches', 'startingCrashCheck', uid)
        BaseWindowsControl.whereIsTheDir(savePath, 1)
        PRETTYPRINT.pPrint('识别到宕机窗口，正在获取焦点')
        self.logObj.logHandler().info('A down window is recognized and it is getting focus.')
        errorMsg = BaseWindowsControl.activationWindow('错误报告', '#32770')
        if errorMsg:
            self.logObj.logHandler().error(errorMsg)
        if savePath:
            # 截图 -> 捕捉可能出现的宕机界面
            imgSavePath = os.path.join(savePath, '{}_{}.jpg'.format(uid, version))
            PRETTYPRINT.pPrint('已截图当前显示器内容')
            self.logObj.logHandler().info('Screenshot of the current display content: {}'.format(imgSavePath))
            BaseWindowsControl.screenshots(imgSavePath)


if __name__ == '__main__':
    pass
