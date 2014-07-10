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
    d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}
    cation = d['Ca']*Ca + d['Mg']*Mg + d['Na']*Na + d['K']*K
    anion = d['Cl']*Cl + d['HCO3']*HCO3 + d['CO3']*CO3 + d['SO4']*SO4 + d['NO3']+d['NO2']    
    bal = (cation-anion)/(cation + anion)*100
    return round(bal,2), cation, anion
   
# import stuff from table
arr = arcpy.da.TableToNumPyArray(infile, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg',arcpy.GetParameterAsText(1)), null_value=0)


nosamp = len(arr['Cl']) # Determine number of samples in file

# Multipliers to convert from mg/l to meq/l
d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}

# Convert to meq/L and assign to variables

Cl = arr['Cl']
Mg = arr['Mg']
K = arr['K']
Ca = arr['Ca']
Na = arr['Na']
HCO3 =arr['HCO3']
CO3 = arr['CO3']
NaK = np.array([Na[i]+K[i] for i in range(nosamp)])
SO4 = arr['SO4']


Cl_meq = np.array([arr['Cl'][i]*d['Cl'] for i in range(nosamp)])
Mg_meq = np.array([arr['Mg'][i]*d['Mg'] for i in range(nosamp)])
K_meq = np.array([arr['K'][i]*d['K'] for i in range(nosamp)])
Ca_meq = np.array([arr['Ca'][i]*d['Ca'] for i in range(nosamp)])
Na_meq = np.array([arr['Na'][i]*d['Na'] for i in range(nosamp)])
HCO3_meq = np.array([arr['HCO3'][i]*d['HCO3'] for i in range(nosamp)])
CO3_meq = np.array([arr['CO3'][i]*d['CO3'] for i in range(nosamp)])
NaK_meq = np.array([Na_meq[i]+K_meq[i] for i in range(nosamp)])
SO4_meq = np.array([arr['SO4'][i]*d['SO4'] for i in range(nosamp)])

# field having unique station identifier
stid = arr[arcpy.GetParameterAsText(1)]

NO3 = [0]*nosamp
NO2 = [0]*nosamp

#calculate charge balance for each sample
cb = np.array([chrgbal(Ca[i],Mg[i],Na[i],K[i],Cl[i],HCO3[i],CO3[i],SO4[i],NO3[i],NO2[i])[0] for i in range(nosamp)])
an = np.array([chrgbal(Ca[i],Mg[i],Na[i],K[i],Cl[i],HCO3[i],CO3[i],SO4[i],NO3[i],NO2[i])[2] for i in range(nosamp)])
cat = np.array([chrgbal(Ca[i],Mg[i],Na[i],K[i],Cl[i],HCO3[i],CO3[i],SO4[i],NO3[i],NO2[i])[1] for i in range(nosamp)])    
# looks for missing values, then fills them in if it can
for i in range(len(cb)):
    if cb[i]<0:
        if Ca[i]==0 and (Na[i] <> 0 and K[i] <> 0 and Mg[i] <> 0):
            Ca[i]= abs(cat[i]-an[i])/d['Ca']
        elif Mg[i]==0 and (Na[i] <> 0 and K[i] <> 0 and Ca[i] <> 0):
            Mg[i]= abs(cat[i]-an[i])/d['Mg']
        elif Na[i]==0 and (Ca[i] <> 0 and K[i] <> 0 and Mg[i] <> 0):
            Na[i]= abs(cat[i]-an[i])/d['Na']
        elif K[i]==0 and (Na[i] <> 0 and Ca[i] <> 0 and Mg[i] <> 0):
            K[i]= abs(cat[i]-an[i])/d['K']
        else:
            arcpy.AddMessage('No missing cations to make correct balance')
    elif cb[i]<0:
        if SO4[i]==0 and (Cl[i] <> 0 and HCO3[i] <> 0):
            SO4[i]=abs(cat[i]-an[i])/d['SO4']
        elif Cl[i]==0 and (SO4[i] <> 0 and HCO3[i] <> 0):
            Cl[i]=abs(cat[i]-an[i])/d['Cl']
        elif HCO3[i]==0 and (SO4[i] <> 0 and Cl[i] <> 0):
            HCO3[i]=abs(cat[i]-an[i])/d['HCO3']
        elif CO3[i]<>0 and (HCO3[i]<>0 and SO4[i] <> 0 and Cl[i] <> 0):
            CO3[i]=abs(cat[i]-an[i])/d['CO3']
        else:
            arcpy.AddMessage('No missing anions to make correct balance')
    else:
        arcpy.AddMessage('What do you expect me to do with this?!?!')

arcpy.AddMessage([len(cb)])




fields = [Na,K,Ca,Mg,Cl,HCO3,CO3,SO4,cb,stid]
inay = zip(*fields)
arcpy.AddMessage([inay, len(inay), len(inay[0])])
dts = {'names': ('Na_new','K_new','Ca_new','Mg_new','Cl_new','HCO3_new','CO3_new','SO4_new','chgbal','stid1'), 'formats' : (np.float64, np.float64, np.float64, np.float64, np.float64, np.float64,np.float64,np.float64,np.float64,'|S256')}
inarray = np.rec.fromrecords(inay,dtype = dts)


arcpy.da.ExtendTable(infile,arcpy.GetParameterAsText(1),inarray,'stid1')