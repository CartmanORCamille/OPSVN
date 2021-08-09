#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/30 20:12:24
@Author  :   Camille
@Version :   1.0
'''


from logging import debug
import sys
import json
import os
from typing import Tuple
from scripts.windows.windows import BaseWindowsControl
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint
from pathlib import Path


PRETTYPRINT = PrettyPrint()


# 更新此目录的脚本到JX3游戏中
class Update():
    def __init__(self, *args, **kwargs) -> None:
        logName = kwargs.get('logName', '1')
        assert logName, 'Can not find logName.'
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
        self.writeSearchPanelTabMoudle = WriteSearchPanelTabMoudle()

    def update(self, beginning, destination):
        command = 'copy /y {} {}'.format(beginning, destination)
        result = BaseWindowsControl.consoleExecutionWithRun(command)
        PRETTYPRINT.pPrint('更新 -> 已复制 {}，目的路径 {}'.format(beginning, destination)) 
        self.logObj.logHandler().info('Update -> {}, Destination path {}'.format(beginning, destination))
        if result:
            PRETTYPRINT.pPrint('结果 -> {}'.format(result))
            self.logObj.logHandler().info('RESULT -> {}'.format(result))

    def _updateAutoLogin(self):
        PRETTYPRINT.pPrint('准备更新 OPSVN AUTOLOGIN SCRIPT')
        self.logObj.logHandler().info('Ready to update AUTOLOGIN SCRIPT.')
        localPath = os.path.join('.', 'scripts', 'game', 'autoLogin')

        for file in os.listdir(localPath):
            if file not in self.keyDocuments:
                filePath = os.path.join(localPath, file)
                if file == 'module_info.xml':
                    # update XML
                    # '<module name="AutoLogin" load="true" layer="1" type="lib"><file>\ui\script\AutoLogin.lua</file></module>'
                    destination = os.path.join(self.clientPath, 'ui', )
                elif file == 'AutoLogin.ini' or file == 'AutoLogin.lua':
                    destination = os.path.join(self.clientPath, 'ui', 'Script')
                elif file == 'Automation.ini':
                    destination = os.path.join(self.clientPath)
                self.update(filePath, destination)

    def _updateSeachPanel(self, resultPath, inMap):
        # 复制 BVTTEST.xx, 案例文件
        assert inMap, '需要提供字段 inMap'
        PRETTYPRINT.pPrint('准备更新 OPSVN SearchPanel lua SCRIPT')
        self.logObj.logHandler().info('Ready to update SearchPanel lua SCRIPT.')
        with open(r'.\config\gamePlayCases.json', 'r', encoding='utf-8') as f:
            cases = json.load(f)
        searchPanelPath = os.path.join(self.clientPath, 'interface', 'SearchPanel')
        # 复制 BVTTest.xx 文件
        self.update(r'.\scripts\game\SearchPanel\BVTTest.lua', os.path.join(searchPanelPath, 'BVTTest.lua'))
        luaCase = cases.get(inMap, None)
        tabText = self.writeSearchPanelTabMoudle.updateTab(resultPath, luaCase)

        with open(os.path.join(searchPanelPath, 'runMap.tab'), 'w', encoding='gbk') as f:
            f.write(tabText)
        
    def dispatch(self, resultPath, inMap=None, *args, **kwargs) -> None:
        resultPath = Path(os.path.join(os.getcwd(), resultPath)).as_posix()
        self._updateAutoLogin()
        self._updateSeachPanel(resultPath, inMap)


class WriteSearchPanelTabMoudle():

    def _createFileLua(self, status):
        return  "/ WriteRunMapResultOPSVN('{}')".format(status)

    def updateTab(self, resultPath, file):
        file = os.path.join(r'.\scripts\game\SearchPanel', file)
        with open(file, 'r', encoding='gbk') as f:
            text = f.read()
            # 更换数据
            text = text.replace('/ WriteRunMapResult("PerfMon", 0)', self._createFileLua(
                Path(os.path.join(resultPath, 'start')).as_posix()
            ))
            text = text.replace('/ WriteRunMapResult("PerfMon", 1)', self._createFileLua(
                Path(os.path.join(resultPath, 'completed')).as_posix()
            ))
            text = text.replace('_video_', '4')
            text = text.replace('_video1_', '7')
        return text

if __name__ == '__main__':
    obj = Update(logName='1')
    obj.dispatch(r'.\usuallyData\ALPHA_16248491144391608', inMap='DaoxiangVillage')
    # obj.updateMoudleInfoXML()