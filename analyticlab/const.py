# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 13:10:41 2018

@author: wzv100
"""
import math
from .system.numberformat import dec2Latex

class Const():
    '''Const为常数类，通过该类定义的常数，可以在数值运算、LaTeX符号运算、符号显示中使用。'''
    __value = 0
    __symText = None
    __prior = 6  #初始符号式优先级为6
    __brac = -1  #当前符号式括号级别：-1为无括号，0为()，0为[]，0为{}
    __isUt1e = False
    __isT1e = False
    __isHPercent = False
    '''
    符号优先级规定：
    + -：1
    * / //：2
    ** exp：3
    sqrt 绝对值：4
    lg ln sin cos tan csc sec cot arcsin arccos arctan arccsc arcsec arccot ：5
    初始符号：6
    '''
    
    def __init__(self, sym, value):
        '''初始化一个Const常数
        【参数说明】
        1.sym（str）：常数符号。
        2.value（int或float）：常数对应的数值。
        【应用举例】
        >>> k = Const('k', 8.973e-7)
        '''
        self.__symText = sym
        self.__value = value

    def __bracket(self, bId):
        if bId == 0:
            return r'\left(%s\right)'
        elif bId == 1:
            return r'\left[%s\right]'
        elif bId >= 2:
            return r'\left \{%s\right \}'
        
    def __newInstance(self, symText, value, prior, brac):
        new = Const(symText, value)
        new.__prior = prior
        new.__brac = brac
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
    
    def __abs__(self):
        symText = r'\left\lvert %s \right\rvert' % self.__symText
        return self.__newInstance(symText, abs(self.__value), 4, self.__brac)
    
    def __neg__(self, obj):
        #取负需要考虑self的括号
        brac = self.__brac
        symText = self.__symText
        if type(obj) in (int, float, Const) and 1 == self.__prior:
            brac += 1
            symText = self.__bracket(brac) % symText
        symText = '-' + self.__symText
        return self.__newInstance(symText, -self.__value, 1, self.__brac)
    
    def __add__(self, obj):
        brac = self.__brac
        if type(obj) == int or type(obj) == float:
            symText = '%s+%s' % (self.__symText, dec2Latex(obj))
            return self.__newInstance(symText, self.__value + obj, 1, brac)
        elif type(obj) == Const:
            symText = '%s+%s' % (self.__symText, obj)
            return self.__newInstance(symText, self.__value + obj.__value, 1, max(brac, obj.__brac))
        else:
            return obj.__radd__(self)
        
    def __radd__(self, obj):
        if type(obj) == int or type(obj) == float:
            symText = '%s+%s' % (dec2Latex(obj), self.__symText)
            return self.__newInstance(symText, obj + self.__value, 1, self.__brac)
        elif type(obj) == Const:
            symText = '%s+%s' % (obj, self.__symText)
            return self.__newInstance(symText, obj.__value + self.__value, 1, max(obj.__brac, self.__brac))
        else:
            return obj.__add__(self)
        
    def __sub__(self, obj):
        if type(obj) == Const:
            obrac = obj.__brac
            osymText = obj.__symText
        if type(obj) == Const and 1 == obj.__prior:
            obrac += 1
            osymText = self.__bracket(obrac) % osymText
        if type(obj) == int or type(obj) == float:
            symText = '%s-%s' % (self.__symText, dec2Latex(obj))
            return self.__newInstance(symText, self.__value - obj, 1, self.__brac)
        elif type(obj) == Const:
            symText = '%s-%s' % (self.__symText, obj)
            return self.__newInstance(symText, self.__value - obj.__value, 1, max(self.__brac, obrac))
        else:
            return obj.__rsub__(self)
        
    def __rsub__(self, obj):
        brac = self.__brac
        symText = self.__symText
        if type(obj) in (int, float, Const) and 1 == self.__prior:  
            brac += 1
            symText = self.__bracket(brac) % symText
        if type(obj) == int or type(obj) == float:
            symText = '%s-%s' % (dec2Latex(obj), symText)
            return self.__newInstance(symText, obj - self.__value, 1, brac)
        elif type(obj) == Const:
            symText = '%s-%s' % (obj, symText)
            return self.__newInstance(symText, obj.__value - self.__value, 1, max(obj.__brac, brac))
        else:
            return obj.__sub__(self)
    
    def __mul__(self, obj):
        brac = self.__brac
        symText = self.__symText
        if type(obj) == Const:
            obrac = obj.__brac
            osymText = obj.__symText
        if type(obj) in (int, float, Const) and 2 > self.__prior:
            brac += 1
            symText = self.__bracket(brac) % symText
        if type(obj) == Const and 2 > obj.__prior:
            obrac += 1
            osymText = self.__bracket(obrac) % osymText
        if type(obj) == int or type(obj) == float:
            symText = r'%s \cdot %s' % (symText, dec2Latex(obj))
            return self.__newInstance(symText, self.__value * obj, 2, brac)
        elif type(obj) == Const:
            if obj.__isUt1e or obj.__isT1e:
                symText = r'%s \cdot %s' % (symText, osymText)
            else:
                symText = symText + osymText
            return self.__newInstance(symText, self.__value * obj.__value, 2, max(brac, obrac))
        else:
            return obj.__rmul__(self)
        
    def __rmul__(self, obj):
        brac = self.__brac
        symText = self.__symText
        if type(obj) == Const:
            obrac = obj.__brac
            osymText = obj.__symText
        if type(obj) in (int, float, Const) and 2 > self.__prior:
            brac += 1
            symText = self.__bracket(brac) % symText
        if type(obj) == Const and 2 > obj.__prior:
            obrac += 1
            osymText = self.__bracket(obrac) % osymText
        if type(obj) == int or type(obj) == float:
            symText = r'%s %s' % (dec2Latex(obj), symText)
            return self.__newInstance(symText, obj * self.__value, 2, brac)
        elif type(obj) == Const:
            if obj.__isUt1e or obj.__isT1e:
                symText = r'%s \cdot %s' % (osymText, symText)
            else:
                symText = osymText + symText
            return self.__newInstance(symText, obj.__value * self.__value, 2, max(obrac, brac))
        else:
            return obj.__mul__(self)
        
    def __truediv__(self, obj):
        if type(obj) == int or type(obj) == float:
            symText = r'\cfrac{%s}{%s}' % (self.__symText, dec2Latex(obj))
            return self.__newInstance(symText, self.__value / obj, 2, self.__brac)
        elif type(obj) == Const:
            symText = r'\cfrac{%s}{%s}' % (self.__symText, obj)
            return self.__newInstance(symText, self.__value / obj.__value, 2, max(self.__brac, obj.__brac))
        else:
            return obj.__rtruediv__(self)
        
    def __rtruediv__(self, obj):
        if type(obj) == int or type(obj) == float:
            symText = r'\cfrac{%s}{%s}' % (dec2Latex(obj), self.__symText)
            return self.__newInstance(symText, obj / self.__value, 2, self.__brac)
        elif type(obj) == Const:
            symText = r'\cfrac{%s}{%s}' % (obj, self.__symText)
            return self.__newInstance(symText, obj.__value / self.__value, 2, max(obj.__brac, self.__brac))
        else:
            return obj.__truediv__(self)
        
    def __floordiv__(self, obj):
        brac = self.__brac
        symText = self.__symText
        if type(obj) == Const:
            obrac = obj.__brac
            osymText = obj.__symText
        #/式除号，考虑prior
        if type(obj) in (int, float, Const) and 2 > self.__prior:
            brac += 1
            symText = self.__bracket(brac) % symText
        #右除需要考虑obj除号
        if type(obj) == Const and 2 >= obj.__prior:
            obrac += 1
            osymText = self.__bracket(obrac) % osymText
        if type(obj) == int or type(obj) == float:
            symText = r'%s/%s' % (symText, dec2Latex(obj))
            return self.__newInstance(symText, self.__value / obj, 2, brac)
        elif type(obj) == Const:
            symText = r'%s/%s' % (symText, obj)
            return self.__newInstance(symText, self.__value / obj.__value, 2, max(brac, obrac))
        else:
            return obj.__rfloordiv__(self)
        
    def __rfloordiv__(self, obj):
        brac = self.__brac
        symText = self.__symText
        if type(obj) == Const:
            obrac = obj.__brac
            osymText = obj.__symText
        #/式除号，考虑prior
        #左除需要考虑self除号
        if type(obj) in (int, float, Const) and 2 >= self.__prior:  #左除需要考虑self除号
            brac += 1
            symText = self.__bracket(brac) % symText
        if type(obj) == Const and 2 > obj.__prior:
            obrac += 1
            osymText = self.__bracket(obrac) % osymText
        if type(obj) == int or type(obj) == float:
            symText = r'%s/%s' % (dec2Latex(obj), symText)
            return self.__newInstance(symText, obj / self.__value, 2, brac)
        elif type(obj) == Const:
            symText = r'%s/%s' % (obj, symText)
            return self.__newInstance(symText, obj.__value / self.__value, 2, max(obrac, brac))
        else:
            return obj.__floordiv__(self)
    
    def __pow__(self, b):
        brac = self.__brac
        symText = self.__symText
        if type(b) in (int, float, Const) and 3 >= self.__prior:
            brac += 1
            symText = self.__bracket(brac) % symText
        if type(b) == int or type(b) == float:
            symText = r'{%s}^{%g}' % (symText, b)
            return self.__newInstance(symText, self.__value**b, 3, brac)
        elif type(b) == Const:
            symText = r'{%s}^{%s}' % (symText, b)
            return self.__newInstance(symText, self.__value**b.__value, 3, max(brac, b.__brac))
        else:
            return b.__rpow__(self)
        
    def __rpow__(self, a):
        if type(a) == int or type(a) == float:
            symText = r'{%s}^{%s}' % (dec2Latex(a), self.__symText)
            return Const(symText, a**self.__value, 3, self.__brac)
        elif type(a) == Const:
            symText = r'{%s}^{%s}' % (a, self.__symText)
            return Const(symText, a.__value**self.__value, max(a.__brac, self.__brac))
        else:
            return a.__pow__(self)
    
    
PI = Const(r'\pi ', math.pi)
E = Const('e', math.e)

hPercent = Const(r'100\%', 1)
hPercent._Const__isHPercent = True

def t1e(n):
    '''生成一般的科学记数法常量
    【参数说明】
    n（int）：科学记数法指数，即10的n次方'''
    u = Const('10^{%d}' % n, 10**n)
    u._Const__isT1e = True
    u._Const__prior = 2
    return u

def ut1e(n):
    '''生成用于单位换算的科学记数法常量
    【参数说明】
    n（int）：科学记数法指数，即10的n次方'''
    u = Const('10^{%d}' % n, 10**n)
    u._Const__isUt1e = True
    u._Const__prior = 2
    return u