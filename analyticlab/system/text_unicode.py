#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:54:15 2018

@author: xingrongtech
"""

from .exceptions import subUnsupportedException, supUnsupportedException

sub_dict = {'0':'⁰', '1':'¹', '2':'²', '3':'³', '4':'⁴', '5':'⁵', '6':'⁶', 
            '7':'⁷', '8':'⁸', '9':'⁹', 
            '-':'⁻', '+':'⁺', '=':'⁼', '(':'⁽', ')':'⁾', 
            'a':'ᵃ', 'b':'ᵇ', 'c':'ᶜ', 'd':'ᵈ', 'e':'ᵉ', 'f':'ᶠ', 'g':'ᵍ', 
            'h':'ʰ', 'i':'ⁱ', 'j':'ʲ', 'k':'ᵏ', 'l':'ˡ', 'm':'ᵐ', 'n':'ⁿ', 
            'o':'ᵒ', 'p':'ᵖ', 'r':'ʳ', 's':'ˢ', 't':'ᵗ', 'u':'ᵘ', 'v':'ᵛ', 
            'w':'ʷ', 'x':'ˣ', 'y':'ʸ', 'z':'ᶻ'}

sup_dict = {'0':'₀', '1':'₁', '2':'₂', '3':'₃', '4':'₄', '5':'₅', '6':'₆', 
            '7':'₇', '8':'₈', '9':'₉', 
            '-':'₋', '+':'₊', '=':'₌', '(':'₍', ')':'₎',
            'a':'ₐ', 'e':'ₑ', 'h':'ₕ', 'i':'ᵢ', 'k':'ₖ', 'l':'ₗ', 'm':'ₘ', 
            'n':'ₙ', 'o':'ₒ', 'p':'ₚ', 'r':'ᵣ', 's':'ₛ', 't':'ₜ', 'u':'ᵤ', 
            'v':'ᵥ', 'x':'ₓ'}

def usub(text):
    if type(text) == int:
        text = str(text)
    elif type(text) == float:
        text = '%g' % text
    res = []
    for ti in text:
        if ti not in sub_dict:
            raise subUnsupportedException(ti)
        else:
            res.append(sub_dict[ti])
    return ''.join(res)

def usup(text):
    if type(text) == int:
        text = str(text)
    elif type(text) == float:
        text = '%g' % text
    res = []
    for ti in text:
        if ti not in sup_dict:
            raise supUnsupportedException(ti)
        else:
            res.append(sup_dict[ti])
    return ''.join(res)