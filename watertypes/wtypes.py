# -*- coding: utf-8 -*-
"""
Refactoring of the script of Thiago Medeiros (thiagovmdon)
"""
import pandas as pd
import numpy as np
import os
import numpy
from utils import convert_units, parameter_error, unit_error


comp = ["Na", "K", "Mg", "Ca", "NH4", "Cl", "HCO3", "CO3", "SO4", "NO3", 'NO2', "Fe", "Mn", 'Al']
PARS = set(comp+['pH'])




def water_type_classification(dataset: pd.pandas.core.frame.DataFrame, unit: str) -> pd.pandas.core.frame.DataFrame:
    '''Function to calculate water type for samples organized in a DataFrame:

    Inputs
    ------------------
    dataset[n x y]: dataframe with a sample in each row, and columns with results for ions used in the classification
        Ions must be named as their chemical formula, without charge, examples: NO3,Fe,Mg,Ca,K,Cl
    unit: concentration unit for the chemical results, either mg/L, mmol/L or meq/L are accepted

    Returns
    --------------------
    pandas.DataFrame [n x 7] with columns:
        'MCation': Major cátion Classification
        'MAnion': Major anion classification
        'Salinity': Salinity classification
        'Alkalinity': Alkalinity Classification
        'BEX': Base exchange (bex) Classification
        'Code': Water-type code
    '''
    ### Checking for dataset consistency:
    parameter_error(dataset, 'Water-Type Classification', parameters = PARS)
    unit_error(unit)


    ### Defining inner functions
    """
    Functions that calculate the water classification for:
    Major cations: mcation, Major anions: manion, salinity: salinity, alkalinity: alkalinity, BEX: bex
    """
    #Major cation:
    def mcation(Na,K,NH4,Ca,Mg,pH,Fe,Mn,Al):
        if (Na + K) + NH4 > Ca + Mg + 10**(-pH)*1000 + Fe + Mn + Al:
            if NH4 > (Na+K):
                mcat_class = "NH4"
            elif Na > K:
                mcat_class  = "Na"
            else:
                mcat_class  = "K"
        elif (Ca + Mg) > (10**(-pH)*1000 + Fe + Mn+Al):
            if Ca > Mg:
                mcat_class  = "Ca"
            else:
                mcat_class  = "Mg"
        elif (10**(-pH)*1000+Al) > (Fe + Mn):
            if Al > 10**(-pH)*1000:
                mcat_class  = "Al"
            else:
                mcat_class  = "H"
        else:
            if Fe > Mn:
                mcat_class  = "Fe"
            else:
                mcat_class  = "Mn"
        return mcat_class


    # Major anion:
    def manion(HCO3,SO4,Cl,NO3,NO2,CO3):
        anion_sum = np.sum([HCO3,SO4,Cl,NO3,NO2,CO3])
        if Cl >= 0.5*anion_sum:
            manion_class = "Cl"
        elif (HCO3 + CO3) >= 0.5*anion_sum:
            if HCO3 > CO3:
                manion_class = "HCO3"
            else:
                manion_class = "CO3"
        elif (SO4 + NO3 + NO2) >= 0.5*anion_sum:
            if SO4 > (NO3 + NO2):
                manion_class = "SO4"
            else:
                manion_class = "NO3"
        else:
            manion_class = "MIX"
        return manion_class



    def salinity(Cl):
        # Salinity:
        if Cl >= 564.127:
            salin = "H"
        else:
            if 282.064 <= Cl < 564.127:
                salin = "S"
            elif 28.206 <= Cl < 282.064:
                salin = "b"
            elif 8.462 <= Cl < 28.206:
                salin = "B"
            elif 4.231 <= Cl < 8.462:
                salin = "f"
            elif 0.846 <= Cl < 4.231:
                salin = "F"
            elif 0.141 <= Cl < 0.846:
                salin = "g"
            else:
                salin = "G"
        return salin

    # Alkalinity:
    def alkalinity(HCO3,CO3):
        alk = HCO3 + CO3
        if alk <= 0.5:
            alk_class = "*"
        elif alk <= 1.:
            alk_class = '0'
        elif alk <= 2.:
            alk_class = '1'
        elif alk <= 4.:
            alk_class = '2'
        elif alk <= 8.:
            alk_class = '3'
        elif alk <= 16.:
            alk_class = '4'
        elif alk <= 32.:
            alk_class = '5'
        elif alk <= 64.:
            alk_class = '6'
        else:
            alk_class = '7'
        return alk_class

    # BEX:
    def bex(Na,K,Mg,Cl):
        if (Na + K + Mg) - 1.0716*Cl < -(0.5 + 0.02*Cl):
            bx = "-"
        else:
            if (Na + K + Mg) - 1.0716*Cl > (0.5 + 0.02*Cl):
                bx = "+"
            else:
                bx = ""
        return bx

    #### Converting dataset:
    meqL = convert_units(dataset, unit, parameters = comp)


    wtypes = pd.DataFrame(np.empty((meqL.shape[0],5)), columns = ['MCation','MAnion','Salinity','Alkalinity','BEX'])

    pH = dataset["pH"]
    Na = meqL["Na"]
    K = meqL["K"]
    Mg = meqL["Mg"]
    Ca = meqL["Ca"]
    NH4 = meqL["NH4"]
    Cl = meqL["Cl"]
    HCO3 = meqL["HCO3"]
    SO4 = meqL["SO4"]
    NO3 = meqL["NO3"]
    Fe = meqL["Fe"]
    Mn = meqL["Mn"]
    Al = meqL["Al"]
    CO3 = meqL["CO3"]
    NO2 = meqL["NO2"]

    mcation = np.vectorize(mcation)
    wtypes['MCation'] = mcation(Na,K,NH4,Ca,Mg,pH,Fe,Mn,Al)
    manion = np.vectorize(manion)
    wtypes['MAnion'] = manion(HCO3,SO4,Cl,NO3,NO2,CO3)
    salinity = np.vectorize(salinity)
    wtypes['Salinity'] = salinity(Cl)
    alkalinity = np.vectorize(alkalinity)
    wtypes['Alkalinity'] = alkalinity(HCO3,CO3)
    bex = np.vectorize(bex)
    wtypes['BEX'] = bex(Na,K,Mg,Cl)

    # Final code:
    wtypes["Code"] = wtypes['Salinity'] + wtypes["Alkalinity"] +'-'+ wtypes["MCation"] + wtypes["MAnion"] + wtypes["BEX"]

    return wtypes

def pollution_index(dataset: pd.pandas.core.frame.DataFrame, unit: str, sub_indices = ['A','B']) -> pd.pandas.core.frame.DataFrame:

    pars = []
    ### Checking for dataset consistency:
    if ('A' in sub_indices):
        pars = pars + ['pH']
    if ('B' in sub_indices):
        pars = pars + ['NO3', 'SO4', 'Cl']

    parameter_error(dataset, 'Pollution Classification', parameters = set(pars))
    unit_error(unit)
    if len(sub_indices) < 2:
        raise ValueError('Minimum number of sub_indices is 2')

    #### Converting dataset:
    comp = ['NO3', 'SO4', 'Cl']
    meqL = convert_units(dataset, unit, parameters = comp)


    wtypes = pd.DataFrame(np.empty((meqL.shape[0],len(sub_indices))), columns = sub_indices)

    pH = dataset["pH"]
    Cl = meqL["Cl"]
    SO4 = meqL["SO4"]
    NO3 = meqL["NO3"]

    #Calculation of A:
    if ('A' in sub_indices):
        A = 1.333*np.abs(pH-7)
        wtypes['A'] = A

    if ('B' in sub_indices):
        SO4_c = 0.67*(SO4/2 - 0.0232*Cl)
        SO4_c[SO4_c < 0] = 0
        B = np.log(10*(NO3+SO4_c))/np.log(2)
        B[B < 0] = 0
        wtypes['B'] = B

    # Calculating POLIN Index:
    wtypes['POLIN'] = wtypes.sum(axis='columns')/(wtypes.shape[1]-wtypes.shape[1]/6)
    return wtypes

if __name__ == "__main__":

    test = pd.read_csv('test_data.csv')
    wtype = water_type_classification(test, unit='mmol/L')

    print('Incompatible water type classes:')
    print(wtype.loc[~(wtype['Code']==test['W-type'])],test.loc[~(wtype['Code']==test['W-type']),'W-type'])
