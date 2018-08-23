# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 08:34:23 2018

@author:xingrongtech
"""

import math, sympy
from quantities.quantity import Quantity
from .system import numberformat as nf
from .system.unit_open import openUnit, closeUnit
from .system.format_units import deg, rad

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
        return obj._NumItem__newInstance([sqrt(n) for n in obj._NumItem__arr], obj._NumItem__q**(1/root), dv=obj._NumItem__gd_valid)
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        symText = sNum = calText = symBrac = calBrac = None
        ### 括号与文本预处理 ###
        ### 合成表达式 ###
        #开方运算不考虑prior
        if obj._LSym__genSym:
            if root == 2:
                symText = r'\sqrt{%s}' % (obj._LSym__symText)
            else:
                symText = r'\sqrt[%d]{%s}' % (root, obj._LSym__symText)
            symBrac = obj._LSym__symBrac
        if obj._LSym__genCal:
            sNum = obj._LSym__sNum**(1/root)
            if root == 2:
                calText = r'\sqrt{%s}' % (obj._LSym__calText)
            else:
                calText = r'\sqrt[%d]{%s}' % (root, obj._LSym__calText)
            calBrac = obj._LSym__calBrac
        return obj._LSym__newInstance(sNum, symText, calText, symBrac, calBrac, 5, 5, False, obj._LSym__s_decR)
    elif objType == "<class 'analyticlab.lsymitem.LSymItem'>":
        closeUnit()
        new = obj._LSymItem__newInstance()
        if type(obj._LSymItem__lsyms) == list:
            new._LSymItem__lsyms = [sqrt(ni, root) for ni in obj._LSymItem__lsyms]
        else:
            new._LSymItem__lsyms = {}
            for ki in obj._LSymItem__lsyms.keys():
                new._LSymItem__lsyms[ki] = sqrt(obj._LSymItem__lsyms[ki], root)
        if obj._LSymItem__sepSymCalc:
            new._LSymItem__sepSym = sqrt(obj._LSymItem__sepSym, root)
        new._LSymItem__q = obj._LSymItem__q**(1/root)
        new._LSymItem__qUpdate()
        openUnit()
        return new
    elif objType == "<class 'analyticlab.const.Const'>":
        ### 括号与文本预处理 ###
        ### 合成表达式 ###
        if root == 2:
            symText = r'\sqrt{%s}' % obj._Const__symText
            calText = r'\sqrt{%s}' % obj._Const__calText
            return obj._Const__newInstance(symText, calText, obj._Const__symBrac, obj._Const__calBrac, 5, 5, math.sqrt(obj.value()), obj._Const__q**(1/2), False, obj._Const__s_decR, False, obj._Const__c_decR)
        else:
            symText = r'\sqrt[%d]{%s}' % (root, obj._Const__symText)
            calText = r'\sqrt[%d]{%s}' % (root, obj._Const__calText)
            return obj._Const__newInstance(symText, calText, obj._Const__symBrac, obj._Const__calBrac, 5, 5, obj.value()*(1/root), obj._Const__q**(1/root), False, obj._Const__s_decR, False, obj._Const__c_decR)
    elif objType == "<class 'analyticlab.measure.measure.Measure'>" or objType == "<class 'analyticlab.measure.basemeasure.BaseMeasure'>":
        if root == 2:
            return obj._Measure__newInstance(sympy.sqrt(obj._Uncertainty__symbol), obj._Measure__vl**(1/root), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
        else:
            return obj._Measure__newInstance(obj._Uncertainty__symbol**sympy.Rational(1,root), obj._Measure__vl**(1/root), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
    
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
        n._Num__value = math.log(obj._Num__value)
        #数值的有效数字位数为相应指数的小数点后位数
        n._Num__d_behind = obj._Num__d_valid
        n._Num__d_front = nf.getDigitFront(abs(n._Num__value))
        n._Num__d_valid = n._Num__d_front + n._Num__d_behind
        return n
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        return obj._NumItem__newInstance([ln(n) for n in obj._NumItem__arr])
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        ### 括号与文本预处理 ###
        o_symBrac = obj._LSym__symBrac
        o_symText = obj._LSym__symText
        o_calBrac = obj._LSym__calBrac
        o_calText = obj._LSym__calText
        symText = sNum = calText = symBrac = calBrac = None
        if 4 >= obj._LSym__symPrior:
            if obj._LSym__genSym:
                o_symBrac += 1
                o_symText = obj._LSym__bracket(o_symBrac) % o_symText
        if 4 >= obj._LSym__calPrior:
            if obj._LSym__genCal:
                o_calBrac += 1
                o_calText = obj._LSym__bracket(o_calBrac) % o_calText  
        ### 合成表达式 ###
        if obj._LSym__genSym:
            symText = r'\ln{%s}' % (o_symText)
            symBrac = o_symBrac
        if obj._LSym__genCal:
            sNum = ln(obj._LSym__sNum)
            calText = r'\ln{%s}' % (o_calText)
            calBrac = o_calBrac
        return obj._LSym__newInstance(sNum, symText, calText, symBrac, calBrac, 4, 4, False, obj._LSym__s_decR)
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
        ### 括号与文本预处理 ###
        o_symBrac = obj._Const__symBrac
        o_symText = obj._Const__symText
        o_calBrac = obj._Const__calBrac
        o_calText = obj._Const__calText
        if 4 >= obj._Const__symPrior:
            o_symBrac += 1
            o_symText = obj._Const__bracket(o_symBrac) % o_symText
        if 4 >= obj._Const__calPrior:
            o_calBrac += 1
            o_calText = obj._Const__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = r'\ln %s' % o_symText
        calText = r'\ln %s' % o_calText
        return obj._Const__newInstance(symText, calText, o_symBrac, o_calBrac, 4, 4, math.log(obj.value()), 1, False, obj._Const__s_decR, False, obj._Const__c_decR)
    elif objType == "<class 'analyticlab.measure.measure.Measure'>" or objType == "<class 'analyticlab.measure.basemeasure.BaseMeasure'>":
        return obj._Uncertainty__newInstance(sympy.ln(obj._Uncertainty__symbol), ln(obj._Measure__vl), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
    
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
        n._Num__value = math.log10(obj._Num__value)
        #数值的有效数字位数为相应指数的小数点后位数
        n._Num__d_behind = obj._Num__d_valid
        n._Num__d_front = nf.getDigitFront(abs(n._Num__value))
        n._Num__d_valid = n._Num__d_front + n._Num__d_behind
        return n
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        return obj._NumItem__newInstance([lg(n) for n in obj._NumItem__arr])
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        ### 括号与文本预处理 ###
        o_symBrac = obj._LSym__symBrac
        o_symText = obj._LSym__symText
        o_calBrac = obj._LSym__calBrac
        o_calText = obj._LSym__calText
        symText = sNum = calText = symBrac = calBrac = None
        if 4 >= obj._LSym__symPrior:
            if obj._LSym__genSym:
                o_symBrac += 1
                o_symText = obj._LSym__bracket(o_symBrac) % o_symText
        if 4 >= obj._LSym__calPrior:
            if obj._LSym__genCal:
                o_calBrac += 1
                o_calText = obj._LSym__bracket(o_calBrac) % o_calText  
        ### 合成表达式 ###
        if obj._LSym__genSym:
            symText = r'\lg{%s}' % (o_symText)
            symBrac = o_symBrac
        if obj._LSym__genCal:
            sNum = lg(obj._LSym__sNum)
            calText = r'\lg{%s}' % (o_calText)
            calBrac = o_calBrac
        return obj._LSym__newInstance(sNum, symText, calText, symBrac, calBrac, 4, 4, False, obj._LSym__s_decR)
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
        ### 括号与文本预处理 ###
        o_symBrac = obj._Const__symBrac
        o_symText = obj._Const__symText
        o_calBrac = obj._Const__calBrac
        o_calText = obj._Const__calText
        if 4 >= obj._Const__symPrior:
            o_symBrac += 1
            o_symText = obj._Const__bracket(o_symBrac) % o_symText
        if 4 >= obj._Const__calPrior:
            o_calBrac += 1
            o_calText = obj._Const__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = r'\lg %s' % o_symText
        calText = r'\lg %s' % o_calText
        return obj._Const__newInstance(symText, calText, o_symBrac, o_calBrac, 4, 4, math.log10(obj.value()), 1, False, obj._Const__s_decR, False, obj._Const__c_decR)
    elif objType == "<class 'analyticlab.measure.measure.Measure'>" or objType == "<class 'analyticlab.measure.basemeasure.BaseMeasure'>":
        return obj._Uncertainty__newInstance(sympy.log(obj._Uncertainty__symbol, 10), ln(obj._Measure__vl), obj._Uncertainty__measures, obj._Uncertainty__consts, obj._Uncertainty__lsyms, False)
    
def __refreshMode(q, mode):
    if type(q) == Quantity:
        if q.dimensionality == deg.dimensionality:
            mode = 'deg'
        elif q.dimensionality == rad.dimensionality:
            mode = 'rad'
    return mode
    
def __triFunc(obj, fun, selfFun, funExpr, mode, isArc):
    if type(obj) == int or type(obj) == float:
        return fun(obj, mode)
    objType = str(type(obj))
    if objType == "<class 'analyticlab.num.Num'>":
        if not isArc:
            mode = __refreshMode(obj._Num__q, mode)
        obj._Num__resetDigit()
        n = obj._Num__newInstance()
        n._Num__value = fun(obj._Num__value, mode)
        n._Num__d_valid = obj._Num__d_valid
        usign = abs(n._Num__value)
        n._Num__d_front = nf.getDigitFront(usign)
        n._Num__d_behind = nf.getDigitBehind(usign, n._Num__d_valid, n._Num__d_front)
        if isArc:
            n._Num__q = (deg if mode == 'deg' else rad)
        return n
    elif objType == "<class 'analyticlab.numitem.NumItem'>":
        if not isArc:
            mode = __refreshMode(obj._NumItem__q, mode)
        new = obj._NumItem__newInstance([selfFun(n, mode) for n in obj._NumItem__arr])
        if isArc:
            new._NumItem__q = (deg if mode == 'deg' else rad)
        return new
    elif objType == "<class 'analyticlab.lsym.LSym'>":
        if (not isArc) and obj._LSym__genCal:
            mode = __refreshMode(obj._LSym__sNum._Num__q, mode)
        ### 括号与文本预处理 ###
        o_symBrac = obj._LSym__symBrac
        o_symText = obj._LSym__symText
        o_calBrac = obj._LSym__calBrac
        o_calText = obj._LSym__calText
        symText = sNum = calText = symBrac = calBrac = None
        if 4 >= obj._LSym__symPrior:
            if obj._LSym__genSym:
                o_symBrac += 1
                o_symText = obj._LSym__bracket(o_symBrac) % o_symText
        if 4 >= obj._LSym__calPrior:
            if obj._LSym__genCal:
                o_calBrac += 1
                o_calText = obj._LSym__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if obj._LSym__genSym:
            symText = '%s{%s}' % (funExpr, o_symText)
            symBrac = o_symBrac
        if obj._LSym__genCal:
            sNum = selfFun(obj._LSym__sNum, mode)
            calText = '%s{%s}' % (funExpr, o_calText)
            calBrac = o_calBrac
        new = obj._LSym__newInstance(sNum, symText, calText, symBrac, calBrac, 4, 4, False, obj._LSym__s_decR)
        if obj._LSym__genCal and isArc:
            new._LSym__sNum._Num__q = (deg if mode == 'deg' else rad)
        return new
    elif objType == "<class 'analyticlab.lsymitem.LSymItem'>":
        if not isArc:
            mode = __refreshMode(obj._LSymItem__q, mode)
        new = obj._LSymItem__newInstance()
        if type(obj._LSymItem__lsyms) == list:
            new._LSymItem__lsyms = [selfFun(ni, mode) for ni in obj._LSymItem__lsyms]
        else:
            new._LSymItem__lsyms = {}
            for ki in obj._LSymItem__lsyms.keys():
                new._LSymItem__lsyms[ki] = selfFun(obj._LSymItem__lsyms[ki], mode)
        if obj._LSymItem__sepSymCalc:
            new._LSymItem__sepSym = selfFun(obj._LSymItem__sepSym, mode)
        if isArc:
            new._LSymItem__q = (deg if mode == 'deg' else rad)
        return new
    elif objType == "<class 'analyticlab.const.Const'>":
        if (not isArc) and obj._LSym__genCal:
            mode = __refreshMode(obj._LSym__sNum._Num__q, mode)
        ### 括号与文本预处理 ###
        o_symBrac = obj._Const__symBrac
        o_symText = obj._Const__symText
        o_calBrac = obj._Const__calBrac
        o_calText = obj._Const__calText
        if 4 >= obj._Const__symPrior:
            o_symBrac += 1
            o_symText = obj._Const__bracket(o_symBrac) % o_symText
        if 4 >= obj._Const__calPrior:
            o_calBrac += 1
            o_calText = obj._Const__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = funExpr + o_symText
        calText = funExpr + o_calText
        if isArc:
            q = (deg if mode == 'deg' else rad)
        else:
            q = 1
        return obj._Const__newInstance(symText, calText, o_symBrac, o_calBrac, 4, 4, fun(obj.value(), mode), q, False, obj._Const__s_decR, False, obj._Const__c_decR)

def __trans(number, mode):
    if mode == 'deg':
        return math.pi*(number/180)
    elif mode == 'rad':
        return number
    
def __rtrans(number, mode):
    if mode == 'deg':
        return 180*number/math.pi
    elif mode == 'rad':
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
    
def sin(obj, mode='rad'):
    '''正弦函数计算
    【参数说明】
    1.obj：求谁的正弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：该参数仅供int、float类型使用，表示使用角度计算还是弧度计算。当obj为除int、float外的数据类型时，使用obj的单位，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_sin, sin, r'\sin', mode, False)

def cos(obj, mode='rad'):
    '''余弦函数计算
    【参数说明】
    1.obj：求谁的余弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：该参数仅供int、float类型使用，表示使用角度计算还是弧度计算。当obj为除int、float外的数据类型时，使用obj的单位，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_cos, cos, r'\cos', mode, False)

def tan(obj, mode='rad'):
    '''正切函数计算
    【参数说明】
    1.obj：求谁的正切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：该参数仅供int、float类型使用，表示使用角度计算还是弧度计算。当obj为除int、float外的数据类型时，使用obj的单位，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_tan, tan, r'\tan', mode, False)

def csc(obj, mode='rad'):
    '''余割函数计算
    【参数说明】
    1.obj：求谁的余割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：该参数仅供int、float类型使用，表示使用角度计算还是弧度计算。当obj为除int、float外的数据类型时，使用obj的单位，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_csc, csc, r'\csc', mode, False)

def sec(obj, mode='rad'):
    '''正割函数计算
    【参数说明】
    1.obj：求谁的正割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：该参数仅供int、float类型使用，表示使用角度计算还是弧度计算。当obj为除int、float外的数据类型时，使用obj的单位，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_sec, sec, r'\sec', mode, False)

def cot(obj, mode='rad'):
    '''余切函数计算
    【参数说明】
    1.obj：求谁的余切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：该参数仅供int、float类型使用，表示使用角度计算还是弧度计算。当obj为除int、float外的数据类型时，使用obj的单位，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_cot, cot, r'\cot', mode, False)

def arcsin(obj, mode='rad'):
    '''反正弦函数计算
    【参数说明】
    1.obj：求谁的反正弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：使用角度计算还是弧度计算，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_asin, arcsin, r'\arcsin', mode, True)

def arccos(obj, mode='rad'):
    '''反余弦函数计算
    【参数说明】
    1.obj：求谁的反余弦，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：使用角度计算还是弧度计算，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_acos, arccos, r'\arccos', mode, True)

def arctan(obj, mode='rad'):
    '''反正切函数计算
    【参数说明】
    1.obj：求谁的反正切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：使用角度计算还是弧度计算，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_atan, arctan, r'\arctan', mode, True)

def arccsc(obj, mode='rad'):
    '''反余割函数计算
    【参数说明】
    1.obj：求谁的反余割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：使用角度计算还是弧度计算，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_acsc, arccsc, r'\operatorname{arccsc}', mode, True)

def arcsec(obj, mode='rad'):
    '''反正割函数计算
    【参数说明】
    1.obj：求谁的反正割，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：使用角度计算还是弧度计算，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_asec, arcsec, r'\operatorname{arcsec}', mode, True)

def arccot(obj, mode='rad'):
    '''反余切函数计算
    【参数说明】
    1.obj：求谁的反余切，obj可以是以下数据类型：
    ①int或float；②Num；③NumItem；④LSym；⑤LSymItem；⑥Const；⑦Measure或Uncertainty。
    2.mode（可选，str）：使用角度计算还是弧度计算，mode='deg'时为角度计算，mode='rad'或为空时为弧度计算。默认mode='rad'。
    【返回值】
    根据obj的数据类型，返回值的数据类型如下：
    ①int、float → float；
    ②Num → Num；
    ③NumItem → NumItem；
    ④LSym → LSym；
    ⑤LSymItem → LSymItem；
    ⑥Const → Const；
    ⑦Measure、Uncertainty → Uncertainty。'''
    return __triFunc(obj, __m_acot, arccot, r'\operatorname{arccot}', mode, True)
