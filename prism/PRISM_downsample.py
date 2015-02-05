# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 16:27:39 2014

@author: paulinkenbrandt
"""

import arcpy
import os
from arcpy import env

env.workspace = arcpy.GetParameterAsText(0)
outplace = arcpy.GetParameterAsText(1)


imgFileList = arcpy.ListRasters('*op')
for imgFile in imgFileList:
    imgFileName = os.path.splitext(imgFile)[0]
    imgFile1 = env.workspace + '/' + imgFileName + 'p'
    arcpy.Resample_management(imgFile, imgFile1,arcpy.GetParameterAsText(2), "BILINEAR")