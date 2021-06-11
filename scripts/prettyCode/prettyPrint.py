#!/usr/bin/python
# -*- encoding: utf-8 -*-
'''
@Time    :   2021/06/10 11:23:41
@Author  :   Camille
@Version :   1.0
'''


import time
import datetime


class PrettyPrint():
    def __init__(self) -> None:
        self.colorDict = {
            'default': '\033[',
            'red': '\033[31;',
            'yellow': '\033[33;',
        }

    @staticmethod
    def pTime():
        dt = datetime.datetime.now()
        return dt

    def pPrint(self, text, level='INFO', color=None, bold=False):
        """2021-06-10 11:39:31.317902 - INFO - hello

        Args:
            text (str): 需要输出的字符串
            level (str, optional): 优先级. Defaults to 'INFO'.
            color (str, optional): 字体颜色. Defaults to None.
            bold (bool, optional): 是否加粗字体. Defaults to False.
        """
        color = self.colorDict.get(color, '\033[')
        if level == 'ERROR':
            color = self.colorDict.get('red')

        now = PrettyPrint.pTime()
        if bold:
            # 加粗
            print('{} - {} - {}1m{}'.format(now, level, color, text))
        else:
            print('{} - {} - {}0m{}'.format(now, level, color, text))


if __name__ == '__main__':
    obj = PrettyPrint()
    obj.pPrint('hello')