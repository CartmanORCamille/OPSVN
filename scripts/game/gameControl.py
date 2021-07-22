#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/07/16 14:44:21
@Author  :   Camille
@Version :   1.0
'''


import json
import time
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.windows.windows import BaseWindowsControl


PRETTYPRINT = PrettyPrint()


class GameControl():
    def __init__(self, *args, **kwargs) -> None:
        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            self.controlConfig = json.load(f)
        self.sumiAutoCaseTime = self.controlConfig.get('Debug').get('ClientSurvivalTime')
        self.processName = 'JX3ClientX64.exe'

    def autoMonitorControl(self):
        pass

    def semiAutoMaticDebugControl(self):
        i = 0
        while 1:
            PRETTYPRINT.pPrint('=========================SEMI-AUTOMATIC DEBUG - 游戏内操作=========================')
            PRETTYPRINT.pPrint('客户端已存活时间（秒）: {}，案例时间: {}'.format(i, self.sumiAutoCaseTime))
            if i >= self.sumiAutoCaseTime:
                break
            i += 1
            time.sleep(1)
        
        PRETTYPRINT.pPrint('客户端存活时间结束，尝试结束游戏')
        BaseWindowsControl.killProcess(self.processName)

def debugGameControl():
    i = 0
    while 1:
        PRETTYPRINT.pPrint('=========================DEBUG - 游戏内操作 -> {}========================='.format(i))
        if i == 5:
            with open(r'.\caches\GameStatus.json', 'w', encoding='utf-8') as f:
                data = {'orReady': 1}
                json.dump(data, f, indent=4)
        if i == 10:
            # 关闭游戏
            processName = 'JX3ClientX64.exe'
            PRETTYPRINT.pPrint('尝试结束游戏')
            BaseWindowsControl.killProcess(processName)
            break
        i += 1

        time.sleep(1)


if __name__ == '__main__':
    # debugGameControl()
    BaseWindowsControl.killProcess('JX3ClientX64.exe')