# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 14:59:30 2018

@author: xingrongtech
"""

from analyticlab.system.exceptions import alphaUnsupportedException

oneSide = {0.01: 0.99, 0.05: 0.95, 0.10: 0.90}
twoSide = {0.01: 0.995, 0.05: 0.975, 0.10: 0.95}

def rep(alpha, side):
    try:
        if side == 2:
            return twoSide[alpha]
        else:
            return oneSide[alpha]
    except:
        raise alphaUnsupportedException(alpha)