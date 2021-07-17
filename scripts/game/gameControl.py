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


def debugGameControl():
    i = 0
    while 1:
        PRETTYPRINT.pPrint('=========================DEBUG - 游戏内操作 -> {}========================='.format(i))
        if i == 5:
            with open(r'.\caches\GameStatus.json', 'w', encoding='utf-8') as f:
                data = {'orReady': 1}
                json.dump(data, f, indent=4)
        if i == 20:
            # 关闭游戏
            processName = 'JX3ClientX64.exe'
            PRETTYPRINT.pPrint('尝试结束游戏')
            BaseWindowsControl.killProcess(processName)
            break
        i += 1
        time.sleep(3)


if __name__ == '__main__':
    # debugGameControl()
    BaseWindowsControl.killProcess('JX3ClientX64.exe')