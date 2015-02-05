# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 16:38:46 2014

@author: paulinkenbrandt
"""

import arcpy
import os
from arcpy import env
from arcpy.sa import *

env.workspace = arcpy.GetParameterAsText(0)
imgFileList = arcpy.ListRasters('*opp')
for imgFile in imgFileList:
    imgFileName = os.path.splitext(imgFile)[0]
    imgFile1 = env.workspace + '/' + imgFileName + 'z'
    outZSaT = ZonalStatisticsAsTable(GetParameterAsText(1), arcpy.GetParameterAsText(2), imgFile, imgFile1, "DATA", "ALL")
    arcpy.MakeFeatureLayer_management (GetParameterAsText(1),  arcpy.GetParameterAsText(2))
    arcpy.AddJoin_management(GetParameterAsText(1), arcpy.GetParameterAsText(2), imgFile1, arcpy.GetParameterAsText(2))
    arcpy.CopyFeatures_management(GetParameterAsText(1), imgFile1+"join")
    arcpy.RemoveJoin_management(GetParameterAsText(1))

