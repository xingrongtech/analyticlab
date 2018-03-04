# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 19:28:45 2018

@author: xingrongtech
"""
from analyticlab.numitem import NumItem
from analyticlab.lsym import LSym
from analyticlab.system.exceptions import itemNotSameLengthException, expressionInvalidException

class LSymItem():
    '''LSymItem为LaTeX符号组类，该类能够按组批量计算并生成代数式、数值式的LaTeX表达式。'''
    sepSymCalc = False  #静态属性，控制是否分离代数表达式和计算表达式
    
    __lsyms = []
    __sepSym = None
    __index = 0
    __symText = None
    
    def __init__(self, sym, sNumItem):
        '''初始化一个LSymItem符号组
        【参数说明】
        1.sym：符号组的符号。
        2.sNumItem：符号组对应的数值数组。sNumItem可以是以下数据类型：
        (1)NumItem：直接给出符号组对应的NumItem数组。
        (2)str：对于还没有转换成Num的数值，将数值以空格隔开，表示成字符串表达式，以此生成符号组对应的NumItem数组。
        (3)list<Num>：对于已经转换成Num的数值，将数值用list表示出，以此生成符号组对应的NumItem数组。
        '''
        if sym == None and sNumItem == None:
            return
        self.__symText = sym
        if type(sNumItem) == str or type(sNumItem) == list:
            try:
                sNumItem = NumItem(sNumItem)
            except:
                raise expressionInvalidException('用于创建符号组的数组部分的参数无效')
        else:
            raise expressionInvalidException('用于创建符号组的参数无效')
        if LSymItem.sepSymCalc:  #将符号表达式与计算表达式分离
            self.__lsyms = [LSym(None, ni) for ni in sNumItem]
            self.__sepSym = LSym(sym, None)
        else:
            self.__lsyms = [LSym('{' + sym + '}', ni) for ni in sNumItem]
            for i in range(len(sNumItem)):
                self.__lsyms[i]._LSym__symText += '_{' + str(i+1) + '}'
    
    def __newInstance(self):
        return LSymItem(None, None)
    
    def __sepSymCalc(self):
        return LSymItem.sepSymCalc
        
    def __getitem__(self, index):
        return self.__lsyms[index]
    
    def __len__(self):
        return len(self.__lsyms)
    
    def __next__(self):
        if self.__index >= len(self.__lsyms):
            self.__index = 0
            raise StopIteration
        else:
            result = self.__lsyms[self.__index]
            self.__index += 1
            return result
    
    def getSepSym(self):
        '''当代数表达式与数值表达式分离时，用于获得分离出来的LaTeX符号。
        【返回值】
        LSym：分离出来的LaTeX符号。
        '''
        return self.__sepSym
        
    def __abs__(self):
        new = LSymItem(None, None)
        new.__lsyms = [ni.__abs__() for ni in self.__lsyms]
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__abs__()
        return new
        
    def __neg__(self):
        new = LSymItem(None, None)
        new.__lsyms = [ni.__neg__() for ni in self.__lsyms]
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__neg__()
        return new
        
    def __add__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__add__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__add__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__add__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__add__(obj)
        return new
    
    def __radd__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__radd__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__radd__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__radd__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__radd__(obj)
        return new
    
    def __sub__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__sub__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__sub__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__sub__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__sub__(obj)
        return new
    
    def __rsub__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__rsub__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rsub__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__rsub__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rsub__(obj)
        return new
    
    def __mul__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__mul__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__mul__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__mul__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__mul__(obj)
        return new
    
    def __rmul__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__rmul__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rmul__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__rmul__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rmul__(obj)
        return new
    
    def __truediv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__truediv__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__truediv__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__truediv__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__truediv__(obj)
        return new
    
    def __rtruediv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__rtruediv__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rtruediv__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__rtruediv__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rtruediv__(obj)
        return new
    
    def __floordiv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__floordiv__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__floordiv__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__floordiv__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__floordiv__(obj)
        return new
    
    def __rfloordiv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致！')
            new.__lsyms = []
            for i in range(len(self)):
                new.__lsyms.append(self.__lsyms[i].__rfloordiv__(obj.__lsyms[i]))
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rfloordiv__(obj.__sepSym)
        else:
            new.__lsyms = [ni.__rfloordiv__(obj) for ni in self.__lsyms]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rfloordiv__(obj)
        return new
    
    def __pow__(self, obj):
        new = LSymItem(None, None)
        new.__lsyms = [ni.__pow__(obj) for ni in self.__lsyms]
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__pow__(obj)
        return new
    
    def __rpow__(self, obj):
        new = LSymItem(None, None)
        new.__lsyms = [ni.__rpow__(obj) for ni in self.__lsyms]
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__rpow__(obj)
        return new