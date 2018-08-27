# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 07:16:27 2018

@author: xingrongtech
"""

import numpy
from math import sqrt, log10, floor
from quantities.quantity import Quantity
from .num import Num
from .const import Const
from .latexoutput import LaTeX
from .lookup import t, t_repl
from .system.unit_open import openUnit, closeUnit
from .system.format_units import format_units_unicode, deg
from .system.statformat import statFormat, getMaxDeltaDigit
from .system.exceptions import expressionInvalidException, muNotFoundException, itemNotSameLengthException

class NumItem():
    '''NumItem类为分析数组类，该类具有以下特性：
    1.作为分析数值的容器，能够实现批量初始化，以及增删添改Num数值；
    2.支持仿Matlab数组运算，可以将整个数组与一个纯数字、一个数值或另一个数组进行运算，从而避免了繁琐的for循环；
    3.支持基本的、对单个数组的数理统计功能，包括偏差、误差、置信区间和t检验。'''
    __arr = []
    __q = 1
    __index = 0
    __mu = None
    __sym = None
    __gd_valid = 0
    __isRelative = False
    
    def __init__(self, nums, unit=None, mu=None, sym=None, muSym=r'\mu'):
        '''初始化一个NumItem数组
        【参数说明】
        1.nums：要初始化的数值，可以是str或list：
        (1)str：对于还没有转换成Num的数值，将数值以空格隔开，表示成字符串表达式。
        (2)list<Num>：对于已经转换成Num的数值，将数值用list表示出。
        (3)list<LSym>：从由LSym符号形成的list中获取Num数值，生成NumItem。
        (4)LSymItem：从由LSymItem符号组中获取Num数值，生成NumItem。
        2.unit（可选，str）：单位。当unit为None时，会选择list<Num>或list<LSym>中第1个元素的unit，或者LSymItem的unit作为NumItem的unit，否则没有单位。默认unit=None。
        3.mu（可选，str）：真值μ，用于误差分析。默认不给出，但进行误差分析时，必须给出μ。默认mu=None。
        4.sym（可选，str）：符号，一般情况下不需要给出，当需要展示计算过程时，最好给出。默认sym=None。
        5.muSym（可选，str）：真值μ对应的符号，默认muSym=r'\mu'。
        【应用举例】
        >>> t = NumItem('1.62 1.66 1.58 1.71 1.69')
        >>>
        >>> p1, p2, p3 = Num('13.42'), Num('13.52'), Num('13.49')
        >>> p = NumItem([p1, p2, p3])
        >>>
        >>> t = NumItem('1.62 1.66  58 1.71 1.69', mu='1.65')
        >>> w = NumItem('38.42 38.56 38.47 38.41 38.55')
        >>> t = NumItem('1.62 1.66 1.58 1.71 1.69', 's', sym='t')
        【错误案例】
        >>> t = NumItem(1.62,1.66,1.58,1.71,1.69)  #不能直接用float或int初始化数组
        >>> t = NumItem([1.62,1.66,1.58,1.71,1.69])  #使用list初始化数组时，数值必须是Num
        >>> t = NumItem('1.62,1.66,1.58,1.71,1.69')  #数值之间应该用空格，而不是逗号或其他符号隔开
        >>>
        >>> p1, p2, p3 = Num('13.42'), Num('13.52'), Num('13.49')
        >>> p = NumItem(p1, p2, p3)  #使用list初始化数组时，应将Num用中括号括住，表示是一个list
        '''
        if nums == None:
            return
        if unit != None:
            self.__q = Quantity(1., unit) if type(unit) == str else unit
        if type(nums) == str:
            strArr = nums.split(' ')
            self.__arr = [Num(s) for s in strArr]
            if unit != None:
                for ri in self.__arr:
                    ri._Num__q = self.__q
        elif type(nums) == list:
            if len(nums) == 0:
                self.__arr = []
            elif type(nums[0]) == Num:
                self.__arr = nums
            elif str(type(nums[0])) == "<class 'analyticlab.lsym.LSym'>":
                self.__arr = [ni.num() for ni in nums]
                if unit == None:
                    self.__q = self.__arr[0]._Num__q
            else:
                raise expressionInvalidException('用于创建数组的参数无效')
            if unit == None and len(self.__arr) > 0:
                self.__q = self.__arr[0]._Num__q
            else:
                for ri in self.__arr:
                    ri._Num__q = self.__q
        elif str(type(nums)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            if type(nums._LSymItem__lsyms) == list:
                lsymList = nums._LSymItem__lsyms
            else:
                lsymList = list(nums._LSymItem__lsyms.values())
            self.__arr = [li.num() for li in lsymList]
            if unit == None:
                self.__q = self.__arr[0]._Num__q
            else:
                for ri in self.__arr:
                    ri._Num__q = self.__q
        else:
            raise expressionInvalidException('用于创建数组的参数无效')
        if mu != None:
            if type(mu) == str:
                self.__mu = Num(mu, self.__q)
            elif type(mu) == Num:
                if mu._Num__q != self.__q:
                    self.__mu = mu
                    self.__mu._Num__q = self.__q
                else:
                    self.__mu = mu
            else:
                raise expressionInvalidException('真值参数无效，真值只能以数值或字符串形式给出')
            self.__muSym = muSym
        if len(self.__arr) > 0:
            self.__findGeneralValid()
        if sym == None:
            self.__sym = '{x_{%d}}' % id(self)
        else:
            self.__sym = '{%s}' % sym
        
    def __newInstance(self, arr, q=1, mu=None, isRelative=False, sym=None, dv=None, qIsUpdate=True):
        '''创建新的NumItem实例'''
        new = NumItem(None)
        new.__arr = arr
        new.__q = q
        if qIsUpdate:
            for ri in arr:
                ri._Num__q = q
        new.__mu = mu
        new.setIsRelative(isRelative)
        new.__sym = sym
        if len(arr) > 0 and dv == None:
            new.__findGeneralValid()
        else:
            new.__gd_valid = dv
        return new
        
    def __findGeneralValid(self):
        '''获得数组总体有效数字'''
        gd_front = max([n._Num__d_front for n in self.__arr])  #取小数点前位数最大者作为小数点前位数
        if gd_front > 0:  #对于首位在小数点前的数值
            gd_behind = min([ti._Num__d_behind for ti in self.__arr])  #取小数点后位数最小者作为小数点后位数
            self.__gd_valid = gd_front + gd_behind
            delta = max([(ti._Num__d_front - ti._Num__d_valid) for ti in self.__arr]);
            #若存在某个数的个位不是有效位的情况，减去小数点前有效零位中的较大者
            if (delta > 0):
                self.__gd_valid -= delta
        else:  #对于首位在小数点后的数值
            max_digit = max([(ti._Num__d_valid - ti._Num__d_behind) for ti in self.__arr])
            min_digitbehind = min([ti._Num__d_behind for ti in self.__arr])
            self.__gd_valid = min_digitbehind + max_digit
    
    def __sciDigit(self):
        '''获得整体科学记数法的指数'''
        minNum = min([abs(ni) for ni in self.__arr if ni._Num__value != 0])  #以绝对值最小的数的科学记数法指数作为整体指数
        if minNum._Num__value == 0:
            return 0
        elif abs(floor(log10(abs(minNum._Num__value)))) >= minNum._Num__sci_bound:
            if minNum._Num__d_front > 0:  #对于首个有效位在小数点前的数值
                theory_digit = max(minNum._Num__d_valid, minNum._Num__d_front) - minNum._Num__d_behind  #理论小数点前位数
                if abs(theory_digit - 1) >= minNum._Num__sci_bound:  #通过理论有效数字位数再次检验是否需要使用科学记数法
                    return (theory_digit - 1)
                else:  #若转换后的数字数量级过小，不使用科学记数法
                    return 0
            else:  #对于首个有效位在小数点后的数值
                theory_digit = minNum._Num__d_behind - minNum._Num__d_valid  #理论小数点后位数
                if abs(theory_digit + 1) >= minNum._Num__sci_bound:
                    return -(theory_digit + 1)
                else:
                    return 0
        else:
            return 0
        
    def __qUpdate(self):
        for ri in self.__arr:
            ri._Num__q = self.__q
        
    def __getitem__(self, index):
        if type(index) == int:
            return self.__arr[index]
        elif type(index) == slice:
            return self.__newInstance(self.__arr[index], self.__q, mu=self.__mu, isRelative=self.__isRelative, dv=self.__gd_valid, qIsUpdate=False)
    
    def __setitem__(self, k, v):
        self.__arr[k] = v
        self.__findGeneralValid()
        
    def __delitem__(self, index):
        del self.__arr[index]
        self.__findGeneralValid()
    
    def append(self, v):
        '''扩充当前数组
        【参数说明】
        v：可以是Num或NumItem：
        (1)Num：给出要添加的数值，新添加的数值会增加到原数组的尾部。
        (2)NumItem：给出要添加的数组，新添加的数组会扩充到原数组的尾部。
        【应用举例】
        >>> m1 = NumItem('1.0364 1.0359 1.0362')
        >>> m2 = NumItem('1.0732 1.0739 1.0722')
        >>> m1.append(Num('1.0358'))
        >>> m1
        [1.0364, 1.0359, 1.0362, 1.0358]
        >>> m1.append(m2)
        >>> m1
        [1.0364, 1.0359, 1.0362, 1.0358, 1.0732, 1.0739, 1.0722]
        
        '''
        if type(v) == Num:
            self.__arr.append(v)
        elif type(v) == NumItem:  #合并两个数组
            for ni in v.__arr:
                self.__arr.append(ni)
        self.__findGeneralValid()
        
    def __len__(self):
        '''获得数组的元素个数
        【返回值】
        int：数组元素个数。'''
        return len(self.__arr)
    
    def __str__(self):
        '''获得数组的文本格式
        【返回值】
        str：数组文本。'''
        itemExpr = '[%s]' % ', '.join([ri.strNoUnit() for ri in self.__arr])
        unitExpr = format_units_unicode(self.__q)
        if unitExpr != '' and self.__q.dimensionality != deg.dimensionality:
            itemExpr += ' ' + unitExpr
        return itemExpr
    
    def __repr__(self):
        '''获得数组的文本格式
        【返回值】
        str：数组文本。'''
        return str(self)
        
    def latex(self):
        '''获得数组的LaTeX格式
        【返回值】
        str：数组的LaTeX格式文本。'''
        unitExpr = format_units_unicode(self.__q)
        if unitExpr != '' and self.__q.dimensionality != deg.dimensionality:
            return r'\left[%s\right]%s' % (','.join([n.dlatex() for n in self.__arr]), unitExpr)
        else:
            return r'\left[%s\right]' % ','.join([n.dlatex() for n in self.__arr])
    
    def remainOneMoreDigit(self):
        '''设定多保留一位有效数字'''
        [n.remainOneMoreDigit() for n in self.__arr]
        
    def cutOneDigit(self):
        '''设定少保留一位有效数字'''
        [n.cutOneDigit() for n in self.__arr] 
        
    def __add__(self, obj):
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            new = self.__newInstance([n.__add__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid, qIsUpdate=False)
        elif type(obj) == Num:
            new = self.__newInstance([n.__add__(obj) for n in self.__arr], self.__q, qIsUpdate=False)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__add__(obj.__arr[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__add__(obj[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        return new
    
    def __radd__(self, obj):
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            new = self.__newInstance([n.__radd__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid, qIsUpdate=False)
        elif type(obj) == Num:
            new = self.__newInstance([n.__radd__(obj) for n in self.__arr], self.__q, qIsUpdate=False)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__radd__(obj.__arr[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__radd__(obj[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        return new
    
    def __sub__(self, obj):
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            new = self.__newInstance([n.__sub__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid, qIsUpdate=False)
        elif type(obj) == Num:
            new = self.__newInstance([n.__sub__(obj) for n in self.__arr], self.__q, qIsUpdate=False)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__sub__(obj.__arr[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__sub__(obj[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        return new
    
    def __rsub__(self, obj):
        if type(obj) == int or type(obj) == float or type(obj) == Const:
            new = self.__newInstance([n.__rsub__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid, qIsUpdate=False)
        elif type(obj) == Num:
            new = self.__newInstance([n.__rsub__(obj) for n in self.__arr], self.__q, qIsUpdate=False)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__rsub__(obj.__arr[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__rsub__(obj[i]))
            new = self.__newInstance(newArr, self.__q, sym=self.__sym, qIsUpdate=False)
        return new
    
    def __mul__(self, obj):
        closeUnit()
        if type(obj) == int or type(obj) == float:
            new = self.__newInstance([n.__mul__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid)
        elif type(obj) == Const:
            new = self.__newInstance([n.__mul__(obj) for n in self.__arr], self.__q * obj._Const__q, dv=self.__gd_valid)
        elif type(obj) == Num:
            new = self.__newInstance([n.__mul__(obj) for n in self.__arr], self.__q * obj._Num__q)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__mul__(obj.__arr[i]))
            new = self.__newInstance(newArr, self.__q * obj.__q)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__mul__(obj[i]))
            new = self.__newInstance(newArr, self.__q)
        for ri in new.__arr:
            ri._Num__q = new.__q
        openUnit()
        return new
    
    def __rmul__(self, obj):
        closeUnit()
        if type(obj) == int or type(obj) == float:
            new = self.__newInstance([n.__rmul__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid)
        elif type(obj) == Const:
            new = self.__newInstance([n.__rmul__(obj) for n in self.__arr], obj._Const__q * self.__q, dv=self.__gd_valid)
        elif type(obj) == Num:
            new = self.__newInstance([n.__rmul__(obj) for n in self.__arr], obj._Num__q * self.__q)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__rmul__(obj.__arr[i]))
            new = self.__newInstance(newArr, obj.__q * self.__q)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__rmul__(obj[i]))
            new = self.__newInstance(newArr, self.__q)
        for ri in new.__arr:
            ri._Num__q = new.__q
        openUnit()
        return new
    
    def __truediv__(self, obj):
        closeUnit()
        if type(obj) == int or type(obj) == float:
            new = self.__newInstance([n.__truediv__(obj) for n in self.__arr], self.__q, dv=self.__gd_valid)
        elif type(obj) == Const:
            new = self.__newInstance([n.__truediv__(obj) for n in self.__arr], self.__q / obj._Const__q, dv=self.__gd_valid)
        elif type(obj) == Num:
            new = self.__newInstance([n.__truediv__(obj) for n in self.__arr], self.__q / obj._Num__q)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__truediv__(obj.__arr[i]))
            new = self.__newInstance(newArr, self.__q / obj.__q)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__truediv__(obj[i]))
            new = self.__newInstance(newArr, self.__q)
        for ri in new.__arr:
            ri._Num__q = new.__q
        openUnit()
        return new
    
    def __rtruediv__(self, obj):
        closeUnit()
        if type(obj) == int or type(obj) == float:
            new = self.__newInstance([n.__rtruediv__(obj) for n in self.__arr], 1/self.__q)
        elif type(obj) == Const:
            new = self.__newInstance([n.__rtruediv__(obj) for n in self.__arr], obj._Const__q / self.__q)
        elif type(obj) == Num:
            new = self.__newInstance([n.__rtruediv__(obj) for n in self.__arr], obj._Num__q / self.__q)
        elif type(obj) == NumItem:
            if len(self.__arr) != len(obj.__arr):
                raise itemNotSameLengthException('进行数组运算的两个数组元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__rtruediv__(obj.__arr[i]))
            new = self.__newInstance(newArr, obj.__q / self.__q)
        elif type(obj) == list and (type(obj[0]) == int or type(obj[0]) == float):
            if len(self.__arr) != len(obj):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__rtruediv__(obj[i]))
            new = self.__newInstance(newArr, 1/self.__q)
        for ri in new.__arr:
            ri._Num__q = new.__q
        openUnit()
        return new
    
    def __pow__(self, b):
        closeUnit()
        if type(b) == int or type(b) == float:
            new = self.__newInstance([n.__pow__(b) for n in self.__arr], self.__q**b, dv=self.__gd_valid)
        elif type(b) == Const:
            new = self.__newInstance([n.__pow__(b) for n in self.__arr], self.__q**b.value(), dv=self.__gd_valid)
        elif type(b) == list and (type(b[0]) == int or type(b[0]) == float):
            if len(self.__arr) != len(b):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__pow__(b[i]))
            new = self.__newInstance(newArr)
        for ri in new.__arr:
            ri._Num__q = new.__q
        openUnit()
        return new
    
    def __rpow__(self, a):
        closeUnit()
        if type(a) == int or type(a) == float or type(a) == Const:
            new = self.__newInstance([n.__rpow__(a) for n in self.__arr])
        elif type(a) == list and (type(a[0]) == int or type(a[0]) == float):
            if len(self.__arr) != len(a):
                raise itemNotSameLengthException('进行数组运算的纯数字列表与数组的元素个数必须一致！')
            newArr = []
            for i in range(len(self.__arr)):
                newArr.append(self.__arr[i].__pow__(a[i]))
            new = self.__newInstance(newArr)
        for ri in new.__arr:
            ri._Num__q = new.__q
        openUnit()
        return new
    
    def resetUnit(self, unit=None):
        '''重设NumItem数组的单位
        【参数说明】
        unit（可选，str）：重设后的单位。默认unit=None，即没有单位。'''
        if unit == None:
            self.__q = 1
        else:
            self.__q = Quantity(1., unit) if type(unit) == str else unit
        self.__qUpdate()
    
    def setMu(self, mu):
        '''设定真值μ，用于误差分析
        【参数说明】
        sym（str）：要设定的真值。'''
        if type(mu) == str:
            self.__mu = Num(mu)
        elif type(mu) == Num:
            self.__mu = mu
            
    def setSym(self, sym):
        '''设定符号
        【参数说明】
        sym（str）：要设定的符号。'''
        self.__sym = '{%s}' % sym
        
    def setMuSym(self, muSym):
        '''设定真值的符号
        【参数说明】
        muSym（str）：要设定的真值符号。'''
        self.__muSym = muSym
        
    def sym(self):
        '''获得数组的符号
        【返回值】
        str：数组的符号。
        '''
        return self.__sym
    
    def muSym(self):
        '''获得真值的符号
        【返回值】
        str：真值的符号。
        '''
        return self.__muSym
    
    def __abs__(self):
        return self.__newInstance([n.__abs__() for n in self.__arr], self.__q, dv=self.__gd_valid)
    
    def __neg__(self):
        return self.__newInstance([n.__neg__() for n in self.__arr], self.__q, dv=self.__gd_valid)
    
    def __next__(self):
        if self.__index >= len(self.__arr):
            self.__index = 0
            raise StopIteration
        else:
            result = self.__arr[self.__index]
            self.__index += 1
            return result
    
    def setIsRelative(self, isRelative):
        '''设定是否为相对比（百分数形式）
        【参数说明】
        isRelative（bool）：是否为相对比。'''
        [n.setIsRelative(isRelative) for n in self.__arr]
        self.__isRelative = isRelative
        
    def toFloatList(self):
        '''将当前数组转换成float列表
        【返回值】
        list<float>：数值的float形式组成的列表。'''
        return [float(n._Num__value) for n in self.__arr]
    
    def toIntList(self):
        '''将当前数组转换成int列表
        【返回值】
        list<float>：数值的int形式组成的列表。'''
        return [int(n._Num__value) for n in self.__arr]
    
    def toNumpyArray(self):
        '''将当前数组转换成numpy数组
        【返回值】
        list<float>：新生成的numpy数组。'''
        return numpy.array([float(n._Num__value) for n in self.__arr])
        
    def fix(self):
        '''数字修约
        【返回值】
        NumItem：修约后的NumItem数组。'''
        return self.__newInstance([n.fix() for n in self.__arr], self.__q, sym=self.__sym, dv=self.__gd_valid, qIsUpdate=False)
    
    def sort(self, rev=False):
        '''获得排序后的数组
        【参数说明】
        rev（bool）：是否降序排列，False为升序排列，True为降序排列。默认rev=False。
        【返回值】
        NumItem：排序后的数组
        【应用举例】
        >>> h = NumItem('1.52 1.55 1.56 1.51 1.55 1.53')
        >>> h.sort()
        [1.51, 1.52, 1.53, 1.55, 1.55, 1.56]
        >>> h.sort(rev=True)
        [1.56, 1.55, 1.55, 1.53, 1.52, 1.51]'''
        s = sorted(self.__arr, reverse=rev)
        return self.__newInstance(s, self.__q, sym=self.__sym, mu=self.__mu, isRelative=self.__isRelative, dv=self.__gd_valid, qIsUpdate=False)
    
    def setSciBound(self, bound):
        '''设定数组中的数值使用科学记数法的边界条件
        【参数说明】
        bound（int）：使用科学计数法的指数边界，即数值小于等于10**(-bound)数量级，或大于等于10**bound数量级时，使用科学记数法；否则仍使用一般数字表示法。未设定边界时，默认bound=3。
        【应用举例】
        >>> d = NumItem('15023 15029 15017 15020')
        >>> d
        [1.5023e+04, 1.5029e+04, 1.5017e+04, 1.5020e+04]
        >>> d.setSciBound(5)
        >>> d
        [15023, 15029, 15017, 15020]'''
        [n.setSciBound(bound) for n in self.__arr]
    
    def isum(self, process=False, needValue=False):
        '''数组求和
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为Num类型的和。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为Num类型的和和LaTeX类型的计算过程组成的元组。'''
        s = Num(None)
        s._Num__value = sum([n._Num__value for n in self.__arr])
        s._Num__d_front = max([n._Num__d_front for n in self.__arr])  #取小数点前位数较大者作为小数点前位数
        s._Num__d_behind = min([n._Num__d_behind for n in self.__arr if n._Num__value != 0])  #取小数点后位数较小者作为小数点后位数
        s._Num__d_valid = self.__gd_valid
        s._Num__q = self.__q
        s = s.fix()
        if process:
            latex = LaTeX()
            sciDigit = self.__sciDigit()
            if sciDigit == 0:
                sumExpr = '+'.join([n.dlatex(2) for n in self.__arr])
                latex.add(r'\sum\limits_{i=1}^n %s_{i}=%s=%s' % (self.__sym, sumExpr, s.latex()))
            else:
                d_arr = self * 10**(-sciDigit)
                sumExpr = '+'.join([n.dlatex(2) for n in d_arr])
                if len([x for x in self.__arr if x < 0]) == 0:
                    latex.add(r'\sum\limits_{i=1}^n %s_{i}=\left(%s\right)\times 10^{%d}=%s' % (self.__sym, sumExpr, sciDigit, s.latex()))
                else:
                    latex.add(r'\sum\limits_{i=1}^n %s_{i}=\left[%s\right]\times 10^{%d}=%s' % (self.__sym, sumExpr, sciDigit, s.latex()))
            if needValue:
                return s, latex
            else:
                return latex
        return s
    
    def mean(self, process=False, needValue=False, dec=False):
        '''样本均值（mean）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        3.dec（可选，bool）：是否已纯数字形式（int或float）给出样本均值。dec为True时，以纯数字形式给出；为False时，以数值（Num）形式给出。注意当dec=True时，process将会无效。默认dec=False。
        【返回值】
        ①dec为True时，返回值为float类型的纯数字样本均值；
        ②dec为False时：
        A.process为False时，返回值为Num类型的样本均值。
        B.process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        C.process为True且needValue为True时，返回值为Num类型的样本均值和LaTeX类型的计算过程组成的元组。
        '''
        x = Num(None)
        x._Num__value = sum([n._Num__value for n in self.__arr]) / len(self.__arr)
        x._Num__d_front = max([ti._Num__d_front for ti in self.__arr])  #取小数点前位数较大者作为小数点前位数
        x._Num__d_behind = min([ti._Num__d_behind for ti in self.__arr if ti._Num__value != 0])  #取小数点后位数较小者作为小数点后位数
        x._Num__d_valid = self.__gd_valid
        x._Num__q = self.__q
        result = x
        if dec:
            return result._Num__value
        else:
            if process:
                latex = LaTeX()
                sciDigit = self.__sciDigit()
                if sciDigit == 0:
                    sumExpr = '+'.join([n.dlatex(2) for n in self.__arr])
                    if len([x for x in self.__arr if x < 0]) == 0:
                        latex.add(r'\overline{%s}=\cfrac{1}{n}\sum\limits_{i=1}^n %s_{i}=\cfrac{1}{%d}\left(%s\right)=%s' % (self.__sym, self.__sym, len(self.__arr), sumExpr, result.latex()))
                    else:
                        latex.add(r'\overline{%s}=\cfrac{1}{n}\sum\limits_{i=1}^n %s_{i}=\cfrac{1}{%d}\left[%s\right]=%s' % (self.__sym, self.__sym, len(self.__arr), sumExpr, result.latex()))
                else:
                    d_arr = self * 10**(-sciDigit)
                    sumExpr = '+'.join([n.dlatex(2) for n in d_arr])
                    if len([x for x in self.__arr if x < 0]) == 0:
                        latex.add(r'\overline{%s}=\cfrac{1}{n}\sum\limits_{i=1}^n %s_{i}=\cfrac{1}{%d}\left(%s\right)\times 10^{%d}=%s' % (self.__sym, self.__sym, len(self.__arr), sumExpr, sciDigit, result.latex()))
                    else:
                        latex.add(r'\overline{%s}=\cfrac{1}{n}\sum\limits_{i=1}^n %s_{i}=\cfrac{1}{%d}\left[%s\right]\times 10^{%d}=%s' % (self.__sym, self.__sym, len(self.__arr), sumExpr, sciDigit, result.latex()))
                if needValue:
                    return result, latex
                else:
                    return latex
            return result
    
    def mid(self, process=False, needValue=False):
        '''中位数
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为Num类型的中位数。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为Num类型的中位数和LaTeX类型的计算过程组成的元组。'''
        s = sorted(self.__arr)
        n = len(s)
        if n % 2 == 1:  #若数值个数为奇数个，取最中间的数（例：5个元素，取2）
            res = s[n//2]
        else:  #若数值个数为偶数个，取最中间的相邻两个数（例：6个元素，取2和3）
            res = (s[n//2-1]+s[n//2]) / 2
        if process:
            latex = LaTeX(r'\text{数值从小到大排序得}%s=%s' % (self.__sym, NumItem(s, self.__q).latex()))
            if n % 2 == 1:
                latex.add(r'\text{中位数为}%s_{%d}=%s' % (self.__sym, n//2+1, res.latex()))
            else:
                latex.add(r'\text{中位数为}\cfrac{%s_{%d}+%s_{%d}}{2}=\cfrac{%s+%s}{2}=%s' % (self.__sym, n//2, self.__sym, n//2+1, s[n//2-1].dlatex(), s[n//2].dlatex(), res.latex()))  
            if needValue:
                return res, latex
            else:
                return latex
        return res
    
    def devi(self, process=False, needValue=False):
        '''偏差（deviation）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为NumItem类型的数组中各数值与样本均值的偏差组成的数组。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为NumItem类型的数组中各数值与样本均值的偏差组成的数组和LaTeX类型的计算过程组成的元组。'''
        mean = self.mean()
        result = (self - mean).fix()
        result.setSym('d')
        if process:
            mean, latex = self.mean(process=True, needValue=True)
            meanExpr = mean.dlatex(2)
            latex = LaTeX(r'\text{根据公式}d_{i}=%s_{i}-\overline{%s}\text{，得}' % (self.__sym, self.__sym))
            for i in range(len(self.__arr)):
                latex.add(r'd_{%d}=%s-%s=%s' % (i+1, self.__arr[i].dlatex(), meanExpr, result[i].latex()))
            if needValue:
                return result, latex
            else:
                return latex
        return result
        
    
    def staDevi(self, process=False, processWithMean=True, needValue=False, dec=False, remainOneMoreDigit=False):
        '''样本标准偏差（standard deviation）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.processWithMean（可选，bool）：在获得计算过程时，是否展示均值的计算过程。注意该参数仅在process=True时有效。默认processWithMean=True。
        3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        4.dec（可选，bool）：是否已纯数字形式（int或float）给出样本标准偏差。dec为True时，以纯数字形式给出；为False时，以数值（Num）形式给出。注意当dec=True时，其余参数都将无效。默认dec=False。
        5.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
        【返回值】
        ①dec为True时，返回值为float类型的纯数字标准偏差；
        ②dec为False时：
        A.process为False时，返回值为Num类型的标准偏差。
        B.process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        C.process为True且needValue为True时，返回值为Num类型的标准偏差和LaTeX类型的计算过程组成的元组。'''
        if dec:
            mean = self.mean(dec=True)
            dsum = sum([(ni._Num__value - mean)**2 for ni in self.__arr])
            return sqrt(dsum / (len(self.__arr) - 1))
        else:
            latex = LaTeX()
            if process and processWithMean:
                mean, lsub = self.mean(process=True, needValue=True)
                latex.add(lsub)
            else:
                mean = self.mean()
            dsum = sum([(ni._Num__value - mean._Num__value)**2 for ni in self.__arr])
            res = sqrt(dsum / (len(self.__arr) - 1))
            result = statFormat(getMaxDeltaDigit(self, mean), res)
            result._Num__q = self.__q
            if remainOneMoreDigit:
                result.remainOneMoreDigit()
            if process:
                p_delta = self - mean
                sciDigit = self.__sciDigit()
                if sciDigit == 0:
                    sumExpr = '+'.join([(r'%s^2' % di.dlatex(1)) for di in p_delta])
                    latex.add(r's_{%s}=\sqrt{\cfrac{1}{n-1}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^2}=\sqrt{\cfrac{1}{%d}\left[%s\right]}=%s' % (self.__sym, self.__sym, self.__sym, len(self.__arr)-1, sumExpr, result.latex()))
                else:
                    d_delta = p_delta * 10**(-sciDigit)
                    sumExpr = '+'.join([(r'%s^2' % di.dlatex(1)) for di in d_delta])
                    latex.add(r's_{%s}=\sqrt{\cfrac{1}{n-1}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^2}=\sqrt{\cfrac{1}{%d}\left[%s\right]}\times 10^{%d}=%s' % (self.__sym, self.__sym, self.__sym, len(self.__arr)-1, sumExpr, sciDigit, result.latex()))
                if needValue:
                    return result, latex
                else:
                    return latex
            return result
    
    def relStaDevi(self, process=False, needValue=False):
        '''相对标准偏差/变异系数（RSD/CV）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为Num类型的相对标准偏差。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为Num类型的相对标准偏差和LaTeX类型的计算过程组成的元组。'''
        if process:
            mean, latex = self.mean(process, needValue=True)
            s, latex2 = self.staDevi(process, needValue=True, remainOneMoreDigit=True)
            latex.add(latex2)
        else:
            mean = self.mean()
            s = self.staDevi(remainOneMoreDigit=True)
        result = s / mean
        result.setIsRelative(True)
        if process:
            latex.add(r's_{r}=\cfrac{s_{%s}}{\overline{%s}}\times 100\%%=\cfrac{%s}{%s}\times 100\%%=%s' % (self.__sym, self.__sym, s.dlatex(), mean.dlatex(), result.latex()))
            if needValue:
                return result, latex
            else:
                return latex
        return result
    
    def relDevi(self, process=False, needValue=False):
        '''相对偏差（relative deviation）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为NumItem类型的数组中各数值与样本均值的相对偏差组成的数组。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为NumItem类型的数组中各数值与样本均值的相对偏差组成的数组和LaTeX类型的计算过程组成的元组。'''
        mean = self.mean()
        result = self / mean - 1
        result.setIsRelative(True)
        result.setSym('d_{r}')
        if process:
            mean, latex = self.mean(process=True, needValue=True)
            meanExpr = mean.dlatex()
            meanExpr2 = mean.dlatex(2)
            latex.add(r'根据公式d_{ri}=\cfrac{%s_{i}-\overline{%s}}{\overline{%s}}\times 100\%%，得' % (self.__sym, self.__sym, self.__sym))
            for i in range(len(self.__arr)):
                latex.add(r'd_{r%d}=\cfrac{%s-%s}{%s}\times 100\%%=%s' % (i+1, self.__arr[i].dlatex(), meanExpr2, meanExpr, result.__arr[i].latex()))
            if needValue:
                return result, latex
            else:
                return latex
        return result
    
    def avgDevi(self, process=False, needValue=False):
        '''平均偏差（average deviation）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为Num类型的平均偏差。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为Num类型的平均偏差和LaTeX类型的计算过程组成的元组。'''
        mean = self.mean()
        dsum = sum([abs(ni._Num__value - mean._Num__value) for ni in self.__arr])
        result = statFormat(getMaxDeltaDigit(self, mean), dsum / len(self.__arr))
        result._Num__q = self.__q
        if process:
            sciDigit = self.__sciDigit()
            fracExpr = r'\cfrac{1}{%d}' % len(self.__arr)
            p_mean, latex = self.mean(process=True, needValue=True)
            if sciDigit == 0:
                meanExpr = p_mean.dlatex(2)
                sumExpr = '+'.join([(r'\left\lvert %s-%s\right\rvert' % (xi.dlatex(3), meanExpr)) for xi in self.__arr])
                if len([x for x in self.__arr if x < 0]) == 0:
                    latex.add(r'\overline{d}=\cfrac{1}{n}\sum\limits_{i=1}^n\left\lvert %s_{i}-\overline{%s}\right\rvert= %s \left(%s\right)=%s' % (self.__sym, self.__sym, fracExpr, sumExpr, result.latex()))
                else:
                    latex.add(r'\overline{d}=\cfrac{1}{n}\sum\limits_{i=1}^n\left\lvert %s_{i}-\overline{%s}\right\rvert= %s \left[%s\right]=%s' % (self.__sym, self.__sym, fracExpr, sumExpr, result.latex()))
            else:
                d_arr = self * 10**(-sciDigit)
                meanExpr = (p_mean * 10**(-sciDigit)).dlatex(2)
                sumExpr = '+'.join([(r'\left\lvert %s-%s\right\rvert' % (xi.dlatex(3), meanExpr)) for xi in d_arr._NumItem__arr])
                if len([x for x in self.__arr if x < 0]) == 0:
                    latex.add(r'\overline{d}=\cfrac{1}{n}\sum\limits_{i=1}^n\left\lvert %s_{i}-\overline{%s}\right\rvert= %s \left(%s\right)\times 10^{%d}=%s' % (self.__sym, self.__sym, fracExpr, sumExpr, sciDigit, result.latex()))
                else:
                    latex.add(r'\overline{d}=\cfrac{1}{n}\sum\limits_{i=1}^n\left\lvert %s_{i}-\overline{%s}\right\rvert= %s \left[%s\right]\times 10^{%d}=%s' % (self.__sym, self.__sym, fracExpr, sumExpr, sciDigit, result.latex()))
            if needValue:
                return result, latex
            else:
                return latex
        return result
    
    def relAvgDevi(self, process=False, needValue=False):
        '''相对平均偏差（relative average deviation）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为Num类型的相对平均偏差。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为Num类型的相对平均偏差和LaTeX类型的计算过程组成的元组。'''
        if process:
            mean, latex = self.mean(process, needValue=True)
            d, latex2 = self.avgDevi(process, needValue=True)
            latex.add(latex2)
        else:
            mean = self.mean()
            d = self.avgDevi()
        result = d / mean
        result.setIsRelative(True)
        if process:
            latex.add(r'\overline{d}_{r}=\cfrac{\overline{d}}{\overline{%s}}\times 100\%%=\cfrac{%s}{%s} \times 100\%%=%s' % (self.__sym, d.dlatex(), mean.dlatex(), result.latex()))
            if needValue:
                return result, latex
            else:
                return latex
        return result
    
    def absErr(self, process=False, needValue=False, description=''):
        '''绝对误差（absolute error）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        3.description（可选，str）：当数组中只有一个数值，且需要在计算过程中的计算公式前面添加一些描述时，可以通过此参数添加描述。注意当数字中的数值个数超过一个时，该参数无效。默认description=''，即没有描述。
        【返回值】
        ①process为False时，返回值为NumItem类型的数组中各数值与真值的绝对误差组成的数组。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为NumItem类型的数组中各数值与真值的绝对误差组成的数组和LaTeX类型的计算过程组成的元组。'''
        try:
            result = (self - self.__mu._Num__value).fix()
            result.setSym('E')
            if process:
                latex = LaTeX()
                if len(self.__arr) == 1:
                    latex.add(r'\text{%s}E=%s-%s=%s-%s=%s' % (description, self.__sym, self.__muSym, self.__arr[0].dlatex(), self.__mu.dlatex(2), result[0].latex()))
                else:
                    latex.add(r'\text{根据公式}E_{i}=%s_{i}-%s，得' % (self.__sym, self.__muSym))
                    for i in range(len(self.__arr)):
                        latex.add('E_{%d}=%s-%s=%s' % (i+1, self.__arr[i].dlatex(), self.__mu.dlatex(2), result[i].latex()))
                if needValue:
                    return result, latex
                else:
                    return latex
            return result
        except:
            raise muNotFoundException('缺少真值，无法计算绝对误差')
    
    def relErr(self, process=False, needValue=False, description=''):
        '''相对误差（relative error）
        【参数说明】
        1.process（可选，bool）：是否获得计算过程。默认process=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        3.description（可选，str）：当数组中只有一个数值，且需要在计算过程中的计算公式前面添加一些描述时，可以通过此参数添加描述。注意当数字中的数值个数超过一个时，该参数无效。默认description=''，即没有描述。
        【返回值】
        ①process为False时，返回值为NumItem类型的数组中各数值与真值的相对误差组成的数组。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为NumItem类型的数组中各数值与真值的相对误差组成的数组和LaTeX类型的计算过程组成的元组。'''
        try:
            result = abs(self - self.__mu) / self.__mu
            result.setIsRelative(True)
            result.setSym('E_{r}')
            if process:
                latex = LaTeX()
                muExpr = self.__mu.dlatex()
                muExpr2 = self.__mu.dlatex(2)
                if len(self.__arr) == 1:
                    latex.add(r'\text{%s}E_{r}=\cfrac{\left|%s-%s\right|}{%s}\times 100\%%=\cfrac{\left\lvert %s-%s \right\rvert}{%s}\times 100\%%=%s' % (description, self.__sym, self.__muSym, self.__muSym, self.__arr[0].dlatex(), muExpr2, muExpr, result.__arr[0].latex()))
                else:
                    latex.add(r'\text{根据公式}E_{ri}=\cfrac{\left\lvert %s_{i}-%s\right\rvert}{%s}\times 100\%%，得' % (self.__sym, self.__muSym, self.__muSym))
                    for i in range(len(self.__arr)):
                        latex.add(r'E_{r%d}=\cfrac{\left\lvert %s-%s \right\rvert}{%s}\times 100\%%=%s' % (i+1, self.__arr[i].dlatex(), muExpr2, muExpr, result.__arr[i].latex()))
                if needValue:
                    return result, latex
                else:
                    return latex
            return result
        except:
            raise muNotFoundException('缺少真值，无法计算相对误差')
    
    def samConfIntv(self, confLevel=0.95, side='double', process=False, needValue=False):
        '''测量值的置信区间
        【参数说明】
        1.confLevel（float）：置信水平，建议选择0.6826、0.90、0.95、0.98、0.99中的一个（选择推荐值之外的值会使程序变慢），默认confLevel=0.95。
        2.side（str）：哪侧置信限度，'double'表示双侧，'left'表示左侧，'right'表示右侧，默认side='double'。
        3.spread（bool）：置信区间是否展开，默认spread=True。
        4.process（bool）：是否获得计算过程，默认process=False。
        5.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        tuple：由置信上界、下界组成的Num元组，对于单侧置信区间，其另一侧边界用无穷大表示。
        ①process为False时，返回值为tuple。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为tuple和LaTeX类型的计算过程组成的嵌套元组。
        
        【应用举例】
        >>> Al = NumItem('10.69 10.67 10.74 10.72')
        >>> Al.samConfIntv()
        (10.66, 10.74)
        >>> Al.samConfIntv(confLevel=0.99, side='down')
        (10.64, '+∞')'''
        mean = self.mean()
        s = self.staDevi(dec=True)
        n = len(self.__arr)
        if side == 'double':
            tv = t(confLevel, n-1, 2)
        elif side == 'left' or side == 'right':
            tv = t(confLevel, n-1, 1)
        unc = Num(None)
        unc._Num__value = tv*s/sqrt(n)
        unc._Num__setDigit(mean._Num__d_front, mean._Num__d_behind, mean._Num__d_valid)
        unc._Num__q = self.__q
        unc.fix()
        if process:
            latex = self.staDevi(process=True, remainOneMoreDigit=True)
            if side == 'double':
                latex.add(r'\text{对于双侧区间，}P=1-\cfrac{\alpha}{2}=%g\text{，查表得$n$=%d时，}t_{%g}\left(%d\right)=%.3f' % (confLevel, n, confLevel, n-1, tv))
            elif side == 'left' or side == 'right':
                latex.add((r"\text{对于单侧区间，}P=1-\cfrac{\alpha}{2}=%g\text{时，}P'=1-\alpha=%g\text{，查表得$n$=%d时，}t_{%g}\left(%d\right)=%.3f") % (confLevel, t_repl(confLevel), n, t_repl(confLevel), n-1, tv))
        if side == 'double':
            if process:
                latex.add(r'\text{置信区间为}\left(\overline{%s}-\cfrac{ts_{%s}}{\sqrt{n}},\overline{%s}+\cfrac{ts_{%s}}{\sqrt{n}}\right)\text{，代入得}\left(%s,%s\right)' % (self.__sym, self.__sym, self.__sym, self.__sym, (mean - unc).latex(), (mean + unc).latex()))
            if needValue and process:
                return ((mean - unc, mean + unc), latex)
            elif process:
                return latex
            else:
                return (mean - unc, mean + unc)
        elif side == 'left':
            if process:
                latex.add(r'\text{置信区间为}\left(\overline{%s}-\cfrac{ts_{%s}}{\sqrt{n}},+\infty\right)\text{，代入得}\left(%s, +\infty\right)' % (self.__sym, self.__sym, (mean - unc).latex()))
            if needValue and process:
                return ((mean - unc, '+∞'), latex)
            elif process:
                return latex
            else:
                return (mean - unc, '+∞')
        elif side == 'right':
            if process:
               latex.add(r'\text{置信区间为}\left(-\infty,\overline{%s}+\cfrac{ts_{%s}}{\sqrt{n}}\right)\text{，代入得}\left(-\infty, %s\right)' % (self.__sym, self.__sym, (mean + unc).latex()))
            if needValue and process:
                return (('-∞', mean + unc), latex)
            elif process:
                return latex
            else:
                return ('-∞', mean + unc)
        else:
            raise expressionInvalidException('参数side=\'%s\'无法识别' % side)
    
    def tTest(self, confLevel=0.95, side='double', process=False, needValue=False):
        '''使用t检验法，检验测定值与真值μ有无明显差别
        【参数说明】
        1.confLevel（float）：置信水平，建议选择0.6826、0.90、0.95、0.98、0.99中的一个（选择推荐值意外的值会使程序变慢），默认confLevel=0.95。
        2.side（str）：哪侧检验，'double'表示双侧，'down'表示下限，'up'表示上限，默认side='double'。
        3.process（bool）：是否获得计算过程，默认process=False。
        【返回值】
        bool：有显著性差异为True，无显著性差异为False。
        ①process为False时，返回值为bool。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
        ③process为True且needValue为True时，返回值为bool和LaTeX类型的计算过程组成的元组。
        【应用举例】
        >>> Al = NumItem('10.79 10.78 10.75 10.73 10.83', 10.82)
        >>> print('Al含量测量值与真实值是否有明显差别：%s' % Al.ttest())
        Al含量测量值与真实值是否有明显差别：False'''
        try:
            mean = self.mean(dec=True)
            s = self.staDevi(dec=True)
            n = len(self.__arr)
            tCal = abs(self.__mu._Num__value - mean) / s * sqrt(n)
            if side == 'double':  #检验两侧
                tv = t(confLevel, n-1, 2)
            elif side == 'down' or side == 'up':  #检验下限或上限
                tv = t(confLevel, n-1, 1)
            if process: 
                p_mean = self.mean()
                p_s, latex = self.staDevi(process=True, remainOneMoreDigit=True, needValue=True)
                latex.add(r't=\cfrac{\left\lvert\overline{%s}-%s\right\rvert}{s_{%s}/\sqrt{n}}=\cfrac{\left\lvert%s-%s\right\rvert}{%s/\sqrt{%d}}=%.3f' % (self.__sym, self.__muSym, self.__sym, p_mean.dlatex(), self.__mu.dlatex(2), p_s.dlatex(), n, tCal))
                if side == 'double':
                    latex.add(r'\text{对于双侧区间，}P=1-\cfrac{\alpha}{2}=%g\text{，查表得$n$=%d时，}t_{1-\alpha/2}(n-1)=t_{%g}(%d)=%.3f' % (confLevel, n, confLevel, n-1, tv))
                else:
                    latex.add(r"\text{对于单侧区间，}P=1-\cfrac{\alpha}{2}=%g\text{时，}P'=1-\alpha=%g\text{，查表得$n$=%d时，}t_{1-\alpha}(n-1)=t_{%g}(%d)=%.3f" % (confLevel, t_repl(confLevel), n, t_repl(confLevel), n-1, tv))
                if tCal >= tv:
                    if side == 'double':
                        latex.add(r't>t_{%g}(%d)\text{，故在置信度}P=%g\text{下，认定测量结果与真值有明显差异，存在系统误差}' % (confLevel, n-1, confLevel))
                    else:
                        latex.add(r't>t_{%g}(%d)\text{，故在置信度}P=%g\text{下，认定测量结果与真值有明显差异，存在系统误差}' % (t_repl(confLevel), n-1, confLevel))
                else:
                    if side == 'double':
                        latex.add(r't<t_{%g}(%d)\text{，故在置信度}P=%g\text{下，认定测量结果与真值无明显差异，测量结果误差由随机误差引起}' % (confLevel, n-1, confLevel))
                    else:
                        latex.add(r't<t_{%g}(%d)\text{，故在置信度}P=%g\text{下，认定测量结果与真值无明显差异，测量结果误差由随机误差引起}' % (t_repl(confLevel), n-1, confLevel))
                if needValue:
                    return tCal >= tv, latex
                else:
                    return latex
            return tCal >= tv
        except:
            raise muNotFoundException('缺少真值，无法进行准确度分析')
