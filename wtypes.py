# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 12:42:52 2022

@author: User
"""

import glob, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy
import math
import datetime
plt.close("all")

os.chdir(r'C:\Users\User\OneDrive\ERASMUS\4_Thesis\python\quality\water-types')
print("Current Working Directory " , os.getcwd())

comp = ["Na",	"K",	"Mg",	"Ca",	"NH4",	"Cl",	"HCO3",	"SO4",	"NO3",	"Fe2", "Mn2"]
molarw = [22.989,	39.098,	24.305,	40.078,	18.039,	35.453,	61.016,	96.062,	62.004,	55.847,	54.931]
molarnum = [1,	1,	2,	2,	1,	1,	1,	2,	1,	2,	2]


comptable = pd.DataFrame(index = comp)
comptable["mw_mg_mmol"] = molarw
comptable["mnum"] = molarnum

path =r'C:\Users\User\OneDrive\ERASMUS\4_Thesis\python\quality\water-types\quality_data.xlsx'
q_data=pd.read_excel(path)
q_data.set_index('Sample', inplace=True)


q_datammol_l = q_data

for i in (range((q_data.shape[1]-1))):
    q_datammol_l.iloc[:,i+1] = q_data.iloc[:,i+1]/comptable["mw_mg_mmol"].loc[q_data.columns[i+1]]

q_datameq_l = q_data
    
for i in (range((q_data.shape[1]-1))):
    q_datameq_l.iloc[:,i+1] = q_datammol_l.iloc[:,i+1]*comptable["mnum"].loc[q_data.columns[i+1]]



wtypes = pd.DataFrame(q_data["pH"])
wtypes["MCation"] = "-999"
wtypes["MAnion"] = "-999"
wtypes["Salinity"] = "-999"
wtypes["Alkalinity"] = "-999"
wtypes["BEX"] = "-999"
 
for i in range(len(q_data)):
    pH = q_datameq_l.iloc[i].loc["pH"]
    Na = q_datameq_l.iloc[i].loc["Na"]
    K = q_datameq_l.iloc[i].loc["K"]
    Mg = q_datameq_l.iloc[i].loc["Mg"]
    Ca = q_datameq_l.iloc[i].loc["Ca"]
    NH4 = q_datameq_l.iloc[i].loc["NH4"]
    Cl = q_datameq_l.iloc[i].loc["Cl"]
    HCO3 = q_datameq_l.iloc[i].loc["HCO3"]
    SO4 = q_datameq_l.iloc[i].loc["SO4"]
    NO3 = q_datameq_l.iloc[i].loc["NO3"]
    Fe = q_datameq_l.iloc[i].loc["Fe2"]
    Mn2 = q_datameq_l.iloc[i].loc["Mn2"]
    Al = 0
    CO3 = 0
    NO2 = 0
    
    #Major cation:
    if (Na + K) + NH4 > Ca + Mg + 10**(-pH)*1000 + Fe + Mn2:
        if NH4 > (Na+K):
            wtypes["MCation"].iloc[i] = "NH4"
        elif Na > K:
            wtypes["MCation"].iloc[i]  = "Na"
        else:
            wtypes["MCation"].iloc[i]  = "K"
    elif (Ca + Mg) > (10**(-pH)*1000 + Fe + Mn2):
        if Ca > Mg:
            wtypes["MCation"].iloc[i]  = "Ca"
        else:
            wtypes["MCation"].iloc[i]  = "Mg"
    elif 10**(-pH)*1000 > (Fe + Mn2): 
        if Al > 10**(-pH)*1000:
            wtypes["MCation"].iloc[i]  = "Al"
        else:
            wtypes["MCation"].iloc[i]  = "H"
    else:
        if Fe > Mn2:
            wtypes["MCation"].iloc[i]  = "Fe2"
        else:
            wtypes["MCation"].iloc[i]  = "Mn2"
    
    # Major anion:         
    if Cl > (HCO3+SO4+NO3+NO2+CO3):
        wtypes["MAnion"].iloc[i] = "Cl"
    else:
        
        if HCO3 + CO3 > (Cl + SO4 + NO3 + NO2):
            
            if HCO3 > CO3:
                wtypes["MAnion"].iloc[i] = "HCO3"
                
            else:
                
                wtypes["MAnion"].iloc[i] = "CO3"
        elif (SO4 + NO3 + NO2) > (HCO3 + CO3 + Cl):
            
            if SO4 > (NO3 + NO2):
                wtypes["MAnion"].iloc[i] = "SO4"
            else:
                wtypes["MAnion"].iloc[i] = "NO3"
        else:
            wtypes["MAnion"].iloc[i] = "MIX"
         
            
        
    # Salinity:
    if Cl >= 564.127:
        wtypes["Salinity"].iloc[i] = "H"
    else:
            
        if 282.064 <= Cl < 564.127:
            wtypes["Salinity"].iloc[i] = "s"
        elif 28.206 <= Cl < 282.064:
            wtypes["Salinity"].iloc[i] = "b"            
        elif 8.462 <= Cl < 28.206:
            wtypes["Salinity"].iloc[i] = "B"                   
        elif 4.231 <= Cl < 8.462:
            wtypes["Salinity"].iloc[i] = "f" 
        elif 0.846 <= Cl < 4.231:
            wtypes["Salinity"].iloc[i] = "F" 
        elif 0.141 <= Cl < 0.846:
            wtypes["Salinity"].iloc[i] = "g" 
        else:
            wtypes["Salinity"].iloc[i] = "G" 
            
    # Alkalinity:
    if HCO3 < 0.5:
        wtypes["Alkalinity"].iloc[i] = "*"
    else:
        if 0.5 < HCO3 <= 1:
            wtypes["Alkalinity"].iloc[i] = "0"
        elif Cl >= 512:
            wtypes["Alkalinity"].iloc[i] = "9"            
        else:
            wtypes["Alkalinity"].iloc[i] = str(int(np.log10(HCO3)/np.log10(2) + 1))
   
    # BEX:
    if (Na + K + Mg) - 1.0716*Cl < -(0.5 + 0.02*Cl):
        wtypes["BEX"].iloc[i] = "-"
    else:
        if (Na + K + Mg) - 1.0716*Cl > (0.5 + 0.02*Cl):
            wtypes["BEX"].iloc[i] = "+"
        else:
            wtypes["BEX"].iloc[i] = ""

# Final code:
wtypes["Code"] = wtypes["Salinity"] + wtypes["Alkalinity"] + wtypes["MCation"] + wtypes["MAnion"] + wtypes["BEX"]

# Saving the table in xlsx:
dataname="water_facies"
path_output=r'C:\Users\User\OneDrive\ERASMUS\4_Thesis\python\quality\water-types'   
wtypes.to_excel(path_output + '/'+str(dataname)+'.xlsx')
