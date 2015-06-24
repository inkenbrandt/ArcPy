# -*- coding: utf-8 -*-

""" Hydrochemistry: Constructs multiple Stiff plots

    Based on code by:
    B.M. van Breukelen <b.m.vanbreukelen@vu.nl>
    http://python.hydrology-amsterdam.nl/scripts/stiff_fill.py
    Created on Mon Jun 23 11:58:47 2014

    @author: paulinkenbrandt
"""
#Imports
import numpy as np
import os
import arcpy
from arcpy import env

env.workspace = "CURRENT" #Set workspace as open map

#Functions 
def getfilename(path):
    # this function extracts the file name without file path or extension
    return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]


#Inputs
resultstable = arcpy.GetParameterAsText(0)
meq = arcpy.GetParameterAsText(1)
stationidfield = arcpy.GetParameterAsText(2)
mv = int(arcpy.GetParameterAsText(3)) #vertical multiplier
mh = int(arcpy.GetParameterAsText(4)) #horizontal multiplier
fileplace = arcpy.GetParameterAsText(5)

fieldnames = [u'Na', u'K', u'Ca', u'Mg', u'Cl', u'HCO3', u'CO3', u'SO4']

fieldlist = [f.name for f in arcpy.ListFields(resultstable)] #get fields from input table

# Check to see if all parameters are in table; 
# Create empty datasets for the missing parameters
for field in fieldnames: #loop through each field
    if field not in fieldlist:
        arcpy.AddMessage(field + 'not one of the columns, adding field' )
        arcpy.AddField_management(resultstable, field, "FLOAT", 6, "", "", field, "NULLABLE")
        with arcpy.da.UpdateCursor(resultstable,[field]) as cursor:
            for row in cursor:
                row[0] = 0
            cursor.updateRow(row)

# Convert values in table fields to numpy arrays
# populate lists with values from the active table
StatId, Na, K, Ca, Mg, Cl, HCO3, CO3, SO4 = [],[],[],[],[],[],[],[],[]
with arcpy.da.UpdateCursor(resultstable,[stationidfield, 'Na', 'K', 'Ca', 'Mg', 'Cl', 'HCO3', 'CO3', 'SO4']) as cursor:
    for row in cursor:
        StatId.append(row[0])
        Na.append(row[1])
        K.append(row[2])
        Ca.append(row[3])
        Mg.append(row[4])
        Cl.append(row[5])
        HCO3.append(row[6])
        CO3.append(row[7])
        SO4.append(row[8])
        

x, y = [],[]
with arcpy.da.SearchCursor(resultstable, "SHAPE@XY") as cursor:
    for row in cursor:
        x.append(row[0][0])
        y.append(row[0][1]) 

# Get spatial reference of input dataset
desc = arcpy.Describe(resultstable)
spatialref = desc.spatialReference 

nosamp = len(Cl) # Determine number of samples in file

#Conversion factors from mg/L to meq/L
d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}

# Checkbox; If checked, meq/L conversion is done
if str(meq) == 'true':
    # Column Index for parameters
    # Convert ion concentrations in mg/L to meq/L
    Cl = [Cl[i]*d['Cl'] for i in range(nosamp)]
    Mg = [Mg[i]*d['Mg'] for i in range(nosamp)]
    K = [K[i]*d['K'] for i in range(nosamp)]
    Ca = [Ca[i]*d['Ca'] for i in range(nosamp)]
    Na = [Na[i]*d['Na'] for i in range(nosamp)]
    HCO3 = [HCO3[i]*d['HCO3'] for i in range(nosamp)]
    CO3 = [CO3[i]*d['CO3'] for i in range(nosamp)]
    NaK = [Na[i]+K[i] for i in range(nosamp)] #Already Converted above
    SO4 = [SO4[i]*d['SO4'] for i in range(nosamp)]
else:
    NaK = [Na[i]+K[i] for i in range(nosamp)]

#Sum Anions and Cations to determine charge balance
Anions = [Cl[i]+HCO3[i]+CO3[i]+SO4[i] for i in range(nosamp)]
Cations = [K[i]+Mg[i]+Na[i]+Ca[i] for i in range(nosamp)]
EC = [Anions[i]+Cations[i] for i in range(nosamp)]

# Generate x coordinates for stiff leaders based on concentration of major ions
## Cations
xNaK = [-1*NaK[i]*mh + float(x[i]) for i in range(nosamp)]
xCa = [-1*Ca[i]*mh + float(x[i]) for i in range(nosamp)]
xMg = [-1*Mg[i]*mh + float(x[i]) for i in range(nosamp)]
## Anions
xSO4 = [SO4[i]*mh + float(x[i]) for i in range(nosamp)]
xHCO3 = [HCO3[i]*mh + float(x[i]) for i in range(nosamp)]
xCl= [Cl[i]*mh + float(x[i]) for i in range(nosamp)]


# Generate x,y pairs; y coordinates for stiff leaders are independent of concentration
xy1 = [[xNaK[i], 1*10*mv + float(y[i]), 'NaK', NaK[i], StatId[i]] for i in range(nosamp)]
xy2 = [[xCa[i], 0*10*mv + float(y[i]), 'Ca', Ca[i], StatId[i]] for i in range(nosamp)]
xy3 = [[xMg[i], -1*10*mv + float(y[i]), 'Mg', Mg[i], StatId[i]] for i in range(nosamp)]
xy4 = [[xSO4[i], -1*10*mv + float(y[i]), 'SO4', SO4[i], StatId[i]] for i in range(nosamp)]
xy5 = [[xHCO3[i], 0*10*mv + float(y[i]), 'HCO3', HCO3[i], StatId[i]] for i in range(nosamp)]
xy6 = [[xCl[i], 1*10*mv + float(y[i]), 'Cl', Cl[i], StatId[i]] for i in range(nosamp)]
xy7 = [[xNaK[i], 1*10*mv + float(y[i]), 'NaK', NaK[i], StatId[i]] for i in range(nosamp)]

# list coordinate pairs to construct features
feature_info = [[xy6[i],xy5[i],xy4[i],xy3[i],xy2[i],xy1[i]] for i in range(nosamp)]

allpath = os.path.dirname(os.path.abspath(fileplace))

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
varlist = list(zip(*np.array(varlist)))


arcpy.AddMessage(str(len(varlist)) + " Features Plotted" )

# denote table field names and types
dts = {'names':('xfield', 'yfield', 'chemcode', 'conc', 'StationId'), 'formats': (np.float32, np.float32, '|S256', '|S256', '|S256')}

# join table data with table field names and types
inarray = np.rec.fromrecords(varlist, dtype=dts)


pointspath = allpath + '\\' + getfilename(fileplace) + "_points" + os.path.splitext(fileplace)[1]


temptab = arcpy.env.scratchGDB + os.path.sep + "temptab12"
templayer = arcpy.env.scratchGDB + os.path.sep + "templayers"


arcpy.da.NumPyArrayToTable(inarray,temptab)
arcpy.MakeXYEventLayer_management(temptab,"xfield","yfield",templayer,spatialref)
points = arcpy.CopyFeatures_management(templayer, pointspath)

arcpy.Delete_management(temptab)
arcpy.Delete_management(templayer)

 
# Create a Polygon object based on the array of points
# Append to the list of Polygon objects
polyFeatures = []
for i in feature_info:
    pointSet = []    
    for j in range(len(i)):
        pointSet.append(arcpy.Point(X = i[j][0],Y = i[j][1]))
    polyFeatures.append(arcpy.Polygon(arcpy.Array(pointSet),spatialref))
polygons = arcpy.CopyFeatures_management(polyFeatures, fileplace)

# Set the local parameters
inFeatures = polygons
joinField = arcpy.Describe(inFeatures).OIDFieldName
joinField2 = arcpy.Describe(resultstable).OIDFieldName
fieldList = ["land_use", "land_cover"]

# Join two feature classes by the OID field and only carry 
arcpy.JoinField_management (inFeatures, joinField, resultstable, joinField2)


# create a reference bar for the diagrams
lineFeatures = []
pointA = [[x[i], 1.1*10*mv + float(y[i])] for i in range(nosamp)]
pointB = [[x[i], -1.1*10*mv + float(y[i])] for i in range(nosamp)]
pointC = [[x[i]+5*mh, 1.1*10*mv + float(y[i])] for i in range(nosamp)]
pointD = [[x[i]-5*mh, 1.1*10*mv + float(y[i])] for i in range(nosamp)]

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


# Create Label Points for Labeling the Scale Bar
lab5 = [[x[i]+ 5*mh, 1.1*10*mv + float(y[i]), 5] for i in range(nosamp)]
lab4 = [[x[i]+ 4*mh, 1.1*10*mv + float(y[i]), 4] for i in range(nosamp)]
lab3 = [[x[i]+ 3*mh, 1.1*10*mv + float(y[i]), 3] for i in range(nosamp)]
lab2 = [[x[i]+ 2*mh, 1.1*10*mv + float(y[i]), 2] for i in range(nosamp)]
lab1 = [[x[i]+ 1*mh, 1.1*10*mv + float(y[i]), 1] for i in range(nosamp)]
lab0 =  [[x[i]-0*mh, 1.1*10*mv + float(y[i]), 0] for i in range(nosamp)]
lab1n = [[x[i]-1*mh, 1.1*10*mv + float(y[i]), -1] for i in range(nosamp)]
lab2n = [[x[i]-2*mh, 1.1*10*mv + float(y[i]), -2] for i in range(nosamp)]
lab3n = [[x[i]-3*mh, 1.1*10*mv + float(y[i]), -3] for i in range(nosamp)]
lab4n = [[x[i]-4*mh, 1.1*10*mv + float(y[i]), -4] for i in range(nosamp)]
lab5n = [[x[i]-5*mh, 1.1*10*mv + float(y[i]), -5] for i in range(nosamp)]

barLabels = [[lab5[i], lab4[i], lab3[i], lab2[i], lab1[i], lab0[i], lab1n[i], lab2n[i], lab3n[i], lab4n[i], lab5n[i]] for i in range(nosamp)]

labelpointspath = os.path.dirname(os.path.abspath(fileplace))
labelpointsname = getfilename(fileplace) + "_lbpnts" + os.path.splitext(fileplace)[1]

sclpnts = arcpy.CreateFeatureclass_management(allpath,labelpointsname,"POINT",points, "DISABLED","DISABLED", spatialref)

cursor = arcpy.da.InsertCursor(sclpnts,['SHAPE@X','SHAPE@Y','conc'])

for i in barLabels:
    for j in range(len(i)):
        cursor.insertRow([i[j][0],i[j][1],i[j][2]])

del cursor
# get the map document
mxd = arcpy.mapping.MapDocument("CURRENT")

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd)[0]

layer = arcpy.mapping.Layer(linespath)
layer1 = arcpy.mapping.Layer(pointspath)
layer2 = arcpy.mapping.Layer(allpath+"\\"+labelpointsname)
arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, layer1, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, layer2, "AUTO_ARRANGE")


arcpy.Delete_management(layer)
arcpy.Delete_management(layer1)

'''
Advanced Expression for labels (python):

def FindLabel ( [chemcode], [conc]  ):
  return [chemcode] + '\n' + str(round(float([conc]),1))
'''  
