# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 06:58:20 2014

@author: paulinkenbrandt
"""

import arcpy
import os
from arcpy import env
from arcpy.sa import *


outplace = arcpy.GetParameterAsText(0)
env.workspace = outplace

def setdefaultvalue(variable, default):
    '''fills in default value when user does not input one'''
    if variable =='#' or not variable:
        return default
    else:
        return variable

HUCS = setdefaultvalue(arcpy.GetParameterAsText(1),"U:\\GWP\\Groundwater\\PowderMt\\Powder_Mtn.gdb\\Base\\Watershed")    

## Clip File to HUCS
runclipper = arcpy.GetParameterAsText(5)
imgFileList = arcpy.ListRasters()
outrasterdest = arcpy.GetParameterAsText(4)
if str(runclipper) == 'true':
    for imgFile in imgFileList:
        # set start year and start month for processing
        rasteryear = setdefaultvalue(int(arcpy.GetParameterAsText(2)), 1895)        
        rastermonth = setdefaultvalue(int(arcpy.GetParameterAsText(3)), 1)
        # skip files younger than start year and month
        if int(imgFile[1:])>= (rasteryear*100+rastermonth): 
            imgFileName = os.path.splitext(imgFile)[0]            
            imgFile1 = outrasterdest + '/' + imgFileName
            outExtractByMask = ExtractByMask(imgFile, arcpy.GetParameterAsText(1))
            outExtractByMask.save(imgFile1)
            arcpy.AddMessage("Clipped " +imgFileName)

env.workspace = outrasterdest

zoneFileList = arcpy.ListRasters()
for zoneFile in zoneFileList:
    # set start year and start month for processing
    rasteryear = setdefaultvalue(int(arcpy.GetParameterAsText(2)), 1895)        
    rastermonth = setdefaultvalue(int(arcpy.GetParameterAsText(3)), 1)
    # skip files younger than start year and month
    if int(os.path.splitext(zoneFile[1:])[0])>= (rasteryear*100+rastermonth): 
        # Execute RasterToPoint
        arcpy.env.overwriteOutput = True        
        outsheds = outrasterdest + "/sheds"+zoneFile[1:]+".shp"       
        points = arcpy.CreateFeatureclass_management("in_memory","FC"+zoneFile,"POINT")        

        points = arcpy.RasterToPoint_conversion(zoneFile, points, "VALUE")
        
        arcpy.AddMessage("Pointillized " +zoneFile)        
        # Create a new fieldmappings and add the two input feature classes.
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(HUCS)
        fieldmappings.addTable(points)
        pointFieldIndex = fieldmappings.findFieldMapIndex("grid_code")
        fieldmap = fieldmappings.getFieldMap(pointFieldIndex)
         
        # Get the output field's properties as a field object
        field = fieldmap.outputField
        # Rename the field and pass the updated field object back into the field map
        field.name = "a"+ zoneFile[1:]
        field.aliasName = "a"+ zoneFile[1:]
        fieldmap.outputField = field
        
        # Set the merge rule to mean and then replace the old fieldmap in the mappings object
        # with the updated one
        fieldmap.mergeRule = "mean"
        fieldmappings.replaceFieldMap(pointFieldIndex, fieldmap)     
        # Delete fields that are no longer applicable, such as city CITY_NAME and CITY_FIPS
        # as only the first value will be used by default
        try:      
            x = fieldmappings.findFieldMapIndex("Join_Count")
            fieldmappings.removeFieldMap(x)
            y = fieldmappings.findFieldMapIndex("TARGET_FID")
            fieldmappings.removeFieldMap(y)   
            z = fieldmappings.findFieldMapIndex("Shape_Leng")
            fieldmappings.removeFieldMap(y)
        except (RuntimeError, TypeError, NameError, ValueError):
            pass

        arcpy.AddMessage("Field Mapped " +zoneFile)

        arcpy.SpatialJoin_analysis(HUCS,points, outsheds,"JOIN_ONE_TO_ONE","#",fieldmappings, "INTERSECT")
        arcpy.AddMessage("Joined and created " + outsheds)
        HUCS = arcpy.CopyFeatures_management(outsheds, HUCS)
        #arcpy.DeleteFeatures_management(outsheds)
