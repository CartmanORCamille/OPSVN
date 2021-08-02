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
    def __init__(self, queue, *args, **kwargs) -> None:
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
            'start.done': 'start',
            'completed.done': BaseWindowsControl.killProcess,
        }
        self.queue = queue

    def autoMonitorControl(self, path):
        while 1:
            self.autoMonitorControlFlag.wait()
            PRETTYPRINT.pPrint('Auto Monitor Control 等待 result 文件中')
            self.logObj.logHandler().info('Auto Monitor Control waits in the result file.')
            for file in os.listdir(path):
                if file.endswith('.done'):
                    result = self.statusDict.get(file, None)
                    PRETTYPRINT.pPrint('获取到 result 文件，状态更新')
                    self.logObj.logHandler('Get the result file, status update.')

                    if callable(result):
                        result(self.processName)
                        self.queue.put('completed')
                        PRETTYPRINT.pPrint('识别到 lua case 已经执行完成，游戏退出，标识符已推入线程队列(D-G-P)')
                        self.logObj.logHandler().info('It is recognized that the lua case has been executed, the game exits, and the identifier has been pushed into the thread queue (D-G-P).')
                    else:
                        self.queue.put(result)
                        PRETTYPRINT.pPrint('识别到 result 文件，result 值为: {}，已推入线程队列 (D-G-P)'.format(result))
                        self.logObj.logHandler().info('The result file is recognized, the result value is: {}, which has been pushed into the thread queue (D-G-P).'.format(result))

                    newFile = '{}.scanned'.format(file)
                    os.rename(
                        os.path.join(path, file),
                        os.path.join(path, newFile)
                    )
                    PRETTYPRINT.pPrint('结果文件名更换: {} -> {}'.format(file, newFile))
                    self.logObj.logHandler().info('Result file name replacement: {} -> {}'.format(file, newFile))
                    
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

    def _createNewThread(self, func, name, path, *args, **kwargs) -> Thread:
        print(*args)
        t = Thread(target=func, name=name, args=(path, ))
        self.logObj.logHandler().info('gameControl.py - Child thread object has been generated: {}, child process name: {}'.format(t, name))
        return t

    def _startAutoMonitorControlFlag(self):
        self.autoMonitorControlFlag.set()

    def _pauseAutoMonitorControlFlag(self):
        self.autoMonitorControlFlag.clear()

    def dispatch(self, path):
        monitorThread = self._createNewThread(self.autoMonitorControl, name='autoMonitorControl', path=path)
        monitorThread.start()
        

class DEBUGGAMECONTROL():
    def debugGameControl(self, ):
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

    @staticmethod
    def debugCreateEndFile(path):
        endFile = os.path.join(path, 'completed.done')
        with open(endFile, 'w', encoding='utf-8') as f:
            f.writable('sb')

    @staticmethod
    def debugCreateStartFile(path):
        startFile = os.path.join(path, 'start.done')
        with open(startFile, 'w', encoding='utf-8') as f:
            f.writable('sb')
        time.sleep(60)




if __name__ == '__main__':
    # debugGameControl()
    BaseWindowsControl.killProcess('JX3ClientX64.exe')