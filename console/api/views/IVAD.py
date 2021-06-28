#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/22 17:42:18
@Author  :   Camille
@Version :   1.0
'''


import time
import datetime
import json
from django.http import response, StreamingHttpResponse
from rest_framework import request
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status


class IVAD(APIView):
    renderer_classes = [JSONRenderer, ]
    def get(self, request, *args, **kwargs):
        
        return Response({'msg': 'hi'})

    def post(self, request, *args, **kwargs):
        caseDataDict = request.data

        # 生成测试案例编号
        uid = 'ALPHA_{}'.format(str(time.time()).replace('.', ''))
        fileName = 'api\\data\\caches\\case_{}.json'.format(uid)

        cleanCaseDataDict = {
            'uid': uid,
            'SVN': {
                "versionRangeForVersionNumber": None,
                "versionRangeForDate": None,
            },
            'GamePlay': caseDataDict.get('gamePlay'),
            'DefectBehavior': caseDataDict.get('defectBehavior'),
            'Path': {
                "Jx3BVTNeedCheck": caseDataDict.get('needCheckPath'),
                "Jx3BVTWorkPath": caseDataDict.get('binPath'),
                "Jx3Remake": "JX3ClientX64.exe",
            }
        }
        
        versionRangeList = caseDataDict.get('versionRange')
        dateRangeList = caseDataDict.get('dateRange')

        # versionRange校验
        for version in versionRangeList:
            if not version or not version.isdigit():
                # version缺失 -> version范围不能用
                cleanCaseDataDict['SVN']['versionRangeForVersionNumber'] = 'E599: Abnormal data information.'
                
                # 版本范围不能用 -> 检查时间范围
                for date in dateRangeList:
                    if not date:
                        # 缺少时间范围
                        cleanCaseDataDict['SVN']['versionRangeForDate'] = 'E599: Abnormal data information.'
                        return Response({
                            'status': 599,
                            'msg': 'E599: 不符合 OPSVN CASE 运行标准。',
                            'dataOfResult': cleanCaseDataDict,
                        })
                    else:
                        cleanCaseDataDict['SVN']['versionRangeForDate'] = dateRangeList
                break
            else:
                cleanCaseDataDict['SVN']['versionRangeForVersionNumber'] = versionRangeList
                cleanCaseDataDict['SVN']['versionRangeForDate'] = 'E598: When using the version range, the time range will not be saved.'

        # 写入文件
        with open(fileName, 'w', encoding='utf-8') as f:
            json.dump(cleanCaseDataDict, f, indent=4)

        downloadUrl = '/api/download/{}'.format(uid)
        return Response({
            'status': 200,
            'msg': '即刻执行你的测试需求！',
            'dataOfResult': cleanCaseDataDict,
            'downloadUrl': downloadUrl,
        })


class DownloadCase(APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, uid, *args, **kwargs):
        if not uid:
            return Response({
                'status': 598,
                'msg': '缺失ID，请在 CASE 生成页面重新提交'
            })

        fileName = 'case_{}.json'.format(uid)
        with open('api\\data\\caches\\{}'.format(fileName)) as f:
            data = f.read()
        
        responseData = StreamingHttpResponse(data)

        responseData['Content-Type'] = 'application/octet-stream'
        responseData['Content-Disposition'] = 'attachment;filename={}'.format(fileName)

        return responseData