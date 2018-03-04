# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 15:07:26 2018

@author: xingrongtech
"""

def mul(A, B):
    if A == B:
        return '{%s}^2' % bracTreat(A)
    else:
        return r'%s \cdot %s' % (bracTreat(A), bracTreat(B))
    
def bracTreat(unit):
    if r'\cdot' in unit or '/' in unit:
        if '{' in unit or '[' in unit:
            unit = r'\{' + unit + r'\}'
        elif '(' in unit:
            unit = '[' + unit + ']'
        else:
            unit = '(' + unit + ')'
    return unit