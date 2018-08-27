# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 18:22:57 2018

@author: xingrongtech
"""
from ..num import Num
from ..latexoutput import LaTeX

kValue = (1, 3**0.5, 6**0.5, 2**0.5, 1)
kExpr = ('1', r'\sqrt{3}', r'\sqrt{6}', r'\sqrt{2}', '1')
    
def b(instrument, sym=None, process=False, needValue=False, remainOneMoreDigit=True):
    '''计算B类不确定度
    【参数说明】
    1.instrument（Ins）：测量仪器。可以在analyticlab.uncertainty.ins模块中选择已经预设好的测量仪器，或者通过Ins类创建新的测量仪器。
    2.sym（可选，str）：符号。默认sym=None。
    3.process（可选，bool）：是否展示计算过程。默认proces=False。
    4.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    5.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=True。
    【返回值】
    ①process为False时，返回值为Num类型的B类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的B类不确定度和LaTeX类型的计算过程组成的元组。'''
    a = instrument.a
    a.setSciBound(9)
    if instrument.distribution <= 4:
        uB = a / kValue[instrument.distribution]
    else:
        uB = a / (6/(1+instrument.beta**2))**0.5
    if remainOneMoreDigit:
        uB.remainOneMoreDigit()
    if process:
        if instrument.distribution <= 4:
            latex = LaTeX(r'u_{%s B}=\cfrac{a}{k}=\cfrac{%s}{%s}=%s' % (sym, a.dlatex(), kExpr[instrument.distribution], uB.latex()))
        else:
            latex = LaTeX(r'u_{%s B}=\cfrac{a}{k}=\cfrac{%s}{\sqrt{6/(1+%g^{2})}}=%s' % (sym, a.dlatex(), instrument.beta, uB.latex()))
        if needValue:
            return uB, latex
        else:
            return latex
    return uB