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


class FEISHU():
    def __init__(self) -> None:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.url = json.load(f).get('Contact').get('FEISHU')
        with open(r'.\config\version.json') as f:
            self.versionInfo = json.load(f)

    def dataModuleOfNormalBody(self) -> str:
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

    def dataMoudleOfAbnormalBody(self):
        pass

    def drawTheNormalMsg(self, uid, version, equipment, FPS, VRAM, gamePlay, defectBehavior, status, reportDateTime, resolution, isFinal=False):
        # 'ALPHA_16248491144391608', '941542', 'Test Equipment: 610', 'FPS: 22', 'VRAM: 2200', 'Game Play: stand', 'Defect Behavior: crash'
        if not isFinal:
            dataResultIdentifier = 'NOT FINAL'
        else:
            dataResultIdentifier = 'FINAL'
        normalFieldAmount = 8
        OPSVNVersion = self.versionInfo.get('OPSVN').get('version')
        data = self.dataModuleOfNormalBody()
        data['content']['post']['en_us']['title'] = 'OPSVN_{}({}) - {} TEST REPORT [{}]'.format(
            OPSVNVersion, uid, version, dataResultIdentifier)

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
        
        for index, eachDataDict in enumerate(data['content']['post']['en_us']['content']):
            for key, value in eachDataDict[0].items():
                if key != 'tag' and index < normalFieldAmount:
                    eachDataDict[0][key] = userData[index]

        return data

    def sendMsg(self, data=None):
        response = requests.post(self.url, json=data)
        if response.json().get('StatusCode') != 0:
            raise ValueError('发送失败 -> {}'.format(response.json()))


if __name__ == '__main__':
    obj = FEISHU()
    obj.sendMsg()
