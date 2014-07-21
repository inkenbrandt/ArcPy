# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 10:19:00 2014

@author: paulinkenbrandt
"""

import arcpy
import numpy as np

# input table having the fields Cl, HCO3, CO3, SO4, Na, K, Ca, Mg
infile = arcpy.GetParameterAsText(0)

# field having unique station identifier
stid = arcpy.GetParameterAsText(1)

# function to calculate charge balance
def chrgbal(Ca,Mg,Na,K,Cl,HCO3,CO3,SO4,NO3,NO2):
    # Multipliers to convert from mg/l to meq/l    
    d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}
    cation = d['Ca']*Ca + d['Mg']*Mg + d['Na']*Na + d['K']*K
    anion = d['Cl']*Cl + d['HCO3']*HCO3 + d['CO3']*CO3 + d['SO4']*SO4 + d['NO3']+d['NO2']    
    bal = (cation-anion)/(cation + anion)*100
    return round(bal,2), cation, anion
   
# import stuff from table; converts null values to zero for calculations
arr = arcpy.da.TableToNumPyArray(infile, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg','NO3',arcpy.GetParameterAsText(1)), null_value=0)


nosamp = len(arr['Cl']) # Determine number of samples in file

# Multipliers to convert from mg/l to meq/l
d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}


# import major ions as arrays
Cl = arr['Cl']
Mg = arr['Mg']
K = arr['K']
Ca = arr['Ca']
Na = arr['Na']
HCO3 =arr['HCO3']
CO3 = arr['CO3']
NaK = np.array([Na[i]+K[i] for i in range(nosamp)])
SO4 = arr['SO4']
NO3 = arr['NO3']

# field having unique station identifier
stid = arr[arcpy.GetParameterAsText(1)]

# create zero arrays for charge balance funtion

NO2 = [0]*nosamp

#calculate charge balance for each sample
cb = np.array([chrgbal(Ca[i],Mg[i],Na[i],K[i],Cl[i],HCO3[i],CO3[i],SO4[i],NO3[i],NO2[i])[0] for i in range(nosamp)])
# calculate anion total


#define field order to add to table
fields = [cb,stid]
#transpose array from columns to rows for proper tool input
inay = zip(*fields)

# define field names and data types for the array
dts = {'names': ('chargebal','stid1'), 'formats' : (np.float64,'|S256')}
inarray = np.rec.fromrecords(inay,dtype = dts)

# add fields to existing table by joining using the unique station id
arcpy.da.ExtendTable(infile,arcpy.GetParameterAsText(1),inarray,'stid1')