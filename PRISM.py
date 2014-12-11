# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 13:52:49 2014

@author: paulinkenbrandt

http://gis.stackexchange.com/questions/108113/loop-with-arcpy-listfiles
"""

import arcpy
import os
from arcpy import env
from arcpy.sa import *
import arcpy_metadata as md
import datetime

#r'C:\GIS\PRISM\S\MAY_OCT_14'
env.workspace = arcpy.GetParameterAsText(0)
outplace = arcpy.GetParameterAsText(1)

# Uncomment the following if you are using asc files

ischecked1 = arcpy.GetParameterAsText(2)
ischecked2 = arcpy.GetParameterAsText(3)


ascFileList = arcpy.ListFiles("*.asc")

if str(ischecked1) == 'true':
    for ascFile in ascFileList:
        if int(ascFile[1:-1])>= (int(arcpy.GetParameterAsText(8))*100+int(arcpy.GetParameterAsText(9))):           
            # get the file name without extension (replaces the %Name% variable from ModelBuidler)
            ascFileName = os.path.splitext(ascFile)[0]    
            # define the output file
            rastFile = env.workspace + '/' + ascFileName + 'o'
            ascinFile = env.workspace + '/' + ascFile
            arcpy.ASCIIToRaster_conversion(ascinFile, rastFile, 'INTEGER')

if str(ischecked2) == 'true': 
# the following defines projections and clips the PRISM raster file
    imgFileList = arcpy.ListRasters()
    for imgFile in imgFileList:
        if int(imgFile[1:-1])>= (int(arcpy.GetParameterAsText(8))*100+int(arcpy.GetParameterAsText(9))):   
            imgFileName = os.path.splitext(imgFile)[0]
            imgFile1 = env.workspace + '/' + imgFileName + 'p'
            incoords = arcpy.GetParameterAsText(4)
            # Process: Projektion definieren
            arcpy.DefineProjection_management(imgFile, incoords)
            outExtractByMask = ExtractByMask(imgFile, arcpy.GetParameterAsText(5))
            outExtractByMask.save(imgFile1)
            arcpy.AddMessage("Clipped " +imgFileName)

arcpy.AddMessage("Finished Clipping Data!")

outcoord = arcpy.GetParameterAsText(6)


ischecked3 = arcpy.GetParameterAsText(7)
# the following projects the rasters and downsamples them
if str(ischecked3) == 'true':   
    prjFileList = arcpy.ListRasters()
    for prjFile in prjFileList:
        if int(prjFile[1:-1])>= (int(arcpy.GetParameterAsText(8))*100+int(arcpy.GetParameterAsText(9))):       
            prjFileName = os.path.splitext(prjFile)[0]
            prjFile1 = outplace + '/' + prjFileName
            arcpy.ProjectRaster_management(prjFile, prjFile1 ,outcoord, "CUBIC", arcpy.GetParameterAsText(10))
            arcpy.AddMessage("Projected and downsampled " +prjFileName)

arcpy.AddMessage("Finished Downsampling Data!")

# convert from mm to inches of ppt
ischecked4 = arcpy.GetParameterAsText(11)
if str(ischecked4) == 'true': 
    env.workspace = outplace    
    calcFileList = arcpy.ListRasters()
    for calcFile in calcFileList:
        if int(calcFile[1:-1])>= (int(arcpy.GetParameterAsText(8))*100+int(arcpy.GetParameterAsText(9))):           
            # Overwrite pre-existing files
            arcpy.env.overwriteOutput = True            
            calcFileName = os.path.splitext(calcFile)[0]
            calcFile1 = outplace + '/' + 'a' + calcFileName[1:-1]
            arcpy.Times_3d(calcFile,0.0393701,calcFile1)            
            arcpy.AddMessage("Converted " + calcFileName + ' to inches')


# Add Metadata Input
ischecked5 = arcpy.GetParameterAsText(12)

if str(ischecked5) == 'true':
    env.workspace = outplace
    metaFileList = arcpy.ListRasters('a*')
    for metafile in metaFileList:
        if int(metafile[1:-1])>= (int(arcpy.GetParameterAsText(8))*100+int(arcpy.GetParameterAsText(9))): 
            metaplace = outplace + '/' + metafile          
            metadata = md.MetadataEditor(metaplace)
            metadata.title.set('PRISM precipitation data (inches) ' + metafile[-3:-1] + ' ' + metafile[1:-3] ) #
            metadata.purpose.set('PRISM Raster File in Inches ' + metafile[-3:-1] + ' ' + metafile[1:-3])
            metadata.abstract.append('PRISM Raster File in Inches ' + metafile[-3:-1] + ' ' + metafile[1:-3])
            metadata.tags.add(["PRISM", "Precipitation", "Inches",metafile[-3:-1],metafile[1:-3] ])  # tags.extend is equivalent to maintain list semantics
            metadata.finish()  # save the metadata back to the original source feature class and cleanup. Without calling finish(), your edits are NOT saved!
            arcpy.AddMessage("Added Metadata to " + metafile + ' to inches')

## Run Zonal Statistics
#ischecked5 = arcpy.GetParameterAsText(13)
#
#if str(ischecked5) == 'true':
#    env.workspace = outplace
#    zoneFileList = arcpy.ListRasters()
#    for zoneFile in zoneFileList:
#        if int(zoneFile[1:-1])>= (int(arcpy.GetParameterAsText(8))*100+int(arcpy.GetParameterAsText(9))): 
#            zoneplace = outplace + '/' + zoneFile          
#            Zone_field = arcpy.GetParameterAsText(14)
#            if Zone_field == '#' or not Zone_field:
#                Zone_field = "ID" # provide a default value if unspecified
#            v_Name_ = arcpy.GetParameterAsText(15)
#            if v_Name_ == '#' or not v_Name_:
#                v_Name_ = "C:\\GIS\\PRISM\\Table\\"+zoneFile[1:-1]# provide a default value if unspecified
#            #files to calculate mean precip
#            HUCS = arcpy.GetParameterAsText(16)
#            if HUCS == '#' or not HUCS:
#                HUCS = "U:\\GWP\\Groundwater\\PowderMt\\Powder_Mtn.gdb\\Base\\Watershed" # provide a default value if unspecified
#            # Process: Zonal Statistics as Table
#            ZonalStatisticsAsTable(HUC,Zone_field, zoneFile, v_Name_, "DATA", "MEAN")