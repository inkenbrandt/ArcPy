# -*- coding: utf-8 -*-

""" Hydrochemistry: Constructs multiple Stiff plots

    Based on code by:
    B.M. van Breukelen <b.m.vanbreukelen@vu.nl>
    http://python.hydrology-amsterdam.nl/scripts/stiff_fill.py
    Created on Mon Jun 23 11:58:47 2014

    @author: paulinkenbrandt
"""


from pylab import * 
import os
import arcpy



path = os.getcwd() 


input = arcpy.GetParameterAsText(0)


arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3', 'CO3', 'SO4', 'Na', 'K', 'Ca', 'Mg', 'NO3', 'Cond', 'StationId',arcpy.GetParameterAsText(1), arcpy.GetParameterAsText(2)),null_value=0)

d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}

x = arr[arcpy.GetParameterAsText(1)]
y = arr[arcpy.GetParameterAsText(2)]
m = float(arcpy.GetParameterAsText(3)) #multiplier
c = float(arcpy.GetParameterAsText(4)) #coodinate type 

nosamp = len(arr['Cl']) # Determine number of samples in file


# Column Index for parameters
# Convert to meq/L
Cl = [arr['Cl'][i]*d['Cl'] for i in range(nosamp)]
Mg = [arr['Mg'][i]*d['Mg'] for i in range(nosamp)]
K = [arr['K'][i]*d['K'] for i in range(nosamp)]
Ca = [arr['Ca'][i]*d['Ca'] for i in range(nosamp)]
Na = [arr['Na'][i]*d['Na'] for i in range(nosamp)]
HCO3 = [arr['HCO3'][i]*d['HCO3'] for i in range(nosamp)]
CO3 = [arr['CO3'][i]*d['CO3'] for i in range(nosamp)]
NaK = [Na[i]+K[i] for i in range(nosamp)]
SO4 = [arr['SO4'][i]*d['SO4'] for i in range(nosamp)]
NO3 = [arr['NO3'][i]*d['NO3'] for i in range(nosamp)]

StatId = arr['StationId']


Anions = [Cl[i]+HCO3[i]+CO3[i]+SO4[i] for i in range(nosamp)]
Cations = [K[i]+Mg[i]+Na[i]+Ca[i] for i in range(nosamp)]
EC = [Anions[i]+Cations[i] for i in range(nosamp)]




xNaK = [-1*NaK[i]*c*m + float(x[i]) for i in range(nosamp)]
xCa = [-1*Ca[i]*c*m + float(x[i]) for i in range(nosamp)]
xMg = [-1*Mg[i]*c*m + float(x[i]) for i in range(nosamp)]
xSO4 = [SO4[i]*c*m + float(x[i]) for i in range(nosamp)]
xHCO3 = [HCO3[i]*c*m + float(x[i]) for i in range(nosamp)]
xCl= [Cl[i]*c*m + float(x[i]) for i in range(nosamp)]

cy = c*10

xy1 = []
xy2 = []
xy3 = []
xy4 = []
xy5 = []
xy6 = []
xy7 = []

feature_info = []
feature_info2 = []
feature_info3 = []

for i in range(nosamp):
    xy1.append([xNaK[i], 1*cy*m + float(y[i])])
    xy2.append([xCa[i], 0*cy*m + float(y[i])])
    xy3.append([xMg[i], -1*cy*m + float(y[i])])
    xy4.append([xSO4[i], -1*cy*m + float(y[i])])
    xy5.append([xHCO3[i], 0*cy*m + float(y[i])])
    xy6.append([xCl[i], 1*cy*m + float(y[i])]) 
    xy7.append([xNaK[i], 1*cy*m + float(y[i])])
    feature_info.append([xy6[i],xy5[i],xy4[i],xy3[i],xy2[i],xy1[i]])

    # A list of features and coordinate pairs
    



spatialref = arcpy.GetParameterAsText(5)
    
# A list that will hold each of the Polygon objects
features = []

featuresp = []
featureln = []

for feature in feature_info:
    # Create a Polygon object based on the array of points
    # Append to the list of Polygon objects
    features.append(
        arcpy.Polygon(
            arcpy.Array([arcpy.Point(*coords) for coords in feature]),spatialref))


pnt = arcpy.Point()
for i in feature_info:
    for j in range(len(i)):    
        pnt.X = i[j][0]
        pnt.Y = i[j][1]
        featuresp.append(arcpy.PointGeometry(pnt,spatialref))
#
#ary = arcpy.Array()
#
#for feature in feature_info:
#    for x,y in feature:
#        pnt = arcpy.Point(x,y)        
#        ary.add(pnt)
#    features.append(arcpy.Polygon(ary,spatialref))

# Persist a copy of the Polyline objects using CopyFeatures
feature_class = arcpy.CopyFeatures_management(features, arcpy.GetParameterAsText(6))



arcpy.CopyFeatures_management(featuresp, arcpy.GetParameterAsText(7))
#arcpy.CopyFeatures_management(featuresp, arcpy.GetParameterAsText(6))
#    # Stiff plots with color depending on water type
#    h1=fill(x, y, 'r')
#    
#    plot([0,0], [1,3],'b')
#    
#    # NO3 plotted as extra circle
#    #h6=plot(5.*NO3[sID], 1, 'yo', ms=markersize)
#    
#    # SI Calcite plotted as extra square
#    #h7=plot(2*obs[sID, 9], 2, 'ks', ms=markersize)
#
#    # Add legend at one selected stiff diagram    
#    #if sID == 1:
#    text(-4.5,2.9,'Na+K')
#    text(-4.5,1.9,'Ca')
#    text(-4.5,0.9,'Mg')
#    text(2.5,2.9,'Cl')
#    text(2.5,1.9,'HCO3')
#    text(2.5,0.9,'SO4')
#    xlabel('(meq/L)')
#    xticks(xtickpositions)
#    xticklabels=('5','3','1','0','-1','-3','-5')
#    title("{s}\n{v}".format(s=StatId[sID],v=geo[sID]),size = 10)
#    ylim(0.8, 3.2)
#    xlim(-5.2, 5.2)
#    xticks(xtickpositions)
#    setp(gca(), yticks=[], yticklabels=[])
#
## adjust position subplots
#subplots_adjust(left=0.05, bottom=0.1, right=0.95, top=0.95, wspace=0.2, hspace=0.30)
#savefig(arcpy.GetParameterAsText(2))
#
#
#close()
