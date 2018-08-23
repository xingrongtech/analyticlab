#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 22:47:34 2018

@author: xingrongtech
"""

UnitIsOpen = True

def openUnit():
    global UnitIsOpen
    UnitIsOpen = True
        
def closeUnit():
    global UnitIsOpen
    UnitIsOpen = False
    
def unitIsOpen():
    global UnitIsOpen
    return UnitIsOpen