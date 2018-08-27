# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:15:25 2018

@author: xingrongtech
"""

from . import std
from ..amath import sqrt
from ..latexoutput import LaTeX
from ..numitem import NumItem
from ..lookup.Physics_tTable import phy_t
from ..lookup.RangeTable import v as rv
from ..lookup.RangeTable import C as rC
from ..system.unit_open import openUnit, closeUnit

def Bessel(item, process=False, needValue=False, remainOneMoreDigit=False):
    '''贝塞尔公式法计算A类不确定度
    【参数说明】
    1.item（NumItem）：用于A类不确定度计算的样本数据。
    2.process（可选，bool）：是否获得计算过程。默认proces=False。
    3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    4.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    result = std.Bessel(item, remainOneMoreDigit) / len(item)**0.5
    if process:
        signal = item._NumItem__sym
        sciDigit = item._NumItem__sciDigit()
        if sciDigit == 0:
            p_mean = item.mean()
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in item._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=\sqrt{\cfrac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\cfrac{1}{%d\times %d}\left[%s\right]}=%s' % (signal, signal, signal, len(item), len(item)-1, sumExpr, result.latex())) 
        else:
            d_arr = item * 10**(-sciDigit)
            p_mean = item.mean() * 10**(-sciDigit)
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in d_arr._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=\sqrt{\cfrac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\cfrac{1}{%d \times %d}\left[%s\right]}\times 10^{%d}=%s' % (signal, signal, signal, len(item), len(item)-1, sumExpr, sciDigit, result.latex()))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def Range(item, process=False, needValue=False, remainOneMoreDigit=False):
    '''极差法计算A类不确定度
    【参数说明】
    1.item（NumItem）：用于A类不确定度计算的样本数据。
    2.process（可选，bool）：是否获得计算过程。默认proces=False。
    3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    4.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    result = std.Range(item, remainOneMoreDigit) / len(item._NumItem__arr)**0.5
    if process:
        signal = item._NumItem__sym
        p_max, p_min = max(item._NumItem__arr), min(item._NumItem__arr)
        C = rC(len(item))
        latex = LaTeX(r'u_{%s A}=\cfrac{R}{C\sqrt{n}}=\cfrac{%s-%s}{%s\times\sqrt{%s}}=%s' % (signal, p_max.dlatex(), p_min.dlatex(2), C, len(item), result.latex()))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def CollegePhysics(item, process=False, needValue=False, remainOneMoreDigit=False):
    '''大学物理实验中的A类不确定度计算
    【参数说明】
    1.item（NumItem）：用于A类不确定度计算的样本数据。
    2.process（可选，bool）：是否获得计算过程。默认proces=False。
    3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    4.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    n = len(item._NumItem__arr)
    result = phy_t(n) * std.CollegePhysics(item, remainOneMoreDigit) / n**0.5
    if process:
        signal = item._NumItem__sym
        sciDigit = item._NumItem__sciDigit()
        if sciDigit == 0:
            p_mean = item.mean()
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in item._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=t_{n}\sqrt{\cfrac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=%.2f \times\sqrt{\cfrac{1}{%d\times %d}\left[%s\right]}=%s' % (signal, signal, signal, phy_t(len(item)), len(item), len(item)-1, sumExpr, result.latex())) 
        else:
            d_arr = item * 10**(-sciDigit)
            p_mean = item.mean() * 10**(-sciDigit)
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in d_arr._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=t_{n}\sqrt{\cfrac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=%.2f \times\sqrt{\cfrac{1}{%d \times %d}\left[%s\right]}\times 10^{%d}=%s' % (signal, signal, signal, phy_t(len(item)), len(item), len(item)-1, sumExpr, sciDigit, result.latex()))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def CombSamples(items, method='auto', process=False, needValue=False, sym=None, remainOneMoreDigit=False):
    '''合并样本的A类不确定度计算
    【参数说明】
    1.items（list<NumItem>）：用于A类不确定度计算的多个样本数据。
    2.method（可选，str）：使用何种方法计算每个样本的A类不确定度，从以下列表中取值：
    (1)'auto'：根据样本数量的大小，决定使用那种方法，即样本数量最大的组为9以上时，使用Bessel法；否则用极差法。
    (2)'Bessel'：使用贝塞尔公式法。
    (3)'Range'：使用极差法。
    (4)'CollegePhysics'：使用大学物理实验中的不确定度公式。
    3.process（可选，bool）：是否获得计算过程。默认proces=False。
    4.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    5.sym（可选，str）：合并样本的符号。默认sym=None。
    6.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的合并样本的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的合并样本的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    m = len(items)
    #计算各组样本的标准偏差
    if method == 'auto':
        if max([len(item) for item in items]) > 9:  #样本数量最大的组为9以上时，使用Bessel法
            s = [std.Bessel(item, remainOneMoreDigit=True) for item in items]
            method = 'Bessel'
        else:  #样本数量均不超过9时，使用极差法
            s = [std.Range(item, remainOneMoreDigit=True) for item in items]
            method = 'Range'
    elif method == 'Bessel':
        s = [std.Bessel(item, remainOneMoreDigit=True) for item in items]
    elif method == 'Range':
        s = [std.Range(item, remainOneMoreDigit=True) for item in items]
    elif method == 'CollegePhysics':
        s = [std.CollegePhysics(item, remainOneMoreDigit=True) for item in items]
    if process:
        resArr = []
        latex = LaTeX()
        if method == 'Range':
            for item in items:
                res = std.Range(item, remainOneMoreDigit=True)
                resArr.append(res)
                signal = item._NumItem__sym
                p_max, p_min = max(item._NumItem__arr), min(item._NumItem__arr)
                C = rC(len(item))
                latex.add(r's_{%s}=\cfrac{R}{C}=\cfrac{%s-%s}{%s}=%s' % (signal, p_max.dlatex(), p_min.dlatex(2), C, res.latex()))
        else:
            for item in items:
                res = std.Bessel(item, remainOneMoreDigit=True)
                resArr.append(res)
                signal = item._NumItem__sym
                sciDigit = item._NumItem__sciDigit()
                if sciDigit == 0:
                    p_mean = item.mean()
                    sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in item._NumItem__arr])
                    latex.add(r's_{%s}=\sqrt{\cfrac{1}{n-1}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\cfrac{1}{%d}\left[%s\right]}=%s' % (signal, signal, signal, len(item)-1, sumExpr, res.latex())) 
                else:
                    d_arr = item * 10**(-sciDigit)
                    p_mean = item.mean() * 10**(-sciDigit)
                    sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in d_arr._NumItem__arr])
                    latex.add(r's_{%s}=\sqrt{\cfrac{1}{n-1}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\cfrac{1}{%d}\left[%s\right]}\times 10^{%d}=%s' % (signal, signal, signal, len(item)-1, sumExpr, sciDigit, res.latex()))
    #根据所有样本的样本数量是否一致，判断使用哪个公式
    nSame = True
    n = len(items[0])
    for item in items:
        if len(item._NumItem__arr) != n:
            nSame = False
            break
    closeUnit()
    if nSame:
        nTotal = m*n
        sp = sqrt(sum([si**2 for si in s]) / m)
        if method == 'CollegePhysics':
            vSum = m*(n-1)
    else:
        nTotal = sum([len(item._NumItem__arr) for item in items])
        dSum = 0
        vSum = 0
        if method == 'Range':
            for i in range(m):
                v = rv(len(items[i]))
                dSum += v * s[i]**2
                vSum += v
            sp = sqrt(dSum / vSum)
        else:
            for i in range(m):
                v = len(items[i]) - 1
                dSum += v * s[i]**2
                vSum += v
            sp = sqrt(dSum / vSum)
    openUnit()
    sp._Num__q = items[0]._NumItem__q
    if method == 'CollegePhysics':
        result = phy_t(vSum+1) * sp / nTotal**0.5
    else:
        result = sp / nTotal**0.5
    if not remainOneMoreDigit:
        result.cutOneDigit()
    if process:
        resItem = NumItem(resArr)
        sciDigit = resItem._NumItem__sciDigit()
        if sciDigit != 0:
            resItem = resItem * 10**(-sciDigit)
        if nSame:
            sumExpr = '+'.join([('%s^{2}' % res.dlatex(1)) for res in resItem._NumItem__arr])
            if sciDigit == 0:
                latex.add(r's_{p}=\sqrt{\cfrac{\sum\limits_{i=1}^m {s_{%s i}}^{2}}{m}}=\sqrt{\cfrac{%s}{%d}}=%s' % (sym, sumExpr, m, sp.latex()))
            else:
                latex.add(r's_{p}=\sqrt{\cfrac{\sum\limits_{i=1}^m {s_{%s i}}^{2}}{m}}=\sqrt{\cfrac{%s}{%d}}\times 10^{%d}=%s' % (sym, sumExpr, m, sciDigit, sp.latex()))
            if method == 'CollegePhysics':
                latex.add(r'u_{%s A}=\cfrac{t_{v+1}s_p}{\sqrt{mn}}=\cfrac{%.2f \times %s}{\sqrt{%s}}=%s' % (sym, phy_t(vSum+1), sp.dlatex(2), nTotal, result.latex()))
            else:
                latex.add(r'u_{%s A}=\cfrac{s_p}{\sqrt{mn}}=\cfrac{%s}{\sqrt{%s}}=%s' % (sym, sp.dlatex(), nTotal, result.latex()))
        else:
            sumExpr = ''
            if method == 'Range':
                for i in range(len(items)):
                    sumExpr += r'%s \times %s^{2}+' % (rv(len(items[i]._NumItem__arr)), resItem._NumItem__arr[i].dlatex(1))
                vSumExpr = '+'.join(['%s' % rv(len(item._NumItem__arr)) for item in items])
            else:
                for i in range(len(items)):
                    sumExpr += r'%s \times %s^{2}+' % (len(items[i]._NumItem__arr) - 1, resItem._NumItem__arr[i].dlatex(1))
                vSumExpr = '+'.join(['%s' % (len(item._NumItem__arr) - 1) for item in items]) 
            sumExpr = sumExpr[:-1]
            if sciDigit == 0:
                latex.add(r's_{p}=\sqrt{\cfrac{\sum\limits_{i=1}^m \left(v_{i}s_{%s i}^{2}\right)}{\sum\limits_{i=1}^m v_{i}}}=\sqrt{\cfrac{%s}{%s}}=%s' % (sym, sumExpr, vSumExpr, sp.latex()))
            else:
                latex.add(r's_{p}=\sqrt{\cfrac{\sum\limits_{i=1}^m \left(v_{i}s_{%s i}^{2}\right)}{\sum\limits_{i=1}^m v_{i}}}=\sqrt{\cfrac{%s}{%s}}\times 10^{%d}=%s' % (sym, sumExpr, vSumExpr, sciDigit, sp.latex()))
            if method == 'CollegePhysics':
                latex.add(r'u_{%s A}=\cfrac{t_{v+1}s_p}{\sqrt{\sum\limits_{i=1}^m n_{i}}}=\cfrac{%s \times %s}{\sqrt{%s}}=%s' % (sym, phy_t(vSum+1), sp.dlatex(2), nTotal, result.latex()))
            else:
                latex.add(r'u_{%s A}=\cfrac{s_p}{\sqrt{\sum\limits_{i=1}^m n_{i}}}=\cfrac{%s}{\sqrt{%s}}=%s' % (sym, sp.dlatex(), nTotal, result.latex()))
        if needValue:
            return result, latex
        else:
            return latex
    return result