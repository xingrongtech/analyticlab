# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:18:09 2018

@author: xingrongtech
"""

import sympy
from quantities.quantity import Quantity
from .num import Num
from .const import Const
from .system.numberformat import dec2Latex
from .system.exceptions import expressionInvalidException

superiorTypes = ("<class 'analyticlab.lsymitem.LSymItem'>"
        "<class 'analyticlab.measure.basemeasure.BaseMeasure'>", 
        "<class 'analyticlab.measure.measure.Measure'>")

class LSym():
    '''LSym为LaTeX符号生成类，该类能够通过计算公式，自动生成符号式、运算式的LaTeX表达式。'''
    __symPrior = 6  #初始符号式优先级为6
    __calPrior = 6  #初始计算式优先级为6
    __symText = None
    __calText = None
    __sNum = None
    __symBrac = -1  #当前符号式括号级别：-1为无括号，0为()，1为[]，2为{}
    __calBrac = -1  #当前计算式括号级别：-1为无括号，0为()，1为[]，2为{}
    __genSym = True
    __genCal = True
    #下述两个布尔变量用于乘法运算的符号式中，根据是否为数字判断省略乘号还是用点乘号
    __s_decL = False  #符号式的左端是否为数字
    __s_decR = False  #符号式的右端是否为数字
    '''
    符号优先级规定：
    负数：0  #仅适用于cal
    科学记数法：2  #仅适用于cal
    + -：1
    * / //：2
    ** exp：3
    lg ln sin cos tan csc sec cot arcsin arccos arctan arccsc arcsec arccot：4
    sqrt 绝对值：5
    初始符号：6
    '''
    
    def __init__(self, sym=None, sNum=None, unit=None):
        '''初始化一个LSym符号
        【参数说明】
        1.sym（可选，str）：符号。sym为None时，将不会生成代数表达式。默认sym=None。
        2.sNum（可选）：符号对应的数值。默认sNum=None。sNum可以是以下数据类型：
        (1)Num：直接给出符号对应的Num数值。
        (2)str：通过给出数值的字符串表达式，得到符号对应的Num数值。
        3.unit（可选，str）：当unit为None时，会选择Num的unit作为LSym的unit，否则没有单位。默认unit=None。
        注意：sym和sNum必须至少有一个不为None，否则LSym的符号运算将失去意义。
        【应用举例】
        >>> m = LSym('m')  #有符号，无数值和单位
        >>> t = LSym('t', '13.35')  #有符号和数值，无单位
        >>> x = LSym('x', ('3.66', 'mm'))  #有符号、数值和单位
        >>> g = LSym('g', 9.7964)  #有符号，纯数字
        '''
        if sym == None and sNum == None:
            return
        if sym != None:
            self.__symText = '{' + sym + '}'
        self.__genSym = (sym != None)
        self.__genCal = (sNum != None)
        if type(sNum) == Num:
            self.__sNum = sNum
            if unit != None:
                self.__sNum._Num__q = Quantity(1., unit) if type(unit) == str else unit
        elif type(sNum) == str:
            self.__sNum = Num(sNum)
            if unit != None:
                self.__sNum._Num__q = Quantity(1., unit) if type(unit) == str else unit
        elif sNum != None:
            raise expressionInvalidException('用于创建符号的参数无效')
        if type(self.__sNum) == Num:
            if self.__sNum._Num__sciDigit() != 0:
                self.__calPrior = 2
            self.__calText = '{' + self.__sNum.dlatex() + '}'
        if self.__sNum != None:  #如果是原始符号，则需要考虑是否因为负数或科学记数法而需要改变prior的情形
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
        self.__symText = '{%s}' % sym
        if type(self.__sNum) == Num:
            if self.__sNum._Num__sciDigit() != 0:
                self.__calPrior = 2
            self.__calText = '{%s}' % self.__sNum.dlatex()
        if self.__sNum != None:  #如果是原始符号，则需要考虑是否因为负数或科学记数法而需要改变prior的情形
            if self.__sNum < 0:  #负数prior为0
                self.__calPrior = 0
            elif type(self.__sNum) == Num and self.__sNum._Num__sciDigit() != 0:  #科学记数法prior为2
                self.__calPrior = 2
            else:
                self.__calPrior = 6
        else:
            self.__calPrior = 6
    
    def __newInstance(self, sNum, symText, calText, symBrac, calBrac, symPrior, calPrior, s_decL=False, s_decR=False):
        '''创建新的LSym实例'''
        new = LSym(None, None)
        new.__sNum = sNum
        if symText != None and calPrior == 6:
            new.__symText = '{%s}' % symText
        else:
            new.__symText = symText
        new.__calText = calText
        new.__symBrac = symBrac
        new.__calBrac = calBrac
        new.__genSym = (symText != None)
        new.__genCal = (sNum != None)
        new.__symPrior = symPrior
        new.__calPrior = calPrior
        new.__s_decL = s_decL
        new.__s_decR = s_decR
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
    
    def resetUnit(self, unit=None):
        '''重设LSym符号中数值的单位
        【参数说明】
        unit（可选，str）：重设后的单位。默认unit=None，即没有单位。'''
        if self.__sNum != None:
            if unit == None:
                self.__sNum._Num__q = 1
            else:
                self.__sNum._Num__q = Quantity(1., unit) if type(unit) == str else unit
    
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
            return '$%s$' % self.__symText
        else:
            return '$%s$' % self.__calText
    
    def __abs__(self):
        symText = sNum = calText = symBrac = calBrac = None
        if self.__genSym:
            symText = r'\left\lvert %s \right\rvert' % self.__symText
            symBrac = self.__symBrac
        if self.__genCal:
            sNum = abs(self.__sNum)
            calText = r'\left\lvert %s \right\rvert' % self.__calText
            calBrac = self.__calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 5, 5)
    
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
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 1, 1)
    
    def __add__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__radd__(self)
        ### 括号与文本预处理 ###
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
        if str(type(obj)) in superiorTypes:
            return obj.__radd__(self)
        if 0 == self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 0 == obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const and 0 == obj._Const__calPrior:
            o_calBrac += 1
            o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = '%s+%s' % (self.__symText, obj.__symText)
                symBrac = max(self.__symBrac, obj.__symBrac)
            if self.__genCal:
                sNum = self.__sNum + obj.__sNum
                calText = '%s+%s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = '%s+%s' % (self.__symText, dec2Latex(obj))
                symBrac = max(self.__symBrac, -(obj>=0))
            if self.__genCal:
                sNum = self.__sNum + obj
                calText = '%s+%s' % (s_calText, dec2Latex(obj))
                calBrac = max(s_calBrac, -(obj>=0))
        elif type(obj) == Const:
            if self.__genSym:
                symText = '%s+%s' % (self.__symText, obj._Const__symText)
                symBrac = max(self.__symBrac, obj._Const__symBrac)
            if self.__genCal:
                sNum = self.__sNum + obj
                calText = '%s+%s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = '%s+%s' % (self.__symText, sympy.latex(obj))
                symBrac = self.__symBrac
            if self.__genCal:
                sNum = self.__sNum + float(obj)
                calText = '%s+%s' % (s_calText, sympy.latex(obj))
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 1, 1)
    
    def __radd__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__add__(self)
        ### 括号与文本预处理 ###
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
        if 0 == self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 0 == obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const and 0 == obj._Const__calPrior:
            o_calBrac += 1
            o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = '%s+%s' % (obj.__symText, self.__symText)
                symBrac = max(obj.__symBrac, self.__symBrac)
            if self.__genCal:
                sNum = obj.__sNum + self.__sNum
                calText = '%s+%s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = '%s+%s' % (dec2Latex(obj), self.__symText)
                symBrac = max(-(obj>=0), self.__symBrac)
            if self.__genCal:
                sNum = obj + self.__sNum
                calText = '%s+%s' % (dec2Latex(obj), s_calText)
                calBrac = max(-(obj>=0), s_calBrac)
        elif type(obj) == Const:
            if self.__genSym:
                symText = '%s+%s' % (obj._Const__symText, self.__symText)
                symBrac = max(obj._Const__symBrac, self.__symBrac)
            if self.__genCal:
                sNum = obj + self.__sNum
                calText = '%s+%s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = '%s+%s' % (sympy.latex(obj), self.__symText)
                symBrac = self.__symBrac
            if self.__genCal:
                sNum = float(obj) + self.__sNum
                calText = '%s+%s' % (sympy.latex(obj), s_calText)
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 1, 1)
    
    def __sub__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__rsub__(self)
        ### 括号与文本预处理 ###
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            o_symBrac = obj._Const__symBrac
            o_symText = obj._Const__symText
            o_calBrac = obj._Const__symBrac
            o_calText = obj._Const__calText
        #左减需要考虑obj的括号，不用考虑self的括号
        if 0 == self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym:
            if 1 == obj.__symPrior:
                if obj.__genSym:
                    o_symBrac += 1
                    o_symText = self.__bracket(o_symBrac) % o_symText
            if 1 >= obj.__calPrior:
                if obj.__genCal:
                    o_calBrac += 1
                    o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const:
            if 1 == obj._Const__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 1 >= obj._Const__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = '%s-%s' % (self.__symText, o_symText)
                symBrac = max(self.__symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum - obj.__sNum
                calText = '%s-%s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = '%s-%s' % (self.__symText, dec2Latex(obj))
                symBrac = max(self.__symBrac, -(obj>=0))
            if self.__genCal:
                sNum = self.__sNum - obj
                calText = '%s-%s' % (s_calText, dec2Latex(obj))
                calBrac = max(s_calBrac, -(obj>=0))
        elif type(obj) == Const:
            if self.__genSym:
                symText = '%s-%s' % (self.__symText, o_symText)
                symBrac = max(self.__symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum - obj
                calText = '%s-%s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = '%s-%s' % (self.__symText, sympy.latex(obj))
                symBrac = self.__symBrac
            if self.__genCal:
                sNum = self.__sNum - float(obj)
                calText = '%s-%s' % (s_calText, sympy.latex(obj))
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 1, 1)
    
    def __rsub__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__sub__(self)
        ### 括号与文本预处理 ###
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if type(obj) == LSym:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
        elif type(obj) == Const:
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
        #右减需要考虑self的括号，不用考虑obj的括号
        if 1 == self.__symPrior:  
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 1 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym and 0 == obj.__calPrior:
            if obj.__genCal:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const and 0 == obj._Const__calPrior:
            o_calBrac += 1
            o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = '%s-%s' % (obj.__symText, s_symText)
                symBrac = max(obj.__symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj.__sNum - self.__sNum
                calText = '%s-%s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = '%s-%s' % (dec2Latex(obj), s_symText)
                symBrac = max(-(obj>=0), s_symBrac)
            if self.__genCal:
                sNum = obj - self.__sNum
                calText = '%s-%s' % (dec2Latex(obj), s_calText)
                calBrac = max(-(obj>=0), s_calBrac)
        elif type(obj) == Const:
            if self.__genSym:
                symText = '%s-%s' % (obj._Const__symText, s_symText)
                symBrac = max(obj._Const__symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj - self.__sNum
                calText = '%s-%s' % (obj._Const__calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = '%s-%s' % (sympy.latex(obj), s_symText)
                symBrac = s_symBrac
            if self.__genCal:
                sNum = float(obj) - self.__sNum
                calText = '%s-%s' % (sympy.latex(obj), s_calText)
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 1, 1)
    
    def __mul__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__rmul__(self)
        ### 括号与文本预处理 ###
        symPrior = 2
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
            o_symBrac = obj._Const__symBrac
            o_symText = obj._Const__symText
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
        if 2 > self.__symPrior:
            if self.__genSym:
                if not (type(obj) == Const and obj._Const__special == 'ut1e'):
                    s_symBrac += 1
                    s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym:
            if 2 > obj.__symPrior:
                if obj.__genSym:
                    o_symBrac += 1
                    o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj.__calPrior:
                if obj.__genCal:
                    o_calBrac += 1
                    o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const:
            if 2 > obj._Const__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj._Const__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
            if obj._Const__special == 'ut1e':  #对于ut1e科学记数法符号，符号优先级为原来的符号优先级
                symPrior = self.__symPrior
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            o_decR = obj.__s_decR
            if self.__genSym:
                #是否需要乘号根据后面的数，即obj左端是否为数字而定，或者在外围为函数时由self右端而定
                if obj.__s_decL or (self.__symPrior == 4 and self.__s_decR): 
                    symText = r'%s \cdot %s' % (s_symText, o_symText)
                else:
                    symText = s_symText + o_symText
                symBrac = max(s_symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum * obj.__sNum
                calText = r'%s \times %s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            o_decR = True
            if self.__genSym:
                symText = r'%s \cdot %s' % (s_symText, dec2Latex(obj))  #右侧与常数相乘，需要点乘号
                symBrac = max(s_symBrac, -(obj>=0))
            if self.__genCal:
                sNum = self.__sNum * obj
                calText = r'%s \times %s' % (s_calText, dec2Latex(obj))
                calBrac = max(s_calBrac, -(obj>=0))
        elif type(obj) == Const:
            o_decR = obj._Const__s_decR
            if self.__genSym:
                if obj._Const__special == 'ut1e':
                    symText = s_symText  #当右侧相乘的是ut1e时，该ut1e不出现在符号式中
                elif obj._Const__special == 'hPercent':
                    symText = r'%s \times %s' % (s_symText, o_symText)  #当相乘的是100%时，需要加叉乘号
                #是否需要乘号根据后面的数，即obj左端是否为数字而定，或者在外围为函数时由self右端而定
                if obj._Const__s_decL or (self.__symPrior == 4 and self.__s_decR): 
                    symText = r'%s \cdot %s' % (s_symText, o_symText)
                else:
                    symText = s_symText + o_symText
                symBrac = max(s_symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum * obj
                calText = r'%s \times %s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif 'sympy' in str(type(obj)):
            o_decR = False
            if self.__genSym:
                symText = r'%s \cdot %s' % (s_symText, sympy.latex(obj))  #与常数相乘，需要点乘号
                symBrac = s_symBrac
            if self.__genCal:
                sNum = self.__sNum * float(obj)
                calText = r'%s \times %s' % (s_calText, sympy.latex(obj))
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, symPrior, 2, self.__s_decL, o_decR)
    
    def __rmul__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__mul__(self)
        ### 括号与文本预处理 ###
        symPrior = 2
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
            o_symBrac = obj._Const__symBrac
            o_symText = obj._Const__symText
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
        if 2 > self.__symPrior:
            if self.__genSym:
                if not (type(obj) == Const and obj._Const__special == 'ut1e'):
                    s_symBrac += 1
                    s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == LSym:
            if 2 > obj.__symPrior:
                if obj.__genSym:
                    o_symBrac += 1
                    o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj.__calPrior:
                if obj.__genCal:
                    o_calBrac += 1
                    o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const:
            if 2 > obj._Const__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj._Const__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
            if obj._Const__special == 'ut1e':  #对于ut1e科学记数法符号，符号优先级为原来的符号优先级
                symPrior = self.__symPrior
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            o_decL = obj.__s_decL
            if self.__genSym:
                #是否需要乘号根据后面的数，即self左端是否为数字而定，或者在外围为函数时由obj右端而定
                if self.__s_decL or (obj.__symPrior == 4 and obj.__s_decR):  
                    symText = r'%s \cdot %s' % (o_symText, s_symText)
                else:
                    symText = o_symText + s_symText  #左侧与符号相乘，不需要乘号
                symBrac = max(o_symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj.__sNum * self.__sNum
                calText = r'%s \times %s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            o_decL = True
            if self.__genSym:
                symText = dec2Latex(obj) + s_symText  #与常数相乘，不需要乘号
                symBrac = max(-(obj>=0), s_symBrac)
            if self.__genCal:
                sNum = obj * self.__sNum
                calText = r'%s \times %s' % (dec2Latex(obj), s_calText)
                calBrac = max(-(obj>=0), s_calBrac)
        elif type(obj) == Const:
            o_decL = obj._Const__s_decL
            if self.__genSym:
                if obj._Const__special == 'hPercent':
                    symText = r'%s \times %s' % (o_symText, s_symText)  #当相乘的是100%时，需要加叉乘号
                #是否需要乘号根据后面的数，即self左端是否为数字而定，或者在外围为函数时由obj右端而定
                elif self.__s_decL or (obj._Const__symPrior == 4 and obj._Const__s_decR):
                    symText = r'%s \cdot %s' % (o_symText, s_symText)
                else:
                    symText = s_symText + o_symText
                symBrac = max(o_symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj * self.__sNum
                calText = r'%s \times %s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            o_decL = False
            if self.__genSym:
                symText = sympy.latex(obj) + s_symText  #与常数相乘，不需要乘号
                symBrac = s_symBrac 
            if self.__genCal:
                sNum = float(obj) * self.__sNum
                calText = r'%s \times %s' % (sympy.latex(obj), s_calText)
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, symPrior, 2, o_decL, self.__s_decR)
    
    def __truediv__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__rtruediv__(self)
        ### 括号与文本预处理 ###
        ### 合成表达式 ###
        #\frac式除号，不考虑prior
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            s_dec = self.__s_decL and self.__s_decR and obj.__s_decL and obj.__s_decR
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, obj.__symText)
                symBrac = max(self.__symBrac, obj.__symBrac)
            if self.__genCal:
                sNum = self.__sNum / obj.__sNum
                calText = r'\cfrac{%s}{%s}' % (self.__calText, obj.__calText)
                calBrac = max(self.__calBrac, obj.__calBrac)
        elif type(obj) == int or type(obj) == float:
            s_dec = self.__s_decL and self.__s_decR
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, dec2Latex(obj, noBracket=True))
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (self.__calText, dec2Latex(obj, noBracket=True))
                sNum = self.__sNum / obj
                calBrac = self.__calBrac
        elif type(obj) == Const:
            s_dec = self.__s_decL and self.__s_decR and obj._Const__s_decL and obj._Const__s_decR
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, obj._Const__symText)
                symBrac = max(self.__symBrac, obj._Const__symBrac)
            if self.__genCal:
                sNum = self.__sNum / obj
                calText = r'\cfrac{%s}{%s}' % (self.__calText, obj._Const__calText)
                calBrac = max(self.__calBrac, obj._Const__calBrac)
        elif 'sympy' in str(type(obj)):
            s_dec = False
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (self.__symText, sympy.latex(obj))
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (self.__calText, sympy.latex(obj))
                sNum = self.__sNum / float(obj)
                calBrac = self.__calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 2, 2, s_dec, s_dec)
    
    def __rtruediv__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__truediv__(self)
        ### 括号与文本预处理 ###
        ### 合成表达式 ###
        #\frac式除号，不考虑prior
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            s_dec = obj.__s_decL and obj.__s_decR and self.__s_decL and self.__s_decR
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (obj.__symText, self.__symText)
                symBrac = max(obj.__symBrac, self.__symBrac)
            if self.__genCal:
                sNum = obj.__sNum / self.__sNum
                calText = r'\cfrac{%s}{%s}' % (obj.__calText, self.__calText)
                calBrac = max(obj.__calBrac, self.__calBrac)
        elif type(obj) == int or type(obj) == float:
            s_dec = self.__s_decL and self.__s_decR
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (dec2Latex(obj, noBracket=True), self.__symText)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (dec2Latex(obj, noBracket=True), self.__calText)
                sNum = obj / self.__sNum
                calBrac = self.__calBrac
        elif type(obj) == Const:
            s_dec = obj._Const__s_decL and obj._Const__s_decR and self.__s_decL and self.__s_decR
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (obj._Const__symText, self.__symText)
                symBrac = max(obj._Const__symBrac, self.__symBrac)
            if self.__genCal:
                sNum = obj / self.__sNum
                calText = r'\cfrac{%s}{%s}' % (obj._Const__calText, self.__calText)
                calBrac = max(obj._Const__calBrac, self.__calBrac)
        elif 'sympy' in str(type(obj)):
            s_dec = False
            if self.__genSym:
                symText = r'\cfrac{%s}{%s}' % (sympy.latex(obj), self.__symText)
                symBrac = self.__symBrac
            if self.__genCal:
                calText = r'\cfrac{%s}{%s}' % (sympy.latex(obj), self.__calText)
                sNum = float(obj) / self.__sNum
                calBrac = self.__calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 2, 2, s_dec, s_dec)
    
    def __floordiv__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__rfloordiv__(self)
        ### 括号与文本预处理 ###
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
            o_symBrac = obj._Const__symBrac
            o_symText = obj._Const__symText
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
        #/式除号，考虑prior
        if 2 > self.__symPrior:
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        #右除需要考虑obj除号
        if type(obj) == LSym:
            if 2 >= obj.__symPrior:
                if obj.__genSym:
                    o_symBrac += 1
                    o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 >= obj.__calPrior:
                if obj.__genCal:
                    o_calBrac += 1
                    o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const:
            if 2 >= obj._Const__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 >= obj._Const__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_symBrac) % o_symText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            if self.__genSym:
                symText = r'%s/%s' % (s_symText, o_symText)
                symBrac = max(s_symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum / obj.__sNum
                calText = r'%s/%s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif type(obj) == int or type(obj) == float:
            if self.__genSym:
                symText = r'%s/%s' % (s_symText, dec2Latex(obj))
                symBrac = max(s_symBrac, -(obj>=0))
            if self.__genCal:
                sNum = self.__sNum / obj
                calText = r'%s/%s' % (s_calText, dec2Latex(obj))
                calBrac = max(s_calBrac, -(obj>=0))
        elif type(obj) == Const:
            if self.__genSym:
                symText = r'%s/%s' % (s_symText, o_symText)
                symBrac = max(s_symBrac, o_symBrac)
            if self.__genCal:
                sNum = self.__sNum / obj
                calText = r'%s/%s' % (s_calText, o_calText)
                calBrac = max(s_calBrac, o_calBrac)
        elif 'sympy' in str(type(obj)):
            if self.__genSym:
                symText = r'%s/%s' % (s_symText, sympy.latex(obj))
                symBrac = s_symBrac
            if self.__genCal:
                sNum = self.__sNum / float(obj)
                calText = r'%s/%s' % (s_calText, sympy.latex(obj))
                calBrac = s_calBrac 
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 2, 2, self.__s_decL, True)
    
    def __rfloordiv__(self, obj):
        if str(type(obj)) in superiorTypes:
            return obj.__floordiv__(self)
        ### 括号与文本预处理 ###
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
            o_symBrac = obj._Const__symBrac
            o_symText = obj._Const__symText
            o_calBrac = obj._Const__calBrac
            o_calText = obj._Const__calText
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
        if type(obj) == LSym:
            if 2 > obj.__symPrior:
                if obj.__genSym:
                    o_symBrac += 1
                    o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj.__calPrior:
                if obj.__genCal:
                    o_calBrac += 1
                    o_calText = self.__bracket(o_calBrac) % o_calText
        elif type(obj) == Const:
            if 2 > obj._Const__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj._Const__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(obj) == LSym:
            o_decL = obj.__s_decL
            if self.__genSym:
                symText = r'%s/%s' % (o_symText, s_symText)
                symBrac = max(o_symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj.__sNum / self.__sNum
                calText = r'%s/%s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif type(obj) == int or type(obj) == float:
            o_decL = True
            if self.__genSym:
                symText = r'%s/%s' % (dec2Latex(obj), s_symText)
                symBrac = max(-(obj>=0), s_symBrac)
            if self.__genCal:
                sNum = obj / self.__sNum
                calText = r'%s/%s' % (dec2Latex(obj), s_calText)
                calBrac = max(-(obj>=0), s_calBrac)  
        elif type(obj) == Const:
            o_decL = obj._Const__s_decL
            if self.__genSym:
                symText = r'%s/%s' % (o_symText, s_symText)
                symBrac = max(o_symBrac, s_symBrac)
            if self.__genCal:
                sNum = obj / self.__sNum
                calText = r'%s/%s' % (o_calText, s_calText)
                calBrac = max(o_calBrac, s_calBrac)
        elif 'sympy' in str(type(obj)):
            o_decL = False
            if self.__genSym:
                symText = r'%s/%s' % (sympy.latex(obj), s_symText)
                symBrac = s_symBrac
            if self.__genCal:
                calText = r'%s/%s' % (sympy.latex(obj), s_calText)
                sNum = float(obj) / self.__sNum
                calBrac = s_calBrac
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 2, 2, o_decL, True)
    
    def __pow__(self, b):
        if str(type(b)) in superiorTypes:
            return b.__rpow__(self)
        ### 括号与文本预处理 ###
        assert type(b) != LSym, 'LaTeX符号/符号组之间不能进行乘方运算'
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 3 >= self.__symPrior:
            if self.__genSym:
                s_symBrac += 1
                s_symText = self.__bracket(s_symBrac) % s_symText
        if 3 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(b) == Const:
            s_dec = self.__s_decL and self.__s_decR and b._Const__s_decL and b._Const__s_decR
        elif type(b) == int or type(b) == float:
            s_dec = self.__s_decL and self.__s_decR
        else:
            s_dec = False
        if self.__genSym:
            if self.__symPrior == 4:  #对于对数函数、三角函数的乘方
                symText = s_symText
                lId = symText.find('{')
                if symText[:13] == r'\operatorname':
                    lId = symText.find('{', lId + 1)
                if type(b) == Const:
                    symText = '%s^{%s}%s' % (symText[:lId], b._Const__symText, symText[lId:])
                elif type(b) == int or type(b) == float:
                    symText = '%s^{%s}%s' % (symText[:lId], dec2Latex(b, noBracket=True), symText[lId:])
                elif 'sympy' in str(type(b)):
                    symText = '%s^{%s}%s' % (symText[:lId], sympy.latex(b), symText[lId:])
                else:
                    symText = '%s^{%s}%s' % (symText[:lId], b, symText[lId:])
            else:
                if type(b) == Const:
                    symText = '%s^{%s}' % (s_symText, b._Const__symText)
                elif type(b) == int or type(b) == float:
                    symText = '%s^{%s}' % (s_symText, dec2Latex(b, noBracket=True))
                elif 'sympy' in str(type(b)):
                    symText = '%s^{%s}' % (s_symText, sympy.latex(b))
                else:
                    symText = '%s^{%s}' % (s_symText, b)
            if type(b) == Const:
                symBrac = max(s_symBrac, b._Const__symBrac)
            else:
                symBrac = s_symBrac
        if self.__genCal:
            if type(b) == Const:
                sNum = self.__sNum ** b
                calBrac = max(s_calBrac, b._Const__calBrac)
            elif 'sympy' in str(type(b)):
                sNum = self.__sNum ** float(b)
                calBrac = s_calBrac
            else:
                sNum = self.__sNum ** b
                calBrac = s_calBrac
            if self.__calPrior == 4:  #对于对数函数、三角函数的乘方
                calText = s_calText
                lId = calText.find('{')
                if calText[:13] == r'\operatorname':
                    lId = calText.find('{', lId + 1)
                if type(b) == Const:
                    calText = '%s^{%s}%s' % (calText[:lId], b._Const__calText, calText[lId:])
                elif type(b) == int or type(b) == float:
                    calText = '%s^{%s}%s' % (calText[:lId], dec2Latex(b, noBracket=True), calText[lId:])
                elif 'sympy' in str(type(b)):
                    calText = '%s^{%s}%s' % (calText[:lId], sympy.latex(b), calText[lId:])
                else:
                    calText = '%s^{%s}%s' % (calText[:lId], b, calText[lId:])
            else:
                if type(b) == Const:
                    calText = '%s^{%s}' % (s_calText, b._Const__calText)
                elif type(b) == int or type(b) == float:
                    calText = '%s^{%s}' % (s_calText, dec2Latex(b, noBracket=True))
                elif 'sympy' in str(type(b)):
                    calText = '%s^{%s}' % (s_calText, sympy.latex(b))
                else:
                    calText = '%s^{%s}' % (s_calText, b)
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 3, 3, self.__s_decL, s_dec)
    
    def __rpow__(self, a):
        if str(type(a)) in superiorTypes:
            return a.__pow__(self)
        ### 括号与文本预处理 ###
        assert type(a) != LSym, 'LaTeX符号/符号组之间不能进行乘方运算'
        if type(a) == Const:
            o_symBrac = a._Const__symBrac
            o_symText = a._Const__symText
            o_calBrac = a._Const__calBrac
            o_calText = a._Const__calText
            if 3 >= a._Const__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 3 >= a._Const__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        symText = sNum = calText = symBrac = calBrac = None
        if type(a) == Const:
            o_s_decL = a._Const__s_decL
            s_dec = self.__s_decL and self.__s_decR and a._Const__s_decL and a._Const__s_decR
        elif type(a) == int or type(a) == float:
            o_s_decL = True
            s_dec = self.__s_decL and self.__s_decR
        else:
            o_s_decL = False
            s_dec = False
        if self.__genSym:
            if type(a) == Const:
                symText = '%s^{%s}' % (o_symText, self.__symText)
                symBrac = max(o_symBrac, self.__symBrac)
            elif type(a) == int or type(a) == float:
                symText = '%s^{%s}' % (dec2Latex(a), self.__symText)
                symBrac = max(-(a>=0), self.__symBrac)
            elif 'sympy' in str(type(a)):
                symText = '%s^{%s}' % (sympy.latex(a), self.__symText)
                symBrac = self.__symBrac
            else:
                symText = '%s^{%s}' % (a, self.__symText)
                symBrac = self.__symBrac
        if self.__genCal:
            if type(a) == Const:
                sNum = a ** self.__sNum
                calText = '%s^{%s}' % (o_calText, self.__calText)
                calBrac = max(o_calBrac, self.__calBrac)
            elif type(a) == int or type(a) == float:
                sNum = a ** self.__sNum
                calText = '%s^{%s}' % (dec2Latex(a), self.__calText)
                calBrac = max(-(a>=0), self.__calBrac)  
            elif 'sympy' in str(type(a)):
                sNum = float(a) ** self.__sNum
                calText = '%s^{%s}' % (sympy.latex(a), self.__calText)
                calBrac = self.__calBrac  
            else:
                sNum = a ** self.__sNum
                calText = '%s^{%s}' % (a, self.__calText)
                calBrac = self.__calBrac  
        return self.__newInstance(sNum, symText, calText, symBrac, calBrac, 3, 3, o_s_decL, s_dec)
