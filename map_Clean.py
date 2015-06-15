# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 08:30:02 2015

@author: paulinkenbrandt
"""


tsimport arcpy
import os


arcpy.env.overwriteOutput=True
mxd = arcpy.mapping.MapDocument("C:\\PROJECTS\\Ashley_Spring\\Figure Maps\\06_Geomap.mxd")

for df in arcpy.mapping.ListDataFrames(mxd):
    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
        if lyr.isServiceLayer:
            arcpy.mapping.RemoveLayer(df, lyr)
arcpy.RefreshTOC()
mxd.saveACopy("C:\\PROJECTS\\Ashley_Spring\\Figure Maps\\06_GeomapA.mxd")
#del mxd