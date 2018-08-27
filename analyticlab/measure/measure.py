# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 22:21:31 2018

@author: xingrongtech
"""

import re, sympy, copy
from sympy import Symbol, diff
from quantities.quantity import Quantity
from ..amath import sqrt
from ..const import Const
from ..lsym import LSym
from ..system.exceptions import keyNotInTableException
from ..system.text_unicode import usub
from ..system.unit_open import openUnit, closeUnit
from ..system.format_units import format_units_unicode, format_units_latex

KTable = {0.67:(0.50,'50'), 1.645:(0.90,'90'), 1.960:(0.95,'95'), 2:(0.9545,'95'), 2.576:(0.99,'99'), 3:(0.9973,'99')}

class Measure():
    ## vl的含义：
    ## vl = value + lsym：process为True时，返回lsym符号；为False时，返回Num数值
    process = False  #静态属性，表明是否展示计算过程
    simplifyUnc = False  #静态属性，表明是否化简不确定度计算式
    
    __isPureMulDiv = True
    __K = None
    __q_rep = None
    useRelUnc = False
    
    def __newInstance(self, symbol, vl, baseMeasures, consts, lsyms, isPureMulDiv):
        new = Measure()
        new.useRelUnc = False
        new.__symbol = symbol
        new.__vl = vl
        new.__baseMeasures = baseMeasures
        new.__consts = consts
        new.__lsyms = lsyms
        if self.__isPureMulDiv == False or isPureMulDiv == False:
            new.__isPureMulDiv = False
        return new
    
    def __process(self):
        return Measure.process
    
    def __getSymbol(self, obj):
        '''获得用于符号运算的符号（包括sObj和vlObj），以及基本组成baseMeasures、consts和lsyms'''
        baseMeasures = self.__baseMeasures
        consts = self.__consts
        lsyms = self.__lsyms
        if str(type(self)) == "<class 'analyticlab.measure.basemeasure.BaseMeasure'>" and self._BaseMeasure__sym not in baseMeasures:  #对于测量，判断是否要将该测量添加到测量列表中
            if Measure.process:
                baseMeasures[self._BaseMeasure__sym] = (self, self.__vl, LSym('u_{%s}' % self._BaseMeasure__sym, self.unc(remainOneMoreDigit=True)))
                self.__vl = copy.deepcopy(self.__vl)
                self.__vl._LSym__symText = r'{\overline%s}' % self.__vl._LSym__symText
            else:
                baseMeasures[self._BaseMeasure__sym] = (self, self.__vl, self.unc(remainOneMoreDigit=True))
        if type(obj) == Measure:
            for oKey in obj._Measure__baseMeasures.keys():
                if oKey not in baseMeasures:
                    baseMeasures[oKey] = obj._Measure__baseMeasures[oKey]
            for oKey in obj._Measure__consts.keys():
                if oKey not in consts:
                    consts[oKey] = obj._Measure__consts[oKey]
            for oKey in obj._Measure__lsyms.keys():
                if oKey not in lsyms:
                    lsyms[oKey] = obj._Measure__lsyms[oKey]
            sObj = obj._Measure__symbol
            vlObj = obj.__vl
        elif str(type(obj)) == "<class 'analyticlab.measure.basemeasure.BaseMeasure'>":
            vlObj = None
            if obj._BaseMeasure__sym not in baseMeasures:
                if Measure.process:
                    baseMeasures[obj._BaseMeasure__sym] = (obj, obj.__vl, LSym('u_{%s}' % obj._BaseMeasure__sym, obj.unc(remainOneMoreDigit=True)))
                    vlObj = copy.deepcopy(obj.__vl)
                    vlObj._LSym__symText = r'{\overline%s}' % vlObj._LSym__symText
                else:
                    baseMeasures[obj._BaseMeasure__sym] = (obj, obj.__vl, obj.unc(remainOneMoreDigit=True))
                sObj = obj._Measure__symbol
            else:
                sObj = baseMeasures[obj._BaseMeasure__sym][0]._Measure__symbol
            if vlObj == None:
                vlObj = obj.__vl
        elif type(obj) == Const:
            if obj._Const__symText not in self.__consts:
                sObj = Symbol(obj._Const__symText, real=True)
                consts[obj._Const__symText] = (obj, sObj)
            else:
                sObj = self.__consts[obj._Const__symText][1]
            if Measure.process:
                vlObj = obj
            else:
                vlObj = obj.value()
        elif type(obj) == LSym:
            if obj._LSym__symText not in self.__lsyms:
                sObj = Symbol(obj._LSym__symText, real=True)
                lsyms[obj._LSym__symText] = (obj, sObj)
            else:
                sObj = self.__lsyms[obj._LSym__symText][1]
            if Measure.process:
                vlObj = obj
            else:
                vlObj = obj.num()
        else:
            sObj = obj
            vlObj = obj
        return sObj, vlObj, baseMeasures, consts, lsyms
        
    def __neg__(self):
        return self.__newInstance(-self.__symbol, -self.__vl, self.__baseMeasures, self.__consts, self.__lsyms, True)
        
    def __add__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol + sObj
        vl = self.__vl + vlObj
        return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, False)
    
    def __radd__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj + self.__symbol
        vl = vlObj + self.__vl
        return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, False)
    
    def __sub__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol - sObj
        vl = self.__vl - vlObj
        return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, False)
    
    def __rsub__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj - self.__symbol
        vl = vlObj - self.__vl
        return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, False)
    
    def __mul__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol * sObj
        vl = self.__vl * vlObj
        if type(obj) == Measure:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, True)
    
    def __rmul__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj * self.__symbol
        vl = vlObj * self.__vl
        if type(obj) == Measure:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, True)
    
    def __truediv__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol / sObj
        vl = self.__vl / vlObj
        if type(obj) == Measure:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, True)
    
    def __rtruediv__(self, obj):
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj / self.__symbol
        vl = vlObj / self.__vl
        if type(obj) == Measure:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, True)

    def __pow__(self, obj):
        '''幂运算'''
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol ** sObj
        vl = self.__vl ** vlObj
        if type(obj) == Measure:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, True)
 
    def __rpow__(self, obj):
        '''指数运算'''
        sObj, vlObj, baseMeasures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj ** self.__symbol
        vl = vlObj ** self.__vl
        return self.__newInstance(symbol, vl, baseMeasures, consts, lsyms, False)
        
    def setK(self, K):
        '''设置扩展不确定度的K值'''
        if K not in KTable:
            raise keyNotInTableException('找不到K=%s时对应的置信区间')
        self.__K = K
        
    def __checkIsNumber(s):
        '''检查一个字符串是否为数字'''
        if s.find('^'):
            s = s.split('^')[0]
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def __getUnc(self):
        '''获得合成不确定度'''
        ms = self.__baseMeasures
        if self.__isPureMulDiv:
            #对于纯乘除测量公式的不确定度计算
            meaTimes = []
            symbolExpr = str(self.__symbol)  #获得诸如x1**2*x2或4*x1**2*x2**3/(x3*x4)的符号表达式
            symbolExpr = symbolExpr.replace('**', '^')  #将**替换成^，防止**干扰*
            for ci in self.__consts.values():  #将所有Const常数替换为1，防止符号干扰
                symbolExpr = symbolExpr.replace(ci[0]._Const__symText, '1')
            for li in self.__lsyms.values():  #将所有LSym替换为1，防止符号干扰
                symbolExpr = symbolExpr.replace(li[0]._LSym__symText, '1')
            mulArr = symbolExpr.split('/')  #以除号为界分割符号表达式
            if len(mulArr) == 2:  #如果除号右边有表达式，去掉右边其中的括号，得到['4*x1^2*x2^3', 'x3*x4']
                mulArr[1] = mulArr[1].replace('(', '').replace(')', '')
            mulArr = [mri.split('*') for mri in mulArr]  #分割乘号，得到['4', 'x1^2', 'x2^3']
            if len(mulArr) == 2:  #合并所有的被乘项
                mulArr = mulArr[0] + mulArr[1]
            else:
                mulArr = mulArr[0]
            for mri in mulArr:
                if not Measure.__checkIsNumber(mri):  #只对非纯数字和非常数进行处理
                    si = mri.split('^')  #将每个符号对应的测量和次数映射到dict中
                    if len(si) == 1:
                        meaTimes.append([si[0], 1])
                    else:
                        meaTimes.append([si[0], float(si[1])])
            closeUnit()
            def times(mea):
                if mea[1] == 1:
                    return (ms[mea[0]][2]/ms[mea[0]][1])**2
                else:
                    return (mea[1]*ms[mea[0]][2]/ms[mea[0]][1])**2
            uSum = times(meaTimes[0])
            for mea in meaTimes[1:]:
                uSum += times(mea)
            res = sqrt(uSum)
            openUnit()
        else:
            #对于纯乘除测量公式的不确定度计算，使用sympy求偏导实现
            y = self.__symbol
            m = list(self.__baseMeasures.values())
            cs, ls = self.__consts, self.__lsyms
            um0 = Symbol('u_{%s}' % m[0][0]._BaseMeasure__sym, real=True)
            ssum = diff(y, m[0][0]._Measure__symbol)**2 * um0**2
            for mi in m[1:]:
                umi = Symbol('u_{%s}' % mi[0]._BaseMeasure__sym, real=True)
                ssum += diff(y, mi[0]._Measure__symbol)**2 * umi**2
            u = sympy.sqrt(ssum)
            if Measure.simplifyUnc:
                u = sympy.simplify(u)
            uExpr = str(u)
            def repRat(matched):
                return 'Rational%s' % matched.group('rat').replace('/', ',')
            uExpr = re.sub('(?P<rat>\((-?\d+)(\.\d+)?/(-?\d+)(\.\d+)?\))', repRat, uExpr)
            uExpr = uExpr.replace('log(10)', '2.303').replace('Abs', 'abs')
            for mi in m:
                si = mi[0]._BaseMeasure__sym
                uExpr = uExpr.replace(si, 'ms[r"%s"][1]' % si)
                uExpr = uExpr.replace('u_{ms[r"%s"][1]}' % si, 'ms[r"%s"][2]' % si)
            for ci in self.__consts.values():
                uExpr = uExpr.replace(ci[0]._Const__symText, 'cs[r"%s"][0]' % ci[0]._Const__symText)
            for li in self.__lsyms.values():
                uExpr = uExpr.replace(li[0]._LSym__symText, 'ls[r"%s"][0]' % li[0]._LSym__symText)
            closeUnit()
            res = eval(uExpr)
            openUnit()
        if Measure.process:
            res._LSym__sNum._Num__q = self.__q_rep if self.__q_rep != None else self.__vl._LSym__sNum._Num__q
        else:
            res._Num__q = self.__q_rep if self.__q_rep != None else self.__vl._Num__q
        return res
            
    def __res(self):
        '''返回供展示不确定度使用的结果'''
        if not Measure.process:
            return
        res = {}
        res['K'] = self.__K
        if self.__K != None:
            res['P'] = KTable[self.__K]
        if type(self) == Measure:
            uncLSym = self.__getUnc()
            unc = uncLSym._LSym__sNum
            unc.setIsRelative(self.__isPureMulDiv)
            res['unc'] = uncLSym._LSym__sNum
            res['isRate'] = self.__isPureMulDiv
            if Measure.process:
                res['uncLSym'] = uncLSym
                if not self.__isPureMulDiv:
                    res['baseMeasures'] = self.__baseMeasures
        return res
    
    def value(self):
        '''获得测量值
        【返回值】
        Num：测量值。'''
        if Measure.process:
            return self.__vl.num()
        else:
            return self.__vl
    
    def valueLSym(self):
        assert Measure.process, 'Measure.process为False时，无法获取LSym'
        return self.__vl
    
    def unc(self):
        '''获得不确定度
        【返回值】
        Num：K=1时，为标准不确定度数值；K>1时，为扩展不确定度数值。'''
        if Measure.process:
            unc = self.__getUnc()._LSym__sNum
        else:
            unc = self.__getUnc()
        if self.__K != None:
            unc *= self.__K
        return unc
    
    def relUnc(self):
        '''获得相对不确定度
        【返回值】
        Num：K=1时，为相对标准不确定度数值；K>1时，为相对扩展不确定度数值。'''
        ur = self.unc() / self.value()
        ur.setIsRelative = True
        return ur
    
    def uncLSym(self):
        assert Measure.process, 'Measure.process为False时，无法获取LSym'
        u = self.__getUnc()
        return u
    
    def resetUnit(self, unit=None):
        '''重设测量（含测量值和不确定度）的单位
        【参数说明】
        unit（可选，str）：重设后的单位。默认unit=None，即没有单位。'''
        assert type(self) == Measure, '单位重设仅供Measure使用，不可用于BaseMeasure'
        if unit == None:
            q = 1
        else:
            q = Quantity(1., unit) if type(unit) == str else unit
        self.value()._Num__q = q
        self.__q_rep = q

    def __str__(self):
        '''获得测量值和不确定度的字符串形式
        【返回值】
        str：(测量值±不确定度)，如已给出单位，会附加单位'''
        val = self.value()
        u = self.unc()
        if Measure.process:
            unitExpr = format_units_unicode(self.__vl._LSym__sNum._Num__q)
        else:
            unitExpr = format_units_unicode(self.__vl._Num__q)
        sciDigit = val._Num__sciDigit()
        if self.useRelUnc:
            ur = u / val
            ur.setIsRelative(True)
            expr = r'%s(1±%s)%s' % (val.strNoUnit(), ur, unitExpr)
        else:
            if sciDigit == 0:
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'%s±%s' % (val.strNoUnit(), u.strNoUnit())
                if unitExpr != '':
                    expr = '(%s)%s' % (expr, unitExpr)
            else:
                val *= 10**(-sciDigit)
                u *= 10**(-sciDigit)
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'(%s±%s)×10%s%s' % (val.strNoUnit(), u.strNoUnit(), usub(sciDigit), unitExpr)
        return expr
        
    def __repr__(self):
        '''获得测量值和不确定度的字符串形式
        【返回值】
        str：(测量值±不确定度)，如已给出单位，会附加单位'''
        return self.__str__()
    
    def latex(self):
        val = self.value()
        u = self.unc()
        if Measure.process:
            unitExpr = format_units_latex(self.__vl._LSym__sNum._Num__q)
        else:
            unitExpr = format_units_latex(self.__vl._Num__q)
        sciDigit = val._Num__sciDigit()
        if self.useRelUnc:
            ur = u / val
            ur.setIsRelative(True)
            expr = r'%s\left(1 \pm %s\right)%s' % (val.strNoUnit(), ur.dlatex(), unitExpr)
        else:
            if sciDigit == 0:
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'\left(%s \pm %s\right)%s' % (val.strNoUnit(), u.strNoUnit(), unitExpr)
            else:
                val *= 10**(-sciDigit)
                u *= 10**(-sciDigit)
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'\left(%s \pm %s\right)\times 10^{%d}%s' % (val.strNoUnit(), u.strNoUnit(), sciDigit, unitExpr)
        return expr
    
    def _repr_latex_(self):
       return r'$\begin{align}%s\end{align}$' % self.latex()