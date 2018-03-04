# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 19:20:06 2018

@author: xingrongtech
"""

class Ins():
    '''Ins为测量仪器类，该类用于描述一个测量仪器的B类不确定度和仪器测量值的单位。'''
    norm = 0  #正态分布
    rectangle = 1  #矩形分布
    triangle = 2  #三角分布
    arcsin = 3  #反正弦分布
    twopoints = 4  #两点分布
    trapezoid = 5  #梯形分布
    
    def __init__(self, halfWidth, distribution=1, unit=None, *param):
        '''初始化一个测量仪器
        【参数说明】
        1.halfWidth（str）：半宽度。由于半宽度会决定有效数字位数，因此要以字符串形式给出。
        2.distribution（可选，int）：分布类型，从以下列表中取值。默认distribution=Ins.rectangle。
        ①Ins.norm：正态分布；
        ②Ins.rectangle：矩形分布；
        ③Ins.triangle：三角分布；
        ④Ins.arcsin：反正弦分布；
        ⑤Ins.twopoints：两点分布；
        ⑥Ins.trapezoid：梯形分布，此分布下需要通过*param给出β值
        3.unit（可选，str）：测量值的单位。默认unit=None。
        '''
        self.halfWidth = halfWidth
        self.distribution = distribution
        self.unit = unit
        if len(param) > 0:
            self.beta = param[0]
            
刻度尺_毫米_1 = Ins('0.5', unit='mm')
游标卡尺_毫米_2 = Ins('0.02', unit='mm')
游标卡尺_厘米_3 = Ins('0.002', unit='cm')
游标卡尺_米_5 = Ins('0.00002', unit='m')
一级千分尺_毫米_3 = Ins('0.004', unit='mm')
显微镜螺旋测微器_毫米_3 = Ins('0.015', unit='mm')
米尺_米_4 = Ins('0.0005', unit='m')
米尺_厘米_2 = Ins('0.05', unit='cm')
米尺_厘米_1 = Ins('0.5', unit='cm')