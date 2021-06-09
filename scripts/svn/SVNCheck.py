#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/09 17:17:48
@Author  :   Camille
@Version :   1.0
'''

import sys
import json
import re
sys.path.append('..\..')
from ..windows import windows


class BaseSVNMoudle():
    def __init__(self) -> None:
        self.ignoreVersionKeywords = 'ShaderList commit'
        with open(r'.\config\config.json', 'r', encoding='utf-8') as fConfig, open(r'.\config\case.json', 'r', encoding='utf-8') as fCase:
            self.config, self.case = json.load(fConfig), json.load(fCase)
        
    @staticmethod
    def submitSVNOrder(command) -> None:
        return windows.BaseWindowsControl.consoleExecutionWithRun(command)

    def _updateToVersion(self, version):
        command = 'svn update -r {}'.format(version)
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
        # 根据BVT版本范围查精确的文件版本范围
        command = 'svn log {} -r {}:{}'.format(self.config.get('Path').get('JX3_BVT'), version[0], version[1])
        result = BaseSVNMoudle.submitSVNOrder(command)
        return self._cleanLog(result)
        
    def _cleanLog(self, result):
        realVersion = []
        # 清洗数据
        reText = r'\d+.*\n.*\n.*'
        versionLogList = re.findall(reText, result)

        for versionLog in versionLogList:
            if self.ignoreVersionKeywords not in versionLog:
                realVersion.append(versionLog[:6])
        
        return realVersion

    def _findDayBVT():
        pass


class SVNMoudle(BaseSVNMoudle):
    def __init__(self) -> None:
        super().__init__()
        self.initSVNVersion()
        self.filePath = self.config.get('Path').get('JX3_BVT')

    def initSVNVersion(self) -> None:
        """根据时间范围获取BVT版本范围
        """
        # 如果只有时间范围的话就按照当日BVT做为基准
        versionRangeForVersionNumber, versionRangeForDate = self.case.get('SVN').get('versionRangeForVersionNumber'), self.case.get('SVN').get('versionRangeForDate')
        if not versionRangeForVersionNumber:
            # 根据db查版本号并写入cache
            sqlObj = windows.SQLTools()
            sqlObj.scanningVersion(versionRangeForDate)
            # 标识去case拿BVT范围
            self.getBVTRangeMethod = 'cache'
        else:
            # 标识去config拿BVT
            self.getBVTRangeMethod = 'config'
        
    def getNowFileVersion(self, ) -> None:
        # 更新指定版本主函数
        nowFileInfo = self._showNowInfo(self.filePath)
        nowFileVersion = [i.group() for i in re.finditer(r'Revision: (\d+)', nowFileInfo)][0][10:]

        return nowFileVersion

    def updateCheck(self, versions: list = None) -> None:
        """更新前检查，根据BVT范围数据去查找确切的路径版本数据

        Args:
            versions (list): 需要细查的版本范围

        Returns:
            return: 返回处理后的版本范围
        """
        # 获取BVT版本范围
        if self.getBVTRangeMethod == 'cache':
            with open(r'.\caches\BVTVersion.json', 'r', encoding='utf-8') as f:
                cache = json.load(f)
            BVTVersionRangeList = [cache.get('BVTVersion')[0], cache.get('BVTVersion')[-1]]
        elif self.getBVTRangeMethod == 'config':
            BVTVersionRangeList = self.case.get('SVN').get('versionRangeForVersionNumber')

        realVersionList = self._showLogWithVersionRange(BVTVersionRangeList)
        windows.MakeCache.writeCache('FileRealVersion.json', FileRealVersion = realVersionList)

        return realVersionList

    def dispatch(self, version) -> None:
        # 判断当前文件版本和需求版本是否相同
        nowFileVersion = self.getNowFileVersion()
        if nowFileVersion != version:
            while 1:
                # 锁库循环
                result = self._updateToVersion(self.filePath)
                if 'E155004' in result:
                    # 锁库
                    self._cleanup(self.filePath)

                elif 'Updated to revision' in result:
                    # 更新成功
                    print('更新成功')
                    break
                    
                else:
                    raise Exception('SVN 未知错误，请手动处理。')
        return 1
        

if __name__ == '__main__':
    obj = SVNMoudle()
    obj.dispatch()