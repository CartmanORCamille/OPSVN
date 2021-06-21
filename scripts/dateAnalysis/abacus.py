#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/11 11:37:46
@Author  :   Camille
@Version :   1.0
'''


import random
import json
import os
from win32api import RegUnLoadKey
from scripts.windows.windows import BaseWindowsControl, ProcessMonitoring
from scripts.prettyCode.prettyPrint import PrettyPrint


PRETTYPRINT = PrettyPrint()


class DataAbacus():

    def __init__(self) -> None:
        with open(r'.\config\config.json', 'r', encoding='utf-8') as f:
            self.abacusConfig = json.load(f).get('AbacusDictionary')

    def testResult():
        result = random.randint(0, 1)
        return result

