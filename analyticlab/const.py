# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 13:10:41 2018

@author: wzv100
"""
import math
from quantities.quantity import Quantity
from .system.numberformat import dec2Latex

class Const():
    '''Const为常数类，通过该类定义的常数，可以在数值运算、LaTeX符号运算、符号显示中使用。'''
    __symPrior = 6  #初始符号式优先级为6
    __calPrior = 6  #初始计算式优先级为6
    __symText = None
    __calText = None
    __symBrac = -1  #当前符号式括号级别：-1为无括号，0为()，0为[]，0为{}
    __calBrac = -1  #当前计算式括号级别：-1为无括号，0为()，1为[]，2为{}
    __value = 0
    __q = 1
    __special = None
    # 下述两个布尔变量用于乘法运算的符号式中，根据是否为数字判断省略乘号还是用点乘号，这两
    # 个变量仅在symPrior>=2时需要考虑，加减运算外围是乘除运算的情况下会括号，故不需要考虑
    __s_decL = False  #符号式的左端是否为数字
    __s_decR = False  #符号式的右端是否为数字
    __c_decL = True  #计算式的左端是否为数字
    __c_decR = True  #计算式的右端是否为数字
    '''
    符号优先级规定：
    负数：0  #仅适用于cal
    科学记数法：2  #仅适用于cal
    + -：1
    * / //：2
    ** exp：3
    lg ln sin cos tan csc sec cot arcsin arccos arctan arccsc arcsec arccot：4
    sqrt 绝对值：5
    初始符号/正数：6
    '''
    
    def __init__(self, sym, value, unit=None, showValue=True):
        '''初始化一个Const常数
        【参数说明】
        1.sym（str）：常数符号。
        2.value（int或float）：常数对应的数值。
        【应用举例】
        >>> k = Const('k', 8.973e-7)
        '''
        if sym == None:
            return
        self.__symText = '{%s}' % sym
        self.__value = value
        if showValue:
            self.__calText = dec2Latex(value, noBracket=True)
            if value < 0:  #负数calPrior为0
                self.__calPrior = 0
            elif '^' in self.__calText:  #科学计数法calPrior为0
                self.__calPrior = 2
        else:
            self.__calText = self.__symText
            self.__c_decL = False
            self.__c_decR = False
        if unit != None:
            if type(unit) == str:
                self.__q = Quantity(1, unit)
            elif type(unit) == Quantity:
                self.__q = unit
            
    def __bracket(self, bId):
        if bId == 0:
            return r'\left(%s\right)'
        elif bId == 1:
            return r'\left[%s\right]'
        elif bId >= 2:
            return r'\left \{%s\right \}'
        
    def __newInstance(self, symText, calText, symBrac, calBrac, symPrior, calPrior, value, q, s_decL=False, s_decR=False, c_decL=True, c_decR=True):
        new = Const(None, None)
        new.__symText = symText
        new.__calText = calText
        new.__symBrac = symBrac
        new.__calBrac = calBrac
        new.__symPrior = symPrior
        new.__calPrior = calPrior
        new.__value = value
        new.__q = q
        new.__s_decL = s_decL
        new.__s_decR = s_decR
        new.__s_decL = s_decL
        new.__s_decR = s_decR
        return new
    
    def value(self):
        '''获得常数对应的数值'''
        return self.__value
    
    def sym(self):
        '''获得常数符号'''
        return self.__symText
    
    def __str__(self):
        return self.__symText
    
    def __repr__(self):
        return self.__symText
    
    def _repr_latex_(self):
        return '$%s$' % self.__symText
    
    def __abs__(self):
        symText = r'\left\lvert %s \right\rvert' % self.__symText
        calText = r'\left\lvert %s \right\rvert' % self.__calText
        return self.__newInstance(symText, calText, self.__symBrac, self.__calBrac, 5, 5, abs(self.__value), self.__q, False, False, self.__c_decL, self.__c_decR)
    
    def __neg__(self):
        #取负需要考虑self的括号
        ### 括号与文本预处理 ###
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 1 == self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 1 >= self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        ### 合成表达式 ###
        symText = '-' + s_symText
        calText = '-' + s_calText
        return self.__newInstance(symText, calText, s_symBrac, s_calBrac, 1, 1, -self.__value, self.__q)
    
    def __add__(self, obj):
        ### 括号与文本预处理 ###
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 0 == self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            if 0 == obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = '%s+%s' % (self.__symText, dec2Latex(obj))
            calText = '%s+%s' % (s_calText, dec2Latex(obj))
            symBrac = max(self.__symBrac, -(obj>=0))
            calBrac = max(s_calBrac, -(obj>=0))
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, self.__value + obj, self.__q)
        elif type(obj) == Const:
            symText = '%s+%s' % (self.__symText, obj.__symText)
            calText = '%s+%s' % (s_calText, o_calText)
            symBrac = max(self.__symBrac, obj.__symBrac)
            calBrac = max(s_calBrac, o_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, self.__value + obj.__value, self.__q)
        else:
            return obj.__radd__(self)
        
    def __radd__(self, obj):
        ### 括号与文本预处理 ###
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 0 == self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            if 0 == obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = '%s+%s' % (dec2Latex(obj), self.__symText)
            calText = '%s+%s' % (dec2Latex(obj), s_calText)
            symBrac = max(-(obj>=0), self.__symBrac)
            calBrac = max(-(obj>=0), s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, obj + self.__value, self.__q)
        elif type(obj) == Const:
            symText = '%s+%s' % (obj.__symText, self.__symText)
            calText = '%s+%s' % (o_calText, s_calText)
            symBrac = max(obj.__symBrac, self.__symBrac)
            calBrac = max(o_calBrac, s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, obj.__value + self.__value, self.__q)
        else:
            return obj.__add__(self)
        
    def __sub__(self, obj):
        ### 括号与文本预处理 ###
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 0 == self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            if 1 == obj.__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 1 >= obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = '%s-%s' % (self.__symText, dec2Latex(obj))
            calText = '%s-%s' % (s_calText, dec2Latex(obj))
            symBrac = max(self.__symBrac, -(obj>=0))
            calBrac = max(s_calBrac, -(obj>=0))
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, self.__value - obj, self.__q)
        elif type(obj) == Const:
            symText = '%s-%s' % (self.__symText, o_symText)
            calText = '%s-%s' % (s_calText, o_calText)
            symBrac = max(self.__symBrac, o_symBrac)
            calBrac = max(s_calBrac, o_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, self.__value - obj.__value, self.__q)
        else:
            return obj.__rsub__(self)
        
    def __rsub__(self, obj):
        ### 括号与文本预处理 ###
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 1 == self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 1 >= self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            if 0 == obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = '%s-%s' % (dec2Latex(obj), s_symText)
            calText = '%s-%s' % (dec2Latex(obj), s_calText)
            symBrac = max(-(obj>=0), s_symBrac)
            calBrac = max(-(obj>=0), s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, obj - self.__value, self.__q)
        elif type(obj) == Const:
            symText = '%s-%s' % (obj.__symText, s_symText)
            calText = '%s-%s' % (o_calText, s_calText)
            symBrac = max(obj.__symBrac, s_symBrac)
            calBrac = max(o_calBrac, s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 1, 1, obj.__value - self.__value, self.__q)
        else:
            return obj.__sub__(self)
    
    def __mul__(self, obj):
        ### 括号与文本预处理 ###
        symPrior = 2
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 2 > self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_symText = obj.__symText
            o_calText = obj.__calText
            if obj.__special != 'ut1e':
                o_symBrac = obj.__symBrac
                o_calBrac = obj.__calBrac
            assert self.__special != 'ut1e' or obj.__special != 'ut1e', '请不要将两个ut1e相乘'
            if 2 > obj.__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
            if obj.__special == 'ut1e':  #对于ut1e科学记数法符号，符号优先级为原来的符号优先级
                symPrior = self.__symPrior
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = r'%s \cdot %s' % (s_symText, dec2Latex(obj))
            calText = r'%s \times %s' % (s_calText, dec2Latex(obj))
            symBrac = max(s_symBrac, -(obj>=0))
            calBrac = max(s_calBrac, -(obj>=0))
            return self.__newInstance(symText, calText, symBrac, calBrac, symPrior, 2, self.__value * obj, self.__q, self.__s_decL, True, self.__c_decL, True)
        elif type(obj) == Const:
            if obj.__special == 'ut1e':
                symText = s_symText
                #科学计数法本身无括号，故不需要考虑科学计数法的括号
                symBrac = s_symBrac
                calBrac = s_calBrac
            else:
                #是否需要乘号根据后面的数，即obj左端是否为数字而定，或者在外围为函数时由self右端而定
                if obj.__s_decL or (self.__symPrior == 4 and self.__s_decR): 
                    symText = r'%s \cdot %s' % (s_symText, o_symText)
                else:
                    symText = s_symText + o_symText
                symBrac = max(s_symBrac, o_symBrac)
                calBrac = max(s_calBrac, o_calBrac)
            calText = '%s \times %s' % (s_calText, o_calText)
            return self.__newInstance(symText, calText, symBrac, calBrac, symPrior, 2, self.__value * obj.__value, self.__q * obj.__q, self.__s_decL, obj.__s_decR, self.__c_decL, obj.__s_decR)
        else:
            return obj.__rmul__(self)
        
    def __rmul__(self, obj):
        ### 括号与文本预处理 ###
        symPrior = 2
        s_symText = self.__symText
        s_calText = self.__calText
        if self.__special != 'ut1e':
            s_symBrac = self.__symBrac
            s_calBrac = self.__calBrac
        if 2 > self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            assert obj.__special != 'ut1e' or self.__special != 'ut1e', '请不要将两个ut1e相乘'
            if 2 > obj.__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
            if self.__special == 'ut1e':  #对于ut1e科学记数法符号，符号优先级为原来的符号优先级
                symPrior = obj.__symPrior
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            if self.__s_decL:
                symText = r'%s \cdot %s' % (dec2Latex(obj), s_symText)
            else:
                symText = dec2Latex(obj) + s_symText
            calText = r'%s \times %s' % (dec2Latex(obj), s_symText)
            symBrac = max(-(obj>=0), s_symBrac)
            calBrac = max(-(obj>=0), s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, symPrior, 2, obj * self.__value, self.__q, True, self.__s_decR, True, self.__c_decR)
        elif type(obj) == Const:
            if obj.__special == 'ut1e':
                symText = s_symText
                #科学计数法本身无括号，故不需要考虑科学计数法的括号
                symBrac = s_symBrac
                calBrac = s_calBrac
            else:
                #是否需要乘号根据后面的数，即self左端是否为数字而定，或者在外围为函数时由obj右端而定
                if self.__s_decL or (obj.__symPrior == 4 and obj.__s_decR):  
                    symText = r'%s \cdot %s' % (o_symText, s_symText)
                else:
                    symText = o_symText + s_symText
                symBrac = max(o_symBrac, s_symBrac)
                calBrac = max(o_calBrac, s_calBrac)
            calText = '%s \times %s' % (o_calText, s_calText)
            return self.__newInstance(symText, calText, symBrac, calBrac, symPrior, 2, obj.__value * self.__value, obj.__q * self.__q, obj.__s_decL, self.__s_decR, obj.__c_decL, self.__c_decR)
        else:
            return obj.__mul__(self)
        
    def __truediv__(self, obj):
        ### 括号与文本预处理 ###
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = r'\cfrac{%s}{%s}' % (self.__symText, dec2Latex(obj, noBracket=True))
            calText = r'\cfrac{%s}{%s}' % (self.__calText, dec2Latex(obj, noBracket=True))
            s_dec = self.__s_decL and self.__s_decR
            c_dec = self.__c_decL and self.__c_decR
            return self.__newInstance(symText, calText, self.__symBrac, self.__calBrac, 2, 2, self.__value / obj, self.__q, s_dec, s_dec, c_dec, c_dec)
        elif type(obj) == Const:
            symText = r'\cfrac{%s}{%s}' % (self.__symText, obj.__symText)
            calText = r'\cfrac{%s}{%s}' % (self.__calText, obj.__calText)
            symBrac = max(self.__symBrac, obj.__symBrac)
            calBrac = max(self.__calBrac, obj.__calBrac)
            s_dec = self.__s_decL and self.__s_decR and obj.__s_decL and obj.__s_decR
            c_dec = self.__c_decL and self.__c_decR and obj.__c_decL and obj.__c_decR
            return self.__newInstance(symText, calText, symBrac, calBrac, 2, 2, self.__value / obj.__value, self.__q / obj.__q, s_dec, s_dec, c_dec, c_dec)
        else:
            return obj.__rtruediv__(self)
        
    def __rtruediv__(self, obj):
        ### 括号与文本预处理 ###
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = r'\cfrac{%s}{%s}' % (dec2Latex(obj, noBracket=True), self.__symText)
            calText = r'\cfrac{%s}{%s}' % (dec2Latex(obj, noBracket=True), self.__calText)
            s_dec = self.__s_decL and self.__s_decR
            c_dec = self.__c_decL and self.__c_decR
            return self.__newInstance(symText, calText, self.__symBrac, self.__calBrac, 2, 2, obj / self.__value, self.__q, s_dec, s_dec, c_dec, c_dec)
        elif type(obj) == Const:
            symText = r'\cfrac{%s}{%s}' % (obj.__symText, self.__symText)
            calText = r'\cfrac{%s}{%s}' % (obj.__calText, self.__calText)
            symBrac = max(obj.__symBrac, self.__symBrac)
            calBrac = max(obj.__calBrac, self.__calBrac)
            s_dec = obj.__s_decL and obj.__s_decR and self.__s_decL and self.__s_decR
            c_dec = obj.__c_decL and obj.__c_decR and self.__c_decL and self.__c_decR
            return self.__newInstance(symText, calText, symBrac, calBrac, 2, 2, obj.__value / self.__value, self.__q / obj.__q, s_dec, s_dec, c_dec, c_dec)
        else:
            return obj.__truediv__(self)
        
    def __floordiv__(self, obj):
        ### 括号与文本预处理 ###
        #/式除号，考虑prior
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 2 > self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 > self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            #右除需要考虑obj除号
            if 2 >= obj.__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 >= obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = r'%s/%s' % (s_symText, dec2Latex(obj))
            calText = r'%s/%s' % (s_calText, dec2Latex(obj))
            symBrac = max(s_symBrac, -(obj>=0))
            calBrac = max(s_calBrac, -(obj>=0))
            return self.__newInstance(symText, calText, symBrac, calBrac, 2, 2, self.__value / obj, self.__q, self.__s_decL, True, self.__c_decL, True)
        elif type(obj) == Const:
            symText = r'%s/%s' % (s_symText, o_symText)
            calText = r'%s/%s' % (s_calText, o_calText)
            symBrac = max(s_symBrac, o_symBrac)
            calBrac = max(s_calBrac, o_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 2, 2, self.__value / obj.__value, self.__q / obj.__q, self.__s_decL, True, self.__c_decL, True)
        else:
            return obj.__rfloordiv__(self)
        
    def __rfloordiv__(self, obj):
        ### 括号与文本预处理 ###
        #/式除号，考虑prior
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        #左除需要考虑self除号
        if 2 >= self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 2 >= self.__calPrior:
            if self.__genCal:
                s_calBrac += 1
                s_calText = self.__bracket(s_calBrac) % s_calText
        if type(obj) == Const:
            o_symBrac = obj.__symBrac
            o_symText = obj.__symText
            o_calBrac = obj.__calBrac
            o_calText = obj.__calText
            if 2 > obj.__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 2 > obj.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(obj) == int or type(obj) == float:
            symText = r'%s/%s' % (dec2Latex(obj), s_symText)
            calText = r'%s/%s' % (dec2Latex(obj), s_calText)
            symBrac = max(-(obj>=0), s_symBrac)
            calBrac = max(-(obj>=0), s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 2, 2, obj / self.__value, 1 / self.__q, True, True, True, True)
        elif type(obj) == Const:
            symText = r'%s/%s' % (o_symText, s_symText)
            calText = r'%s/%s' % (o_calText, s_calText)
            symBrac = max(o_symBrac, s_symBrac)
            calBrac = max(o_calBrac, s_calBrac)
            return self.__newInstance(symText, calText, symBrac, calBrac, 2, 2, obj.__value / self.__value, obj.__q / self.__q, obj.__s_decL, True, obj.__c_decL, True)
        else:
            return obj.__floordiv__(self)
    
    def __pow__(self, b):
        ### 括号与文本预处理 ###
        s_symBrac = self.__symBrac
        s_symText = self.__symText
        s_calBrac = self.__calBrac
        s_calText = self.__calText
        if 3 >= self.__symPrior:
            s_symBrac += 1
            s_symText = self.__bracket(s_symBrac) % s_symText
        if 3 >= self.__calPrior:
            s_calBrac += 1
            s_calText = self.__bracket(s_calBrac) % s_calText
        ### 合成表达式 ###
        if self.__symPrior == 4:  #对于对数函数、三角函数的乘方
            symText, calText = s_symText, s_calText
            lId = symText.find('{')
            if symText[:13] == r'\operatorname':
                lId = symText.find('{', lId + 1)
        if type(b) == int or type(b) == float:
            if self.__symPrior == 4:  #对于对数函数、三角函数的乘方
                symText = '%s^{%s}%s' % (symText[:lId], dec2Latex(b, noBracket=True), symText[lId:])
                calText = '%s^{%s}%s' % (calText[:lId], dec2Latex(b, noBracket=True), calText[lId:])
            else:
                symText = r'{%s}^{%s}' % (s_symText, dec2Latex(b, noBracket=True))
                calText = r'{%s}^{%s}' % (s_calText, dec2Latex(b, noBracket=True))
            symBrac = max(s_symBrac, -(b>=0))
            calBrac = max(s_calBrac, -(b>=0))
            s_dec = self.__s_decL and self.__s_decR
            c_dec = self.__c_decL and self.__c_decR
            return self.__newInstance(symText, calText, symBrac, calBrac, 3, 3, self.__value**b, self.__q**b, self.__s_decL, s_dec, self.__c_decL, c_dec)
        elif type(b) == Const:
            if self.__symPrior == 4:  #对于对数函数、三角函数的乘方
                symText = '%s^{%s}%s' % (symText[:lId], b.__symText, symText[lId:])
                calText = '%s^{%s}%s' % (calText[:lId], b.__calText, calText[lId:])
            else:
                symText = r'{%s}^{%s}' % (s_symText, b.__symText)
                calText = r'{%s}^{%s}' % (s_calText, b.__calText)
            symBrac = max(s_symBrac, b.__symBrac)
            calBrac = max(s_calBrac, b.__calBrac)
            s_dec = self.__s_decL and self.__s_decR and b.__s_decL and b.__s_decR
            c_dec = self.__c_decL and self.__c_decR and b.__c_decL and b.__c_decR
            return self.__newInstance(symText, calText, symBrac, calBrac, 3, 3, self.__value**b.__value, self.__q**b.__value, self.__s_decL, s_dec, self.__c_decL, c_dec)
        else:
            return b.__rpow__(self)
        
    def __rpow__(self, a):
        ### 括号与文本预处理 ###
        if type(a) == Const:
            o_symBrac = a.__symBrac
            o_symText = a.__symText
            o_calBrac = a.__calBrac
            o_calText = a.__calText
            if 3 >= a.__symPrior:
                o_symBrac += 1
                o_symText = self.__bracket(o_symBrac) % o_symText
            if 3 >= a.__calPrior:
                o_calBrac += 1
                o_calText = self.__bracket(o_calBrac) % o_calText
        ### 合成表达式 ###
        if type(a) == int or type(a) == float:
            symText = r'{%s}^{%s}' % (dec2Latex(a), self.__symText)
            calText = r'{%s}^{%s}' % (dec2Latex(a), self.__calText)
            symBrac = max(-(a>=0), self.__symBrac)
            calBrac = max(-(a>=0), self.__calText)
            o_s_decL = True
            o_c_decL = True
            s_dec = self.__s_decL and self.__s_decR
            c_dec = self.__c_decL and self.__c_decR
            return self.__newInstance(symText, calText, symBrac, calBrac, 3, 3, a**self.__value, 1, o_s_decL, s_dec, o_c_decL, c_dec)
        elif type(a) == Const:
            symText = r'{%s}^{%s}' % (o_symText, self.__symText)
            calText = r'{%s}^{%s}' % (o_calText, self.__calText)
            symBrac = max(a.__symBrac, self.__symBrac)
            calBrac = max(a.__calBrac, self.__calBrac)
            o_s_decL = a.__s_decL
            o_c_decL = a.__c_decL
            s_dec = a.__s_decL and a.__s_decR and self.__s_decL and self.__s_decR
            c_dec = a.__c_decL and a.__c_decR and self.__c_decL and self.__c_decR
            return self.__newInstance(symText, calText, symBrac, calBrac, 3, 3, a.__value**self.__value, a.__q**self.__value, o_s_decL, s_dec, o_c_decL, c_dec)
        else:
            return a.__pow__(self)
    
    
PI = Const(r'\pi ', math.pi, showValue=False)
E = Const('e', math.e, showValue=False)

hPercent = Const(r'100\%', 1, showValue=False)
hPercent._Const__special = 'hPercent'

def t1e(n, unit=None):
    '''生成一般的科学记数法常量
    【参数说明】
    n（int）：科学记数法指数，即10的n次方'''
    u = Const('10^{%d}' % n, 10**n, unit, showValue=False)
    u._Const__symPrior = 2
    u._Const__s_decL = True
    u._Const__s_decR = True
    return u

def ut1e(n, unit=None):
    '''生成用于单位换算的科学记数法常量
    【参数说明】
    n（int）：科学记数法指数，即10的n次方'''
    u = Const('10^{%d}' % n, 10**n, unit, showValue=False)
    u._Const__special = 'ut1e'
    u._Const__symPrior = 2
    return u