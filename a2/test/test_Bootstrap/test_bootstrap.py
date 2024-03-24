import os
import sys
test_directory = os.path.dirname(__file__)
src_dir = os.path.join(test_directory, '..', '..')
sys.path.append(src_dir)
import numpy as np
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
from src.FinancialInstruments.Bond import DatedBond
from src.Bootstrapper.bootstrap import bootstrap

TOL = 1e-6


class TestBootstrap:
    def test_single(self):
        bonds = [DatedBond("A1", 100.0, 0.01, "01-01-1970", 110.0, 365, [])]
        result = bootstrap(bonds)
        a = -np.log([110.0/100.0, 365/365])[0]
        expected = BinarySortedDict()
        expected[365] = a

        result_x, result_y = result.sorted_key_vals()
        exp_x, exp_y = result.sorted_key_vals()
        assert len(result_x) == len(exp_x)
        for i in range(len(result_x)):
            assert abs(result_x[i] - exp_x[i]) < TOL
            assert abs(result_y[i] - exp_y[i]) < TOL
    
    def test_two_period(self):
        pass