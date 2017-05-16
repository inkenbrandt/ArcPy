# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 16:00:30 2016

@author: paulinkenbrandt
"""

import numpy as np
import os
import scipy.special
import arcpy
from arcpy import env
#import math

#"CURRENT" #Set workspace as open map

#points = "sample"
#buff = 0.05
#outFeatureClass = "aatest3"
#pumpfield = "Q"
#
# Number of rows and columns together with origin and opposite corner 
# determine the size of each cell 
numRows =  '150'
numColumns = numRows
#S = 0.005
#T = 10000
#t = 100
#Inputs
points = arcpy.GetParameterAsText(0)
pumpfield = arcpy.GetParameterAsText(1)
buff = float(arcpy.GetParameterAsText(2))
t = float(arcpy.GetParameterAsText(3))
T = float(arcpy.GetParameterAsText(4)) #vertical multiplier
S = float(arcpy.GetParameterAsText(5)) #horizontal multiplier
cellSize = float(arcpy.GetParameterAsText(6))
fileplace = arcpy.GetParameterAsText(7)
outraster = arcpy.GetParameterAsText(8)

outFeatureClass = outraster + "points"
wellidfield = arcpy.Describe(points).OIDFieldName

env.workspace = fileplace


x, y = [], []
wellid = []
pump = []

for row in arcpy.da.SearchCursor(points, ["SHAPE@XY",wellidfield, pumpfield]):
    # Print x,y coordinates of each point feature
    x.append(row[0][0])
    y.append(row[0][1])    
    wellid.append(row[1])
    pump.append(row[2])


desc = arcpy.Describe(points)
spatialref = desc.spatialReference 

meanx = np.average(x)
meany = np.average(y)

miny = np.min(y)
minx = np.min(x)
maxy = np.max(y)
maxx = np.max(x)

# Set coordinate system of the output fishnet
env.outputCoordinateSystem = spatialref


# Set the origin of the fishnet
originCoordinate = str(minx-buff)+" "+str(miny-buff)

# Set the orientation
yAxisCoordinate = str(minx-buff)+" "+str(maxy+buff)


# Enter 0 for width and height - these values will be calculated by the tool
cellSizeWidth = '0'#str(cellSize*5) #'0'
cellSizeHeight = '0'#str(cellSize*5) #'0'

oppositeCoorner = str(maxx+buff)+" "+str(maxy+buff)

# Create a point label feature class 
labels = 'LABELS'

# Extent is set by origin and opposite corner - no need to use a template fc
templateExtent = points

# Each output cell will be a polygon
geometryType = 'POLYGON'

arcpy.CreateFishnet_management(outFeatureClass, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, templateExtent, geometryType)

grid_points = outFeatureClass+"_label"


with arcpy.da.InsertCursor(grid_points, ["SHAPE@XY"]) as cursor:
    # insert wells into grid
    for row in arcpy.da.SearchCursor(points, ["SHAPE@XY"]):
        xy = (row[0][0]+0.01,row[0][1]+0.01)
        cursor.insertRow([xy])


oid, gx, gy = [],[],[]

grid_oid =arcpy.Describe(grid_points).OIDFieldName

for row in arcpy.da.SearchCursor(grid_points, ["SHAPE@XY", grid_oid]):
    # Print x,y coordinates of each point feature
    #
    oid.append(row[1])
    gx.append(row[0][0])
    gy.append(row[0][1])    





# adapted from: https://github.com/Applied-Groundwater-Modeling-2nd-Ed/Chapter_3_problems-1
def well_function(u):
    return scipy.special.exp1(u)

def theis(Q, T, S, r, t):
    u = r ** 2 * S / 4. / T / t
    s = Q / 4. / np.pi / T * well_function(u)
    return s


hval = {}

for j in range(len(x)):  
    h = []
    for i in range(len(gx)):
        dist = np.sqrt(np.power((x[j]-gx[i]),2)+np.power((y[j]-gy[i]),2))
#        u = (np.power(dist,2)*S)/(4*T*t)
#        qpart = (pump[j]/(4.0*np.pi*T))
#        lnpart = (-0.5772-np.log(u)+u-(np.power(u,2)/(2.0*np.math.factorial(2)))+(np.power(u,3)/(3*np.math.factorial(3)))-(np.power(u,4)/(4*np.math.factorial(4))))

        h.append(theis(pump[j],T,S,dist,t))
        hval[wellid[j]] = h

alldraw = []
for i in range(len(gx)):
    sumdraw = 0    
    for j in range(len(x)):
        sumdraw = hval[wellid[j]][i] + sumdraw
    alldraw.append(sumdraw)

lines = [oid,gx,gy]
typefields = [('idfield','<i4'),('long', '<f8'),('lat', '<f8')]


for j in range(len(x)):
    lines.append(hval[wellid[j]])
    typefields.append(('dWl'+ str(wellid[j]), '<f8'))

lines.append(alldraw)
typefields.append(('alldraw','<f8'))
hlines = np.transpose(lines)

arrlines = []
for i in range(len(hlines)):
    arrlines.append(tuple(hlines[i]))
    
arr = np.asarray(arrlines,dtype=typefields)

arcpy.da.ExtendTable(grid_points, grid_oid, arr, 'idfield')

# Set local variables


# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Execute NaturalNeighbor
outNatNbr = arcpy.sa.NaturalNeighbor(grid_points, 'alldraw', cellSize)

# Save the output 
outNatNbr.save(outraster)
