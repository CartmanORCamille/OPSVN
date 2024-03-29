#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/09 17:17:48
@Author  :   Camille
@Version :   1.0
'''

from logging import fatal
import os
import sys
sys.path.append(os.getcwd())
import psutil
import pythoncom
import json
import subprocess
import sqlite3
import time
import win32api, win32gui, win32com, win32con
import win32com.client
import hashlib
from PIL import ImageGrab
from scripts.prettyCode.prettyPrint import PrettyPrint
from scripts.windows.journalist import BasicLogs


PRETTYPRINT = PrettyPrint()


def writeLogs(self, logName, *args, **kwargs) -> None:
    logObj = BasicLogs.handler(logName=logName, mark='dispatch')
    logObj.logHandler().info('Initialize writeLogs(window) function instance.')
    return logObj


class BaseWindowsControl():
    
    @staticmethod
    def consoleExecutionWithRun(command, cwd=None, *args, **kwargs) -> str:
        # CMD命令执行
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        result = process.stdout.decode('gbk')
        error = process.stderr.decode('gbk')
        if error:
            return error
        return result

    @staticmethod
    def consoleExecutionWithPopen(command: str, cwd=None, *args, **kwargs) -> subprocess.Popen:
        # CMD命令执行
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        return process

    @staticmethod
    def getNowActiveHandle(*args, **kwargs) -> tuple:
        """获取当前活动窗口的句柄

        Returns:
            tuple: (hwnd，caption，className)
        """
        activeHwnd = win32gui.GetForegroundWindow()
        hwndCaption = win32gui.GetWindowText(activeHwnd)
        hwndClassName = None
        try:
            hwndClassName = win32gui.GetClassName(activeHwnd)
        except Exception as e:
            errorLog = '获取句柄(getNowActiveHandle) - 或许触碰点击到了 windows 菜单，任务栏或者其他不属于 win32 所控制的地点，报错信息: {} - {}'.format(e.__traceback__.tb_lineno, str(e))
            PRETTYPRINT.pPrint(errorLog, 'ERROR', bold=True)
        time.sleep(1)
            
        if hwndClassName == 'Ghost':
            PRETTYPRINT.pPrint('窗口活动信息出现未响应！', 'WARING', bold=True)
            return 'Ghost'
        PRETTYPRINT.pPrint('目前活动窗口信息 -> hwnd: {}, caption: {}, className: {}'.format(activeHwnd, hwndCaption, hwndClassName))
        return (activeHwnd, hwndCaption, hwndClassName)

    @staticmethod
    def activationWindow(caption, className=None, *args, **kwargs) -> None:
        # 将程序设为活动窗口
        # 必要参数
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')

        try:
            win32gui.SetForegroundWindow(win32gui.FindWindow(className, caption))
        except Exception as e:
            errorLog = '激活句柄(activationWindow) - 或许触碰点击到了 windows 菜单，任务栏或者其他不属于 win32 所控制的地点，报错信息: {} - {}'.format(e.__traceback__.tb_lineno, str(e))
            PRETTYPRINT.pPrint(errorLog, 'ERROR', bold=True)
            return errorLog

    @staticmethod
    def useMd5(obj, method, *args, **kwargs):
        # 生成md5
        if method == 'file':
            if isinstance(obj, str):
                md5Obj = hashlib.md5(obj.encode('utf-8'))
        return md5Obj.hexdigest()

    @staticmethod
    def showWindowToMax(hwnd, *args, **kwargs) -> None:
        # 显示并将其最大化一个窗口
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)

    @staticmethod
    def screenshots(imgPath, *args, **kwargs) -> None:
        # 截图
        im = ImageGrab.grab()
        im.save(imgPath, 'jpeg')

    @staticmethod
    def openProcess(path, *args, **kwargs) -> None:
        # 启动进程
        os.startfile(path)

    @staticmethod
    def killProcess(process, *args, **kwargs) -> None:
        # 结束进程
        command = 'taskkill /F /IM {}'.format(process)
        BaseWindowsControl.consoleExecutionWithRun(command)

    @staticmethod
    def whereIsTheDir(path, create=False, *args, **kwargs) -> bool:
        if not os.path.exists(path):
            PRETTYPRINT.pPrint('文件目录不存在')
            if create:
                os.makedirs(path)
                PRETTYPRINT.pPrint('已创建文件目录 -> {}'.format(path))
                return True
            else:
                PRETTYPRINT.pPrint('未创建目录文件', 'WARING', bold=True)
                return False
        else:
            PRETTYPRINT.pPrint('文件目录存在')
            return True

    @staticmethod
    def loading(loadingTime, *args, **kwargs):
        sleep = loadingTime / 100
        for i in range(1, 101):
            print('\r{}%'.format(i),'[', '=' * (i // 2), ']', end="")
            sys.stdout.flush()
            time.sleep(sleep)

class SQLTools():
    def __init__(self, *args, **kwargs) -> None:
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize SQLTools(windows) class instance.')

        with open(r'..\config\config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 连接数据库
        try:
            self.sqlPointer()
            self.logObj.logHandler().info('sql connection is successful.')
        except Exception as e:
            self.logObj.logHandler().error('[P0] sql connection failed, reason: {}'.format(e))
            raise e
    
    def sqlPointer(self, *args, **kwargs) -> None:
        db = self.config.get('db').get('dbFilePath')
        conn = sqlite3.connect(db)
        self.cursor = conn.cursor()

    def scanningVersion(self, dates: list, *args, **kwargs):
        # 根据时间范围查找文件的BVT版本和实际版本
        dateVersions = []
        for date in dates:
            # 查BVT版本
            if len(dates) == 2:
                # 时间范围 -> 起始 TO 结束
                date = SQLTools.cleanDateForBVTSql(date, 0)
                sql = "select Client from Revision where Time = '{}';".format(date)
                version = [i for i in self.cursor.execute(sql)][0][0]
                PRETTYPRINT.pPrint('code: 2 获取时间范围对应BVT版本: {} -> {}'.format(date, version))
                self.logObj.logHandler().info('code: 2 Get the time corresponding to the BVT version: {} -> {}'.format(date, version))
                dateVersions.append(version)
            else:
                # 具体日期
                version = SQLTools.cleanDateForBVTSql(date)
                sql = "select Client from TodayBVT where Time = '{}';".format(date)
                version = [i for i in self.cursor.execute(sql)][0][0]
                PRETTYPRINT.pPrint('code: 1 获取具体时间对应BVT版本：{} -> {}'.format(date, version))
                self.logObj.logHandler().info('code: 1 Get the BVT version corresponding to the specific time: {} -> {}'.format(date, version))
                return version

        ''' 以下是获取时间范围段情况下的逻辑代码 '''
        # 根据两个版本号查BVT中间值
        PRETTYPRINT.pPrint('准备获取BVT版本范围')
        self.logObj.logHandler().info('Ready to obtain the BVT version range.')
        getVersionsCommandSql = "select Client from Revision where Client between '{}' and '{}'".format(dateVersions[0], dateVersions[1])
        versions = [i[0] for i in self.cursor.execute(getVersionsCommandSql)]
        # 写入缓存文件
        for i in versions:
            PRETTYPRINT.pPrint('获取BVT版本范围 -> {}'.format(i))
            self.logObj.logHandler().info('Get BVT version range -> {}'.format(i))

        MakeCache.writeCache('BVTVersion.json', BVTVersion = versions)
        PRETTYPRINT.pPrint('已写入cache -> BVTVersion.json')
        self.logObj.logHandler().info('Has been written to cache -> BVTVersion.json')
        return versions

    @staticmethod
    def cleanDateForBVTSql(date: str, today: bool = True, *args, **kwargs) -> str:
        """将日期清洗为数据库可读格式

        Args:
            date (str): 需要清洗的日期
                eg: eg: 2021-01-01 -> 2021-1-1
            today (bool): 对应的需要查找的数据表日期格式，默认为今日数据BVT数据表
                eg: 2021-01-01 -> 2021年1月1日

        Returns:
            str: 清洗后的日期
        """
        if not today:
            date = [i for i in date]
            date[4] = '年'
            date[7] = '月'
            date.append('日')

        # 去0，如果天数为单个数
        date.pop(8) if date[8] == '0' else None
        # 去0，如果月份是单个数
        date.pop(5) if date[5] == '0' else None

        return ''.join(date)
        

class MakeCache():
    
    @staticmethod
    def writeCache(cacheName, *args, **kwargs):
        BaseWindowsControl.whereIsTheDir(r'..\caches', True)
        with open(r'..\caches\{}'.format(cacheName), 'w', encoding='utf-8') as f:
            kwargs['Time'] = time.asctime(time.localtime(time.time()))
            json.dump(kwargs, f, indent=4)


class GrabFocus():
    # 抢夺焦点
    def __init__(self, *args, **kwargs) -> None:
        self.logName = kwargs.get('logName', None)
        assert self.logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize GrabFocus(windows) class instance.')

    def _useCrashAbacus(self, *args, **kwargs) -> object:
        from scripts.dataAnalysis.abacus import CrashAbacus
        crashCheckObj = CrashAbacus(logName=self.logName)
        return crashCheckObj

    def _useProcessMonitoring(self, *args, **kwargs) -> object:
        processMonitoring = ProcessMonitoring(logName=self.logName)
        return processMonitoring

    def dispatch(self, version, uid, *args, **kwargs):
        with open(r'..\config\version.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        hwndClassName = config.get('windowsInfo').get('JX3RemakeBVT').get('className')
        self.logObj.logHandler().info('hwndClassName: {}'.format(hwndClassName))

        # 获取当前窗口句柄
        activeHandleInfoTuple = BaseWindowsControl.getNowActiveHandle()
        if not activeHandleInfoTuple[-1]:
            return 1400
        if activeHandleInfoTuple == 'Ghost':
            # 未响应 -> 截图
            # BaseWindowsControl.screenshots()
            self.logObj.logHandler().warning('GHOST!')
            self.logObj.logHandler().error('[P3] The program is not responding.')

        if activeHandleInfoTuple[2] != hwndClassName:
            # 判断是否丢失焦点
            # 判断游戏客户端是否存在
            hwndExists = win32gui.FindWindow(hwndClassName, None)
            self.logObj.logHandler().info('hwndExists: {}'.format(hwndExists))

            # 判断宕机窗口是否存在
            crashResult = self._useProcessMonitoring().dispatch(controlledBy='DumpReport64.exe')
            self.logObj.logHandler().info('crashPidExists: {}'.format(crashResult))

            if isinstance(crashResult, tuple):
                PRETTYPRINT.pPrint('crash process exists: {}'.format(crashResult[0]))
                self.logObj.logHandler().warning('crash process exists: {}'.format(crashResult[0]))
                self._useCrashAbacus().dispatch(version, 1)

                # 写入文件
                with open('..\\caches\\{}.txt'.format(), 'a', encoding='utf-8') as f:
                    f.write(version)

                return 'GameCrash'

            if hwndExists:
                PRETTYPRINT.pPrint('识别客户端加载条阶段结束，进入游戏: {}'.format(hwndExists))
                self.logObj.logHandler().info('The stage of identifying the loading bar of the client is over and enter the game. hwndExists: {}'.format(hwndExists))
                PRETTYPRINT.pPrint('焦点丢失，正在抢夺焦点。')
                self.logObj.logHandler().warning('The focus is lost and the focus is being grabbed.')
                errorMsg = BaseWindowsControl.activationWindow(None, hwndClassName)
                if errorMsg:
                    self.logObj.logHandler().error(errorMsg)
            else:
                PRETTYPRINT.pPrint('无法找到句柄，或许是程序暂未启动', 'WARING', bold=True)
                self.logObj.logHandler().warning('[P2] Cannot find the handle, maybe the program has not been started yet.')

        else:
            PRETTYPRINT.pPrint('焦点确认，设置最大化')
            self.logObj.logHandler().info('Focus confirmation, maximize settings.')
            BaseWindowsControl.showWindowToMax(activeHandleInfoTuple[0])


class ProcessMonitoring():
    # 进程监控
    
    def __init__(self, *args, **kwargs) -> None:
        self.logName = kwargs.get('logName', None)
        record = kwargs.get('record', 1)
        if record:
            assert self.logName, 'Can not find logname.'
            self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
            self.logObj.logHandler().info('Initialize ProcessMonitoring(windows) class instance.')

    def _useCrashAbacus(self, *args, **kwargs) -> object:
        from scripts.dataAnalysis.abacus import CrashAbacus
        crashCheckObj = CrashAbacus(logName=self.logName)
        return crashCheckObj

    def dispatch(self, controlledBy=None, isPid=None, *args, **kwargs):    
        if not controlledBy:
            controlledBy = 'JX3ClientX64.exe'
        self.logObj.logHandler().info('controlledBy: {}'.format(controlledBy))
        PRETTYPRINT.pPrint('识别进程中 -> {}'.format(controlledBy))
        # 获取所有进程
        pids = psutil.pids()

        with open(r'..\config\version.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 比对
        for pid in pids:
            try:
                process = psutil.Process(pid)
                if process.name() == controlledBy:
                    # 查找进程是否存在
                    if isPid:
                        self.logObj.logHandler().info('isPid == true, retrun the pid: {}'.format(pid))
                        return pid
                    # 识别到JX3CLIENTX64.EXE
                    PRETTYPRINT.pPrint('已识别进程 - {}'.format(controlledBy))
                    self.logObj.logHandler().info('Processes identified - {}'.format(controlledBy))

                    '''识别是否卡进度条'''
                    loadingHwndClassName = config.get('windowsInfo').get('Loading').get('className')
                    self.logObj.logHandler().info('loadingHwndClassName: {}'.format(loadingHwndClassName))

                    loadingExists = win32gui.FindWindow(loadingHwndClassName, None)
                    self.logObj.logHandler().info('loadingExists: {}'.format(loadingExists))

                    if loadingExists:
                        PRETTYPRINT.pPrint('识别客户端正在加载条阶段，等待中: {}'.format(loadingExists))
                        self.logObj.logHandler().info('Recognize that the client is in the stage of loading the bar, waiting. loadingExists: {}'.format(loadingExists))
                        return 'loading'

                    if controlledBy == 'DumpReport64.exe':
                        # 查找是否有宕机
                        return (pid, 'StartingCrash')
                    return True

            except psutil.NoSuchProcess as ncp:
                self.logObj.logHandler().error('[P2] No such process -> {}'.format(ncp))
            except psutil.AccessDenied as ad:
                self.logObj.logHandler().error('[P3] Unprivileged process -> {}'.format(ad))


class FindTheFile():
    def __init__(self, *args, **kwargs) -> None:
        self.status = {
            'complete': 'complete.done',
        }

    def findFile(self, status, path, *args, **kwargs) -> bool:
        file = self.status.get(status, None)
        exists = os.path.exists(os.path.join(path, status))
        return exists


if __name__ == '__main__':
    pass