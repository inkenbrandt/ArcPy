# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:18:28 2015
@author: paulinkenbrandt
"""

import arcpy
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import datetime
#from rpy2.robjects.packages import importr
#utils = importr("rkt")

resultstable = arcpy.GetParameterAsText(0)
stationidfield = arcpy.GetParameterAsText(1)
datefield = arcpy.GetParameterAsText(2)
paramfield = arcpy.GetParameterAsText(3)
param = arcpy.GetParameterAsText(4)
valuefield = arcpy.GetParameterAsText(5)

fieldlist = [f.name for f in arcpy.ListFields(resultstable)]

stationid,parameter,dt,values = [],[],[],[]

# populate lists with values from the active table
with arcpy.da.UpdateCursor(resultstable,[datefield,paramfield,stationidfield,valuefield]) as cursor:

    for row in cursor:
        if row[1] in param:
            stationid.append(row[2])
            parameter.append(row[1])
            dt.append(row[0])
            values.append(row[3])

d = {'dt':dt, 'stationid':stationid, 'parameter':parameter, 'values':values}
        
df = pd.DataFrame(d, index=dt)
#arcpy.AddMessage(df)
from rpy2.robjects.packages import importr


now = datetime.datetime.now()

plt.figure()
plt.plot(df.index.to_datetime(),df['values'])
plt.savefig("C:\\PROJECTS\\EPA EN\\test_figs\\"+str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"_"+str(now.hour)+"_"+str(now.minute)+".pdf")
plt.show()




