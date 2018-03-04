# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 22:21:31 2018

@author: xingrongtech
"""

import math
from analyticlab import const, amath
from analyticlab.const import Const
from analyticlab.system.exceptions import keyNotInTableException

KTable = {0.67:(0.50,'50'), 1.645:(0.90,'90'), 1.960:(0.95,'95'), 2:(0.9545,'95'), 2.576:(0.99,'99'), 3:(0.9973,'99')}

class Uncertainty():
    process = False  #静态方法，表明是否展示计算过程
    
    __prevCalId = 0  #当前运算符编号
    __item = []  #相同运算符编号下的不确定度组（包括Uncertainty和Measure）
    __sym = None
    __unc = None  #不确定度数值
    __equ = None  #原等式数值
    __uncLSym = None  #不确定度的Latex表达式
    __equLSym = None  #原等式的Latex表达式
    __symBrac = -1  #当前符号式括号级别：-1为无括号，0为()，0为[]，0为{}
    __calBrac = -1  #当前计算式括号级别：-1为无括号，0为()，0为[]，0为{}
    __prevExp = None  #若上一步运算为幂运算，则用prevExp记录上一步运算的幂指数等信息，否则记为None
                 # prevExp所记录的信息为一个dict，包括b（指数），指数运算前的A（equ，equLSym）
    __prevRoot = None  #若上一步运算为求根运算，则用prevRoot记录上一步运算的根指数等信息，否则记为None
                 # prevRoot所记录的信息为一个dict，包括r（根指数），指数运算前的A（equ，equLSym）
    __K = None
    '''
    运算符编号规定：
    【1】与常数的运算：对int，float，Const的计算
    0：u[R]=u[A]（R=A，R=-A，R=A+k，R=k+A，R=A-k，R=k-A）
    1：u[R]=k*u[A]（R=A*k，R=k*A）
    2：u[R]=u[A]/k（R=A/k）
    3：u[R]=k*R/A*u[A]（R=k/A）
    【2】与测量值的运算：对Uncertainty的计算
    4：u[R]=sqrt(u[A]**2+u[B]**2)（R=A+B，R=A-B，R=B+A，R=B-A）
    5：u[R]/R=sqrt((u[A]/A)**2+(u[B]/B)**2)（R=A*B，R=B*A，R=A/B，R=B/A）
    【3】幂运算
    6：具体如何计算，由外层计算为加减法还是乘除法决定（R=A**k）
      ①对于加减法：u[A]→R*k*u[A]/A
      ②对于乘除法：s[A]→k*u[A]
    【4】根式运算
    7：具体如何计算，由外层计算为加减法还是乘除法决定（R=sqrt(A,k)）
      ①对于加减法：u[A]→R*u[A]/(k*A)
      ②对于乘除法：s[A]→u[A]/k
    【4】指数运算
    8：u[R]=ln(a)*u[A]*R（R=a**A，包括R=e**A和R=10**A）
    【5】对数运算
    9：u[R]=u[A]/A（R=lnA）
    10：u[R]=0.4343*u[A]/A（R=lgA）
    '''
    
    def __newInstance(self, calId, item, unc, equ, uncLSym=None, equLSym=None, prevExp=None, prevRoot=None):
        new = Uncertainty()
        new.__prevCalId = calId
        new.__item = item
        new.__unc = unc
        new.__equ = equ
        new.__uncLSym = uncLSym
        new.__equLSym = equLSym
        new.__prevExp = prevExp
        new.__prevRoot = prevRoot
        return new
    
    def __process(self):
        return Uncertainty.process
        
    def __neg__(self):
        calId = 0
        equ = self.equ().__neg__()
        equLSym = None
        if Uncertainty.process:
            equLSym = self.equLSym().__neg__()
        return self.__execute(calId, equ, equLSym)
        
    def __add__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 0
            equ = self.equ().__add__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__add__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 0
            equ = self.equ().__add__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__add__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 4
            equ = self.equ().__add__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__add__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __radd__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 0
            equ = self.equ().__radd__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__radd__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 0
            equ = self.equ().__radd__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__radd__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 4
            equ = self.equ().__radd__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__radd__(obj.equLSym())               
        return self.__execute(calId, equ, equLSym, obj)
    
    def __sub__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 0
            equ = self.equ().__sub__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__sub__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 0
            equ = self.equ().__sub__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__sub__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 4
            equ = self.equ().__sub__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__sub__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __rsub__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 0
            equ = self.equ().__rsub__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__rsub__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 0
            equ = self.equ().__rsub__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__rsub__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 4
            equ = self.equ().__rsub__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__rsub__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __mul__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 1
            equ = self.equ().__mul__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__mul__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 1
            equ = self.equ().__mul__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__mul__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 5
            equ = self.equ().__mul__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__mul__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __rmul__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 1
            equ = self.equ().__rmul__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__rmul__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 1
            equ = self.equ().__rmul__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__rmul__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 5
            equ = self.equ().__rmul__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__rmul__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __truediv__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 2
            equ = self.equ().__truediv__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__truediv__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 2
            equ = self.equ().__truediv__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__truediv__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 5
            equ = self.equ().__truediv__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__truediv__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __rtruediv__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 3
            equ = self.equ().__rtruediv__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__rtruediv__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 3
            equ = self.equ().__rtruediv__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__rtruediv__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 5
            equ = self.equ().__rtruediv__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__rtruediv__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __floordiv__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 2
            equ = self.equ().__truediv__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__floordiv__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 2
            equ = self.equ().__truediv__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__floordiv__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 5
            equ = self.equ().__truediv__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__floordiv__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)
    
    def __rfloordiv__(self, obj):
        equLSym = None
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            calId = 3
            equ = self.equ().__rtruediv__(obj)
            if Uncertainty.process:
                equLSym = self.equLSym().__rfloordiv__(obj)
        elif str(type(obj)) == "<class 'analyticlab.lsym.LSym'>":
            calId = 3
            equ = self.equ().__rtruediv__(obj._LSym__sNum)
            if Uncertainty.process:
                equLSym = self.equLSym().__rfloordiv__(obj._LSym__sNum)
        else:  #对于Uncertainty或Measure
            calId = 5
            equ = self.equ().__rtruediv__(obj.equ())
            if Uncertainty.process:
                equLSym = self.equLSym().__rfloordiv__(obj.equLSym())
        return self.__execute(calId, equ, equLSym, obj)

    def __pow__(self, obj):
        '''幂运算'''
        calId = 6
        if type(obj) == Const:
            equ = self.equ().__pow__(obj.value())
        else:
            equ = self.equ().__pow__(obj)
        equLSym = None
        if Uncertainty.process:
            equLSym = self.equLSym().__pow__(obj)
        return self.__execute(calId, equ, equLSym, obj)
 
    def __rpow__(self, obj):
        '''指数运算'''
        calId = 8
        if type(obj) == Const:
            equ = self.equ().__rpow__(obj.value())
        else:
            equ = self.equ().__rpow__(obj)
        equLSym = None
        if Uncertainty.process:
            equLSym = self.equLSym().__rpow__(obj)
        return self.__execute(calId, equ, equLSym, obj)
 
    def unc(self):
        '''获得合成标准不确定度
        【返回值】
        Num：合成标准不确定度数值。'''
        return self.__unc
    
    def uncLSym(self):
        '''获得合成标准不确定度公式的LaTeX符号
        【返回值】
        LSym：合成标准不确定度公式的LaTeX符号。'''
        return self.__uncLSym
    
    def equ(self):
        '''获得计算结果
        【返回值】
        Num：计算结果数值。'''
        return self.__equ
    
    def equLSym(self):
        '''获得计算式的LaTeX符号
        【返回值】
        LSym：计算式的LaTeX符号。'''
        return self.__equLSym
    
    def __combCal4(self):
        '''加减运算的合并'''
        dsum = 0
        for i in range(len(self.__item)):
            u = self.__item[i]
            if u.__prevExp != None:
                dsum = dsum + ((u.__prevExp['b'] * u.equ() / u.__prevExp['equ']) * u.unc())**2
            elif u.__prevRoot != None:
                dsum = dsum + (u.equ() / (u.__prevRoot['r'] * u.__prevRoot['equ']) * u.unc())**2
            else:
                dsum = dsum + u.unc()**2
        unc = amath.sqrt(dsum)
        uncLSym = None
        if Uncertainty.process:
            u = self.__item[0]
            if u.__prevExp != None:
                uncLSym = ((u.__prevExp['b'] * u.uncLSym() / u.__prevExp['equLSym']) * u.equLSym())**2
            elif u.__prevRoot != None:
                uncLSym = (u.uncLSym() / (u.__prevRoot['r'] * u.__prevRoot['equLSym']) * u.equLSym())**2
            else:
                uncLSym = u.uncLSym()**2
            for i in range(1, len(self.__item)):
                u = self.__item[i]
                if u.__prevExp != None:
                    uncLSym += ((u.__prevExp['b'] * u.uncLSym() / u.__prevExp['equLSym']) * u.equLSym())**2
                elif u.__prevRoot != None:
                    uncLSym += (u.uncLSym() / (u.__prevRoot['r'] * u.__prevRoot['equLSym']) * u.equLSym())**2
                else:
                    uncLSym += u.uncLSym()**2
            uncLSym = amath.sqrt(uncLSym)
        return unc, uncLSym
        
    def __combCal5(self, isRate=False):
        '''乘除运算的合并（包括合并为相对式和合并为绝对式）'''
        dsum = 0
        for i in range(len(self.__item)):
            u = self.__item[i]
            if u.__prevExp == None and u.__prevRoot == None:
                dsum = dsum + (u.unc() / u.equ())**2
            elif u.__prevExp != None:
                dsum = dsum + (u.__prevExp['b'] * u.unc() / u.__prevExp['equ'])**2
            elif u.__prevRoot != None:
                dsum = dsum + (u.unc() / (u.__prevRoot['b'] * u.__prevRoot['equ']))**2
        unc = amath.sqrt(dsum)
        if not isRate:
            unc = self.equ() * unc
        uncLSym = None
        if Uncertainty.process:
            u = self.__item[0]
            if u.__prevExp == None and u.__prevRoot == None:
                uncLSym = (u.uncLSym() / u.equLSym())**2
            elif u.__prevExp != None:
                uncLSym = (u.__prevExp['b'] * u.uncLSym() / u.__prevExp['equLSym'])**2
            elif u.__prevRoot != None:
                uncLSym = (u.uncLSym() / (u.__prevRoot['r'] * u.__prevRoot['equLSym']))**2
            for i in range(1, len(self.__item)):
                u = self.__item[i]
                if u.__prevExp == None and u.__prevRoot == None:
                    uncLSym += (u.uncLSym() / u.equLSym())**2
                elif u.__prevExp != None:
                    uncLSym += (u.__prevExp['b'] * u.uncLSym() / u.__prevExp['equLSym'])**2
                elif u.__prevRoot != None:
                    uncLSym += (u.uncLSym() / (u.__prevRoot['r'] * u.__prevRoot['equLSym']))**2
            uncLSym = amath.sqrt(uncLSym)
            if not isRate:
                uncLSym = self.equLSym() * uncLSym
        return unc, uncLSym
    
    def __cal6(self):
        '''执行非加减、乘除中的幂运算'''
        unc = (self.__prevExp['b'] * self.equ() / self.__prevExp['equ']) * self.unc()
        uncLSym = None
        if Uncertainty.process:
            uncLSym = (self.__prevExp['b'] * self.uncLSym() / self.__prevExp['equLSym']) * self.equLSym()
        return unc, uncLSym
            
    def __cal7(self):
        '''执行非加减、乘除中的根式运算'''
        unc = self.equ() / (self.__prevRoot['r'] * self.__prevExp['equ']) * self.unc()
        uncLSym = None
        if Uncertainty.process:
            uncLSym = self.uncLSym() / (self.__prevRoot['r'] * self.__prevExp['equLSym']) * self.equLSym()
        return unc, uncLSym
        
    def __execute(self, calId, equ, equLSym, obj=None):
        '''执行运算'''
        # calId为本次运算的编号
        # self.__prevCalId为上次运算的编号
        if calId == 0:  # 0：s[R]=s[A]（R=A，R=-A，R=A+k，R=k+A，R=A-k，R=k-A）
            #由于s[R]=s[A]，即不确定度不变，故直接输出之前的不确定度
            return self._Uncertainty__newInstance(self.__prevCalId, self.__item, self.unc(), equ, self.uncLSym(), equLSym)
        elif calId in (1, 2, 3, 8, 9, 10):
            if self.__prevCalId == 4:
                unc, uncLSym = self.__combCal4()
            elif self.__prevCalId == 5:
                unc, uncLSym = self.__combCal5()
            elif self.__prevCalId == 6:
                unc, uncLSym = self.__cal6()
            elif self.__prevCalId == 7:
                unc, uncLSym = self.__cal7()
            else:
                unc, uncLSym = self.unc(), self.uncLSym()
            if calId == 1:  # 1：u[R]=k*u[A]（R=A*k，R=k*A）
                unc = obj * unc  #u[R]=k*u[A]
                if Uncertainty.process:
                    uncLSym = obj * uncLSym
            elif calId == 2:  # 2：u[R]=u[A]/k（R=A/k）
                unc = unc / obj
                if Uncertainty.process:
                    uncLSym = unc / obj
            elif calId == 3:  # 3：u[R]=k*R/A*u[A]（R=k/A）
                unc = obj * equ / self.equ() * unc
                if Uncertainty.process:
                    if obj == 1:
                        uncLSym = equLSym / self.equLSym() * uncLSym
                    else:
                        uncLSym = obj * equLSym / self.equLSym() * uncLSym
            elif calId == 8:  # 8：u[R]=ln(a)*u[A]*R（R=a**A，包括R=e**A和R=10**A）
                if obj == const.E:
                    unc = unc * equ
                    if Uncertainty.process:
                        uncLSym = uncLSym * equLSym
                elif obj == 10:
                    unc = 2.303 * unc * equ
                    if Uncertainty.process:
                        uncLSym = 2.303 * uncLSym * equLSym
                else:
                    if type(obj) == Const:
                        unc = math.log(obj.value()) * unc * equ
                    else:
                        unc = math.log(obj) * unc * equ
                    if Uncertainty.process:
                        uncLSym = const.ln(obj) * uncLSym * equLSym
            elif calId == 9:  # 9：u[R]=u[A]/A（R=lnA）
                unc = unc / self.equ()
                if Uncertainty.process:
                    uncLSym = uncLSym / self.equLSym()
            elif calId == 10:  # 10：u[R]=0.4343*u[A]/A（R=lgA）
                unc = 0.4343 * unc / self.equ()
                if Uncertainty.process:
                    uncLSym = 0.4343 * (uncLSym / self.equLSym())
            return self._Uncertainty__newInstance(calId, [], unc, equ, uncLSym, equLSym)
        elif calId == 4:  # 4：R=A+B，R=A-B，R=B+A，R=B-A
            if self.__prevCalId == 4:  #若self的上一步是加减，则进行如下合并，暂时不计算不确定度
                item = self.__item
                if len(obj.__item) == 0:  #若obj的上一步的组为空组，说明上一步时独立的运算而不是加减组，故直接添加上一步的独立运算到组中
                    item.append(obj)
                else:  #若上一步的组不是空组，说明上一步时是加减组，故直接添加上一步的加减组与当前的加减组合并
                    item += obj.__item
            elif obj.__prevCalId == 4:  #若obj的上一步是加减，则进行如下合并，暂时不计算不确定度
                item = [self] + obj.item  #self的上一步是加减，则self的item一定为空，故直接把self当作独立的运算添加到obj的加减组中
            else:  #若上一步不是加减（self和obj都不是加减），则创建item，并将当前不确定度和不确定度obj（Uncertainty）添加到item中
                if self.__prevCalId == 5:  #对于5运算，执行其运算并将结果放置到self中
                    unc, uncLSym = self.__combCal5()
                    self.__unc = unc
                    self.__uncLSym = uncLSym
                item = [self, obj]
            return self._Uncertainty__newInstance(calId, item, self.unc(), equ, self.uncLSym(), equLSym)
        elif calId == 5:  # 5：R=A*B，R=B*A，R=A/B，R=B/A
            if self.__prevCalId == 5:  #若上一步是乘除，则将不确定度obj（Uncertainty）添加到item中，暂时不计算不确定度
                item = self.__item
                if len(obj.__item) == 0:  #若上一步的组为空组，说明上一步时独立的运算而不是乘除组，故直接添加上一步的独立运算到组中
                    item.append(obj)
                else:  #若上一步的组不是空组，说明上一步时是乘除组，故直接添加上一步的加减组与当前的加减组合并
                    item += obj.__item
            elif obj.__prevCalId == 5:  #若obj的上一步是乘除，则进行如下合并，暂时不计算不确定度
                item = [self] + obj.__item   #self的上一步是乘除，则self的item一定为空，故直接把self当作独立的运算添加到obj的乘除组中
            else:  #若上一步不是乘除，则创建item，并将当前不确定度和不确定度obj（Uncertainty）添加到item中
                if self.__prevCalId == 4:  #对于4运算，执行其运算并将结果放置到self中
                    unc, uncLSym = self.__combCal4()
                    self.__unc = unc
                    self.__uncLSym = uncLSym
                item = [self, obj]
            return self._Uncertainty__newInstance(calId, item, self.unc(), equ, self.uncLSym(), equLSym)
        elif calId == 6:  # 6：R=A**k
            if self.__prevCalId == 6:  #若上一步是幂运算，则只改变prevExp中的b，不改变equ和equLSym，暂时不计算不确定度
                rexp = self.__prevExp
                rexp['b'] = rexp['b'] * obj
            else:  #若上一步不是幂运算，则创建rexp，并将当前（幂运算之前的）幂指数obj、equ和equLSym添加到rexp中
                if self.__prevCalId in (4, 5, 7):  #对于4、5、7三种运算，执行其运算并将结果放置到self中
                    if self.__prevCalId == 4:
                        unc, uncLSym = self.__combCal4()
                    elif self.__prevCalId == 5:
                        unc, uncLSym = self.__combCal5()
                    elif self.__prevCalId == 7:
                        unc, uncLSym = self.__cal7()
                    self.__unc = unc
                    self.__uncLSym = uncLSym
                rexp = {'b': obj, 'equ': self.equ(), 'equLSym': self.equLSym()}
            return self._Uncertainty__newInstance(calId, [], self.unc(), equ, self.uncLSym(), equLSym, prevExp = rexp)
        elif calId == 7:  # 7：R=sqrt(A,k)
            if self.__prevCalId == 7:  #若上一步是求根运算，则只改变prevRoot中的r，不改变equ和equLSym，暂时不计算不确定度
                root = self.__prevRoot
                root['r'] = root['r'] * obj
            else:  #若上一步不是求根运算，则创建root，并将当前（求根运算之前的）根指数r、equ和equLSym添加到root中
                if self.__prevCalId in (4, 5, 6):  #对于4、5、6三种运算，执行其运算并将结果放置到self中
                    if self.__prevCalId == 4:
                        unc, uncLSym = self.__combCal4()
                    elif self.__prevCalId == 5:
                        unc, uncLSym = self.__combCal5()
                    elif self.__prevCalId == 6:
                        unc, uncLSym = self.__cal6()
                    self.__unc = unc
                    self.__uncLSym = uncLSym
                root = {'r': obj, 'equ': self.equ(), 'equLSym': self.equLSym()}
            return self._Uncertainty__newInstance(calId, [], self.unc(), equ, self.uncLSym(), equLSym, prevRoot = root)
        
    def setK(self, K):
        '''设置扩展不确定度的K值'''
        if K not in KTable:
            raise keyNotInTableException('找不到K=%s时对应的置信区间')
        self.__K = K
        
    def __res(self):
        if self.__prevCalId == 4:
            unc, uncLSym = self.__combCal4()
        elif self.__prevCalId == 5:
            unc, uncLSym = self.__combCal5(isRate=True)
        elif self.__prevCalId == 6:
            unc, uncLSym = self.__cal6()
        elif self.__prevCalId == 7:
            unc, uncLSym = self.__cal7()
        else:
            unc, uncLSym = self.unc(), self.uncLSym()
        res = {}
        unc.setIsRelative(True)
        res['unc'] = unc
        res['isRate'] = (self.__prevCalId == 5)
        res['K'] = self.__K
        if self.__K != None:
            res['P'] = KTable[self.__K]
        if Uncertainty.process:
            res['uncLSym'] = uncLSym
        return res
    
    def result(self):
        '''获得不确定度
        【返回值】
        Num：K=1时，为标准不确定度数值；K>1时，为扩展不确定度数值。
        '''
        if self.__prevCalId == 4:
            unc = self.__combCal4()[0]
        elif self.__prevCalId == 5:
            unc = self.__combCal5()[0]
        elif self.__prevCalId == 6:
            unc = self.__cal6()[0]
        elif self.__prevCalId == 7:
            unc = self.__cal7()[0]
        else:
            unc = self.unc()
        if self.__K != None:
            unc = self.__K * unc
        return unc