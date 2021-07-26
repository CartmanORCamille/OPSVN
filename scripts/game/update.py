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
from typing import Tuple
from scripts.windows.windows import BaseWindowsControl
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint
from xml.dom.minidom import parse


PRETTYPRINT = PrettyPrint()


# 更新此目录的脚本到JX3游戏中
class Update():
    def __init__(self, gamePlay, *args, **kwargs) -> None:
        self.gamePlay = gamePlay
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize Update(update) class instance.')

        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            self.case = json.load(f)
        # 调用插件名称
        self.interface = 'OPSVN'
        # 路径操作
        self.clientPath = self.case.get('Path').get('Jx3BVTWorkPath').replace('\\bin64', '')

        self.myselfFile = sys.argv[0].split('\\')[-1]
        self.logObj.logHandler().info('Myself file -> {}'.format(self.myselfFile))
        self.keyDocuments = [self.myselfFile, '__pycache__', 'gameControl.py',]

    def update(self, beginning, destination):
        command = 'copy /y {} {}'.format(beginning, destination)
        print(command)
        result = BaseWindowsControl.consoleExecutionWithRun(command)
        if result:
            PRETTYPRINT.pPrint('结果 -> {}'.format(result))
            self.logObj.logHandler().info('RESULT -> {}'.format(result))
        PRETTYPRINT.pPrint('更新 -> 已复制 {}，目的路径 {}'.format(beginning, destination)) 
        self.logObj.logHandler().info('Update -> {}, Destination path {}'.format(beginning, destination))

    def _updateAutoLogin(self):
        PRETTYPRINT.pPrint('准备更新 OPSVN AUTOLOGIN SCRIPT')
        self.logObj.logHandler().info('Ready to update AUTOLOGIN SCRIPT.')
        localPath = os.path.join('.', 'scripts', 'game', 'autoLogin')

        for file in os.listdir(localPath):
            if file not in self.keyDocuments:
                filePath = os.path.join(localPath, file)
                if file == 'module_info.xml':
                    # update XML
                    # autoLoginXML = '\n<module name="AutoLogin" load="true" layer="1" type="lib"><file>\ui\script\AutoLogin.lua</file></module>\n'
                    destination = os.path.join(self.clientPath, 'ui', )
                elif file == 'AutoLogin.ini' or file == 'AutoLogin.lua':
                    destination = os.path.join(self.clientPath, 'ui', 'Script')
                elif file == 'Automation.ini':
                    destination = os.path.join(self.clientPath)
                self.update(filePath, destination)

    def _updateSeachPannel(self):
        pass
        
    def dispatch(self, *args, **kwargs) -> None:
        self._updateAutoLogin()


if __name__ == '__main__':
    obj = Update(logName='1', gamePlay='run')
    obj.dispatch()
    # obj.updateMoudleInfoXML()