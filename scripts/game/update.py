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
import shutil
from typing import Tuple
from scripts.windows.windows import BaseWindowsControl
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


# 更新此目录的脚本到JX3游戏中
class Update():
    def __init__(self, *args, **kwargs) -> None:
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize Update(update) class instance.')

        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            self.case = json.load(f)
        self.path = self.case.get('Path').get('Jx3BVTWorkPath').replace('\\bin64', '\\interface\\OPSVN')
        self.logObj.logHandler().info('Game interface file: OPSVN')
        self.gamePlayScriptControlDict = self.case.get('gameControl')
        self.myselfFile = sys.argv[0].split('\\')[-1]
        self.logObj.logHandler().info('Myself file -> {}'.format(self.myselfFile))

    def checkAllFileMd5(self, *args, **kwargs) -> Tuple:
        # 生成现在文件夹MD5
        PRETTYPRINT.pPrint('正在生成 OPSVN GAME SCRIPT MD5')
        self.logObj.logHandler().info('Generating GAME SCRIPT MD5.')
        OPSVNFileMd5List = []
        for file in os.listdir('.\scripts\game'):
            if file != self.myselfFile and file != '__pycache__':
                path = '.\scripts\\game\\{}'.format(file)
                PRETTYPRINT.pPrint('OPSVN MD5 -> {}'.format(path))
                with open(path, 'r', encoding='utf-8') as f:
                    i = f.read()
                OPSVNDataMd5 = BaseWindowsControl.useMd5(i, 'file')
                self.logObj.logHandler().info('OPSVN MD5 -> {}: {}'.format(path, OPSVNDataMd5))
                OPSVNFileMd5List.append(OPSVNDataMd5)

        # 生成游戏文件夹MD5
        PRETTYPRINT.pPrint('正在生成 JX3 INTERFACE OPSVN SCRIPT MD5')
        self.logObj.logHandler().info('Generating JX3 INTERFACE OPSVN SCRIPT MD5.')
        GameFileMd5List = []
        for file in os.listdir(self.path):
            PRETTYPRINT.pPrint('INTERFACE MD5 -> {}'.format(file))
            with open(os.path.join(self.path, file), 'r', encoding='utf-8') as f:
                k = f.read()
            gameDataMd5 = BaseWindowsControl.useMd5(k, 'file')
            self.logObj.logHandler().info('INTERFACE -> {}: {}'.format(file, gameDataMd5))
            GameFileMd5List.append(gameDataMd5)
        
        return (OPSVNFileMd5List, GameFileMd5List)
        
    def dispatch(self, *args, **kwargs) -> None:
        JX3InterfaceOPSVNDirMd5, nowOPSVNDirMd5 = self.checkAllFileMd5()
        if sorted(JX3InterfaceOPSVNDirMd5) != sorted(nowOPSVNDirMd5):
            PRETTYPRINT.pPrint('lua script 有新的变动，准备更新')
            self.logObj.logHandler().info('Lua script has new changes, ready to be updated.')
            # 更新
            shutil.rmtree(self.path)
            PRETTYPRINT.pPrint('更新 -> 已删除 {}'.format(self.path))
            self.logObj.logHandler().info('Update -> deleted {}'.format(self.path))
            os.makedirs(self.path)
            PRETTYPRINT.pPrint('更新 -> 已创建 {}'.format(self.path))
            self.logObj.logHandler().info('Update -> Created {}'.format(self.path))
            for file in os.listdir(r'.\scripts\game'):
                if file != self.myselfFile and file != '__pycache__':
                    command = 'copy .\scripts\game\{} {}'.format(file, self.path)
                    BaseWindowsControl.consoleExecutionWithRun(command)
                    PRETTYPRINT.pPrint('更新 -> 已复制 {}'.format(file)) 
                    self.logObj.logHandler().info('Update -> copied {}'.format(file))
        else:
             PRETTYPRINT.pPrint('lua script 无新的变动')
             self.logObj.logHandler().info('No new changes in lua script.')


if __name__ == '__main__':
    obj = Update()
    obj.dispatch()