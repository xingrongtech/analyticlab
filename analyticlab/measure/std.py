# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:18:22 2018

@author: xingrongtech
"""

from ..system.statformat import statFormat, getMaxDeltaDigit
from ..lookup.RangeTable import C as rC

def Bessel(item, remainOneMoreDigit=False):
    '''贝塞尔公式法计算标准偏差
    【参数说明】
    1.item：用于计算标准偏差的样本数据。
    2.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    Num：标准偏差数值。'''
    mean = item.mean()
    dsum = sum([(ni._Num__num - mean._Num__num)**2 for ni in item._NumItem__arr])
    s = (dsum / (len(item._NumItem__arr) - 1))**0.5
    result = statFormat(getMaxDeltaDigit(item, mean), s)
    result._Num__q = item._NumItem__q
    if remainOneMoreDigit:
        result.remainOneMoreDigit()
    return result

def Range(item, remainOneMoreDigit=False):
    '''极差法计算标准偏差
    【参数说明】
    1.item：用于计算标准偏差的样本数据。
    2.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    Num：标准偏差数值。'''
    R = max(item._NumItem__arr) - min(item._NumItem__arr)
    C = rC(len(item._NumItem__arr))
    result = R/C
    if remainOneMoreDigit:
        result.remainOneMoreDigit()
    return result

def CollegePhysics(item, remainOneMoreDigit=False):
    '''大学物理实验中的标准偏差计算
    【参数说明】
    1.item：用于计算标准偏差的样本数据。
    2.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    Num：标准偏差数值。'''
    return Bessel(item, remainOneMoreDigit)
