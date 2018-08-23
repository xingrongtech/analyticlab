# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 18:59:21 2018

@author: xingrongtech
"""

class confLevelUnsupportedException(BaseException):
    def __init__(self, confLevel, tableType):
        print('不支持置信度为%s的%s' % (confLevel, tableType))
        
class alphaUnsupportedException(BaseException):
    def __init__(self, alpha, tableType):
        print('不支持显著性水平为%s的%s' % (alpha, tableType))

class tooMuchDataForTestException(BaseException):
    def __init__(self, msg):
        print(msg) 

class tooLessDataForTestException(BaseException):
    def __init__(self, tableType):
        print('可供%s的数据个数太少，无法进行%s' % (tableType, tableType))
        
class expressionInvalidException(BaseException):
    def __init__(self, msg):
        print(msg) 
        
class muNotFoundException(BaseException):
    def __init__(self, msg):
        print(msg)
        
class itemNotSameLengthException(BaseException):
    def __init__(self, msg):
        print(msg)
        
class itemNotSameTypeException(BaseException):
    def __init__(self, msg):
        print(msg)
        
class itemNotSameKeysException(BaseException):
    def __init__(self, msg):
        print(msg)
        
class keyNotInTableException(BaseException):
    def __init__(self, msg):
        print(msg)
        
class processStateWrongException(BaseException):
    def __init__(self):
        print('Uncertainty.process没有初始化为True，不能展示不确定度')
        
class subUnsupportedException(BaseException):
    def __init__(self, char):
        print('不支持字符\'%s\'的上标' % char)
        
class supUnsupportedException(BaseException):
    def __init__(self, char):
        print('不支持字符\'%s\'的下标' % char)