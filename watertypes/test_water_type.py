import unittest

from wtypes import water_type_classification

import pandas as pd
import numpy as np
test_data = pd.read_csv('test_data.csv')

class TestWaterType(unittest.TestCase):
    ## Test for water type classification based on published data: get source
    def test_water_type_success(self):
        wtype = water_type_classification(test_data, unit='mmol/L')
        wtype_incompatible = wtype.loc[~(wtype['Code']==test_data['W-type'])]
        actual = len(wtype_incompatible.index)
        expected = 0
        self.assertEqual(actual, expected)
