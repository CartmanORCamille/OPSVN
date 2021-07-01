#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/30 20:12:24
@Author  :   Camille
@Version :   1.0
'''


import json
import os
from scripts.windows.windows import BaseWindowsControl
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


# 更新此目录的脚本到JX3游戏中
class Update():
    def __init__(self) -> None:
        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            self.case = json.load(f)
        self.path = self.case.get('Path').get('Jx3BVTWorkPath').replace('\\bin64', '\\interface\\OPSVN')
        
    def dispatch(self):
        # 扫描原目录所有文件
        JX3InterfaceOPSVNDir = os.listdir(self.path)
        # 扫描现目录所有文件
        nowOPSVNDir = os.listdir(r'.\scripts\game')
        # 对比是否需要更新
        if sorted(JX3InterfaceOPSVNDir) != sorted(nowOPSVNDir):
            # 更新
            for file in nowOPSVNDir:
                if file != 'update.py':
                    command = 'copy .\scripts\game\{} {}'.format(file, self.path)
                    BaseWindowsControl.consoleExecutionWithRun(command)
    
if __name__ == '__main__':
    obj = Update()
    obj.dispatch()