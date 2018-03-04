# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:25:11 2018

@author: xingrongtech
"""
from analyticlab.system.exceptions import tooMuchDataForTestException, tooLessDataForTestException

table_C = [1.13, 1.64, 2.06, 2.33, 2.53, 2.70, 2.85, 2.97]
table_v = [0.9, 1.8, 2.7, 3.6, 4.5, 5.3, 6.0, 6.8]

def C(n):
    try:
        return table_C[n-2]
    except:
        if n > 9:
            raise tooMuchDataForTestException('贝塞尔公式法不支持超过9组数据')
        elif n < 2:
            raise tooLessDataForTestException('贝塞尔公式法')

def v(n):
    try:
        return table_v[n-2]
    except:
        if n > 9:
            raise tooMuchDataForTestException('贝塞尔公式法不支持超过9组数据')
        elif n < 2:
            raise tooLessDataForTestException('贝塞尔公式法')