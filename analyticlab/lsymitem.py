# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 19:28:45 2018

@author: xingrongtech
"""
from .num import Num
from .numitem import NumItem
from .lsym import LSym
from .system.exceptions import itemNotSameLengthException, itemNotSameTypeException, itemNotSameKeysException, expressionInvalidException

class LSymItem():
    '''LSymItem为LaTeX符号组类，该类能够按组批量计算并生成代数式、数值式的LaTeX表达式。'''
    sepSymCalc = False  #静态属性，控制是否分离代数表达式和计算表达式
    
    __lsyms = []
    __sepSym = None
    __index = 0
    __symText = None
    
    def __init__(self, sym, sNumItem, subs=None):
        '''初始化一个LSymItem符号组
        【参数说明】
        1.sym（str）：符号组的符号。
        2.sNumItem：符号组对应的数值数组。sNumItem可以是以下数据类型：
        (1)NumItem：直接给出符号组对应的NumItem数组。
        (2)str：对于还没有转换成Num的数值，将数值以空格隔开，表示成字符串表达式，以此生成符号组对应的NumItem数组。
        (3)list<Num>：对于已经转换成Num的数值，将数值用list表示出，以此生成符号组对应的NumItem数组。
        (4)list<int>或list<float>：给出一组纯数字组成的list。
        3.subs（可选，str）：符号组中每个符号的下标，以空格隔开。在LSymItem.sepSymCalc为False的前提下，当subs为None时，会按照0、1、2...给每个符号索引，1、2、3...给每个符号编号；给出subs时，按照subs中给出的编号给每个符号索引和编号。默认subs=None。
        '''
        if sym == None and sNumItem == None:
            return
        self.__symText = sym
        if type(sNumItem) == str or (type(sNumItem) == list and type(sNumItem[0]) == Num):
            try:
                sNumItem = NumItem(sNumItem)
            except:
                raise expressionInvalidException('用于创建符号组的数组部分的参数无效')
        elif type(sNumItem) == NumItem:
            pass
        elif type(sNumItem) == list and (type(sNumItem[0]) == int or type(sNumItem[0]) == float):
            pass
        else:
            raise expressionInvalidException('用于创建符号组的参数无效')
        if LSymItem.sepSymCalc:  #将代数表达式与数值表达式分离
            if subs == None:  #未给出下标时，lsyms为list
                self.__lsyms = [LSym(None, ni) for ni in sNumItem]
            else:  #给出下标时，lsyms为dict
                subs = subs.split(' ')
                if len(sNumItem) != len(subs):
                    raise itemNotSameLengthException('给出subs时，sNumItem和subs必须为等长列表')
                self.__lsyms = {}
                for i in range(len(sNumItem)):
                    self.__lsyms[subs[i]] = LSym(None, sNumItem[i])
            self.__sepSym = LSym(sym, None)
        else:
            if subs == None:  #未给出下标时，lsyms为list
                self.__lsyms = [LSym('{' + sym + '}', ni) for ni in sNumItem]
                for i in range(len(sNumItem)):
                    self.__lsyms[i]._LSym__symText += '_{' + str(i+1) + '}'
            else:  #给出下标时，lsyms为dict
                subs = subs.split(' ')
                if len(sNumItem) != len(subs):
                    raise itemNotSameLengthException('给出subs时，sNumItem和subs必须为等长列表')
                self.__lsyms = {}
                for i in range(len(sNumItem)):
                    self.__lsyms[subs[i]] = LSym('{%s}_{%s}' % (sym, subs[i]), sNumItem[i])
    
    
    def refreshSym(self, sym):
        '''更新符号
        调用此方法后，原本的符号表达式将会被更新成新的符号表达式，原本的计算表达式将会被更新为当前LaTeX符号组中每个符号的数值，即LaTeX符号组被以新的符号和数值初始化。
        【参数说明】
        sym（str）：要更新成的符号。
        '''
        ##############################################
        def lsymSetCal(li):
            '''设置一个LSym的与计算计算有关的参量'''
            if type(li._LSym__sNum) == int or type(li._LSym__sNum) == float:
                li._LSym__calText = '%g' % li._LSym__sNum
            elif str(type(li._LSym__sNum)) == "<class 'analyticlab.num.Num'>":
                if li._LSym__sNum._Num__sciDigit() != 0:
                    li._LSym__calPrior = 2
                li._LSym__calText = '{' + li._LSym__sNum.latex() + '}'
            if li._LSym__sNum != None:  #如果是原始符号，则需要考虑是否因为负数或科学记数法而需要改变prior的情形
                if li._LSym__sNum < 0:  #负数prior为0
                    li._LSym__calPrior = 0
                elif str(type(li._LSym__sNum)) == "<class 'analyticlab.num.Num'>" and li._LSym__sNum._Num__sciDigit() != 0:  #科学记数法prior为2
                    li._LSym__calPrior = 2
                else:
                    li._LSym__calPrior = 6
            else:
                li._LSym__calPrior = 6
        ##############################################
        if LSymItem.sepSymCalc:  #代数表达式与数值表达式分离时，更新sepSym的symText和lsyms的calText
            self.__sepSym._LSym__symText = '{' + sym + '}'
            if type(self.__lsyms) == list:
                for li in self.__lsyms:
                    lsymSetCal(li)
            else:
                for ki in self.__lsyms.keys():
                    lsymSetCal(self.__lsyms[ki])
        else:  #代数表达式与数值表达式不分离时，更新lsyms的symText和calText
            if type(self.__lsyms) == list:
                for i in range(len(self.__lsyms)):
                    self.__lsyms[i]._LSym__symText = '{%s}_{%d}' % (sym, i+1)
                    lsymSetCal(self.__lsyms[i])
            else:
                for ki in self.__lsyms.keys():
                    self.__lsyms[ki]._LSym__symText = '{%s}_{%s}' % (sym, ki)
                    lsymSetCal(self.__lsyms[ki])
    
    def __newInstance(self):
        return LSymItem(None, None)
    
    def __sepSymCalc(self):
        return LSymItem.sepSymCalc
        
    def __getitem__(self, index):
        if type(index) == int or type(index) == str:
            return self.__lsyms[index]
        elif type(index) == slice:
            new = LSymItem(None, None)
            new.__lsyms = self.__lsyms[index]
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym
            return new
    
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
        if type(self.__lsyms) == list:
            new.__lsyms = [ni.__abs__() for ni in self.__lsyms]
        else:
            new.__lsyms = {ki: self.__lsyms[ki].__abs__() for ki in self.__lsyms.keys()}
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__abs__()
        return new
        
    def __neg__(self):
        new = LSymItem(None, None)
        if type(self.__lsyms) == list:
            new.__lsyms = [ni.__neg__() for ni in self.__lsyms]
        else:
            new.__lsyms = {ki: self.__lsyms[ki].__neg__() for ki in self.__lsyms.keys()}
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__neg__()
        return new
        
    def __add__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__add__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {ki: self.__lsyms[ki].__neg__() for ki in self.__lsyms.keys()}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__add__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__add__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__add__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__add__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__add__(obj)
        return new
    
    def __radd__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__radd__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__radd__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__radd__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__radd__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__radd__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__radd__(obj)
        return new
    
    def __sub__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__sub__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__sub__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__sub__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__sub__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__sub__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__sub__(obj)
        return new
    
    def __rsub__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__rsub__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__rsub__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rsub__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__rsub__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__rsub__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rsub__(obj)
        return new
    
    def __mul__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__mul__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__mul__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__mul__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__mul__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__mul__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__mul__(obj)
        return new
    
    def __rmul__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__rmul__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__rmul__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rmul__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__rmul__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__rmul__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rmul__(obj)
        return new
    
    def __truediv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__truediv__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__truediv__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__truediv__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__truediv__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__truediv__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__truediv__(obj)
        return new
    
    def __rtruediv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__rtruediv__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__rtruediv__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rtruediv__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__rtruediv__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__rtruediv__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rtruediv__(obj)
        return new
    
    def __floordiv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__floordiv__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__floordiv__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__floordiv__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__floordiv__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__floordiv__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__floordiv__(obj)
        return new
    
    def __rfloordiv__(self, obj):
        new = LSymItem(None, None)
        if type(obj) == LSymItem:
            if len(self) != len(obj):
                raise itemNotSameLengthException('进行符号组运算的两个符号组元素个数必须一致')
            if type(self.__lsyms) != type(obj.__lsyms):
                raise itemNotSameTypeException('进行符号组运算的两个符号组必须是同种类型')
            if type(self.__lsyms) == list:
                new.__lsyms = []
                for i in range(len(self)):
                    new.__lsyms.append(self.__lsyms[i].__rfloordiv__(obj.__lsyms[i]))
            else:
                try:
                    new.__lsyms = {}
                    for ki in self.__lsyms.keys():
                        new.__lsyms[ki] = self.__lsyms[ki].__rfloordiv__(obj.__lsyms[ki])
                except:
                    raise itemNotSameKeysException('进行符号组运算的两个符号组下标必须一致')
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rfloordiv__(obj.__sepSym)
        else:
            if type(self.__lsyms) == list:
                new.__lsyms = [ni.__rfloordiv__(obj) for ni in self.__lsyms]
            else:
                new.__lsyms = {ki: self.__lsyms[ki].__rfloordiv__(obj) for ki in self.__lsyms.keys()}
            if LSymItem.sepSymCalc:
                new.__sepSym = self.__sepSym.__rfloordiv__(obj)
        return new
    
    def __pow__(self, obj):
        new = LSymItem(None, None)
        if type(self.__lsyms) == list:
            new.__lsyms = [ni.__pow__(obj) for ni in self.__lsyms]
        else:
            new.__lsyms = {ki: self.__lsyms[ki].__pow__(obj) for ki in self.__lsyms.keys()}
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__pow__(obj)
        return new
    
    def __rpow__(self, obj):
        new = LSymItem(None, None)
        if type(self.__lsyms) == list:
            new.__lsyms = [ni.__rpow__(obj) for ni in self.__lsyms]
        else:
            new.__lsyms = {ki: self.__lsyms[ki].__rpow__(obj) for ki in self.__lsyms.keys()}
        if LSymItem.sepSymCalc:
            new.__sepSym = self.__sepSym.__rpow__(obj)
        return new
