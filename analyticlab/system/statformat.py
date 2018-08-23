# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 11:50:19 2018

@author: wzv100
"""

from math import fabs
from ..num import Num
from .numberformat import getDigitFront, getDigitBehind

def statFormat(gd_valid, number, isRelative=False):
    '''统计结果格式化'''
    s = Num(None)
    s._Num__value = number
    usign = fabs(number)
    s._Num__d_valid = gd_valid
    s._Num__d_front = getDigitFront(number)
    s._Num__d_behind = getDigitBehind(usign, s._Num__d_valid, s._Num__d_front)
    s.setIsRelative(isRelative)
    return s.fix()

def getMaxDeltaDigit(item, mean):
    '''获得与均值差值最大的数值的有效数字位数'''
    dmax = max(item._NumItem__arr) - mean
    dmin = mean - min(item._NumItem__arr)
    d = max(dmax, dmin)
    d._Num__resetDigit()
    return d._Num__d_valid
