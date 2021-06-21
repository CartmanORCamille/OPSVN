#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/11 11:37:46
@Author  :   Camille
@Version :   1.0
'''


import random
import json

from win32api import RegUnLoadKey
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


class RAMAbacus(DataAbacus):
    pass


class FPSAbacus(DataAbacus):
    pass


class CrashAbacus(DataAbacus):
    '''
        1. 截图
        2. 查找进程
    '''
    def __init__(self) -> None:
        super().__init__()

    def dispatch(self) -> bool:
        # 获取标识符
        with open(r'.\caches\FileRealVersion.json', 'r', encoding='utf-8') as f:
            uid = json.load(f).get('uid')

        # 保存数据文件夹目录
        savePath = '.\caches\{}'.format(uid)
        BaseWindowsControl.whereIsTheDir(savePath)
        if savePath:
            # 截图 -> 捕捉可能出现的宕机界面
            BaseWindowsControl.screenshots(uid)
            # 查找进程
            crashProcess = self.abacusConfig.get('crashProcess')
            if ProcessMonitoring.dispatch(crashProcess):
                PRETTYPRINT.pPrint('已识别宕机进程')
                return True
            else:
                return False



if __name__ == "__main__":
    obj = DataAbacus()