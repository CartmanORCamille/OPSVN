#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/07/16 15:42:42
@Author  :   Camille
@Version :   1.0
'''


import requests
import json
import datetime
from scripts.windows.journalist import BasicLogs


class FEISHU():
    def __init__(self, *args, **kwargs) -> None:
        logName = kwargs.get('logName', None)
        assert logName, 'Can not find logname.'
        self.logObj = BasicLogs.handler(logName=logName, mark='dispatch')
        self.logObj.logHandler().info('Initialize FEISHU(contact) class instance.')

        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.url = json.load(f).get('Contact').get('FEISHU')
        with open(r'.\config\version.json') as f:
            self.versionInfo = json.load(f)

    def _drawTheNormalMsg(self, uid, version, equipment, FPS, VRAM, gamePlay, defectBehavior, status, reportDateTime, resolution, isFinal=False):
        # 'ALPHA_16248491144391608', '941542', 'Test Equipment: 610', 'FPS: 22', 'VRAM: 2200', 'Game Play: stand', 'Defect Behavior: crash'
        if not isFinal:
            dataResultIdentifier = 'NOT FINAL'
        else:
            dataResultIdentifier = 'FINAL'
        normalFieldAmount = 8
        OPSVNVersion = self.versionInfo.get('OPSVN').get('version')
        data = self._dataModuleOfNormalBody()
        data['content']['post']['en_us']['title'] = 'OPSVN_{}({}) - {} TEST REPORT [{}]'.format(
            OPSVNVersion, uid, version, dataResultIdentifier
        )

        equipment = 'Test Equipment: {}'.format(equipment)
        FPS = 'FPS: {}'.format(FPS)
        VRAM = 'VRAM: {}'.format(VRAM)
        gamePlay = 'Game Play: {}'.format(gamePlay)
        defectBehavior = 'Defect Behavior: {}'.format(defectBehavior)
        status = 'Status: {}'.format(status)
        reportDateTime = 'Report Datetime: {}'.format(str(datetime.datetime.now()))
        resolution = 'Resolution: {}'.format(resolution)
        # machine = 'Machine: {}'.format(machine)
        
        userData = [equipment, FPS, VRAM, gamePlay, defectBehavior, status, reportDateTime, resolution,]
        
        data = self.coloring(data, userData, normalFieldAmount)

        return data

    def _drawTheStartingCrashMsg(self, uid, equipment, version):
        data = self._dataMoudleOfStartingCrash()
        data['content']['post']['en_us']['title'] = 'OPSVN_{}({}) - {} Staring Crash'.format(
            self.versionInfo.get('OPSVN').get('version'), uid, version
        )
        reportDateTime = 'Report Datetime: {}'.format(str(datetime.datetime.now()))
        equipment = 'Test Equipment: {}'.format(equipment)
        userData = [equipment, reportDateTime]
        data = self.coloring(data, userData, 2)
        return data

    def _drawTheGamingCrashMsg(self, uid, equipment, version):
        data = self._dataMoudleOfStartingCrash()
        data['content']['post']['en_us']['title'] = 'OPSVN_{}({}) - {} Gaming Crash'.format(
            self.versionInfo.get('OPSVN').get('version'), uid, version
        )
        reportDateTime = 'Report Datetime: {}'.format(str(datetime.datetime.now()))
        equipment = 'Test Equipment: {}'.format(equipment)
        userData = [equipment, reportDateTime]
        data = self.coloring(data, userData, 2)
        return data

    def _drawTheLoadingTimeoutMsg(self, uid, equipment, version):
        data = self._dataMoudleOfStartingCrash()
        data['content']['post']['en_us']['title'] = 'OPSVN_{}({}) - {} Loading Timeout / Strating Crash [No dumper.exe]'.format(
            self.versionInfo.get('OPSVN').get('version'), uid, version
        )
        reportDateTime = 'Report Datetime: {}'.format(str(datetime.datetime.now()))
        equipment = 'Test Equipment: {}'.format(equipment)
        userData = [equipment, reportDateTime]
        data = self.coloring(data, userData, 2)
        return data

    def coloring(self, data, userData, fieldAmount):
        for index, eachDataDict in enumerate(data['content']['post']['en_us']['content']):
            for key, value in eachDataDict[0].items():
                if key != 'tag' and index < fieldAmount:
                    eachDataDict[0][key] = userData[index]
        return data

    def sendMsg(self, data=None):
        response = requests.post(self.url, json=data)
        self.logObj.logHandler().info('FEISHU information sent successfully.')
        if response.json().get('StatusCode') != 0:
            self.logObj.logHandler().error('The FEISHU message failed to be sent due to the following reasons: {}'.format(response.json()))
            raise ValueError('发送失败 -> {}'.format(response.json()))

    def _dataModuleOfNormalBody(self) -> str:
        '''
            0. Test Equipment
            1. FPS
            2. VRAM
            3. Game Play
            4. Defect Behavior
            5. Status
            6. Report DateTime
            7. Resolution
        '''
        dataModuleDict = {
            'msg_type': 'post',
            'content': {                
                'post': {
                    'en_us': {
                        'title': None,
                        'content': [
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': '------------------------------------------------------------'}],
                            [{'tag': 'text', 'text': 'OPSVN GIT PROJECT: '}, {'tag': 'a', 'text': 'http://www.github.com/', 'href': 'http://www.github.com/'}],
                            [{'tag': 'text', 'text': 'OPSVN API: '}, {'tag': 'a', 'text': 'http://127.0.0.1/', 'href': 'http://127.0.0.1/'}],
                        ]
                    }}}
        }
        return dataModuleDict

    def _dataMoudleOfAbnormalBody(self):
        pass

    def _dataMoudleOfStartingCrash(self) -> str:
        '''
            0. Test Equipment
            1. Report DateTime
        '''
        dataModuleDict = {
            'msg_type': 'post',
            'content': {                
                'post': {
                    'en_us': {
                        'title': None,
                        'content': [
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': None}],
                            [{'tag': 'text', 'text': '------------------------------------------------------------'}],
                            [{'tag': 'text', 'text': 'OPSVN GIT PROJECT: '}, {'tag': 'a', 'text': 'http://www.github.com/', 'href': 'http://www.github.com/'}],
                            [{'tag': 'text', 'text': 'OPSVN API: '}, {'tag': 'a', 'text': 'http://127.0.0.1/', 'href': 'http://127.0.0.1/'}],
                        ]
                    }}}
        }
        return dataModuleDict

if __name__ == '__main__':
    obj = FEISHU()
    obj.sendMsg()
