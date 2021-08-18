#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/21 10:22:31
@Author  :   Camille
@Version :   1.0
'''


import logging
import os
import datetime

class BaseLogs():
    """
        @logName:       types_datetime
        @callerPath:    caller function path
    """
    def __init__(self, logName, mark, callerPath='..\\'):
        if not logName:
            todays = datetime.date.today()
            self.logName = '{}{}'.format(todays, '.log')
        self.logName = logName
        self.callerPath = callerPath
        # The main log folder path.
        # self.callerLogsPath = '{}{}'.format(self.callerPath , r'\logs')
        self.callerLogsPath = os.path.join(callerPath, 'logs', mark)
        # Default log name.
        self.baseLogDir()
    
    def baseLogDir(self):
        """
            Complete the main log folder creation requirements.
        """
        if not os.path.exists(self.callerLogsPath):
            os.makedirs(self.callerLogsPath)

    def subLogDir(self, subLogPath):
        """
            Complete other log folder creation requirements.
        """
        os.makedirs('{}{}{}'.format(self.callerPath, '\\', subLogPath))

    def logHandler(self, logName=None, w_logName=None):

        # Create the log.
        logPath = '{}{}{}'.format(self.callerLogsPath, '\\', self.logName)
        fileHandler = logging.FileHandler(logPath, 'a', encoding='utf-8')
        # The logs format.
        fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s')
        fileHandler.setFormatter(fmt)
        # Use the log. Write to self.logName.
        # Default log name: today.
        if w_logName:
            logger = logging.Logger(w_logName)    
        logger = logging.Logger(logPath)
        logger.addHandler(fileHandler)
        return logger
        

class BasicLogs(BaseLogs):
    
    @staticmethod
    def handler(mark, logName=None):
        logsObj = BaseLogs(logName, mark)
        return logsObj