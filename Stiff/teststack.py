# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 09:19:06 2015

@author: paulinkenbrandt
"""
import numpy as np
import os

def getfilename(path):
    # this function extracts the file name without file path or extension
    return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]

fileplace = r'C:\Users\PAULINKENBRANDT\Documents\GitHub\Arcpy\PLSS\jog'
#fileplace = arcpy.GetParameterAsText(5)

direct = os.path.dirname(os.path.abspath(fileplace)) + '\\' + getfilename(fileplace) + "_points" + os.path.splitext(fileplace)[1]
#stack = np.append(xy1,(xy2,xy3),axis=1)
print direct
#print stack

print os.path.splitext(fileplace)[1]