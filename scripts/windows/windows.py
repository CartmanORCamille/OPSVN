#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/09 17:17:48
@Author  :   Camille
@Version :   1.0
'''

import json
import subprocess
import sqlite3
import time
import win32api, win32gui, win32com
import win32com.client

class BaseWindowsControl():
    
    @staticmethod
    def consoleExecutionWithRun(command):
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process.stdout.decode('gbk')
        error = process.stderr.decode('gbk')
        if error:
            return error
        return result

    @staticmethod
    def getNowActiveHandle():
        # 获取当前活动窗口的句柄
        activeHwnd = win32gui.GetForegroundWindow()
        hwndCaption = win32gui.GetWindowText(activeHwnd)
        hwndClassName = win32gui.GetClassName(activeHwnd)
        return activeHwnd, hwndCaption, hwndClassName

    @staticmethod
    def checkWindow(caption, className=None) -> None:
        # 将程序设为活动窗口
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(win32gui.FindWindow(className, caption))

class SQLTools():
    def __init__(self) -> None:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 连接数据库
        self.sqlPointer()
    
    def sqlPointer(self):
        db = self.config.get('db').get('dbFilePath')
        conn = sqlite3.connect(db)
        self.cursor = conn.cursor()

    def scanningVersion(self, dates: list):
        # 查找文件具体版本
        dateVersions = []
        for date in dates:
            if len(dates) == 2:
                # 时间范围
                date = SQLTools.cleanDateForBVTSql(date, 0)
                sql = "select Client from Revision where Time = '{}';".format(date)
                version = [i for i in self.cursor.execute(sql)][0][0]
                dateVersions.append(version)
            else:
                # 具体日期
                version = SQLTools.cleanDateForBVTSql(date)
                sql = "select Client from TodayBVT where Time = '{}';".format(date)
                version = [i for i in self.cursor.execute(sql)][0][0]
                return version

        ''' 以下是获取时间范围段情况下的逻辑代码 '''
        # 根据两个版本号查中间值
        getVersionsCommandSql = "select Client from Revision where Client between '{}' and '{}'".format(dateVersions[0], dateVersions[1])
        versions = [i[0] for i in self.cursor.execute(getVersionsCommandSql)]
        # 写入缓存文件
        MakeCache.writeCache('BVTVersion.json', BVTVersion = versions)

        return versions

    @staticmethod
    def cleanDateForBVTSql(date: str, today: bool = True) -> str:
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
        with open(r'.\caches\{}'.format(cacheName), 'w', encoding='utf-8') as f:
            kwargs['Time'] = time.asctime(time.localtime(time.time()))
            json.dump(kwargs, f, indent=4)

if __name__ == '__main__':
    obj = SQLTools()
    # obj.scanningVersion(['2018-01-23', '2018-01-29'])
    time.sleep(5)
    a, b, c = BaseWindowsControl.getNowActiveHandle()
    print(a, b, c)