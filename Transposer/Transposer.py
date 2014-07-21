# -*- coding: utf-8 -*-
"""
Created on Thu Jul 03 11:56:58 2014

@author: paulinkenbrandt
"""

import arcpy
import numpy as np
import pandas as pd

infile = arcpy.GetParameterAsText(0)

#input = "C:\\Temp\\test.gdb\\WQP_Results"
#
#tview = arcpy.MakeTableView_management(input)

arr = arcpy.da.TableToNumPyArray(infile, ('Param', 'ResultValue','SampleId'))

param = arr['Param']
result = arr['ResultValue']
smid = arr['SampleId']

shortparam = []
shortresult = []
shortname = []
shortsmid = []

chemlist = ['Sulfate', 'Nitrate', 'Nitrite', 'Calcium', 'Potassium', 'Magnesium','Sodium', 'Sodium plus potassium', 'Bicarbonate', 'Carbonate', 'Chloride']

chemdict = {'Ammonia-nitrogen as N':'N','Inorganic nitrogen (nitrate and nitrite) as N':'N','Inorganic nitrogen (nitrate and nitrite)':'N','Kjeldahl nitrogen':'N','Total dissolved solids':'TDS','Sulfate as SO4':'SO4','pH, lab':'pH','Temperature, water':'Temp_C','Arsenic':'As','Bromide':'Br','Carbon dioxide':'CO2', 'Specific Conductance':'Cond','Conductivity':'Cond', 'Sulfate':'SO4', 'Nitrate':'NO3', 'Nitrite':'NO2','Magnesium':'Mg', 'Calcium':'Ca', 'Potassium':'K', 'Sodium':'Na', 'Sodium plus potassium':'NaK', 'Bicarbonate':'HCO3', 'Carbonate':'CO3', 'Chloride':'Cl'}


for i in range(len(param)):
    if param[i] in chemlist:
        shortparam.append(param[i])
        shortresult.append(float(result[i]))
        shortname.append(chemdict[param[i]])
        shortsmid.append(smid[i])

dat = zip(shortparam,shortresult,shortname,shortsmid)
df = pd.DataFrame(dat,columns=['shortparam','shortresult','shortname','shortsmid'])

dpiv = df.pivot(index='smid', columns='shortparam', values='shortresult')

dgrp = dpiv.groupby('smid').agg(np.mean)


arcpy.AddMessage(dgrp)
