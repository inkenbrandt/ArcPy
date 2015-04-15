# -*- coding: utf-8 -*-

""" Hydrochemistry: Constructs multiple Stiff plots

    Based on code by:
    B.M. van Breukelen <b.m.vanbreukelen@vu.nl>
    http://python.hydrology-amsterdam.nl/scripts/stiff_fill.py
    Created on Mon Jun 23 11:58:47 2014

    @author: paulinkenbrandt
"""


#from pylab import * 
import numpy as np
import os
import arcpy
from arcpy import env
env.workspace = "CURRENT"

#path = os.getcwd() 

input = arcpy.GetParameterAsText(0)

# Convert values in table fields to numpy arrays
arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3', 'CO3', 'SO4', 'Na', 'K', 'Ca', 'Mg', 'Cond', 'StationId',arcpy.GetParameterAsText(1), arcpy.GetParameterAsText(2)),null_value=0)

d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}

x = arr[arcpy.GetParameterAsText(1)]
y = arr[arcpy.GetParameterAsText(2)]
m = float(arcpy.GetParameterAsText(3)) #multiplier

spatialref = arcpy.GetParameterAsText(4)

nosamp = len(arr['Cl']) # Determine number of samples in file


# Column Index for parameters
# Convert ion concentrations in mg/L to meq/L
Cl = [arr['Cl'][i]*d['Cl'] for i in range(nosamp)]
Mg = [arr['Mg'][i]*d['Mg'] for i in range(nosamp)]
K = [arr['K'][i]*d['K'] for i in range(nosamp)]
Ca = [arr['Ca'][i]*d['Ca'] for i in range(nosamp)]
Na = [arr['Na'][i]*d['Na'] for i in range(nosamp)]
HCO3 = [arr['HCO3'][i]*d['HCO3'] for i in range(nosamp)]
CO3 = [arr['CO3'][i]*d['CO3'] for i in range(nosamp)]
NaK = [Na[i]+K[i] for i in range(nosamp)]
SO4 = [arr['SO4'][i]*d['SO4'] for i in range(nosamp)]


StatId = arr['StationId']


Anions = [Cl[i]+HCO3[i]+CO3[i]+SO4[i] for i in range(nosamp)]
Cations = [K[i]+Mg[i]+Na[i]+Ca[i] for i in range(nosamp)]
EC = [Anions[i]+Cations[i] for i in range(nosamp)]

# Generate x coordinates for stiff leaders based on concentration of major ions
## Cations
xNaK = [-1*NaK[i]*m + float(x[i]) for i in range(nosamp)]
xCa = [-1*Ca[i]*m + float(x[i]) for i in range(nosamp)]
xMg = [-1*Mg[i]*m + float(x[i]) for i in range(nosamp)]
## Anions
xSO4 = [SO4[i]*m + float(x[i]) for i in range(nosamp)]
xHCO3 = [HCO3[i]*m + float(x[i]) for i in range(nosamp)]
xCl= [Cl[i]*m + float(x[i]) for i in range(nosamp)]


# Generate x,y pairs; y coordinates for stiff leaders are independent of concentration
xy1 = [[xNaK[i], 1*10*m + float(y[i]), 'NaK', NaK[i], StatId[i]] for i in range(nosamp)]
xy2 = [[xCa[i], 0*10*m + float(y[i]), 'Ca', Ca[i], StatId[i]] for i in range(nosamp)]
xy3 = [[xMg[i], -1*10*m + float(y[i]), 'Mg', Mg[i], StatId[i]] for i in range(nosamp)]
xy4 = [[xSO4[i], -1*10*m + float(y[i]), 'SO4', SO4[i], StatId[i]] for i in range(nosamp)]
xy5 = [[xHCO3[i], 0*10*m + float(y[i]), 'HCO3', HCO3[i], StatId[i]] for i in range(nosamp)]
xy6 = [[xCl[i], 1*10*m + float(y[i]), 'Cl', Cl[i], StatId[i]] for i in range(nosamp)]
xy7 = [[xNaK[i], 1*10*m + float(y[i]), 'NaK', NaK[i], StatId[i]] for i in range(nosamp)]

# list coordinate pairs to construct features
feature_info = [[xy6[i],xy5[i],xy4[i],xy3[i],xy2[i],xy1[i]] for i in range(nosamp)]

#restructure arrays for a new table
def unstack(stuff):
    x,y,par,conc,stat=[],[],[],[],[]    
    for i in stuff:
        x.append(i[0])
        y.append(i[1])
        par.append(i[2])
        conc.append(i[3])
        stat.append(i[4])
    stack = [x,y,par,conc,stat]
    return stack
a = unstack(xy1)
b = unstack(xy2)
c = unstack(xy3)
d = unstack(xy4)
e = unstack(xy5)
f = unstack(xy6)

axy,bxy,cxy,dxy,exy = [],[],[],[],[]
varlist =[axy,bxy,cxy,dxy,exy]
for i in range(len(a)):
    varlist[i] = np.append(a[i],(b[i],c[i],d[i],e[i],f[i]))
varlist = zip(*np.array(varlist))
arcpy.AddMessage(len(varlist))
# denote table field names and types
dts = {'names':('xfield', 'yfield', 'chemcode', 'conc', 'StationId'), 'formats': (np.float32, np.float32, '|S256', '|S256', '|S256')}

# join table data with table field names and types
inarray = np.rec.fromrecords(varlist, dtype=dts)



def getfilename(path):
    # this function extracts the file name without file path or extension
    return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]

fileplace = arcpy.GetParameterAsText(5)
pointspath = os.path.dirname(os.path.abspath(fileplace)) + '\\' + getfilename(fileplace) + "_points" + os.path.splitext(fileplace)[1]

temptab = arcpy.env.scratchGDB + os.path.sep + "temptab3"
templayer = arcpy.env.scratchGDB + os.path.sep + "templayers"

arcpy.da.NumPyArrayToTable(inarray,temptab)
arcpy.MakeXYEventLayer_management(temptab,"xfield","yfield",templayer,spatialref)
points = arcpy.CopyFeatures_management(templayer, pointspath)

arcpy.Delete_management(temptab)
arcpy.Delete_management(templayer)

# get spatail ref from user


 
# Create a Polygon object based on the array of points
# Append to the list of Polygon objects
polyFeatures = []
for i in feature_info:
    pointSet = []    
    for j in range(len(i)):
        pointSet.append(arcpy.Point(X = i[j][0],Y = i[j][1]))
    polyFeatures.append(arcpy.Polygon(arcpy.Array(pointSet),spatialref))
polygons = arcpy.CopyFeatures_management(polyFeatures, arcpy.GetParameterAsText(5))


lineFeatures = []
pointA = [[x[i], 1.1*10*m + float(y[i])] for i in range(nosamp)]
pointB = [[x[i], -1.1*10*m + float(y[i])] for i in range(nosamp)]
pointC = [[x[i]+5*m, 1.1*10*m + float(y[i])] for i in range(nosamp)]
pointD = [[x[i]-5*m, 1.1*10*m + float(y[i])] for i in range(nosamp)]

# list coordinate pairs to construct features
lineFeatureVert_info = [[pointA[i],pointB[i]] for i in range(nosamp)]
lineFeatureHor_info = [[pointC[i],pointD[i]] for i in range(nosamp)]
for i in lineFeatureVert_info:
    pointSet = []    
    for j in range(len(i)):
        pointSet.append(arcpy.Point(X = i[j][0],Y = i[j][1]))
    lineFeatures.append(arcpy.Polyline(arcpy.Array(pointSet),spatialref))
for i in lineFeatureHor_info:
    pointSet = []    
    for j in range(len(i)):
        pointSet.append(arcpy.Point(X = i[j][0],Y = i[j][1]))
    lineFeatures.append(arcpy.Polyline(arcpy.Array(pointSet),spatialref))
    
linespath = os.path.dirname(os.path.abspath(fileplace)) + '\\' + getfilename(fileplace) + "_lines" + os.path.splitext(fileplace)[1]
polylines = arcpy.CopyFeatures_management(lineFeatures, linespath)



# get the map document
mxd = arcpy.mapping.MapDocument("CURRENT")

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd)[0]

layer = arcpy.mapping.Layer(linespath)
layer1 = arcpy.mapping.Layer(pointspath)
arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, layer1, "AUTO_ARRANGE")
arcpy.RefreshTOC()

del mxd #, DF, Layer
arcpy.Delete_management(layer)
arcpy.Delete_management(layer1)

'''
Advanced Expression for labels (python):

def FindLabel ( [chemcode], [conc]  ):
  return [chemcode] + '\n' + str(round(float([conc]),1))
'''  
