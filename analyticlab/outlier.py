# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 14:13:19 2018

@author: xingrongtech
"""

from math import sqrt
from .numitem import NumItem
from .lsymitem import LSymItem
from .latexoutput import LaTeX
from .lookup import G, D, b, R, rep

def Nair(item, sigma, detLevel=0.05, delLevel=0.01, side='double', process=False, needValue=False):
    '''Nair检验
    【参数说明】
    1.item（NumItem）：要检验的数组。
    2.sigma（float）：标准差。
    3.detLevel（可选，float）：检出水平，只能选择0.01、0.05、0.10中的一个。默认detLevel=0.05。
    4.delLevel（可选，float）：剔除水平，只能选择0.01、0.05、0.10中的一个。默认delLevel=0.01。
    5.side（可选，str）：哪侧检验，'double'表示双侧，'down'表示下限，'up'表示上限。默认side='double'。
    6.process（可选，bool）：是否获得计算过程。默认process=False。
    7.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    【返回值】
    tuple：由离群值（dictionary<str,list>）和正常值（list）组成的元组。
    A.dictionary<str,list>：离群值，包括statOutliers（统计离群值）和stragglers（歧离值）。
    B.list：正常值。
    ①process为False时，返回值为tuple。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为tuple和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> sample = NumItem("3.13 3.49 4.01 4.48 4.61 4.76 4.98 5.25 5.32 5.39 5.42 5.57 5.59 5.59 5.63 5.63 5.65 5.66 5.67 5.69 5.71 6.00 6.03 6.12 6.76")
    >>> outlier.Nair(sample, 0.65, side='down')
    ({'statOutliers': [3.13], 'stragglers': [3.49]}, 
     [4.01, 4.48, 4.61, 4.76, 4.98, 5.25, 5.32, 5.39, 5.42, 5.57, 5.59, 5.59, 5.63, 5.63, 5.65, 5.66, 5.67, 5.69, 5.71, 6.00, 6.03, 6.12, 6.76])
    '''
    if type(item) == LSymItem:
        item = NumItem(item)
    keep = sorted(item._NumItem__arr)
    ikeep = NumItem(keep, sym=item._NumItem__sym)
    detected = {'stragglers':[], 'statOutliers':[]}
    if process:
        sigmaExpr = '%g' % sigma
        sid = sigmaExpr.find('e')
        if sid > 0:
            sigmaExpr = sigmaExpr[:sid] + r'\times 10^{' + str(int(sigmaExpr[sid+1:])) + '}'
        symX = item._NumItem__sym
        latex = LaTeX(r'\text{将测量数据由小到大排序：}%s' % ikeep.latex())
        first = True
    if side == 'double':
        rep_detLevel = rep(detLevel, side=2)
        rep_delLevel = rep(delLevel, side=2)
        while True:
            n = len(keep)
            mean = ikeep.mean(dec=True)
            Rv = R(rep_detLevel, n)  #查表获得检出水平下的R值（双侧）
            R_max = (keep[-1]._Num__value - mean) / sigma  
            R_min = (mean - keep[0]._Num__value) / sigma
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），求其样本均值}' % (n, n))
                    first = False                    
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），求其样本均值}' % (n, n))
                p_mean, lsub = ikeep.mean(process=True, needValue=True)
                latex.add(lsub)
                latex.add('\text{使用}')
                latex.add(r'R_{%d}=\cfrac{%s_{(%d)}-\overline{%s}}{\sigma}=\cfrac{%s-%s}{%s}=%.3f' % (n, symX, n, symX, keep[-1].dlatex(), p_mean.dlatex(2), sigmaExpr, R_max))
                latex.add(r"R'_{%d}=\cfrac{\overline{%s}-%s_{(1)}}{\sigma}=\cfrac{%s-%s}{%g}=%.3f" % (n, symX, symX, p_mean.dlatex(), keep[0].dlatex(2), sigmaExpr, R_min))
                latex.add(r'\text{确定检出水平}\alpha=%g\text{，查表得临界值}R_{1-\alpha/2}(n)=R_{%g}(%d)=%.3f' % (detLevel, rep_detLevel, n, Rv))
            if R_max > R_min:
                if R_max > Rv:
                    Rv2 = R(rep_delLevel, n)  #查表获得剔除水平下的R值（双侧）
                    if process:
                        latex.add(r"\text{因}R_{%d}> R_{%d}'\text{且}R_{%d}>R_{%g}(%d)\text{，故判定}%s_{(%d)}\text{为离群值}" % (n, n, n, rep_detLevel, n, symX, n))
                        latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}R_{1-\alpha^{*}/2}(n)=R_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Rv2))
                        if R_max > Rv2:
                            latex.add(r'\text{因}D_{%d}>R_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}' % (n, rep_delLevel, n, symX, n, keep[-1].latex()))
                        else:
                            latex.add(r'\text{因}D_{%d}<R_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}' % (n, rep_delLevel, n, symX, n, keep[-1].latex(), symX, n))
                    if R_max > Rv2:
                        detected['statOutliers'].append(keep[-1])
                    else:
                        detected['stragglers'].append(keep[-1])
                    keep.remove(keep[-1])
                else:
                    if process:
                        latex.add(r"\text{因}R_{%d}>R_{%d}'\text{，}R_{%d}<R_{%g}(%d)\text{，故不能再检出离群值}" % (n, n, n, rep_detLevel, n))
                    break
            else:
                if R_min > Rv:
                    Rv2 = R(rep_delLevel, n)  #查表获得剔除水平下的R值（双侧）
                    if process:
                        latex.add(r"\text{因}R_{%d}'> R_{%d}\text{且}R_{%d}'>R_{%g}(%d)\text{，故判定}%s_{(1)}\text{为离群值}" % (n, n, n, rep_detLevel, n, symX))
                        latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}R_{1-\alpha^{*}/2}(n)=R_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Rv2))
                        if R_min > Rv2:
                            latex.add(r"\text{因}R_{%d}'>R_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (n, rep_delLevel, n, symX, keep[0].latex()))
                        else:
                            latex.add(r"\text{因}R_{%d}'<R_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (n, rep_delLevel, n, symX, keep[0].latex(), symX))
                    if R_min > Rv2:
                        detected['statOutliers'].append(keep[0])
                    else:
                        detected['stragglers'].append(keep[0])
                    keep.remove(keep[0])
                else:
                    if process:
                        latex.add(r"\text{因}R'_{%d}>R_{%d}\text{，}R_{%d}'<R_{%g}(%d)\text{，故不能再检出离群值}" % (n, n, n, rep_detLevel, n))
                    break
            if len(keep) < 3:
                if process:
                    latex.add(r'\text{剩余观测值数量小于3个，不能继续进行Nair检验，检验结束}')
                break;
    elif side == 'up':
        rep_detLevel = rep(detLevel, side=1)
        rep_delLevel = rep(delLevel, side=1)
        while True:
            n = len(keep)
            mean = ikeep.mean(dec=True)
            Rv = R(rep_detLevel, n)  #查表获得检出水平下的R值（单侧）
            R_max = (keep[-1]._Num__value - mean) / sigma
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），求其样本均值}' % (n, n))
                    first = False                    
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），求其样本均值}' % (n, n))
                p_mean, lsub = ikeep.mean(process=True, needValue=True)
                latex.add(lsub)
                latex.add(r'\text{使用}')
                latex.add(r'R_{%d}=\cfrac{%s_{(%d)}-\overline{%s}}{\sigma}=\cfrac{%s-%s}{%s}=%.3f' % (n, symX, n, symX, keep[-1].dlatex(), p_mean.dlatex(2), sigmaExpr, R_max))
                latex.add(r'\text{确定检出水平}\alpha=%g\text{，查表得临界值}R_{1-\alpha}(n)=R_{%g}(%d)=%.3f' % (detLevel, rep_detLevel, n, Rv))
            if R_max > Rv:
                Rv2 = R(rep_delLevel, n)  #查表获得剔除水平下的R值（单侧）
                if process:
                    latex.add(r"\text{因}R_{%d}>R_{%g}(%d)\text{，故判定}%s_{(%d)}\text{为离群值}" % (n, rep_detLevel, n, symX, n))
                    latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}R_{1-\alpha^{*}}(n)=R_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Rv2))
                    if R_max > Rv2:
                        latex.add(r'\text{因}D_{%d}>R_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}' % (n, rep_delLevel, n, symX, n, keep[-1].latex()))
                    else:
                        latex.add(r'\text{因}D_{%d}<R_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}' % (n, rep_delLevel, n, symX, n, keep[-1].latex(), symX, n))
                if R_max > Rv2:
                    detected['statOutliers'].append(keep[-1])
                else:
                    detected['stragglers'].append(keep[-1])
                keep.remove(keep[-1])
            else:
                if process:
                    latex.add(r"\text{因}R_{%d}<R_{%s}(%d)\text{，故不能再检出离群值}" % (n, rep_detLevel, n))
                break
            if len(keep) < 3:
                if process:
                    latex.add(r'\text{剩余观测值数量小于3个，不能继续进行Nair检验，检验结束}')
                break;
    elif side == 'down':
        rep_detLevel = rep(detLevel, side=1)
        rep_delLevel = rep(delLevel, side=1)        
        while True:
            n = len(keep)
            mean = ikeep.mean(dec=True)
            Rv = R(rep_detLevel, n)  #查表获得检出水平下的R值（单侧）
            R_min = (mean - keep[0]._Num__value) / sigma
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），求其样本均值}' % (n, n))
                    first = False                    
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），求其样本均值}' % (n, n))
                p_mean, lsub = ikeep.mean(process=True, needValue=True)
                latex.add(lsub)
                latex.add(r'\text{使用}')
                latex.add(r"R'_{%d}=\cfrac{\overline{%s}-%s_{(1)}}{\sigma}=\cfrac{%s-%s}{%s}=%.3f" % (n, symX, symX, p_mean.dlatex(), keep[0].dlatex(2), sigmaExpr, R_min))
                latex.add(r'\text{确定检出水平}\alpha=%g\text{，查表得临界值}R_{1-\alpha}(n)=R_{%g}(%d)=%.3f' % (detLevel, rep_detLevel, n, Rv))
            if R_min > Rv:
                Rv2 = R(rep_delLevel, n)  #查表获得剔除水平下的R值（单侧）
                if process:
                    latex.add(r"\text{因}R_{%d}'>R_{%g}(%d)\text{，故判定}%s_{(1)}\text{为离群值}" % (n, rep_detLevel, n, symX))
                    latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}R_{1-\alpha^{*}}(n)=R_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Rv2))
                    if R_min > Rv2:
                        latex.add(r"\text{因}R_{%d}'>R_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (n, rep_delLevel, n, symX, keep[0].latex()))
                    else:
                        latex.add(r"\text{因}R_{%d}'<R_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (n, rep_delLevel, n, symX, keep[0].latex(), symX))
                if R_min > Rv2:
                    detected['statOutliers'].append(keep[0])
                else:
                    detected['stragglers'].append(keep[0])
                keep.remove(keep[0])
            else:
                if process:
                    latex.add(r"\text{因}R_{%d}'<R_{%g}(%d)\text{，故不能再检出离群值}" % (n, rep_detLevel, n))
                break
            if len(keep) < 3:
                if process:
                    latex.add(r'\text{剩余观测值数量小于3个，不能继续进行Nair检验，检验结束}')
                break;
    remained = item._NumItem__arr[:]
    for r in detected['statOutliers']:
        remained.remove(r)
    for r in detected['stragglers']:
        remained.remove(r)   
    detected['statOutliers'] = NumItem(sorted(detected['statOutliers']), sym=item._NumItem__sym)
    detected['stragglers'] = NumItem(sorted(detected['stragglers']), sym=item._NumItem__sym)
    if process:
        detectedCount = len(item) - len(remained)
        if detectedCount == 0:
            latex.add(r'\text{综上，未检验到离群值}')
        elif detectedCount == 1:
            if len(detected['statOutliers']) == 1:
                latex.add(r'\text{综上，检验出了1个统计离群值}' + detected['statOutliers'][0].latex())
            else:
                latex.add(r'\text{综上，检验出了1个歧离值}' + detected['stragglers'][0].latex())
        else:
            sExpr = r'\text{综上，共检验到%d个离群值，其中}' % detectedCount
            if len(detected['statOutliers']) > 0:
                sExpr += r'\text{统计离群值为}' + detected['statOutliers'].latex()
            if len(detected['stragglers']) > 0:
                sExpr += len(detected['statOutliers']) * '，' + r'\text{歧离值为}' + detected['stragglers'].latex()
            latex.add(sExpr)
        if needValue:
            return (detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)), latex
        else:
            return latex
    return detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)
    
def Grubbs(item, detLevel=0.05, delLevel=0.01, side='double', process=False, needValue=False):
    '''
    Grubbs检验
    【参数说明】
    1.item（NumItem）：要检验的数组。
    2.detLevel（可选，float）：检出水平，只能选择0.01、0.05、0.10中的一个。默认detLevel=0.05。
    3.delLevel（可选，float）：剔除水平，只能选择0.01、0.05、0.10中的一个。默认delLevel=0.01。
    4.side（可选，str）：哪侧检验，'double'表示双侧，'down'表示下限，'up'表示上限。默认side='double'。
    5.process（可选，bool）：是否获得计算过程。默认process=False。
    6.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    【返回值】
    tuple：由离群值（dictionary<str,list>）和正常值（list）组成的元组。
    A.dictionary<str,list>：离群值，包括statOutliers（统计离群值）和stragglers（歧离值）。
    B.list：正常值。
    ①process为False时，返回值为tuple。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为tuple和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> sample = NumItem('13.52 13.56 13.55 13.54 13.12 13.54')
    >>> outlier.Grubbs(sample)
    ({'statOutliers': [13.12], 'stragglers': []}, [13.52, 13.56, 13.55, 13.54, 13.54])
    '''
    if type(item) == LSymItem:
        item = NumItem(item)
    remained = item._NumItem__arr[:]
    detected = {'stragglers':[], 'statOutliers':[]}
    s = item.staDevi(dec=True)
    if s == 0:  #若发现方差为零，则离群数据为空，直接返回
        if process:
            print('测量数据方差为0，所有数据均为保留数据')
        return None, remained
    mean = item.mean(dec=True)
    if process:
        symX = item._NumItem__sym
        ikeep = NumItem(sorted(item._NumItem__arr), sym=item._NumItem__sym)  #将keep list转换成数值数组以进行均值、标准差计算
        n = len(item)
        latex = LaTeX(r'\text{将测量数据由小到大排序：}%s' % ikeep.latex())
        p_mean, lsub = ikeep.mean(process=True, needValue=True)
        p_s, lsub2 = ikeep.staDevi(process=True, processWithMean=False, needValue=True, remainOneMoreDigit=True)
        latex.add(lsub)
        latex.add(lsub2)
    if side == 'double':
        Gv = G(rep(detLevel, side=2), len(item))  #查表获得检出水平下的G值（双侧）
        nMax = max(item._NumItem__arr)
        nMin = min(item._NumItem__arr)
        G_max = (nMax._Num__value - mean) / s  
        G_min = (mean - nMin._Num__value) / s     
        if G_max > G_min:
            if G_max > Gv:
                remained.remove(nMax)
                Gv2 = G(rep(delLevel, side=2), len(item))  #查表获得剔除水平下的G值（双侧）
                if G_max > Gv2:
                    detected['statOutliers'].append(nMax)
                else:
                    detected['stragglers'].append(nMax)
        else:
            if G_min > Gv:
                remained.remove(nMin)
                Gv2 = G(rep(delLevel, side=2), len(item))  #查表获得剔除水平下的G值（双侧）
                if G_min > Gv2:
                    detected['statOutliers'].append(nMin)
                else:
                    detected['stragglers'].append(nMin)
        if process:
            latex.add(r'G_{%d}=\cfrac{%s_{(%d)}-\overline{%s}}{s}=\cfrac{%s-%s}{%s}=%.3f' % (n, symX, n, symX, nMax.dlatex(), p_mean.dlatex(2), p_s.dlatex(), G_max))
            latex.add(r"G_{%d}'=\cfrac{\overline{%s}-%s_{(1)}}{s}=\cfrac{%s-%s}{%s}=%.3f" % (n, symX, symX, p_mean.dlatex(), nMin.dlatex(2), p_s.dlatex(), G_min))
            P = rep(detLevel, side=2)
            latex.add(r'\text{确定检验水平}\alpha=%g\text{，查表得临界值}G_{1-\alpha/2}(n)=G_{%g}(%d)=%.3f' % (detLevel, P, n, Gv))
            if G_max > G_min:
                if G_max > Gv:
                    latex.add(r"\text{因}G_{%d}> G_{%d}'\text{且}G_{%d}>G_{%g}(%d)\text{，故判定}%s_{(%d)}\text{为离群值}" % (n, n, n, P, n, symX, n))
                    latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}G_{1-\alpha^{*}/2}(n)=G_{%g}(%d)=%.3f' % (symX, n, delLevel, P, n, Gv2))
                    if G_max > Gv2:
                        latex.add(r'\text{因}G_{%d}>G_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}' % (n, P, n, symX, n, nMax.latex()))
                    else:
                        latex.add(r'\text{因}G_{%d}<G_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}' % (n, P, n, symX, n, nMax.latex(), symX, n))
                else:
                    latex.add(r"\text{因}G_{%d}>G _{%d}'，G_{%d}< G_{%g}(%d)\text{，故不能再检出离群值}" % (n, n, n, P, n))
            else:
                if G_min > Gv:
                    latex.add(r"\text{因}G_{%d}'> G_{%d}\text{且}G_{%d}'>G_{%g}(%d)\text{，故判定}%s_{(1)}\text{为离群值}" % (n, n, n, P, n, symX))
                    latex.add(r'\text{对于检出的离群值}%s_{(1)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}G_{1-\alpha^{*}/2}(n)=G_{%g}(%d)=%.3f' % (symX, delLevel, P, n, Gv2))
                    if G_min > Gv2:
                        latex.add(r"\text{因}G_{%d}'>G_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (n, P, n, symX, nMin.latex()))
                    else:
                        latex.add(r"\text{因}G_{%d}'<G_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (n, P, n, symX, nMin.latex(), symX))
                else:
                    latex.add(r"\text{因}G_{%d}'> G_{%d}\text{，}G_{%d}'< G_{%g}(%d)\text{，故不能再检出离群值}" % (n, n, n, P, n))
            
    elif side == 'up':
        Gv = G(rep(detLevel, side=1), len(item))  #查表获得检出水平下的G值（单侧）
        nMax = max(item._NumItem__arr)
        G_max = (nMax._Num__value - mean) / s  
        if G_max > Gv:
            remained.remove(nMax)
            Gv2 = G(rep(delLevel, side=1), len(item))  #查表获得剔除水平下的G值（单侧）
            if G_max > Gv2:
                detected['statOutliers'].append(nMax)
            else:
                detected['stragglers'].append(nMax)
        if process:
            latex.add(r'G_{%d}=\cfrac{%s_{(%d)}-\overline{%s}}{s}=\cfrac{%s-%s}{%s}=%.3f' % (n, symX, n, symX, nMax.dlatex(), p_mean.dlatex(2), p_s.dlatex(), G_max))
            P = rep(detLevel, side=1)
            latex.add(r'\text{确定检验水平}\alpha=%g\text{，查表得临界值}G_{1-\alpha}(n)=G_{%g}(%d)=%.3f' % (detLevel, P, n, Gv))
            if G_max > Gv:
                latex.add(r"\text{因}G_{%d}>G_{%g}(%d)\text{，故判定}%s_{(%d)}\text{为离群值}" % (n, P, n, symX, n))
                latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}G_{1-\alpha^{*}}(n)=G_{%g}(%d)=%.3f' % (symX, n, delLevel, P, n, Gv2))
                if G_max > Gv2:
                    latex.add(r'\text{因}G_{%d}>G_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}' % (n, P, n, symX, n, nMax))
                else:
                    latex.add(r'\text{因}G_{%d}<G_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}' % (n, P, n, symX, n, nMax.latex(), symX, n))
            else:
                latex.add(r"\text{因}G_{%d}< G_{%g}(%d)\text{，故不能再检出离群值}" % (n, P, n))
    elif side == 'down':
        Gv = G(rep(detLevel, side=1), len(item))  #查表获得检出水平下的G值（单侧）
        nMin = min(item._NumItem__arr)
        G_min = (mean - nMin._Num__value) / s
        if G_min > Gv:
            remained.remove(nMin)
            Gv2 = G(rep(delLevel, side=1), len(item))  #查表获得剔除水平下的G值（单侧）
            if G_min > Gv2:
                detected['statOutliers'].append(nMin)
            else:
                detected['stragglers'].append(nMin)
        if process:
            latex.add(r"G_{%d}'=\cfrac{\overline{%s}-%s_{(1)}}{s}=\cfrac{%s-%s}{%s}=%.3f" % (n, symX, symX, p_mean.dlatex(), nMin.dlatex(2), p_s.dlatex(), G_min))
            P = rep(detLevel, side=1)
            latex.add(r'\text{确定检验水平}\alpha=%g\text{，查表得临界值}G_{1-\alpha}(n)=G_{%g}(%d)=%.3f' % (detLevel, P, n, Gv))
            if G_min > Gv:
                latex.add(r"\text{因}G_{%d}'>G_{%g}(%d)\text{，故判定}%s_{(1)}\text{为离群值}" % (n, P, n, symX))
                latex.add(r'\text{对于检出的离群值}%s_{(1)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}G_{1-\alpha^{*}}(n)=G_{%s}(%d)=%.3f' % (symX, delLevel, P, n, Gv2))
                if G_min > Gv2:
                    latex.add(r"\text{因}G_{%d}'>G_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (n, P, n, symX, nMin.latex()))
                else:
                    latex.add(r"\text{因}G_{%d}'<G_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (n, P, n, symX, nMin.latex(), symX))
            else:
                latex.add(r"\text{因}G_{%d}'< G_{%g}(%d)\text{，故不能再检出离群值}" % (n, P, n))
    detected['statOutliers'] = NumItem(sorted(detected['statOutliers']), sym=item._NumItem__sym)
    detected['stragglers'] = NumItem(sorted(detected['stragglers']), sym=item._NumItem__sym)
    if process:
        if needValue:
            return (detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)), latex
        else:
            return latex
    return detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)

def Dixon(item, detLevel=0.05, delLevel=0.01, side='double', process=False, needValue=False):
    '''Dixon检验
    【参数说明】
    1.item（NumItem）：要检验的数组。
    2.detLevel（可选，float）：检出水平，只能选择0.01、0.05中的一个。默认detLevel=0.05。
    3.delLevel（可选，float）：剔除水平，只能选择0.01、0.05中的一个。默认delLevel=0.01。
    4.side（可选，str）：哪侧检验，'double'表示双侧，'down'表示下限，'up'表示上限。默认side='double'。
    5.process（可选，bool）：是否获得计算过程。默认process=False。
    6.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    【返回值】
    tuple：由离群值（dictionary<str,list>）和正常值（list）组成的元组。
    A.dictionary<str,list>：离群值，包括statOutliers（统计离群值）和stragglers（歧离值）。
    B.list：正常值。
    ①process为False时，返回值为tuple。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为tuple和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> sample = NumItem('13.52 13.56 13.55 13.54 13.12 13.54 13.58 13.53 13.74 13.56 13.51')
    >>> outlier.Dixon(sample)
    ({'statOutliers': [13.12, 13.74], 'stragglers': []}, [13.52, 13.56, 13.55, 13.54, 13.54, 13.58, 13.53, 13.56, 13.51])'''
    if type(item) == LSymItem:
        item = NumItem(item)
    keep = sorted(item._NumItem__arr)
    ikeep = NumItem(keep, sym=item._NumItem__sym)
    detected = {'stragglers':[], 'statOutliers':[]}
    rep_detLevel = rep(detLevel, side=0)
    rep_delLevel = rep(delLevel, side=0)
    if process:
        symX = item._NumItem__sym
        latex = LaTeX(r'\text{将测量数据由小到大排序：}%s' % ikeep.latex())
        first = True
    if side == 'double':
        while True:
            n = len(keep)
            Dv = D(rep_detLevel, n, side=2)
            if n <= 7:
                D_max = (keep[-1]._Num__value - keep[-2]._Num__value) / (keep[-1]._Num__value - keep[0]._Num__value)
                D_min = (keep[1]._Num__value - keep[0]._Num__value) / (keep[-1]._Num__value - keep[0]._Num__value)
            elif n <= 10:
                D_max = (keep[-1]._Num__value - keep[-2]._Num__value) / (keep[-1]._Num__value - keep[1]._Num__value)
                D_min = (keep[1]._Num__value - keep[0]._Num__value) / (keep[-2]._Num__value - keep[0]._Num__value)
            elif n <= 13:
                D_max = (keep[-1]._Num__value - keep[-3]._Num__value) / (keep[-1]._Num__value - keep[1]._Num__value)
                D_min = (keep[2]._Num__value - keep[0]._Num__value) / (keep[-2]._Num__value - keep[0]._Num__value)
            elif n <= 100:
                D_max = (keep[-1]._Num__value - keep[-3]._Num__value) / (keep[-1]._Num__value - keep[2]._Num__value)
                D_min = (keep[2]._Num__value - keep[0]._Num__value) / (keep[-3]._Num__value - keep[0]._Num__value)
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），使用}' % (n, n))
                    first = False
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），使用}' % (n, n))
                if n <= 7:
                    latex.add(r'D_{%d}=r_{10}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-1, symX, n, symX, keep[-1].dlatex(), keep[-2].dlatex(2), keep[-1].dlatex(), keep[0].dlatex(2), D_max))
                    latex.add(r"D_{%d}'=r_{10}'=\cfrac{%s_{(2)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n, symX, keep[1].dlatex(), keep[0].dlatex(2), keep[-1].dlatex(), keep[0].dlatex(2), D_min))
                elif n <= 10:
                    latex.add(r'D_{%d}=r_{11}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(2)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-1, symX, n, symX, keep[-1].dlatex(), keep[-2].dlatex(2), keep[-1].dlatex(), keep[1].dlatex(2), D_max))
                    latex.add(r"D_{%d}'=r_{11}'=\cfrac{%s_{(2)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n-1, symX, keep[1].dlatex(), keep[0].dlatex(2), keep[-2].dlatex(), keep[0].dlatex(2), D_min))
                elif n <= 13:
                    latex.add(r'D_{%d}=r_{21}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(2)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-2, symX, n, symX, keep[-1].dlatex(), keep[-3].dlatex(2), keep[-1].dlatex(), keep[1].dlatex(2), D_max))
                    latex.add(r"D_{%d}'=r_{21}'=\cfrac{%s_{(3)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n-1, symX, keep[2].dlatex(), keep[0].dlatex(2), keep[-2].dlatex(), keep[0].dlatex(2), D_min))
                elif n <= 100:
                    latex.add(r'D_{%d}=r_{22}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(3)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-2, symX, n, symX, keep[-1].dlatex(), keep[-3].dlatex(2), keep[-1].dlatex(), keep[2].dlatex(2), D_max))
                    latex.add(r"D_{%d}'=r_{22}'=\cfrac{%s_{(3)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n-2, symX, keep[2].dlatex(), keep[0].dlatex(2), keep[-3].dlatex(), keep[0].dlatex(2), D_min))
                latex.add(r'\text{确定检出水平}\alpha=%g\text{，查表得临界值}\tilde{D}_{1-\alpha}(n)=\tilde{D}_{%g}(%d)=%.3f' % (detLevel, rep_detLevel, n, Dv))
            if D_max > D_min:
                if D_max > Dv:
                    Dv2 = D(rep_delLevel, n, side=2)  #查表获得剔除水平下的G值（双侧）
                    if process:
                        latex.add(r"\text{因}D_{%d}> D_{%d}'\text{且}D_{%d}>\tilde{D}_{%g}(%d)\text{，故判定}%s_{(%d)}\text{为离群值}" % (n, n, n, rep_detLevel, n, symX, n))
                        latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}\tilde{D}_{1-\alpha^{*}}(n)=\tilde{D}_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Dv2))
                        if D_max > Dv2:
                            latex.add(r'\text{因}D_{%d}>\tilde{D}_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}' % (n, rep_delLevel, n, symX, n, keep[-1].latex()))
                        else:
                            latex.add(r'\text{因}D_{%d}<\tilde{D}_{%g}(%d)\text{，故判为未发现}%d_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}' % (n, rep_delLevel, n, symX, n, keep[-1].latex(), symX, n))
                    if D_max > Dv2:
                        detected['statOutliers'].append(keep[-1])
                    else:
                        detected['stragglers'].append(keep[-1])
                    keep.remove(keep[-1])
                else:
                    if process:
                        latex.add(r"\text{因}D_{%d}>D_{%d}'\text{，}D_{%d}<\tilde{D}_{%g}(%d)\text{，故不能再检出离群值}" % (n, n, n, rep_detLevel, n))
                    break
            else:
                if D_min > Dv:
                    Dv2 = D(rep_delLevel, n, side=2)  #查表获得剔除水平下的G值（双侧）
                    if process:
                        latex.add(r"\text{因}D_{%d}'> D_{%d}\text{且}D_{%d}'>\tilde{D}_{%g}(%d)\text{，故判定}%s_{(1)}\text{为离群值}" % (n, n, n, rep_detLevel, n, symX))
                        latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}\tilde{D}_{1-\alpha^{*}}(n)=\tilde{D}_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Dv2))
                        if D_min > Dv2:
                            latex.add(r"\text{因}D_{%d}'>\tilde{D}_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (n, rep_delLevel, n, symX, keep[0].latex()))
                        else:
                            latex.add(r"\text{因}D_{%d}'<\tilde{D}_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (n, rep_delLevel, n, symX, keep[0].latex(), symX))
                    if D_min > Dv2:
                        detected['statOutliers'].append(keep[0])
                    else:
                        detected['stragglers'].append(keep[0])
                    keep.remove(keep[0])
                else:
                    if process:
                        latex.add(r"\text{因}D'_{%d}>D_{%d}，D_{%d}'<\tilde{D}_{%g}(%d)\text{，故不能再检出离群值}" % (n, n, n, rep_detLevel, n))
                    break
            if len(keep) < 3:
                if process:
                    latex.add(r'\text{剩余观测值数量小于3个，不能继续进行Dixon检验，检验结束}')
                break;
    elif side == 'up':
        while True:
            n = len(keep)
            Dv = D(rep_detLevel, n, side=1)
            if n <= 7:
                D_max = (keep[-1]._Num__value - keep[-2]._Num__value) / (keep[-1]._Num__value - keep[0]._Num__value)
            elif n <= 10:
                D_max = (keep[-1]._Num__value - keep[-2]._Num__value) / (keep[-1]._Num__value - keep[1]._Num__value)
            elif n <= 13:
                D_max = (keep[-1]._Num__value - keep[-3]._Num__value) / (keep[-1]._Num__value - keep[1]._Num__value)
            elif n <= 100:
                D_max = (keep[-1]._Num__value - keep[-3]._Num__value) / (keep[-1]._Num__value - keep[2]._Num__value)
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），使用}' % (n, n))
                    first = False
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个观测值（}n=%d\text{），使用}' % (n, n))
                if n <= 7:
                    latex.add(r'D_{%d}=r_{10}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-1, symX, n, symX, keep[-1].dlatex(), keep[-2].dlatex(2), keep[-1].dlatex(), keep[0].dlatex(2), D_max))
                elif n <= 10:
                    latex.add(r'D_{%d}=r_{11}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(2)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-1, symX, n, symX, keep[-1].dlatex(), keep[-2].dlatex(2), keep[-1].dlatex(), keep[1].dlatex(2), D_max))
                elif n <= 13:
                    latex.add(r'D_{%d}=r_{21}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(2)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-2, symX, n, symX, keep[-1].dlatex(), keep[-3].dlatex(2), keep[-1].dlatex(), keep[1].dlatex(2), D_max))
                elif n <= 100:
                    latex.add(r'D_{%d}=r_{22}=\cfrac{%s_{(%d)}-%s_{(%d)}}{%s_{(%d)}-%s_{(3)}}=\cfrac{%s-%s}{%s-%s}=%.3f' % (n, symX, n, symX, n-2, symX, n, symX, keep[-1].dlatex(), keep[-3].dlatex(2), keep[-1].dlatex(), keep[2].dlatex(2), D_max))
                latex.add(r'\text{确定检出水平}\alpha=%g\text{，查表得临界值}D_{1-\alpha}(n)=D_{%g}(%d)=%.3f' % (detLevel, rep_detLevel, n, Dv))
            if D_max > Dv:
                Dv2 = D(rep_delLevel, n, side=1)  #查表获得剔除水平下的G值（单侧）
                if process:
                    latex.add(r"D_{%d}>D_{%g}(%d)，故判定%s_{(%d)}为离群值" % (n, rep_detLevel, n, symX, n))
                    latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}D_{1-\alpha^{*}}(n)=D_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Dv2))
                    if D_max > Dv2:
                        latex.add(r'\text{因}D_{%d}>D_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}' % (n, rep_delLevel, n, symX, n, keep[-1].latex()))
                    else:
                        latex.add(r'\text{因}D_{%d}<D_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}' % (n, rep_delLevel, n, symX, n, keep[-1].latex(), symX, n))
                if D_max > Dv2:
                    detected['statOutliers'].append(keep[-1])
                else:
                    detected['stragglers'].append(keep[-1])
                keep.remove(keep[-1])
            else:
                if process:
                    latex.add(r"\text{因}D_{%d}<D_{%g}(%d)\text{，故不能再检出离群值}" % (n, rep_detLevel, n))
                break
            if len(keep) < 3:
                if process:
                    latex.add(r'\text{剩余观测值数量小于3个，不能继续进行Dixon检验，检验结束}')
                break;
    elif side == 'down':
        while True:
            n = len(keep)
            Dv = D(rep_detLevel, n, side=1)
            if n <= 7:
                D_min = (keep[1]._Num__value - keep[0]._Num__value) / (keep[-1]._Num__value - keep[0]._Num__value)
            elif n <= 10:
                D_min = (keep[1]._Num__value - keep[0]._Num__value) / (keep[-2]._Num__value - keep[0]._Num__value)
            elif n <= 13:
                D_min = (keep[2]._Num__value - keep[0]._Num__value) / (keep[-2]._Num__value - keep[0]._Num__value)
            elif n <= 100:
                D_min = (keep[2]._Num__value - keep[0]._Num__value) / (keep[-3]._Num__value - keep[0]._Num__value)
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），使用}' % (n, n))
                    first = False
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），使用}' % (n, n))
                if n <= 7:
                    latex.add(r"D_{%d}'=r_{10}'=\cfrac{%s_{(2)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n, symX, keep[1].dlatex(), keep[0].dlatex(2), keep[-1].dlatex(), keep[0].dlatex(2), D_min))
                elif n <= 10:
                    latex.add(r"D_{%d}'=r_{11}'=\cfrac{%s_{(2)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n-1, symX, keep[1].dlatex(), keep[0].dlatex(2), keep[-2].dlatex(), keep[0].dlatex(2), D_min))
                elif n <= 13:
                    latex.add(r"D_{%d}'=r_{21}'=\cfrac{%s_{(3)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n-1, symX, keep[2].dlatex(), keep[0].dlatex(2), keep[-2].dlatex(), keep[0].dlatex(2), D_min))
                elif n <= 100:
                    latex.add(r"D_{%d}'=r_{22}'=\cfrac{%s_{(3)}-%s_{(1)}}{%s_{(%d)}-%s_{(1)}}=\cfrac{%s-%s}{%s-%s}=%.3f" % (n, symX, symX, symX, n-2, symX, keep[2].dlatex(), keep[0].dlatex(2), keep[-3].dlatex(), keep[0].dlatex(2), D_min))
                latex.add(r'\text{确定检出水平}\alpha=%g\text{，查表得临界值}D_{1-\alpha}(n)=D_{%g}(%d)=%.3f' % (detLevel, rep_detLevel, n, Dv))
            if D_min > Dv:
                Dv2 = D(rep_delLevel, n, side=1)  #查表获得剔除水平下的G值（单侧）
                if process:
                    latex.add(r"\text{因}D_{%d}'>D_{%g}(%d)\text{，故判定}%s_{(1)}\text{为离群值}" % (n, rep_detLevel, n, symX))
                    latex.add(r'\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}D_{1-\alpha^{*}}(n)=D_{%g}(%d)=%.3f' % (symX, n, delLevel, rep_delLevel, n, Dv2))
                    if D_min > Dv2:
                        latex.add(r"\text{因}D_{%d}'>D_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (n, rep_delLevel, n, symX, keep[0].latex()))
                    else:
                        latex.add(r"\text{因}D_{%d}'<D_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (n, rep_delLevel, n, symX, keep[0].latex(), symX))
                if D_min > Dv2:
                    detected['statOutliers'].append(keep[0])
                else:
                    detected['stragglers'].append(keep[0])
                keep.remove(keep[0])
            else:
                if process:
                    latex.add(r"\text{因}D_{%d}'<D_{%g}(%d)\text{，故不能再检出离群值}" % (n, rep_detLevel, n))
                break
            if len(keep) < 3:
                if process:
                    latex.add(r'\text{剩余观测值数量小于3个，不能继续进行Dixon检验，检验结束}')
                break;
    remained = item._NumItem__arr[:]
    for r in detected['statOutliers']:
        remained.remove(r)
    for r in detected['stragglers']:
        remained.remove(r)   
    detected['statOutliers'] = NumItem(sorted(detected['statOutliers']), sym=item._NumItem__sym)
    detected['stragglers'] = NumItem(sorted(detected['stragglers']), sym=item._NumItem__sym)
    if process:
        detectedCount = len(item) - len(remained)
        if detectedCount == 0:
            latex.add(r'\text{综上，未检验到离群值}')
        elif detectedCount == 1:
            if len(detected['statOutliers']) == 1:
                latex.add(r'\text{综上，检验出了1个统计离群值}' + detected['statOutliers'][0].latex())
            else:
                latex.add(r'\text{综上，检验出了1个歧离值}' + detected['stragglers'][0].latex())
        else:
            sExpr = r'\text{综上，共检验到%d个离群值，其中}' % detectedCount
            if len(detected['statOutliers']) > 0:
                sExpr += r'\text{统计离群值为}' + detected['statOutliers'].latex()
            if len(detected['stragglers']) > 0:
                sExpr += len(detected['statOutliers']) * '，' + r'\text{歧离值为}' + detected['stragglers'].latex()
            latex.add(sExpr)
        if needValue:
            return (detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)), latex
        else:
            return latex
    return detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)

def SkewKuri(item, detLevel=0.05, delLevel=0.01, side='double', process=False, needValue=False):
    '''偏度-峰度检验
    【参数说明】
    1.item（NumItem）：要检验的数组
    2.detLevel（可选，float）：检出水平，只能选择0.01、0.05中的一个。默认detLevel=0.05。
    3.delLevel（可选，float）：剔除水平，只能选择0.01、0.05中的一个。默认delLevel=0.01。
    4.side（可选，str）：哪侧检验，'double'表示双侧，'down'表示下限，'up'表示上限。默认side='double'。
    5.process（可选，bool）：是否获得计算过程。默认process=False。
    6.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    【返回值】
    tuple：由离群值（dictionary<str,list>）和正常值（list）组成的元组。
    A.dictionary<str,list>：离群值，包括statOutliers（统计离群值）和stragglers（歧离值）。
    B.list：正常值。
    ①process为False时，返回值为tuple。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为tuple和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> sample = NumItem('13.52 13.56 13.55 13.54 13.12 13.54 13.58 13.53 13.64 13.56 13.51')
    >>> outlier.SkewKuri(sample)
    ({'statOutliers': [13.12], 'stragglers': [13.64]}, [13.52, 13.56, 13.55, 13.54, 13.54, 13.58, 13.53, 13.56, 13.51])'''
    if type(item) == LSymItem:
        item = NumItem(item)
    keep = sorted(item._NumItem__arr)
    ikeep = NumItem(keep, sym=item._NumItem__sym)
    detected = {'stragglers':[], 'statOutliers':[]}
    rep_detLevel = rep(detLevel, side=0)
    rep_delLevel = rep(delLevel, side=0)
    if process:
        symX = item._NumItem__sym
        latex = LaTeX(r'\text{将测量数据由小到大排序：}%s' % ikeep.latex())
        first = True
    if side == 'double':
        while True:
            n = len(keep)
            mean = ikeep.mean(dec=True)
            if abs(keep[0]._Num__value - mean) > abs(keep[-1]._Num__value - mean):
                farthest = keep[0]
                farthestId = 1
            else:
                farthest = keep[-1]
                farthestId = n
            bkv = b(rep_detLevel, n, side=2)
            bk = n * sum([(xi._Num__value - mean)**4 for xi in keep]) / sum([(xi._Num__value - mean)**2 for xi in keep])**2
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），求其样本均值}' % (n, n))
                    first = False                    
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），求其样本均值}' % (n, n))
                p_mean, lsub = ikeep.mean(process=True, needValue=True)
                latex.add(lsub)
                latex.add(r'\text{使用}')
                sciDigit = ikeep._NumItem__sciDigit()
                if sciDigit == 0:
                    sum4Expr = '+'.join([(r'%s^{4}' % (xi - p_mean).dlatex(1)) for xi in keep])
                    sum2Expr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in keep])
                else:
                    d_arr = ikeep * 10**(-sciDigit)
                    d_mean = ikeep.mean() * 10**(-sciDigit)
                    sum4Expr = '+'.join([(r'%s^{4}' % (xi - d_mean).dlatex(1)) for xi in d_arr])
                    sum2Expr = '+'.join([(r'%s^{2}' % (xi - d_mean).dlatex(1)) for xi in d_arr])
                latex.add(r'b_{k}=\cfrac{n\sum\limits_{i=1}^n \left(%s_{i}-\overline{%s}\right)^{4}}{\left[\sum\limits_{i=1}^n \left(%s_{i}-\overline{%s}\right)^{2}\right]^{2}}=\cfrac{%d\times\left[%s\right]}{\left[%s\right]^{2}}=%.2f' % (symX, symX, symX, symX, n, sum4Expr, sum2Expr, bk))
                latex.add(r"\text{确定检出水平}\alpha=%g\text{，查表得临界值}b'_{1-\alpha}(n)=b'_{%g}(%d)=%.2f" % (detLevel, rep_detLevel, n, bkv))
            if bk > bkv:
                bkv2 = b(rep_delLevel, n, side=2)  #查表获得剔除水平下的G值（双侧）
                if process:
                    latex.add(r"\text{因}b_{k}>b'_{%g}(%d)\text{，故判定距离均值}%s\text{最远的值}%s_{(%d)}=%s\text{为离群值}" % (rep_detLevel, n, p_mean, symX, farthestId, farthest.latex()))
                    latex.add(r"\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}b'_{1-\alpha^{*}}(n)=b'_{%g}(%d)=%.2f" % (symX, n, delLevel, rep_delLevel, n, bkv2))
                    if bk > bkv2:
                        latex.add(r"\text{因}b_{k}>b'_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}" % (rep_delLevel, n, symX, farthestId, farthest.latex()))
                    else:
                        latex.add(r"\text{因}b_{k}<b'_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}" % (rep_delLevel, n, symX, farthestId, farthest.latex(), symX, farthestId))
                if bk > bkv2:
                    detected['statOutliers'].append(farthest)
                else:
                    detected['stragglers'].append(farthest)
                keep.remove(farthest)
            else:
                if process:
                    latex.add(r"\text{因}b_{k}<b'_{%g}(%d)\text{，故不能再检出离群值}" % (rep_detLevel, n))
                break 
            if len(keep) < 8:
                if process:
                    latex.add(r'\text{剩余观测值数量小于8个，不能继续进行偏度—峰度检验，检验结束}')
                break;
    elif side == 'up' or side == 'down':
        while True:
            n = len(keep)
            mean = ikeep.mean(dec=True)
            bsv = b(rep_detLevel, n, side=1)
            bs = sqrt(n) * sum([(xi._Num__value - mean)**3 for xi in keep]) / sum([(xi._Num__value - mean)**2 for xi in keep])**1.5     
            if process:
                if first:
                    latex.add(r'\text{共有}%d\text{个观测值（}n=%d\text{），求其样本均值}' % (n, n))
                    first = False                    
                else:
                    latex.add(r'\text{取出这个观测值之后，余下的数据为}%s' % ikeep.latex())
                    latex.add(r'\text{对于剩余的}%d\text{个值（}n=%d\text{），求其样本均值}' % (n, n))
                p_mean, lsub = ikeep.mean(process=True, needValue=True)
                latex.add(lsub)
                latex.add(r'\text{使用}')
                sciDigit = ikeep._NumItem__sciDigit()
                if sciDigit == 0:
                    sum3Expr = '+'.join([(r'%s^{3}' % (xi - p_mean).dlatex(1)) for xi in keep])
                    sum2Expr = '+'.join([(r'%s^{2}' % (xi - p_mean).dlatex(1)) for xi in keep])
                else:
                    d_arr = ikeep * 10**(-sciDigit)
                    d_mean = ikeep.mean() * 10**(-sciDigit)
                    sum3Expr = '+'.join([(r'%s^{3}' % (xi - d_mean).dlatex(1)) for xi in d_arr])
                    sum2Expr = '+'.join([(r'%s^{2}' % (xi - d_mean).dlatex(1)) for xi in d_arr])
                latex.add(r'b_{s}=\cfrac{\sqrt{n}\sum\limits_{i=1}^n \left(%s_{i}-\overline{%s}\right)^{3}}{\left[\sum\limits_{i=1}^n \left(%s_{i}-\overline{%s}\right)^{2}\right]^{3/2}}=\cfrac{\sqrt{%d}\times\left[%s\right]}{\left[%s\right]^{3/2}}=%.2f' % (symX, symX, symX, symX, n, sum3Expr, sum2Expr, bs))
                latex.add(r"\text{确定检出水平}\alpha=%g\text{，查表得临界值}b_{1-\alpha}(n)=b_{%g}(%d)=%.2f" % (detLevel, rep_detLevel, n, bsv))
            if side == 'up':
                if bs > bsv:
                    bsv2 = b(rep_delLevel, n, side=1)  #查表获得剔除水平下的G值（双侧）
                    if process:
                        latex.add(r"\text{因}b_{s}>b_{%g}(%d)\text{，故判定距离均值}%s\text{右侧最远的值}%s_{(%d)}=%s\text{为离群值}" % (rep_detLevel, n, p_mean, symX, n, keep[-1].latex()))
                        latex.add(r"\text{对于检出的离群值}%s_{(%d)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}b_{1-\alpha^{*}}(n)=b_{%g}(%d)=%.2f" % (symX, n, delLevel, rep_delLevel, n, bsv2))
                        if bs > bsv2:
                            latex.add(r"\text{因}b_{s}>b_{%g}(%d)\text{，故判定}%s_{(%d)}=%s\text{为统计离群值}" % (rep_delLevel, n, symX, n, keep[-1].latex()))
                        else:
                            latex.add(r"\text{因}b_{s}<b_{%g}(%d)\text{，故判为未发现}%s_{(%d)}=%s\text{是统计离群值（即}%s_{(%d)}\text{为歧离值）}" % (rep_delLevel, n, symX, n, keep[-1].latex(), symX, n))
                    if bs > bsv2:
                        detected['statOutliers'].append(keep[-1])
                    else:
                        detected['stragglers'].append(keep[-1])
                    keep.remove(keep[-1])
                else:
                    if process:
                        latex.add(r"\text{因}b_{s}<b_{%g}(%d)\text{，故不能再检出离群值}" % (rep_detLevel, n))
                    break
            elif side == 'down':
                if -bs > bsv:
                    bsv2 = b(rep_delLevel, n, side=1)  #查表获得剔除水平下的G值（双侧）
                    if process:
                        latex.add(r"\text{因}-b_{s}>b_{%g}(%d)\text{，故判定距离均值}%s\text{左侧最远的值}%s_{(1)}=%s\text{为离群值}" % (rep_detLevel, n, p_mean, symX, keep[0].latex()))
                        latex.add(r"\text{对于检出的离群值}%s_{(1)}\text{，确定剔除水平}\alpha^{*}=%g\text{，查表得临界值}b_{1-\alpha^{*}}(n)=b_{%g}(%d)=%.2f" % (symX, delLevel, rep_delLevel, n, bsv2))
                        if -bs > bsv2:
                            latex.add(r"\text{因}-b_{s}>b_{%g}(%d)\text{，故判定}%s_{(1)}=%s\text{为统计离群值}" % (rep_delLevel, n, symX, keep[0].latex()))
                        else:
                            latex.add(r"\text{因}-b_{s}<b_{%g}(%d)\text{，故判为未发现}%s_{(1)}=%s\text{是统计离群值（即}%s_{(1)}\text{为歧离值）}" % (rep_delLevel, n, symX, keep[0].latex(), symX))
                    if -bs > bsv2:
                        detected['statOutliers'].append(keep[0])
                    else:
                        detected['stragglers'].append(keep[0])
                    keep.remove(keep[0])
                else:
                    if process:
                        latex.add(r"\text{因}-b_{s}<b_{%g}(%d)\text{，故不能再检出离群值}" % (rep_detLevel, n))
                    break 
            if len(keep) < 8:
                if process:
                    latex.add(r'\text{剩余观测值数量小于8个，不能继续进行偏度—峰度检验，检验结束}')
                break;
    remained = item._NumItem__arr[:]
    for r in detected['statOutliers']:
        remained.remove(r)
    for r in detected['stragglers']:
        remained.remove(r)   
    detected['statOutliers'] = NumItem(sorted(detected['statOutliers']), sym=item._NumItem__sym)
    detected['stragglers'] = NumItem(sorted(detected['stragglers']), sym=item._NumItem__sym)
    if process:
        detectedCount = len(item) - len(remained)
        if detectedCount == 0:
            latex.add(r'\text{综上，未检验到离群值}')
        elif detectedCount == 1:
            if len(detected['statOutliers']) == 1:
                latex.add(r'\text{综上，检验出了1个统计离群值}' + detected['statOutliers'][0].latex())
            else:
                latex.add(r'\text{综上，检验出了1个歧离值}' + detected['stragglers'][0].latex())
        else:
            sExpr = r'\text{综上，共检验到%d个离群值，其中}' % detectedCount
            if len(detected['statOutliers']) > 0:
                sExpr += r'\text{统计离群值为}' + detected['statOutliers'].latex()
            if len(detected['stragglers']) > 0:
                sExpr += len(detected['statOutliers']) * '，' + r'\text{歧离值为}' + detected['stragglers'].latex()
            latex.add(sExpr)
        if needValue:
            return (detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)), latex
        else:
            return latex
    return detected, NumItem(remained, item._NumItem__mu, sym=item._NumItem__sym)
