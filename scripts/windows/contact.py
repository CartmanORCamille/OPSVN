#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/07/16 15:42:42
@Author  :   Camille
@Version :   1.0
'''


import requests
import json


class FEISHU():
    def __init__(self) -> None:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.url = json.load(f).get('Contact').get('FEISHU')

    def dataModule(self) -> str:
        dataModuleDict = {
            'msg_type': 'post',
            'content': {                
                'post': {
                    'en_us': {
                        'title': None,
                        'content': [
                            # [{'tag': 'text','text': 'case API: '},{'tag': 'a', 'text': 'http://127.0.0.1/', 'href': 'http://127.0.0.1/'}],
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

    def drawTheMsg(self, uid, version, equipment, FPS, VRAM, GP, DB):
        # 'ALPHA_16248491144391608', '941542', 'Test Equipment: 610', 'FPS: 22', 'VRAM: 2200', 'Game Play: stand', 'Defect Behavior: crash'
        data = self.dataModule()
        data['content']['post']['en_us']['title'] = 'OPSVN_ALPHA({}) - {} TEST REPORT [NOT FINAL]'.format(
            uid, version)

        equipment = 'Test Equipment: {}'.format(equipment)
        FPS = 'FPS: {}'.format(FPS)
        VRAM = 'VRAM: {}'.format(VRAM)
        GP = 'Game Play: {}'.format(GP)
        DB = 'Defect Behavior: {}'.format(DB)
        userData = [equipment, FPS, VRAM, GP, DB]
        
        for index, eachDataDict in enumerate(data['content']['post']['en_us']['content']):
            for key, value in eachDataDict[0].items():
                if key != 'tag' and index < 5:
                    eachDataDict[0][key] = userData[index]

        return data

    def sendMsg(self, data=None):
        response = requests.post(self.url, json=data)
        if response.json().get('StatusCode') != 0:
            raise ValueError('发送失败 -> {}'.format(response.json()))


if __name__ == '__main__':
    obj = FEISHU()
    obj.sendMsg()
