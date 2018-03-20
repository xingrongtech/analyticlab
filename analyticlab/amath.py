# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 08:34:23 2018

@author:xingrongtech
"""

import math, sympy
from .system import numberformat as nf

def sqrt(obj, root=2):
    '''求根计算
    【参数说明】
    1.obj：对谁求根。obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.root（可选，int）：根指数。默认为2，即默认求的是平方根。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    if type(obj) == int or type(obj) == float:
        return math.sqrt(obj)
    objType = str(type(obj))
    if objType == "<class 'analyticlab.num.Num'>":
        return obj.__pow__(1/root)
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        return obj._NumItem__newInstance([sqrt(n) for n in obj._NumItem__arr], dv=obj._NumItem__gd_valid)
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        symText = sNum = calText = symBrac = calBrac = None
        #开方运算不考虑prior
        if obj._LSym__genSym:
            if root == 2:
                symText = r'\sqrt{%s}' % (obj._LSym__symText)
            else:
                symText = r'\sqrt[%d]{%s}' % (root, obj._LSym__symText)
            symBrac = obj._LSym__symBrac
        if obj._LSym__genCal:
            sNum = obj._LSym__sNum ** (1/root)
            if root == 2:
                calText = r'\sqrt{%s}' % (obj._LSym__calText)
            else:
                calText = r'\sqrt[%d]{%s}' % (root, obj._LSym__calText)
            calBrac = obj._LSym__calBrac
        return obj._LSym__newInstance(symText, sNum, calText, symBrac, calBrac, 4, 4)
    elif objType == "<class 'analyticlab.lsymitem.LSymItem'>":
        new = obj._LSymItem__newInstance()
        if type(obj._LSymItem__lsyms) == list:
            new._LSymItem__lsyms = [sqrt(ni, root) for ni in obj._LSymItem__lsyms]
        else:
            new._LSymItem__lsyms = {}
            for ki in obj._LSymItem__lsyms.keys():
                new._LSymItem__lsyms[ki] = sqrt(obj._LSymItem__lsyms[ki], root)
        if obj._LSymItem__sepSymCalc:
            new._LSymItem__sepSym = sqrt(obj._LSymItem__sepSym, root)
        return new
    elif objType == "<class 'analyticlab.const.Const'>":
        if root == 2:
            return obj._Const__newInstance(r'\sqrt{%s}' % obj._Const__symText, math.sqrt(obj.value()), 4, obj._Const__brac)
        else:
            return obj._Const__newInstance(r'\sqrt[%d]{%s}' % (root, obj._Const__symText), obj.value()*(1/root), 4, obj._Const__brac)
    elif objType == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or objType == "<class 'analyticlab.uncertainty.measure.Measure'>":
        if root == 2:
            return obj._Uncertainty__newInstance(sympy.sqrt(obj._Uncertainty__symbol), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
        else:
            return obj._Uncertainty__newInstance(obj._Uncertainty__symbol**sympy.Rational(1,root), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
    
def ln(obj):
    '''ln对数计算
    【参数说明】
    obj：对谁求ln对数，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    if type(obj) == int or type(obj) == float:
        return math.log(obj)
    objType = str(type(obj))
    if objType == "<class 'analyticlab.num.Num'>":
        obj._Num__resetDigit()
        n = obj._Num__newInstance()
        n._Num__num = math.log(obj._Num__num)
        #数值的有效数字位数为相应指数的小数点后位数
        n._Num__d_behind = obj._Num__d_valid
        n._Num__d_front = nf.getDigitFront(math.fabs(n._Num__num))
        n._Num__d_valid = n._Num__d_front + n._Num__d_behind
        return n
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        return obj._NumItem__newInstance([ln(n) for n in obj._NumItem__arr])
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        o_symBrac = obj._LSym__symBrac
        o_symText = obj._LSym__symText
        o_calBrac = obj._LSym__calBrac
        o_calText = obj._LSym__calText
        symText = sNum = calText = symBrac = calBrac = None
        if 5 >= obj._LSym__symPrior:
            if obj._LSym__genSym:
                o_symBrac += 1
                o_symText = obj._LSym__bracket(o_symBrac) % o_symText
        if 5 >= obj._LSym__calPrior:
            if obj._LSym__genCal:
                o_calBrac += 1
                o_calText = obj._LSym__bracket(o_calBrac) % o_calText  
        if obj._LSym__genSym:
            symText = r'\ln{%s}' % (o_symText)
            symBrac = o_symBrac
        if obj._LSym__genCal:
            sNum = ln(obj._LSym__sNum)
            calText = r'\ln{%s}' % (o_calText)
            calBrac = o_calBrac
        return obj._LSym__newInstance(symText, sNum, calText, symBrac, calBrac, 5, 5)
    elif objType == "<class 'analyticlab.lsymitem.LSymItem'>":
        new = obj._LSymItem__newInstance()
        if type(obj._LSymItem__lsyms) == list:
            new._LSymItem__lsyms = [ln(ni) for ni in obj._LSymItem__lsyms]
        else:
            new._LSymItem__lsyms = {}
            for ki in obj._LSymItem__lsyms.keys():
                new._LSymItem__lsyms[ki] = ln(obj._LSymItem__lsyms[ki])
        if obj._LSymItem__sepSymCalc:
            new._LSymItem__sepSym = ln(obj._LSymItem__sepSym)
        return new
    elif objType == "<class 'analyticlab.const.Const'>":
        obrac = obj._Const__brac
        osymText = obj._Const__symText
        if 5 >= obj._Const__prior:
            obrac += 1
            osymText = obj._Const__bracket(obrac) % osymText
        return obj._Const__newInstance(r'\ln %s' % osymText, math.log(obj.value()), 5, obrac)
    elif objType == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or objType == "<class 'analyticlab.uncertainty.measure.Measure'>":
        return obj._Uncertainty__newInstance(sympy.ln(obj._Uncertainty__symbol), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
    
def lg(obj):
    '''lg对数计算
    【参数说明】
    obj：对谁求lg对数，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    if type(obj) == int or type(obj) == float:
        return math.log10(obj)
    objType = str(type(obj))
    if objType == "<class 'analyticlab.num.Num'>":
        obj._Num__resetDigit()
        n = obj._Num__newInstance()
        n._Num__num = math.log10(obj._Num__num)
        #数值的有效数字位数为相应指数的小数点后位数
        n._Num__d_behind = obj._Num__d_valid
        n._Num__d_front = nf.getDigitFront(math.fabs(n._Num__num))
        n._Num__d_valid = n._Num__d_front + n._Num__d_behind
        return n
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        return obj._NumItem__newInstance([lg(n) for n in obj._NumItem__arr])
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        o_symBrac = obj._LSym__symBrac
        o_symText = obj._LSym__symText
        o_calBrac = obj._LSym__calBrac
        o_calText = obj._LSym__calText
        symText = sNum = calText = symBrac = calBrac = None
        if 5 >= obj._LSym__symPrior:
            if obj._LSym__genSym:
                o_symBrac += 1
                o_symText = obj._LSym__bracket(o_symBrac) % o_symText
        if 5 >= obj._LSym__calPrior:
            if obj._LSym__genCal:
                o_calBrac += 1
                o_calText = obj._LSym__bracket(o_calBrac) % o_calText  
        if obj._LSym__genSym:
            symText = r'\lg{%s}' % (o_symText)
            symBrac = o_symBrac
        if obj._LSym__genCal:
            sNum = lg(obj._LSym__sNum)
            calText = r'\lg{%s}' % (o_calText)
            calBrac = o_calBrac
        return obj._LSym__newInstance(symText, sNum, calText, symBrac, calBrac, 5, 5)
    elif objType == "<class 'analyticlab.lsymitem.LSymItem'>":
        new = obj._LSymItem__newInstance()
        if type(obj._LSymItem__lsyms) == list:
            new._LSymItem__lsyms = [lg(ni) for ni in obj._LSymItem__lsyms]
        else:
            new._LSymItem__lsyms = {}
            for ki in obj._LSymItem__lsyms.keys():
                new._LSymItem__lsyms[ki] = lg(obj._LSymItem__lsyms[ki])
        if obj._LSymItem__sepSymCalc:
            new._LSymItem__sepSym = lg(obj._LSymItem__sepSym)
        return new
    elif objType == "<class 'analyticlab.const.Const'>":
        obrac = obj._Const__brac
        osymText = obj._Const__symText
        if 5 >= obj._Const__prior:
            obrac += 1
            osymText = obj._Const__bracket(obrac) % osymText
        return obj._Const__innerCreate(r'\lg{%s}' % osymText, math.log10(n.value()), 5, obrac)
    elif objType == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or objType == "<class 'analyticlab.uncertainty.measure.Measure'>":
        return obj._Uncertainty__newInstance(sympy.log(obj._Uncertainty__symbol, 10), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
    
def __triFunc(obj, fun, selfFun, funExpr, mode):
    if type(obj) == int or type(obj) == float:
        return fun(obj, mode)
    objType = str(type(obj))
    if objType == "<class 'analyticlab.num.Num'>":
        obj._Num__resetDigit()
        n = obj._Num__newInstance()
        n._Num__num = fun(obj._Num__num, mode)
        n._Num__d_valid = obj._Num__d_valid
        usign = math.fabs(n._Num__num)
        n._Num__d_front = nf.getDigitFront(usign)
        n._Num__d_behind = nf.getDigitBehind(usign, n._Num__d_valid, n._Num__d_front)
        return n
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        return obj._NumItem__newInstance([selfFun(n, mode) for n in obj._NumItem__arr])
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        o_symBrac = obj._LSym__symBrac
        o_symText = obj._LSym__symText
        o_calBrac = obj._LSym__calBrac
        o_calText = obj._LSym__calText
        symText = sNum = calText = symBrac = calBrac = None
        if 5 >= obj._LSym__symPrior:
            if obj._LSym__genSym:
                o_symBrac += 1
                o_symText = obj._LSym__bracket(o_symBrac) % o_symText
        if 5 >= obj._LSym__calPrior:
            if obj._LSym__genCal:
                o_calBrac += 1
                o_calText = obj._LSym__bracket(o_calBrac) % o_calText  
        if obj._LSym__genSym:
            symText = '%s{%s}' % (funExpr, o_symText)
            symBrac = o_symBrac
        if obj._LSym__genCal:
            sNum = selfFun(obj._LSym__sNum)
            calText = '%s{%s}' % (funExpr, o_calText)
            calBrac = o_calBrac
        return obj._LSym__newInstance(symText, sNum, calText, symBrac, calBrac, 5, 5)
    elif objType == "<class 'analyticlab.lsymitem.LSymItem'>":
        new = obj._LSymItem__newInstance()
        if type(obj._LSymItem__lsyms) == list:
            new._LSymItem__lsyms = [selfFun(ni) for ni in obj._LSymItem__lsyms]
        else:
            new._LSymItem__lsyms = {}
            for ki in obj._LSymItem__lsyms.keys():
                new._LSymItem__lsyms[ki] = selfFun(obj._LSymItem__lsyms[ki])
        if obj._LSymItem__sepSymCalc:
            new._LSymItem__sepSym = selfFun(obj._LSymItem__sepSym)
        return new
    elif objType == "<class 'analyticlab.const.Const'>":
        obrac = obj._Const__brac
        osymText = obj._Const__symText
        if 5 >= obj._Const__prior:
            obrac += 1
            osymText = obj._Const__bracket(obrac) % osymText
        return obj._Const__newInstance('%s%s' % (funExpr, osymText), fun(obj.value()), 5, obrac)

def __trans(number, mode):
    if mode == 'degree':
        return math.pi*(number/180)
    elif mode == 'radius':
        return number
    
def __rtrans(number, mode):
    if mode == 'degree':
        return 180*number/math.pi
    elif mode == 'radius':
        return number
    
def __m_sin(number, mode):
    return math.sin(__trans(number, mode))

def __m_cos(number, mode):
    return math.cos(__trans(number, mode))

def __m_tan(number, mode):
    return math.tan(__trans(number, mode))
    
def __m_csc(number, mode):
    return 1 / math.sin(__trans(number, mode))

def __m_sec(number, mode):
    return 1 / math.cos(__trans(number, mode))

def __m_cot(number, mode):
    return 1 / math.tan(__trans(number, mode))

def __m_asin(number, mode):
    return __rtrans(math.asin(number), mode)

def __m_acos(number, mode):
    return __rtrans(math.acos(number), mode)

def __m_atan(number, mode):
    return __rtrans(math.atan(number), mode)

def __m_acsc(number, mode):
    return __rtrans(math.asin(1/number, mode))

def __m_asec(number, mode):
    return __rtrans(math.acos(1/number, mode))

def __m_acot(number, mode):
    return __rtrans(math.atan(1/number, mode))
    
def sin(obj, mode='degree'):
    '''正弦函数计算
    【参数说明】
    1.obj：求谁的正弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_sin, sin, r'\sin', mode)

def cos(obj, mode='degree'):
    '''余弦函数计算
    【参数说明】
    1.obj：求谁的余弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_cos, cos, r'\cos', mode)

def tan(obj, mode='degree'):
    '''正切函数计算
    【参数说明】
    1.obj：求谁的正切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_tan, tan, r'\tan', mode)

def csc(obj, mode='degree'):
    '''余割函数计算
    【参数说明】
    1.obj：求谁的余割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_csc, csc, r'\csc', mode)

def sec(obj, mode='degree'):
    '''正割函数计算
    【参数说明】
    1.obj：求谁的正割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_sec, sec, r'\sec', mode)

def cot(obj, mode='degree'):
    '''余切函数计算
    【参数说明】
    1.obj：求谁的余切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_cot, cot, r'\cot', mode)

def arcsin(obj, mode='degree'):
    '''反正弦函数计算
    【参数说明】
    1.obj：求谁的反正弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_asin, arcsin, r'\arcsin', mode)

def arccos(obj, mode='degree'):
    '''反余弦函数计算
    【参数说明】
    1.obj：求谁的反余弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_acos, arccos, r'\arccos', mode)

def arctan(obj, mode='degree'):
    '''反正切函数计算
    【参数说明】
    1.obj：求谁的反正切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_atan, arctan, r'\arctan', mode)

def arccsc(obj, mode='degree'):
    '''反余割函数计算
    【参数说明】
    1.obj：求谁的反余割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_acsc, arccsc, r'\operatorname{arccsc}', mode)

def arcsec(obj, mode='degree'):
    '''反正割函数计算
    【参数说明】
    1.obj：求谁的反正割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_asec, arcsec, r'\operatorname{arcsec}', mode)

def arccot(obj, mode='degree'):
    '''反余切函数计算
    【参数说明】
    1.obj：求谁的反余切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode：角度计算还是弧度计算，mode='degree'时为角度计算，mode='radius'时为弧度计算。默认mode='degree'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_acot, arccot, r'\operatorname{arccot}', mode)
