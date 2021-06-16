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
            'default': '0m',
            'red': '31;40m',
            'yellow': '33;40m',
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
        if level == 'ERROR':
            color = self.colorDict.get('red')
        elif level == 'WARING':
            color = self.colorDict.get('yellow')
        elif level == 'INFO':
            color = self.colorDict.get('default')
        else:
            raise AttributeError('WRONG ATTRIBUTE FOR LEVEL.')

        now = PrettyPrint.pTime()
        if bold:
            # 加粗
            print('\033[1;{}{} - {} - {}\033[0m'.format(color, now, level, text))
        else:     
            print('\033[0;{}{} - {} - {}\033[0m'.format(color, now, level, text))


if __name__ == '__main__':
    PRETTYPRINT = PrettyPrint()
    PRETTYPRINT.pPrint('text')