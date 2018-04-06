# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:18:09 2018

@author: xingrongtech
"""

import sympy
from .num import Num
from .const import Const
from .system.numberformat import dec2Latex
from .system.exceptions import expressionInvalidException

class LSym():
    '''LSym为LaTeX符号生成类，该类能够通过计算公式，自动生成符号式、运算式的LaTeX表达式。'''
    __symPrior = 6  #初始符号式优先级为6
    __calPrior = 6  #初始计算式优先级为6
    __symText = None
    __calText = None
    __sNum = None
    __symBrac = -1  #当前符号式括号级别：-1为无括号，0为()，0为[]，0为{}
    __calBrac = -1  #当前计算式括号级别：-1为无括号，0为()，0为[]，0为{}
    __genSym = True
    __genCal = True
    '''
    符号优先级规定：
    负数：0  #仅适用于cal
    科学记数法：2  #仅适用于cal
    + -：1
    * / //：2
    ** exp：3
    sqrt 绝对值：4
    lg ln sin cos tan csc sec cot arcsin arccos arctan arccsc arcsec arccot ：5
    初始符号：6
    '''
    
    def __init__(self, sym=None, sNum=None):
        '''初始化一个LSym符号
        【参数说明】
        1.sym（可选，str）：符号。sym为None时，将不会生成代数表达式。默认sym=None。
        2.sNum（可选）：符号对应的数值。默认sNum=None。sNum可以是以下数据类型：
        (1)Num：直接给出符号对应的Num数值。
        (2)str：通过给出数值的字符串表达式，得到符号对应的Num数值。
        (3)int或float：表明符号对应的是一个纯数字。
        (4)Const：给定一个Const常数来初始化符号。
        注意：sym和sNum必须至少有一个不为None，否则LSym的符号运算将失去意义。
        【应用举例】
        >>> m = LSym('m')
        >>> t = LSym('t', '13.35')
        >>> g = LSym('g', 9.7964)
        '''
        if sym == None and sNum == None:
            return
        if sym != None:
            self.__symText = '{' + sym + '}'
        self.__genSym = (sym != None)
        self.__genCal = (sNum != None)
        if type(sNum) == Num or type(sNum) == int or type(sNum) == float:
            self.__sNum = sNum
        elif type(sNum) == str:
            self.__sNum = Num(sNum)
        elif type(sNum) == Const:
            self.__sNum = sNum._Const__value
        elif sNum != None:
            raise expressionInvalidException('用于创建符号的参数无效')
        if type(self.__sNum) == int or type(self.__sNum) == float:
            if type(sNum) == Const:
                self.__calText = sNum._Const__symText
                self.__calPrior = sNum._Const__prior
                self.__calBrac = sNum._Const__brac
            else:
                self.__calText = '%g' % self.__sNum
        elif type(self.__sNum) == Num:
            if self.__sNum._Num__sciDigit() != 0:
                self.__calPrior = 2
            self.__calText = '{' + self.__sNum.latex() + '}'
        if self.__sNum != None and type(sNum) != Const:  #如果是原始符号，则需要考虑是否因为负数或科学记数法而需要改变prior的情形
            if self.__sNum < 0:  #负数prior为0
                self.__calPrior = 0
            elif type(self.__sNum) == Num and self.__sNum._Num__sciDigit() != 0:  #科学记数法prior为2
                self.__calPrior = 2
            else:
                self.__calPrior = 6
        else:
            self.__calPrior = 6
            
    def refreshSym(self, sym):
        '''更新符号
        调用此方法后，原本的符号表达式将会被更新成新的符号表达式，原本的计算表达式将会被更新为当前LaTeX符号的数值，即LaTeX符号被以新的符号和数值初始化。
        【参数说明】
        sym（str）：要更新成的符号。
        '''
        self.__symText = '{' + sym + '}'
        if type(self.__sNum) == int or type(self.__sNum) == float:
            self.__calText = '%g' % self.__sNum
        elif type(self.__sNum) == Num:
            if self.__sNum._Num__sciDigit() != 0:
                self.__calPrior = 2
            self.__calText = '{' + self.__sNum.latex() + '}'
        if self.__sNum != None:  #如果是原始符号，则需要考虑是否因为负数或科学记数法而需要改变prior的情形
            if self.__sNum < 0:  #负数prior为0
                self.__calPrior = 0
            elif type(self.__sNum) == Num and self.__sNum._Num__sciDigit() != 0:  #科学记数法prior为2
                self.__calPrior = 2
            else:
                self.__calPrior = 6
        else:
            self.__calPrior = 6
    
    def __newInstance(self, symText=None, sNum=None, calText=None, symBrac=-1, calBrac=-1, symPrior=6, calPrior=6):
        '''创建新的LSym实例'''
        new = LSym(None, None)
        if symText != None and calPrior == 6:
            new.__symText = '{' + symText + '}'
        else:
            new.__symText = symText
        new.__calText = calText
        new.__symBrac = symBrac
        new.__calBrac = calBrac
        new.__genSym = (symText != None)
        new.__genCal = (sNum != None)
        new.__sNum = sNum
        new.__symPrior = symPrior
        new.__calPrior = calPrior
        return new
    
    def __bracket(self, bId):
        if bId == 0:
            return r'\left(%s\right)'
        elif bId == 1:
            return r'\left[%s\right]'
        elif bId >= 2:
            return r'\left \{%s\right \}'
    
    def sym(self):
        '''获得代数表达式
        【返回值】
        str：代数表达式文本'''
        return self.__symText
    
    def cal(self):
        '''获得数值表达式
        【返回值】
        str：数值表达式文本'''
        return self.__calText
    
    def num(self):
        '''获得计算结果数值
        【返回值】
        Num或int、float：根据初始化数值的方式，决定返回值类型。'''
        return self.__sNum
    
    def __gt__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__sNum > obj
        elif type(obj) == LSym:
            return self.__sNum > obj.__sNum
    
    def __lt__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__sNum < obj
        elif type(obj) == LSym:
            return self.__sNum < obj.__sNum
    
    def __ge__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__sNum >= obj
        elif type(obj) == LSym:
            return self.__sNum >= obj.__sNum
    
    def __le__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__sNum <= obj
        elif type(obj) == LSym:
            return self.__sNum <= obj.__sNum
    
    def __str__(self):
        '''获得LaTeX符号的文本形式
        【返回值】
        str：当sym为不空时，返回其符号表达式；当sym为空时，返回其计算表达式。'''
        if self.__symText != None:
            return self.__symText
        else:
            return self.__calText
    
    def __repr__(self):
        '''获得LaTeX符号的文本形式
        【返回值】
        str：当sym为不空时，返回其符号表达式；当sym为空时，返回其计算表达式。'''
        if self.__symText != None:
            return self.__symText
        else:
            return self.__calText
        
    def _repr_latex_(self):
        if self.__symText != None:
            return '$' + self.__symText + '$'
        else:
            return '$' + self.__calText + '$'
    
    def __abs__(self):
        symText = sNum = calText = symBrac = calBrac = None
        if self.__genSym:
            symText = r'\left\lvert %s \right\rvert' % self.__symText
            symBrac = self.__symBrac
        if self.__genCal:
            sNum = abs(self.__sNum)
            calText = r'\left\lvert %s \right\rvert' % self.__calText
            calBrac = self.__calBrac
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 1, 1)
    
    def __neg__(self):
        symText = sNum = calText = symBrac = calBrac = None
        #取负需要考虑self的括号
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 1 == self.__symPrior:
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 1 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if self.__genSym:
            symText = '-' + s_symText
            symBrac = s_symBrac
        if self.__genCal:
            sNum = -self.__sNum
            calText = '-' + s_calText
            calBrac = s_calBrac
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 1, 1)
    
    def __add__(self, obj):
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__radd__(self)
        if 0 == self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 0 == obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = self.__symText + '+' + obj.__symText
                symBrac = max(self.__symBrac, obj.__symBrac)
            if self.__genCal:
                sNum = self.__sNum + obj.__sNum
                calText = s_calText + '+' + o_calText
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = self.__symText + '+' + dec2Latex(obj)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = s_calText + '+' + dec2Latex(obj)
                sNum = self.__sNum + obj
                calBrac = s_calBrac
        elif type(obj) == Const:
            if self.__genSym:
                symText = self.__symText + '+' + c_symText
                symBrac = max(self.__symBrac, c_brac)
            if self.__genCal:
                calText = s_calText + '+' + c_symText
                sNum = self.__sNum + obj
                calBrac = max(s_calBrac, c_brac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = self.__symText + '+' + sympy.latex(obj)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = s_calText + '+' + sympy.latex(obj)
                sNum = self.__sNum + float(obj)
                calBrac = s_calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__radd__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 1, 1)
    
    def __radd__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__add__(self)
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        if 0 == self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 0 == obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = obj.__symText + '+' + self.__symText
                symBrac = max(obj.__symBrac, self.__symBrac)
            if self.__genCal:
                sNum = obj.__sNum + self.__sNum
                calText = o_calText + '+' + s_calText
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = dec2Latex(obj) + '+' + self.__symText
                symBrac = self.__symBrac
            if self.__genCal:
                calText = dec2Latex(obj) + '+' + s_calText
                sNum = obj + self.__sNum
                calBrac = s_calBrac
        elif type(obj) == Const:
            if self.__genSym:
                symText = c_symText + '+' + self.__symText
                symBrac = max(c_brac, self.__symBrac)
            if self.__genCal:
                calText = c_symText + '+' + s_calText
                sNum = obj + self.__sNum
                calBrac = max(s_calBrac, c_brac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = sympy.latex(obj) + '+' + self.__symText
                symBrac = self.__symBrac
            if self.__genCal:
                calText = sympy.latex(obj) + '+' + s_calText
                sNum = float(obj) + self.__sNum
                calBrac = s_calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__add__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 1, 1)
    
    def __sub__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__rsub__(self)
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        #左减需要考虑obj的括号，不用考虑self的括号
        if 0 == self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 1 == obj.__symPrior:
            if obj.__genSym:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
        elif type(obj) == Const and 1 == obj._Const__prior:
            c_brac += 1
            c_symText = self.__bracket(c_brac) % c_symText
        if type(obj) == LSym and 1 >= obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        if type(obj) == LSym:
            if self.__genSym:
                symText = self.__symText + '-' + o_symText
                symBrac = max(self.__symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum - obj.__sNum
                calText = s_calText + '-' + o_calText
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = self.__symText + '-' + dec2Latex(obj)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = s_calText + '-' + dec2Latex(obj)
                sNum = self.__sNum - obj
                calBrac = s_calBrac
        elif type(obj) == Const:
            if self.__genSym:
                symText = self.__symText + '-' + c_symText
                symBrac = max(self.__symBrac, c_brac)
            if self.__genCal:
                calText = s_calText + '-' + c_symText
                sNum = self.__sNum - obj
                calBrac = max(s_calBrac, c_brac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = self.__symText + '-' + sympy.latex(obj)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = s_calText + '-' + sympy.latex(obj)
                sNum = self.__sNum - float(obj)
                calBrac = s_calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__rsub__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 1, 1)
    
    def __rsub__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__sub__(self)
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        #右减需要考虑self的括号，不用考虑obj的括号
        if type(obj) == LSym and 0 == obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        if 1 == self.__symPrior:  
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 1 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym:
            if self.__genSym:
                symText = obj.__symText + '-' + s_symText
                symBrac = max(obj.__symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj.__sNum - self.__sNum
                calText = o_calText + '-' + s_calText
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = dec2Latex(obj) + '-' + s_symText
                symBrac = s_symBrac
            if self.__genCal:
                calText = dec2Latex(obj) + '-' + s_calText
                sNum = obj - self.__sNum
                calBrac = s_calBrac
        elif type(obj) == Const:
            if self.__genSym:
                symText = c_symText + '-' + s_symText
                symBrac = max(c_brac, s_symBrac)
            if self.__genCal:
                calText = c_symText + '-' + s_calText
                sNum = obj - self.__sNum
                calBrac = max(c_brac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = sympy.latex(obj) + '-' + s_symText
                symBrac = s_symBrac
            if self.__genCal:
                calText = sympy.latex(obj) + '-' + s_calText
                sNum = float(obj) - self.__sNum
                calBrac = s_calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__sub__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 1, 1)
    
    def __mul__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__rmul__(self)
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        if 2 > self.__symPrior:
            if self.__genSym:
                if not (type(obj) == Const and obj._Const__isUt1e):
                    s_symBrac += 1
                    s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 2 > obj.__symPrior:
            if obj.__genSym:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
        elif type(obj) == Const and 2 > obj._Const__prior:
            c_brac += 1
            c_symText = self.__bracket(c_brac) % c_symText
        if type(obj) == LSym and 2 > obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        if type(obj) == Const and obj._Const__isUt1e:  #对于ut1e科学记数法符号，符号优先级为原来的符号优先级
            symPrior = self.__symPrior
        else:
            symPrior = 2
        if type(obj) == LSym:
            if self.__genSym:
                symText = s_symText + o_symText  #与符号相乘，不需要乘号
                symBrac = max(s_symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum * obj.__sNum
                calText = s_calText + r' \times ' + o_calText
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = s_symText + r' \cdot ' + dec2Latex(obj)  #与常数相乘，需要点乘号
                symBrac = s_symBrac
            if self.__genCal:
                calText = s_calText + r' \times ' + dec2Latex(obj)
                sNum = self.__sNum * obj
                calBrac = s_calBrac
        elif type(obj) == Const:
            if self.__genSym:
                if obj._Const__isUt1e:
                    symText = s_symText  #当相乘的是用于单位换算的科学记数法时，忽略其符号
                elif obj._Const__isT1e:
                    symText = s_symText + r' \cdot ' + c_symText  #当相乘的是用于一般科学记数法时，需要加点乘号
                elif obj._Const__isHPercent:
                    symText = s_symText + r' \times ' + c_symText  #当相乘的是100%时，需要加叉乘号
                else:
                    symText = s_symText + c_symText
                symBrac = max(s_symBrac, c_brac)
            if self.__genCal:
                calText = s_calText + r' \times ' + c_symText
                sNum = self.__sNum * obj
                calBrac = max(s_calBrac, c_brac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = s_symText + r' \cdot ' + sympy.latex(obj)  #与常数相乘，需要点乘号
                symBrac = s_symBrac
            if self.__genCal:
                calText = s_calText + r' \times ' + sympy.latex(obj)
                sNum = self.__sNum * float(obj)
                calBrac = s_calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__rmul__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, symPrior, 2)
    
    def __rmul__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__mul__(self)
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        if 2 > self.__symPrior:
            if self.__genSym:
                if not (type(obj) == Const and obj._Const__isUt1e):
                    s_symBrac += 1
                    s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 2 > obj.__symPrior:
            if obj.__genSym:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
        elif type(obj) == Const and 2 > obj._Const__prior:
            c_brac += 1
            c_symText = self.__bracket(c_brac) % c_symText
        if type(obj) == LSym and 2 > obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        if type(obj) == Const and obj._Const__isUt1e:
            symPrior = self.__symPrior
        else:
            symPrior = 2
        if type(obj) == LSym:
            if self.__genSym:
                symText = o_symText + s_symText  #与符号相乘，不需要乘号
                symBrac = max(o_symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj.__sNum * self.__sNum
                calText = o_calText + r' \times ' + s_calText
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = dec2Latex(obj) + s_symText  #与常数相乘，不需要乘号
                symBrac = s_symBrac 
            if self.__genCal:
                calText = dec2Latex(obj) + r' \times ' + s_calText
                sNum = obj * self.__sNum
                calBrac = s_calBrac
        elif type(obj) == Const:
            if self.__genSym:
                if obj._Const__isUt1e:
                    symText = s_symText  #当相乘的是用于单位换算的科学记数法时，忽略其符号
                elif obj._Const__isT1e:
                    symText = c_symText + r' \cdot ' + s_symText  #当相乘的是用于一般科学记数法时，需要加点乘号
                elif obj._Const__isHPercent:
                    symText = c_symText + r' \times ' + s_symText  #当相乘的是100%时，需要加叉乘号
                else:
                    symText = c_symText + s_symText
                symBrac = max(c_brac, s_symBrac)
            if self.__genCal:
                calText = c_symText + r' \times ' + s_calText
                sNum = obj * self.__sNum
                calBrac = max(c_brac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = sympy.latex(obj) + s_symText  #与常数相乘，不需要乘号
                symBrac = s_symBrac 
            if self.__genCal:
                calText = sympy.latex(obj) + r' \times ' + s_calText
                sNum = float(obj) * self.__sNum
                calBrac = s_calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__mul__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, symPrior, 2)
    
    def __truediv__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__rtruediv__(self)
        if type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        #\frac式除号，不考虑prior
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, obj.__symText)
                symBrac = max(self.__symBrac, obj.__symBrac)
            if self.__genCal:
                sNum = self.__sNum / obj.__sNum
                calText = r'\cfrac{%s}{%s}' % (self.__calText, obj.__calText)
                calBrac = max(self.__calBrac, obj.__calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, obj)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (self.__calText, obj)
                sNum = self.__sNum / obj
                calBrac = self.__calBrac
        elif type(obj) == Const:
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, c_symText)
                symBrac = max(self.__symBrac, c_brac)
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (self.__calText, c_symText)
                sNum = self.__sNum / obj
                calBrac = max(self.__calBrac, c_brac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, sympy.latex(obj))
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (self.__calText, sympy.latex(obj))
                sNum = self.__sNum / float(obj)
                calBrac = self.__calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__rtruediv__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 2, 2)
    
    def __rtruediv__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__truediv__(self)
        if type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        #\frac式除号，不考虑prior
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (obj.__symText, self.__symText)
                symBrac = max(obj.__symBrac, self.__symBrac)
            if self.__genCal:
                sNum = obj.__sNum / self.__sNum
                calText = r'\cfrac{%s}{%s}' % (obj.__calText, self.__calText)
                calBrac = max(obj.__calBrac, self.__calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (obj, self.__symText)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (obj, self.__calText)
                sNum = obj / self.__sNum
                calBrac = self.__calBrac
        elif type(obj) == Const:
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (c_symText, self.__symText)
                symBrac = max(c_brac, self.__symBrac)
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (c_symText, self.__calText)
                sNum = obj / self.__sNum
                calBrac = max(c_brac, self.__calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (sympy.latex(obj), self.__symText)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (sympy.latex(obj), self.__calText)
                sNum = float(obj) / self.__sNum
                calBrac = self.__calBrac
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__truediv__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 2, 2)
    
    def __floordiv__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__rfloordiv__(self)
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        #/式除号，考虑prior
        symText = sNum = calText = symBrac = calBrac = None
        if 2 > self.__symPrior:
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        #右除需要考虑obj除号
        if type(obj) == LSym and 2 >= obj.__symPrior:
            if obj.__genSym:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
        elif type(obj) == Const and 2 >= obj._Const__prior:
            c_brac += 1
            c_symText = self.__bracket(c_brac) % c_symText
        if type(obj) == LSym and 2 >= obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        if type(obj) == LSym:
            if self.__genSym:
                symText = s_symText + r'/' + o_symText
                symBrac = max(s_symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum / obj.__sNum
                calText = s_calText + r'/' + o_calText
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = s_symText + r'/' + dec2Latex(obj)
                symBrac = s_symBrac
            if self.__genCal:
                calText = s_calText + r'/' + dec2Latex(obj)
                sNum = self.__sNum / obj
                calBrac = s_calBrac 
        elif type(obj) == Const:
            if self.__genSym:
                symText = s_symText + r'/' + c_symText
                symBrac = max(s_symBrac, c_brac)
            if self.__genCal:
                calText = s_calText + r'/' + c_symText
                sNum = self.__sNum / obj
                calBrac = max(s_calBrac, c_brac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = s_symText + r'/' + sympy.latex(obj)
                symBrac = s_symBrac
            if self.__genCal:
                calText = s_calText + r'/' + sympy.latex(obj)
                sNum = self.__sNum / float(obj)
                calBrac = s_calBrac 
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__rfloordiv__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 2, 2)
    
    def __rfloordiv__(self, obj):
        if str(type(obj)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return obj.__floordiv__(self)
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            c_brac = obj._Const__brac
            c_symText = obj._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        #/式除号，考虑prior
        #左除需要考虑self除号
        if 2 >= self.__symPrior:  #左除需要考虑self除号
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 2 > obj.__symPrior:
            if obj.__genSym:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
        elif type(obj) == Const and 2 > obj._Const__prior:
            c_brac += 1
            c_symText = self.__bracket(c_brac) % c_symText
        if type(obj) == LSym and 2 > obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        if type(obj) == LSym:
            if self.__genSym:
                symText = o_symText + r'/' + s_symText
                symBrac = max(o_symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj.__sNum / self.__sNum
                calText = o_calText + r'/' + s_calText
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = dec2Latex(obj) + r'/' + s_symText
                symBrac = s_symBrac
            if self.__genCal:
                calText = dec2Latex(obj) + r'/' + s_calText
                sNum = obj / self.__sNum
                calBrac = s_calBrac  
        elif type(obj) == Const:
            if self.__genSym:
                symText = c_symText + r'/' + s_symText
                symBrac = max(c_brac, s_symBrac)
            if self.__genCal:
                calText = c_symText + r'/' + s_calText
                sNum = obj / self.__sNum
                calBrac = max(c_brac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = sympy.latex(obj) + r'/' + s_symText
                symBrac = s_symBrac
            if self.__genCal:
                calText = sympy.latex(obj) + r'/' + s_calText
                sNum = float(obj) / self.__sNum
                calBrac = s_calBrac  
        elif str(type(obj)) == "<class 'analyticlab.uncertainty.unc.Uncertainty'>" or str(type(obj)) == "<class 'analyticlab.uncertainty.measure.Measure'>":
            return obj.__floordiv__(self)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 2, 2)
    
    def __pow__(self, b):
        if str(type(b)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return b.__rpow__(self)
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(b) == Const:
            c_brac = b._Const__brac
            c_symText = b._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        if 3 >= self.__symPrior:
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 3 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if self.__genSym:
            if self.__symPrior == 5:  #对于对数函数、三角函数的乘方
                symText = s_symText
                lId = symText.find('{')
                if symText[:13] == r'\operatorname':
                    lId = symText.find('{', lId + 1)
                if type(b) == Const:
                    symText = symText[:lId] + '^{' + c_symText + '}' + symText[lId:]
                elif type(b) == float:
                    symText = symText[:lId] + '^{' + dec2Latex(b) + '}' + symText[lId:]
                elif 'sympy' in str(type(b)):
                    symText = symText[:lId] + '^{' + sympy.latex(b) + '}' + symText[lId:]
                else:
                    symText = symText[:lId] + '^{' + str(b) + '}' + symText[lId:]
            else:
                if type(b) == Const:
                    symText = '%s^{%s}' % (s_symText, c_symText)
                elif type(b) == float:
                    symText = '%s^{%s}' % (s_symText, dec2Latex(b))
                elif 'sympy' in str(type(b)):
                    symText = '%s^{%s}' % (s_symText, sympy.latex(b))
                else:
                    symText = '%s^{%s}' % (s_symText, b)
            if type(b) == Const:
                symBrac = max(s_symBrac, c_brac)
            else:
                symBrac = s_symBrac
        if self.__genCal:
            if type(b) == Const:
                sNum = self.__sNum ** b
                calBrac = max(s_calBrac, c_brac)
            elif 'sympy' in str(type(b)):
                sNum = self.__sNum ** float(b)
                calBrac = s_calBrac
            else:
                sNum = self.__sNum ** b
                calBrac = s_calBrac
            if self.__calPrior == 5:  #对于对数函数、三角函数的乘方
                calText = s_calText
                lId = calText.find('{')
                if calText[:13] == r'\operatorname':
                    lId = calText.find('{', lId + 1)
                if type(b) == Const:
                    calText = calText[:lId] + '^{' + c_symText + '}' + calText[lId:]
                elif type(b) == float:
                    calText = calText[:lId] + '^{' + dec2Latex(b) + '}' + calText[lId:]
                elif 'sympy' in str(type(b)):
                    calText = calText[:lId] + '^{' + sympy.latex(b) + '}' + calText[lId:]
                else:
                    calText = calText[:lId] + '^{' + str(b) + '}' + calText[lId:]
            else:
                if type(b) == Const:
                    calText = '%s^{%s}' % (s_calText, c_symText)
                elif type(b) == float:
                    calText = '%s^{%s}' % (s_calText, dec2Latex(b))
                elif 'sympy' in str(type(b)):
                    calText = '%s^{%s}' % (s_calText, sympy.latex(b))
                else:
                    calText = '%s^{%s}' % (s_calText, b)
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 3, 3)
    
    def __rpow__(self, a):
        if str(type(a)) == "<class 'analyticlab.lsymitem.LSymItem'>":
            return a.__pow__(self)
        if type(a) == Const:
            c_brac = a._Const__brac
            c_symText = a._Const__symText
        symText = sNum = calText = symBrac = calBrac = None
        if self.__genSym:
            if type(a) == Const:
                symText = '%s^{%s}' % (c_symText, self.__symText)
                symBrac = max(c_brac, self.__symBrac)
            elif type(a) == float:
                symText = '%s^{%s}' % (dec2Latex(a), self.__symText)
                symBrac = self.__symBrac
            elif 'sympy' in str(type(a)):
                symText = '%s^{%s}' % (sympy.latex(a), self.__symText)
                symBrac = self.__symBrac
            else:
                symText = '%s^{%s}' % (a, self.__symText)
                symBrac = self.__symBrac
        if self.__genCal:
            if type(a) == Const:
                sNum = a ** self.__sNum
                calText = '%s^{%s}' % (c_symText, self.__calText)
                calBrac = max(c_brac, self.__calBrac)
            elif type(a) == float:
                sNum = a ** self.__sNum
                calText = '%s^{%s}' % (dec2Latex(a), self.__calText)
                calBrac = self.__calBrac  
            elif 'sympy' in str(type(a)):
                sNum = float(a) ** self.__sNum
                calText = '%s^{%s}' % (sympy.latex(a), self.__calText)
                calBrac = self.__calBrac  
            else:
                sNum = a ** self.__sNum
                calText = '%s^{%s}' % (a, self.__calText)
                calBrac = self.__calBrac  
        return self.__newInstance(symText, sNum, calText, symBrac, calBrac, 3, 3)
