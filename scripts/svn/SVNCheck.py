#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/09 17:17:48
@Author  :   Camille
@Version :   1.0
'''


import os
import sys
import json
import re

sys.path.append('..\..')
from scripts.windows import windows
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class BaseSVNMoudle():
    prettyPrint = PrettyPrint()

    def __init__(self) -> None:
        PRETTYPRINT.pPrint('BaseSVNMoudle模块加载')
        self.ignoreVersionKeywords = 'ShaderList commit'

        PRETTYPRINT.pPrint('读取config.json文件')
        with open(r'.\config\config.json', 'r', encoding='utf-8') as fConfig:
            self.config = json.load(fConfig)

        PRETTYPRINT.pPrint('读取case.json文件')
        with open(r'.\config\case.json', 'r', encoding='utf-8') as fCase:
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
    def __init__(self) -> None:
        super().__init__()
        PRETTYPRINT.pPrint('SVNMoudle模块加载')
        self.filePath = self.case.get('Path').get('Jx3BVTNeedCheck')
        self.initSVNVersion()

    def initSVNVersion(self) -> None:
        """根据时间范围获取BVT版本范围
        """
        # 如果只有时间范围的话就按照当日BVT做为基准
        versionRangeForVersionNumber, versionRangeForDate = self.case.get('SVN').get('versionRangeForVersionNumber'), self.case.get('SVN').get('versionRangeForDate')
        if versionRangeForVersionNumber:
            # 标识去config拿BVT
            PRETTYPRINT.pPrint('获取到 case.json 具体BVT版本范围')
            self.getBVTRangeMethod = 'config'
            
        elif not isinstance(versionRangeForDate, str) and not versionRangeForVersionNumber:
            PRETTYPRINT.pPrint('未获取到 case.json 具体BVT版本范围，获取到时间范围')
            # 根据db查版本号并写入cache
            sqlObj = windows.SQLTools()
            sqlObj.scanningVersion(versionRangeForDate)
            # 标识去case拿BVT范围
            self.getBVTRangeMethod = 'cache'
            
        else:
            raise ValueError('未获取到具体BVT版本，未获取到时间范围，请检查config.json')
        
    def getNowFileVersion(self, ) -> None:
        # 获取指定版本
        nowFileInfo = self._showNowInfo(self.filePath)
        nowFileVersion = [i.group() for i in re.finditer(r'Revision: (\d+)', nowFileInfo)][0][10:]

        return nowFileVersion

    def updateCheck(self, uid: str, versions: list = None, *args, **kwargs) -> None:
        """更新前检查，根据BVT范围数据去查找确切的路径版本数据

        Args:
            uid (str): 写入cache.FileRealVersion的标识符
            versions (list): 需要细查的版本范围

        Returns:
            return: 返回处理后的版本范围
        """
        # 获取BVT版本范围
        if self.getBVTRangeMethod == 'cache':
            with open(r'.\caches\BVTVersion.json', 'r', encoding='utf-8') as f:
                cache = json.load(f)
            PRETTYPRINT.pPrint('读取cache -> BVTVersion.json 文件')
            BVTVersionRangeList = [cache.get('BVTVersion')[0], cache.get('BVTVersion')[-1]]
        elif self.getBVTRangeMethod == 'config':
            PRETTYPRINT.pPrint('读取config -> config.json 文件')
            BVTVersionRangeList = self.case.get('SVN').get('versionRangeForVersionNumber')

        realVersionList = self._showLogWithVersionRange(BVTVersionRangeList)
        windows.MakeCache.writeCache('FileRealVersion.json', uid = uid, FileRealVersion = realVersionList)
        PRETTYPRINT.pPrint('已写入cache -> FileRealVersion.json: {}'.format(realVersionList))

        return realVersionList

    def update(self, version) -> None:
        # 判断当前文件版本和需求版本是否相同
        nowFileVersion = self.getNowFileVersion()
        PRETTYPRINT.pPrint('文件现在版本: {}'.format(nowFileVersion))
        if nowFileVersion != version:
            PRETTYPRINT.pPrint('目标版本({})与现在版本({})不一致，准备更新'.format(version, nowFileVersion))
            while 1:
                PRETTYPRINT.pPrint('准备更新，目标版本: {}'.format(version))
                # 锁库循环
                result = self._updateToVersion(version, self.filePath)
                if 'E155004' in result or 'E155037' in result:
                    # 锁库
                    PRETTYPRINT.pPrint('识别到锁库，准备执行cleanup，错误信息 -> {}'.format(result), 'WARING', bold=True)
                    self._cleanup(self.filePath)

                elif 'Updated to revision' in result:
                    # 更新成功
                    PRETTYPRINT.pPrint('版本更新成功: {}'.format(version))
                    break
                    
                else:
                    PRETTYPRINT.pPrint(result, 'ERROR', bold=True)
                    raise Exception('SVN 未知错误，请手动处理。')
        else:
            PRETTYPRINT.pPrint('目标版本({})与现在版本({})一致，无须更新'.format(version, nowFileVersion), 'WARING', bold=True)
        return 1
        

if __name__ == '__main__':
    pass