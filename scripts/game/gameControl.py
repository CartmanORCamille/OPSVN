#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/07/16 14:44:21
@Author  :   Camille
@Version :   1.0
'''


import os
import json
import time
from threading import Thread, Event
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.windows.windows import BaseWindowsControl, FindTheFile
from scripts.windows.journalist import BasicLogs


PRETTYPRINT = PrettyPrint()


class GameControl():
    def __init__(self, *args, **kwargs) -> None:
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize GameControl(gameControl) class instance.')
        
        with open(r'.\config\case.json', 'r', encoding='utf-8') as f:
            self.controlConfig = json.load(f)
        self.sumiAutoCaseTime = self.controlConfig.get('Debug').get('ClientSurvivalTime')
        self.processName = 'JX3ClientX64.exe'
        self.autoMonitorControlFlag = Event()

        self.statusDict = {
            'completed.done': 'completed'
        }

    def autoMonitorControl(self, path):
        while 1:
            self.autoMonitorControlFlag.wait()
            for file in os.listdir(path):
                if file.endswith('.result'):
                    result = self.statusDict.get(file, None)
                    PRETTYPRINT.pPrint('获取到completed.result文件，lua tab用例完成')
                    self.logObj.logHandler('Get the completed.result file, the lua tab use case is completed.')
                    BaseWindowsControl.killProcess(self.processName)
                    newFile = '{}.scanned'.format(file)
                    os.rename(
                        os.path.join(path, file),
                        os.path.join(path, newFile)
                    )
                    PRETTYPRINT.pPrint('结果文件名更换: {} -> {}'.format(file, newFile))
                    self.logObj.logHandler().info('Result file name replacement: {} -> {}'.format(file, newFile))
                    return result
            time.sleep(10)

    def semiAutoMaticDebugControl(self):
        i = 0
        while 1:
            self.logObj.logHandler().info('SEMI-AUTOMATIC DEBUG - Game Control.')
            PRETTYPRINT.pPrint('=========================SEMI-AUTOMATIC DEBUG - 游戏内操作=========================')
            PRETTYPRINT.pPrint('客户端已存活时间（秒）: {}，案例时间: {}'.format(i, self.sumiAutoCaseTime))
            self.logObj.logHandler().info('Client alive time (seconds): {}, case time: {}'.format(i, self.sumiAutoCaseTime))
            if i >= self.sumiAutoCaseTime:
                break
            i += 1
            time.sleep(1)
        
        PRETTYPRINT.pPrint('客户端存活时间结束，尝试结束游戏')
        self.logObj.logHandler('Client survival time is over, try to end the game.')
        BaseWindowsControl.killProcess(self.processName)

    def _createNewThread(self, func, name, *args, **kwargs) -> Thread:
        t = Thread(target=func, name=name)
        self.logObj.logHandler().info('gameControl.py - Child thread object has been generated: {}, child process name: {}'.format(t, name))
        return t

    def _startAutoMonitorControlFlag(self):
        self.autoMonitorControlFlag.set()

    def _pauseAutoMonitorControlFlag(self):
        self.autoMonitorControlFlag.clear()

    def dispatch(self, path):
        monitorThread = self._createNewThread(self.autoMonitorControl, name='autoMonitorControl', args=(path, ))
        monitorThread.start()
        






if __name__ == '__main__':
    # debugGameControl()
    BaseWindowsControl.killProcess('JX3ClientX64.exe')