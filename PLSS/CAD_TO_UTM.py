# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 09:56:30 2015

@author: paulinkenbrandt
"""

import arcpy
import os

table = arcpy.GetParameterAsText(0) #table of CAD coordinates you are seeking to assign utms
field = arcpy.GetParameterAsText(1) #field within input table that contains the CAD coordinates
trsLocal = arcpy.GetParameterAsText(2) #Location of TRS database

arcpy.env.workspace = trsLocal



arr = arcpy.da.TableToNumPyArray('QQQ3','quad')