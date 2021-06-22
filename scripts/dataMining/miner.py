#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/21 14:51:24
@Author  :   Camille
@Version :   1.0
'''


import os
import json
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class Miner():
    def __init__(self) -> None:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.abacusConfig = json.load(f).get('AbacusDictionary')


class RAMMiner(Miner):
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