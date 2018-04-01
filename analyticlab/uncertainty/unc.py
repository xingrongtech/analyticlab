# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 22:21:31 2018

@author: xingrongtech
"""

import re, sympy
from sympy import Symbol, diff
from ..amath import sqrt
from ..const import Const
from ..lsym import LSym
from ..system.exceptions import keyNotInTableException

KTable = {0.67:(0.50,'50'), 1.645:(0.90,'90'), 1.960:(0.95,'95'), 2:(0.9545,'95'), 2.576:(0.99,'99'), 3:(0.9973,'99')}

class Uncertainty():
    process = False  #静态方法，表明是否展示计算过程
    simplifyUnc = False  #静态方法，表明是否化简不确定度计算式
    
    __isPureMulDiv = True
    __K = None
    
    def __newInstance(self, symbol, measures, consts, lsyms, isPureMulDiv):
        new = Uncertainty()
        new.__symbol = symbol
        new.__measures = measures
        new.__consts = consts
        new.__lsyms = lsyms
        if self.__isPureMulDiv == False or isPureMulDiv == False:
            new.__isPureMulDiv = False
        return new
    
    def __process(self):
        return Uncertainty.process
    
    def __getSymbol(self, obj):
        '''获得用于符号运算的符号、measures和consts'''
        measures = self.__measures
        consts = self.__consts
        lsyms = self.__lsyms
        if type(self) != Uncertainty and self._Measure__sym not in measures:  #对于测量，判断是否要将该测量添加到测量列表中
            if Uncertainty.process:
                measures[self._Measure__sym] = (self, LSym(self._Measure__sym, self._Measure__value), LSym('u_{%s}' % self._Measure__sym, self.unc(remainOneMoreDigit=True)))
            else:
                measures[self._Measure__sym] = (self, self._Measure__value, self.unc(remainOneMoreDigit=True))
        if type(obj) == Uncertainty:
            for oKey in obj._Uncertainty__measures.keys():
                if oKey not in measures:
                    measures[oKey] = obj._Uncertainty__measures[oKey]
            for oKey in obj._Uncertainty__consts.keys():
                if oKey not in consts:
                    consts[oKey] = obj._Uncertainty__consts[oKey]
            for oKey in obj._Uncertainty__lsyms.keys():
                if oKey not in lsyms:
                    lsyms[oKey] = obj._Uncertainty__lsyms[oKey]
            sObj = obj._Uncertainty__symbol
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            if obj._Measure__sym not in measures:
                if Uncertainty.process:
                    measures[obj._Measure__sym] = (obj, LSym(obj._Measure__sym, obj._Measure__value), LSym('u_{%s}' % obj._Measure__sym, obj.unc(remainOneMoreDigit=True)))
                else:
                    measures[obj._Measure__sym] = (obj, obj._Measure__value, obj.unc(remainOneMoreDigit=True))
                sObj = obj._Uncertainty__symbol
            else:
                sObj = measures[obj._Measure__sym][0]._Uncertainty__symbol
        elif type(obj) == Const:
            if obj._Const__symText not in self.__consts:
                sObj = Symbol(obj._Const__symText, real=True)
                consts[obj._Const__symText] = (obj, sObj)
            else:
                sObj = self.__consts[obj._Const__symText][1]
        elif type(obj) == LSym:
            if obj._LSym__symText not in self.__lsyms:
                sObj = Symbol(obj._LSym__symText, real=True)
                lsyms[obj._LSym__symText] = (obj, sObj)
            else:
                sObj = self.__lsyms[obj._LSym__symText][1]
        else:
            sObj = obj
        return sObj, measures, consts, lsyms
        
    def __neg__(self):
        return self.__newInstance(-self.__symbol, self.__measures, self.__consts, self.__lsyms, True)
        
    def __add__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol + sObj
        return self.__newInstance(symbol, measures, consts, lsyms, False)
    
    def __radd__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj + self.__symbol
        return self.__newInstance(symbol, measures, consts, lsyms, False)
    
    def __sub__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol - sObj
        return self.__newInstance(symbol, measures, consts, lsyms, False)
    
    def __rsub__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj - self.__symbol
        return self.__newInstance(symbol, measures, consts, lsyms, False)
    
    def __mul__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol * sObj
        if type(obj) == Uncertainty:
            return self.__newInstance(symbol, measures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, measures, consts, lsyms, True)
    
    def __rmul__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj * self.__symbol
        if type(obj) == Uncertainty:
            return self.__newInstance(symbol, measures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, measures, consts, lsyms, True)
    
    def __truediv__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol / sObj
        if type(obj) == Uncertainty:
            return self.__newInstance(symbol, measures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, measures, consts, lsyms, True)
    
    def __rtruediv__(self, obj):
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj / self.__symbol
        if type(obj) == Uncertainty:
            return self.__newInstance(symbol, measures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, measures, consts, lsyms, True)

    def __pow__(self, obj):
        '''幂运算'''
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = self.__symbol ** sObj
        if type(obj) == Uncertainty:
            return self.__newInstance(symbol, measures, consts, lsyms, obj.__isPureMulDiv)
        else:
            return self.__newInstance(symbol, measures, consts, lsyms, True)
 
    def __rpow__(self, obj):
        '''指数运算'''
        sObj, measures, consts, lsyms = self.__getSymbol(obj)
        symbol = sObj ** self.__symbol
        return self.__newInstance(symbol, measures, consts, lsyms, False)
        
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
        ms = self.__measures
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
                if not Uncertainty.__checkIsNumber(mri):  #只对非纯数字和非常数进行处理
                    si = mri.split('^')  #将每个符号对应的测量和次数映射到dict中
                    if len(si) == 1:
                        meaTimes.append([si[0], 1])
                    else:
                        meaTimes.append([si[0], float(si[1])])
            def times(mea):
                if mea[1] == 1:
                    return (ms[mea[0]][2]/ms[mea[0]][1])**2
                else:
                    return (mea[1]*ms[mea[0]][2]/ms[mea[0]][1])**2
            uSum = times(meaTimes[0])
            for mea in meaTimes[1:]:
                uSum += times(mea)
            res = sqrt(uSum)
        else:
            #对于纯乘除测量公式的不确定度计算，使用sympy求偏导实现
            y = self.__symbol
            m = list(self.__measures.values())
            cs, ls = self.__consts, self.__lsyms
            um0 = Symbol('u_{%s}' % m[0][0]._Measure__sym, real=True)
            ssum = diff(y, m[0][0]._Uncertainty__symbol)**2 * um0**2
            for mi in m[1:]:
                umi = Symbol('u_{%s}' % mi[0]._Measure__sym, real=True)
                ssum += diff(y, mi[0]._Uncertainty__symbol)**2 * umi**2
            u = sympy.sqrt(ssum)
            if Uncertainty.simplifyUnc:
                u = sympy.simplify(u)
            uExpr = str(u)
            def repRat(matched):
                return 'Rational%s' % matched.group('rat').replace('/', ',')
            uExpr = re.sub('(?P<rat>\((-?\d+)(\.\d+)?/(-?\d+)(\.\d+)?\))', repRat, uExpr)
            uExpr = uExpr.replace('log(10)', '2.303').replace('Abs', 'abs')
            for mi in m:
                si = mi[0]._Measure__sym
                uExpr = uExpr.replace(si, 'ms[r"%s"][1]' % si)
                uExpr = uExpr.replace('u_{ms[r"%s"][1]}' % si, 'ms[r"%s"][2]' % si)
            for ci in self.__consts.values():
                uExpr = uExpr.replace(ci[0]._Const__symText, 'cs[r"%s"][0]' % ci[0]._Const__symText)
            for li in self.__lsyms.values():
                uExpr = uExpr.replace(li[0]._LSym__symText, 'ls[r"%s"][0]' % li[0]._LSym__symText)
            res = eval(uExpr)
        return res
            
    def __res(self):
        '''返回供展示不确定度使用的结果'''
        if not Uncertainty.process:
            return
        res = {}
        res['K'] = self.__K
        if self.__K != None:
            res['P'] = KTable[self.__K]
        if type(self) == Uncertainty:
            uncLSym = self.__getUnc()
            unc = uncLSym._LSym__sNum
            unc.setIsRelative(self.__isPureMulDiv)
            res['unc'] = uncLSym._LSym__sNum
            res['isRate'] = self.__isPureMulDiv
            if Uncertainty.process:
                res['uncLSym'] = uncLSym
                if not self.__isPureMulDiv:
                    res['measures'] = self.__measures
        return res
    
    def result(self):
        '''获得不确定度
        【返回值】
        Num：K=1时，为标准不确定度数值；K>1时，为扩展不确定度数值。
        '''
        if Uncertainty.process:
            unc = self.__getUnc()._LSym__sNum
        else:
            unc = self.__getUnc()
        if self.__K != None:
            unc *= self.__K
        return unc