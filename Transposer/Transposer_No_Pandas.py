# -*- coding: utf-8 -*-
"""
Created on Thu Jul 03 12:39:03 2014

@author: paulinkenbrandt
"""

import arcpy
import numpy as np
import os

infile = arcpy.GetParameterAsText(0)



arcpy.AddField_management(infile,'ParamSht',field_type = 'TEXT', field_length = 10)

temptb = arcpy.env.scratchGDB + os.path.sep + "temptb"
temptb1 = arcpy.env.scratchGDB + os.path.sep + "temptb1"
temptb2 = arcpy.env.scratchGDB + os.path.sep + "temptb2"

arcpy.TableSelect_analysis(infile, temptb, '"Param" in(\'Sulfate\', \'Nitrate\', \'Nitrite\', \'Calcium\', \'Potassium\', \'Sodium\',\'Magnesium\', \'Sodium plus potassium\', \'Bicarbonate\', \'Carbonate\', \'Chloride\')')



expression = "getChem(!Param!)"
codeblock = '''
def getChem(p):
    chemdict = {'Sulfate':'SO4', 'Nitrate':'NO3','Magnesium':'Mg', 'Nitrite':'NO2', 'Calcium':'Ca', 'Potassium':'K', 'Sodium':'Na', 'Sodium plus potassium':'NaK', 'Bicarbonate':'HCO3', 'Carbonate':'CO3', 'Chloride':'Cl'}    
    return chemdict.get(p)
    '''

arcpy.CalculateField_management(temptb,'ParamSht',expression, 'PYTHON_9.3', codeblock)


# Set a variable to store value field name
valueFieldName = "ResultValue"
out = arcpy.GetParameterAsText(1)

arcpy.PivotTable_management(temptb, 'SampleId','ParamSht','ResultValue',temptb1)
arr = arcpy.da.TableToNumPyArray(temptb1, ('SampleId','Cl', 'HCO3','CO3', 'SO4','Na','NaK','K','Ca','Mg','NO3'), null_value='')
arcpy.Delete_management(temptb)


nosamp = len(arr['Ca'])
Cl = arr['Cl']
Mg = arr['Mg']
K = arr['K']
Ca = arr['Ca']
Na = arr['Na']
HCO3 =arr['HCO3']
CO3 = arr['CO3']
NaK = arr['NaK']
SO4 = arr['SO4']
NO3 = arr['NO3']


for i in range(nosamp):
    if NaK[i]=='':
        NaK[i]=0.0
    else:
        NaK[i]=float(NaK[i])
    if Ca[i]=='':
        Ca[i]=0.0
    else:
        Ca[i]=float(Ca[i])
    if Mg[i]=='':
        Mg[i]=0.0
    else:
        Mg[i]=float(Mg[i])
    if HCO3[i]=='':
        HCO3[i]=0.0
    else:
        HCO3[i]=float(HCO3[i])
    if SO4[i]=='':
        SO4[i]=0.0
    else:
        SO4[i]=float(SO4[i])        
    if Na[i]=='':
        Na[i]=0.0
    else:
        Na[i]=float(Na[i])
    if K[i]=='':
        K[i]=0.0
    else:
        K[i]=float(K[i])
    if Cl[i]=='':
        Cl[i]=0.0
    else:
        Cl[i]=float(Cl[i]) 
    if CO3[i]=='':
        CO3[i]=0.0
    else:
        CO3[i]=float(CO3[i])
    if NO3[i]=='':
        NO3[i]=0.0
    else:
        NO3[i]=float(NO3[i])

stid = arr['SampleId']

for i in range(nosamp):
    if NaK[i]==0:
        NaK[i]=Na[i]+K[i]



#define field order to add to table
fields = [Na,K,Ca,Mg,Cl,HCO3,CO3,SO4,NaK,NO3,stid]
#transpose array from columns to rows for proper tool input
inay = zip(*fields)


# define field names and data types for the array
dts = {'names': ('Na','K','Ca','Mg','Cl','HCO3','CO3','SO4','NaK','NO3','stid'), 'formats' : (np.float64, np.float64, np.float64, np.float64, np.float64, np.float64,np.float64,np.float64,np.float64,np.float64,'|S256')}
inarray = np.rec.fromrecords(inay,dtype = dts)

# add fields to existing table by joining using the unique station id

arcpy.Delete_management(temptb1)

arcpy.da.NumPyArrayToTable(inarray,temptb2)

for field in arcpy.ListFields(temptb2):
    with arcpy.da.UpdateCursor(temptb2, [field.name]) as cursor:
        for row in cursor:
            if row[0] == 0:
                row[0] = None
                cursor.updateRow(row)



stats=[]
for field in arcpy.ListFields(temptb2):
    # Just find the fields that have a numeric type
    if field.type in ("Double", "Integer", "Single", "SmallInteger"):
        # Add the field name and Sum statistic type
        #    to the list of fields to summarize
        stats.append([field.name, "MEAN"])


arcpy.Statistics_analysis(temptb2,arcpy.GetParameterAsText(1),stats,'stid')

for field in arcpy.ListFields(arcpy.GetParameterAsText(1)):
            # Process: Add Field
            name = str(field.name)
            if field.type in ("Double", "Integer", "Single", "SmallInteger") and name <> 'FREQUENCY':            
                arcpy.AddField_management(arcpy.GetParameterAsText(1), name.replace('MEAN_',''), "DOUBLE", "", "", "50", "",        "NULLABLE", "NON_REQUIRED", "")
            
            # Process: Calculate Field                            
                arcpy.CalculateField_management(arcpy.GetParameterAsText(1), name.replace('MEAN_',''), "!"+name+"!", "PYTHON_9.3", "")
            # Process: Delete Field                 
                arcpy.DeleteField_management(arcpy.GetParameterAsText(1), name)
                          
arcpy.Delete_management(temptb2)