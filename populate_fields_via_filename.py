# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:39:44 2015

@author: paulinkenbrandt
"""

import arcpy

arcpy.env.workspace = r"O:\Washington_co\GIS\TO_USGS_Structure.gdb\Structure_Contours"

fcList = arcpy.ListFeatureClasses()
for fc in fcList:
    fcdescr = arcpy.Describe(fc)
    name = fcdescr.baseName
    parts = name.split("_")
    unit = parts[0]
    block = parts[1]
    with arcpy.da.UpdateCursor(fc,['Unit','Block']) as cursor:
        for row in cursor:
            row[0] = unit
            row[1] = block
            cursor.updateRow(row)