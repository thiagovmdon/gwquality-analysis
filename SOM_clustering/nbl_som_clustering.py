# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 10:20:04 2023

@author: nascimth
"""

import glob, os
import pandas as pd
import numpy as np

#%% Get the names of the compounds based on the .xlsx filenames:
    
def names_compounds(filenames):
    
    namescompounds = [''] * len(filenames)
    i = 0
    for filename in filenames:
        namecompound = os.path.basename(filename)
        namecompound = namecompound.replace(".xlsx", "")
        namescompounds[i] = namecompound
        i = i + 1

    compounds = namescompounds
    return compounds

#%% NBL computation:    
def compute_NBL(filenames, wells_infos):
    
    compounds = names_compounds(filenames)
    
    tablemedian = pd.DataFrame(index = compounds, columns = wells_infos.index) # Empty table for the median

    i = 0

    for filename in filenames:
    
        data=pd.read_excel(filename)
        data.set_index('date', inplace=True)
        datamon=data.resample('M').median()
    
        descriptors = datamon.describe(percentiles=[.10, .25, .5, .75, .90, .95])
    
        tablemedian.loc[compounds[i]] = descriptors.loc["50%"]
    
        i = i+1


    tablemedianT = tablemedian.T

    
    # Now we select only the wells which have median NO3 concentration below 10 mg/L
    indexmedian = tablemedianT["NO3"] <= 10

    descriptorsex = pd.DataFrame(data = datamon.loc[:,indexmedian].describe(percentiles=[.10, .25, .5, .75, .90, .95]).T.mean())
    tablebaseline = pd.DataFrame(index = descriptorsex.index, columns = compounds)
    
    
    j = 0

    for filename in filenames:
    
        data=pd.read_excel(filename)
        data.set_index('date', inplace=True)
        datamon=data.resample('M').median()
    
        descriptors = pd.DataFrame(data = datamon.loc[:,indexmedian].describe(percentiles=[.10, .25, .5, .75, .90, .95]).T.mean())
    
        tablebaseline.loc[:, compounds[j]] = descriptors.values
    
        j = j + 1
    max_nbl = tablebaseline.loc["90%"]
    return tablebaseline, max_nbl

#%% Build a dataframe only with the compounds to be clustered:
def compounds_forclustering(filenames, compounds_used, 
                            start_range = '2016', end_range = '2021'):
    
    # The data must have one column called date:
    i = 0
    for compound in compounds_used:
    
        # First we read the compound file:
        filename = "dataset/" + compound + ".xlsx"
        data = pd.read_excel(filename)
    
    
        # It is better to use the water year, istead of the calendar year for the medians computation:
        # Here the water year starts in October (10)
        data['water_year'] = data.date.dt.year.where(data.date.dt.month < 10, data.date.dt.year + 1)
        data.set_index('date', inplace=True)
        data_year_data = data.groupby('water_year', dropna=False).median()
        med2021 = data_year_data.loc[start_range:end_range].median()
    
        # Now we can fill a dataframe with our seelcted data
        if i == 0:
            dataforcluster = pd.DataFrame(index = med2021.index, columns = ['NO3', 'SO4', 'Cl'])
            dataforcluster.loc[:, compound] = med2021
        else:
            dataforcluster.loc[:, compound] = med2021
    
        i = i + 1
    
    return dataforcluster