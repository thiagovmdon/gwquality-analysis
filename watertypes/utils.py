import pandas as pd
import numpy as np
from ions import ions_WEIGHT,ions_CHARGE

ALLOWED_UNITS = ['mg/L', 'mmol/L', 'meq/L']

### UNIT CONVERSION TO MEQ/L

def convert_units(df: pd.pandas.core.frame.DataFrame, unit: str, parameters=['Ca', 'Mg', 'Na', 'K', 'HCO3', 'CO3', 'Cl', 'SO4']) -> pd.pandas.core.frame.DataFrame:
    """
    To be used internally
    Convert major ions from allowed units to meq/L
    Returns dataframe of the parameters converted to meqL.
    """
    # Convert unit if needed
    df = df[parameters]
    df.reset_index(inplace=True)
    gmol = pd.DataFrame(ions_WEIGHT, index = [0])
    gmol = gmol[parameters]
    gmol = pd.DataFrame(np.repeat(gmol.values, df.shape[0], axis=0), columns=gmol.columns)
    eqmol = pd.DataFrame(ions_CHARGE, index = [0])
    eqmol = eqmol[parameters]
    eqmol = pd.DataFrame(np.repeat(eqmol.values, df.shape[0], axis=0), columns=eqmol.columns)

    if unit == 'mg/L':
        
        meqL = (df.div(gmol,axis=1)).mul(eqmol.abs(),axis=1)

    elif unit == 'mmol/L':

        meqL = df.mul(np.abs(eqmol),axis=1)

    elif unit == 'meq/L':

        meqL = df

    return meqL

### ERROR CHECKING:

def parameter_error(df: pd.pandas.core.frame.DataFrame, plot_type: str, parameters: set={'Ca','Mg','Na','K','HCO3','CO3','Cl','SO4'}) -> None:
    if not parameters.issubset(df.columns):
        raise RuntimeError(f"""{plot_type} diagram requires geochemical parameters:
            {parameters}.
            Confirm that these parameters are provided in the input file.""")

def unit_error(unit: str) -> None:
    if unit not in ALLOWED_UNITS:
        raise RuntimeError(f"""
        Currently only {ALLOWED_UNITS} are supported.
        Convert the unit manually if needed.""")
