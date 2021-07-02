#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/30 20:12:24
@Author  :   Camille
@Version :   1.0
'''


import sys
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
        self.gamePlayScriptControlDict = self.case.get('gameControl')
        self.myselfFile = sys.argv[0].split('\\')[-1]

    def checkAllFileMd5(self):
        # 生成现在文件夹MD5
        OPSVNFileMd5List = []
        for file in os.listdir('.\script\game'):
            if file != self.myselfFile:
                with open('.\script\\game\\{}'.format(file), 'r', encoding='utf-8') as f:
                    i = f.read()
                OPSVNDataMd5 = BaseWindowsControl.useMd5(i, 'file')
                OPSVNFileMd5List.append(OPSVNDataMd5)

        # 生成游戏文件夹MD5
        GameFileMd5List = []
        for file in os.listdir(self.path):
            with open(os.path.join(self.path, file), 'r', encoding='utf-8') as f:
                k = f.read()
            gameDataMd5 = BaseWindowsControl.useMd5(k, 'file')
            GameFileMd5List.append(gameDataMd5)
        
    def dispatch(self, gamePlay):
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
    # obj = Update()
    # obj.dispatch()
    import sys
    print(sys.argv[0].split('\\')[-1])