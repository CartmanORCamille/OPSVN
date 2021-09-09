#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/09 17:17:48
@Author  :   Camille
@Version :   1.0
'''


import os
import sys
sys.path.append(os.getcwd())
import json
import re
from scripts.windows import windows
from scripts.windows.journalist import BasicLogs
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class BaseSVNMoudle():
    prettyPrint = PrettyPrint()

    def __init__(self, *args, **kwargs) -> None:
        PRETTYPRINT.pPrint('BaseSVNMoudle模块加载')
        self.ignoreVersionKeywords = 'ShaderList commit'

        PRETTYPRINT.pPrint('读取config.json文件')
        with open(r'..\config\config.json', 'r', encoding='utf-8') as fConfig:
            self.config = json.load(fConfig)

        PRETTYPRINT.pPrint('读取case.json文件')
        with open(r'..\config\case.json', 'r', encoding='utf-8') as fCase:
            self.case = json.load(fCase)
            
    @staticmethod
    def submitSVNOrder(command) -> None:
        PRETTYPRINT.pPrint('开始执行 -> {}'.format(command))
        return windows.BaseWindowsControl.consoleExecutionWithRun(command)

    def _updateToVersion(self, version, path):
        command = 'svn update -r {} {}'.format(version, path)
        return BaseSVNMoudle.submitSVNOrder(command)

    def _cleanup(self, path):
        command = 'svn cleanup {}'.format(path)
        return BaseSVNMoudle.submitSVNOrder(command)

    def _showNowInfo(self, path):
        command = 'svn info {}'.format(path)
        return BaseSVNMoudle.submitSVNOrder(command)

    def _showLogWithDateRange(self, ):
        pass

    def _showLogWithVersionRange(self, version: list):
        """根据BVT版本范围查精确的文件版本范围，返回清洗后的数据 -> 版本列表

        """
        # 获取版本范围日期日志
        command = 'svn log {} -r {}:{}'.format(self.case.get('Path').get('Jx3BVTNeedCheck'), version[0], version[1])
        PRETTYPRINT.pPrint('获取版本范围日志 -> {} TO {}'.format(version[0], version[1]))
        result = BaseSVNMoudle.submitSVNOrder(command)
        if 'cleanup' in result:
            return result  
        return self._cleanLog(result)
        
    def _cleanLog(self, result):
        realVersion = []
        # 清洗数据
        reText = r'\d+.*\n.*\n.*'
        versionLogList = re.findall(reText, result)
        PRETTYPRINT.pPrint('识别数据模块加载')
        for versionLog in versionLogList:
            if self.ignoreVersionKeywords not in versionLog and '.' not in versionLog:
                ver = versionLog[:6]
                PRETTYPRINT.pPrint('获取版本详细版本 -> {}'.format(ver))
                realVersion.append(ver)
        
        return realVersion

    def _findDayBVT():
        pass


class SVNMoudle(BaseSVNMoudle):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logName = kwargs.get('logName', None)
        assert self.logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=self.logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize SVNMoudle(SVNCheck) class instance.')
        PRETTYPRINT.pPrint('SVNMoudle模块加载')

        self.SVNExceptionHandling = {
            'E155004': self._SVNunlock,
            'E155037': self._SVNunlock,
            'E720005': self._SVNProcessOccupation,
        }

        self.filePath = self.case.get('Path').get('Jx3BVTNeedCheck')
        self.initSVNVersion()

    def _SVNunlock(self, result=None, *args, **kwargs) -> None:
        PRETTYPRINT.pPrint('识别到锁库，准备执行cleanup，错误信息 -> {}'.format(result), 'WARING', bold=True)
        self.logObj.logHandler().warning('Identify the lock library, prepare to execute cleanup, error message -> {}'.format(result))
        cleanupClientStatus = (
            'client',
            'E155037',
        )
        for i in cleanupClientStatus:
            if i in result:
                # cleanup Client
                PRETTYPRINT.pPrint('需要cleanup client')
                self._cleanup(self.case.get('Path').get('Jx3BVTWorkPath').replace('\\bin64', ''))
                self.logObj.logHandler().info('SVN clean over.')
                return
            
        self._cleanup(self.filePath)
        self.logObj.logHandler().info('SVN clean over.')

    def _SVNProcessOccupation(self,*args, **kwargs) -> None:
        PRETTYPRINT.pPrint('某个文件占用了导致SVN无法更新，请检查，尝试关闭客户端进程')
        self.logObj.logHandler().error('[P2] A certain file is occupied and SVN cannot be updated. Please check and try to close the client process.')
        windows.BaseWindowsControl.killProcess('JX3ClientX64.exe')

    def initSVNVersion(self) -> None:
        """根据时间范围获取BVT版本范围
        """
        # 如果只有时间范围的话就按照当日BVT做为基准
        versionRangeForVersionNumber, versionRangeForDate = self.case.get('SVN').get('versionRangeForVersionNumber'), self.case.get('SVN').get('versionRangeForDate')
        if versionRangeForVersionNumber:
            # 标识去config拿BVT
            PRETTYPRINT.pPrint('获取到 case.json 具体BVT版本范围')
            self.getBVTRangeMethod = 'config'
            self.logObj.logHandler().info('Get the specific BVT version range of case.json, getBVTRangeMethod == config.')
            
        elif not isinstance(versionRangeForDate, str) and not versionRangeForVersionNumber:
            PRETTYPRINT.pPrint('未获取到 case.json 具体BVT版本范围，获取到时间范围')
            # 根据db查版本号并写入cache
            sqlObj = windows.SQLTools(logName=self.logName)
            sqlObj.scanningVersion(versionRangeForDate)
            # 标识去case拿BVT范围
            self.getBVTRangeMethod = 'cache'
            self.logObj.logHandler().info('The specific BVT version range of case.json is not obtained, but the time range is obtained, getBVTRangeMethod == cache.')
            
        else:
            self.logObj.logHandler().error('[P1] The specific BVT version has not been obtained, and the time range has not been obtained, please check case.json')
            raise ValueError('未获取到具体BVT版本，未获取到时间范围，请检查case.json')
        
    def getNowFileVersion(self, ) -> None:
        # 获取指定版本
        nowFileInfo = self._showNowInfo(self.filePath)
        nowFileVersion = [i.group() for i in re.finditer(r'Revision: (\d+)', nowFileInfo)][0][10:]
        self.logObj.logHandler().info('Get the now file version: {}'.format(nowFileVersion))
        return nowFileVersion

    def updateCheck(self, uid: str, versions: list = None, *args, **kwargs) -> None:
        """更新前检查，根据BVT范围数据去查找确切的路径版本数据

        Args:
            uid (str): 写入cache.FileRealVersion的标识符
            versions (list): 需要细查的版本范围

        Returns:
            return: 返回处理后的版本范围
        """
        while 1:
            # 获取BVT版本范围
            if self.getBVTRangeMethod == 'cache':
                with open(r'..\caches\BVTVersion.json', 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                self.logObj.logHandler().info('Read cache -> BVTVersion.json file')
                PRETTYPRINT.pPrint('读取cache -> BVTVersion.json 文件')
                BVTVersionRangeList = [cache.get('BVTVersion')[0], cache.get('BVTVersion')[-1]]
                self.logObj.logHandler().info('Get the SVN BVT version: {}'.format(BVTVersionRangeList))
                
            elif self.getBVTRangeMethod == 'config':
                self.logObj.logHandler().info('Read config -> case.json file')
                PRETTYPRINT.pPrint('读取config -> case.json 文件')
                BVTVersionRangeList = self.case.get('SVN').get('versionRangeForVersionNumber')
                self.logObj.logHandler().info('Get the SVN BVT version: {}'.format(BVTVersionRangeList))

            realVersionList = self._showLogWithVersionRange(BVTVersionRangeList)
            if 'cleanup' in realVersionList:
                PRETTYPRINT.pPrint('[P0] 未查到版本，需要cleanup', 'ERROR', bold=True)
                self.logObj.logHandler().error('[P0] not found the versions, need cleanup.')
                self._SVNunlock('E155037')
    
            else:
                self.logObj.logHandler().info('Get SVN BVT real version: {}'.format(realVersionList))
                windows.MakeCache.writeCache('FileRealVersion.json', uid = uid, FileRealVersion = realVersionList)
                PRETTYPRINT.pPrint('已写入cache -> FileRealVersion.json: {}'.format(realVersionList))
                self.logObj.logHandler().info('Has been written to cache -> FileRealVersion.json: {}'.format(realVersionList))
                break

        return realVersionList

    def update(self, version) -> None:
        # 判断当前文件版本和需求版本是否相同
        nowFileVersion = self.getNowFileVersion()
        self.logObj.logHandler().info('SVN now version: {}'.format(nowFileVersion))
        PRETTYPRINT.pPrint('文件现在版本: {}'.format(nowFileVersion))
        if nowFileVersion != version:
            PRETTYPRINT.pPrint('目标版本({})与现在版本({})不一致，准备更新'.format(version, nowFileVersion))
            self.logObj.logHandler().info('The target version ({}) is inconsistent with the current version ({}), ready to update'.format(version, nowFileVersion))
            while 1:
                PRETTYPRINT.pPrint('准备更新，目标版本: {}'.format(version))
                self.logObj.logHandler().info('Ready to update, target version: {}'.format(version))
                # 锁库循环
                result = self._updateToVersion(version, self.filePath)
                if 'E155004' in result or 'E155037' in result:
                    # 锁库
                    self.SVNExceptionHandling.get('E155004')(result)

                elif 'E720005' in result:
                    self.SVNExceptionHandling.get('E720005')()
                    
                elif 'Updated to revision' in result:
                    # 更新成功
                    PRETTYPRINT.pPrint('版本更新成功: {}'.format(version))
                    self.logObj.logHandler().info('Successful version update: {}'.format(version))
                    break
                    
                else:
                    PRETTYPRINT.pPrint(result, 'ERROR', bold=True)
                    self.logObj.logHandler().error('[P0] SVN unknown error, please handle it manually.')
                    raise Exception('SVN 未知错误，请手动处理。')
        else:
            PRETTYPRINT.pPrint('目标版本({})与现在版本({})一致，无须更新'.format(version, nowFileVersion), 'WARING', bold=True)
            self.logObj.logHandler().info('The target version ({}) is the same as the current version ({}), no need to update.'.format(version, nowFileVersion))
        return 1
        

if __name__ == '__main__':
    pass