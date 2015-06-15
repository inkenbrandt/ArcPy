# -*- coding: utf-8 -*-
"""
Created on Mon Feb 02 08:08:41 2015

@author: paulinkenbrandt
"""

# Query Wells
# http://gis.stackexchange.com/questions/29735/select-features-by-attribute-if-in-python-list

import arcpy

def qmatch(div):
    quarters={'NE':'a','NW':'b','SW':'c','SE':'d'}
    q = quarters.get(div)
    return q