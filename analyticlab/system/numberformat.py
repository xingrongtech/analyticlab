# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 06:17:01 2018

@author: xingrongtech
"""

from math import log10, floor

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
    
def fstr(num, digit):
    if digit > 0:
        return ('%.' + str(digit) + 'f') % f(num, digit)
    else:
        return '%d' % f(num, digit)

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
            zero_minus = -1 - floor(log10(cut * 1.00000000001))  #计算要减去的无效位数0
            digit_behind += zero_minus  #重置小数点后位数
            ''' 按应有的小数点后位数，若生成的有效数值越界（如0.099973，保留3位有效数字，
            则理论上小数点后保留4位，而实际生成的小数越界成为0.10000，故此时小数点后应少
            一位，即0.1000）
            判断越界的方法：以0.099973为例，保留小数点后4位，则取10**(-4)的一半，即
            10**(-4)/2=0.00005，无效位数0有1个，故理论上生成的数值不应超过10**(-1)=0.1，
            而0.099973+0.00005=0.100023>0.1，故越界。'''
            if usign + 10**(-digit_behind)/2 > 10**(-zero_minus):
                digit_behind -= 1
    if (digit_behind < 0):
        digit_behind = 0
    return digit_behind

def getBound(num):
    '''获得数字的科学记数法指数'''
    return abs(floor(log10(abs(num._Num__value * 1.00000000001))))

def dec2Latex(dec, noBracket=False):
    if type(dec) == int:
        expr = str(dec)
    else:
        expr = '%g' % dec
        if len(expr) >= 16:
            expr = '%.3g' % dec
        if 'e' in expr:
            e_list = expr.split('e')
            expr = r'%s \times 10^{%s}' % (e_list[0], e_list[1].replace('+', ''))
    if (not noBracket) and dec < 0:
        expr = '(%s)' % expr
    return expr
