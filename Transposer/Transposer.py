# -*- coding: utf-8 -*-
"""
Created on Thu Jul 03 11:56:58 2014

@author: paulinkenbrandt
"""

import arcpy
import numpy as np
import pandas as pd

input = arcpy.GetParameterAsText(0)

#input = "C:\\Temp\\test.gdb\\WQP_Results"
#
#tview = arcpy.MakeTableView_management(input)

arr = arcpy.da.TableToNumPyArray(input, ('Param', 'ResultValue','Unit','SampleId'))

param = arr['Param']
result = arr['ResultValue']
unit = arr['Unit']
smid = arr['SampleId']

shortparam = []
shortresult = []
shortunit = []
shortname = []
shortsmid = []

chemlist = ['Sulfate', 'Nitrate', 'Nitrite', 'Calcium', 'Potassium', 'Sodium', 'Sodium plus potassium', 'Bicarbonate', 'Carbonate', 'Chloride']

chemdict = {'Sulfate':'SO4', 'Nitrate':'NO3', 'Nitrite':'NO2', 'Calcium':'Ca', 'Potassium':'K', 'Sodium':'Na', 'Sodium plus potassium':'NaK', 'Bicarbonate':'HCO3', 'Carbonate':'CO3', 'Chloride':'Cl'}


for i in range(len(param)):
    if param[i] in chemlist:
        shortparam.append(param[i])
        shortresult.append(float(result[i]))
        shortname.append(chemdict[param[i]])
        shortunit.append(unit[i])
        shortsmid.append(smid[i])

dat = zip(shortparam,shortresult,shortname,shortunit,shortsmid)
df = pd.DataFrame(dat)
        
arcpy.AddMessage(df)
