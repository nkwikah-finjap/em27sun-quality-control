import unittest
import numpy as np
import pandas as pd
from analysis import dry_air_fraction,screen_xair,corrected_fraction,sza_correction,ROOT
class Tests(unittest.TestCase):
    def test_dry_air_fraction(self):self.assertAlmostEqual(dry_air_fraction([400e-6/.2095],[1.])[0],400.)
    def test_invalid_o2(self):
        with self.assertRaises(ValueError):dry_air_fraction([1],[0])
    def test_spike_rejected(self):
        f=pd.DataFrame({'UTC':pd.date_range('2020-01-01',periods=9,freq='10min'),'XAIR':[1.]*9})
        f.loc[4,'XAIR']=1.01
        got=screen_xair(f)
        self.assertFalse(got.loc[4,'accepted']);self.assertEqual(got.accepted.sum(),8)
    def test_days_not_mixed(self):
        f=pd.DataFrame({'UTC':pd.to_datetime(['2020-01-01 23:55','2020-01-02 00:05']),'XAIR':[1.,1.001]})
        self.assertTrue(screen_xair(f).accepted.all())
    def test_constant_reference(self):
        f=pd.DataFrame({'UTC':pd.date_range('2020-01-01',periods=5,freq='10min'),'XAIR':[1.]*5})
        self.assertTrue(screen_xair(f).accepted.all())
    def test_sza_reference_normalisation(self):self.assertAlmostEqual(float(sza_correction(60,[.1,.01,.001])),1.,places=7)
    def test_reference_reconstruction(self):
        f=pd.read_csv(ROOT/'data/sodankyla_reference.csv',skipinitialspace=True)
        for gas,column,tol in [('CO2','XCO2',.003),('CH4','XCH4',.00002),('CO','XCO',.000002)]:
            self.assertLess(float(np.max(np.abs(corrected_fraction(f,gas)-f[column]))),tol)
