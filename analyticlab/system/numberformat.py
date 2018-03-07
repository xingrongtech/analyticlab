# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 06:17:01 2018

@author: xingrongtech
"""

from math import log10, floor, fabs

def f(num, digit):
    '''实现四舍六入五成双'''
    numConverted = num * 10**(digit+1)
    numInt = int(numConverted)
    unit = numInt % 10
    if unit <= 4:  #四舍
        numInt = (numInt - unit) // 10
    elif unit >= 6:  #六入
        numInt = (numInt - unit) // 10 + 1
    elif unit == 5:  #五成双
        if numConverted - numInt > 0:  #若保留位后面有剩余数字，则直接进一位
            numInt = (numInt - unit) // 10 + 1
        else:
            decade = (numInt - unit) % 100 // 10
            if decade % 2 == 0:  #偶数保留
                numInt = (numInt - unit) // 10
            else:  #奇数进一
                numInt = (numInt - unit) // 10 + 1
    return numInt * 10**(-digit)

def cutInt(number):
    '''去除数字的整数部分'''
    return number - int(number);

def getDigitFront(usign):
    '''获得小数点前的数字位数'''
    usign = int(usign)
    if usign == 0:  #重置小数点前位数
        return 0
    else:
        return int(log10(usign * 1.00000000001)) + 1
    
def getDigitBehind(usign, digit_valid, digit_front):
    '''根据已知的有效数字位数和小数点前位数，得到小数点后的应有位数'''
    digit_behind = digit_valid - digit_front
    if digit_front == 0:
        cut = cutInt(usign)
        if (cut > 0):
            zero_minus = floor(log10(cut * 1.00000000001)) + 1  #计算要减去的无效位数0
            digit_behind -= zero_minus  #重置小数点后位数
    if (digit_behind < 0):
        digit_behind = 0
    return digit_behind

def getBound(num):
    '''获得数字的科学记数法指数'''
    return fabs(floor(log10(fabs(num._Num__num * 1.00000000001))))

def dec2Latex(dec):
    decStr = '%g' % dec
    if len(decStr) >= 16:
        bound = floor(log10(fabs(dec * 1.00000000001)))
        if dec >= 1:
            return '%.2f' % dec
        else:
            return ('%.' + (bound+2) + 'f') % dec
    else:
        return decStr