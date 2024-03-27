from src.FinancialInstruments.Bond import DatedBond, sort_bond_list
import numpy as np

class TestDatedBond:
    def test_sort(self):
        b1 = DatedBond("B1", 100, 2.5, np.datetime64("2005-02-25"), 110, 12, [6])
        b2 = DatedBond("B2", 100, 2.5, np.datetime64("2007-02-25"), 110, 12, [6])
        b3 = DatedBond("B3", 100, 2.5, np.datetime64("2008-02-25"), 110, 12, [6])
        b4 = DatedBond("B4", 100, 2.5, np.datetime64("2009-02-25"), 110, 12, [6])
        lst = [b4, b1, b3, b2]
        expected = [b1, b2, b3, b4]
        actual = sort_bond_list(lst)
        for i in range(4):
            assert actual[i] == expected[i]