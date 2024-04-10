from src.FinancialModels.FinancialModel import MertonModel
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialInstruments.Stock import DatedStock
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
TOL = 1e-6


class TestMerton:
    def test_goodrich(self):
        gr_stock = DatedStock(117540000,"01-03-2003",17.76)
        gr_stock.volatility = 0.4959
        assets = 6.826
        equity = (117540000 * 17.76)/1e9
        debt =  4.759
        gr = StockCompany("Goodrich", [], gr_stock, assets, equity, debt)
        gov = Company("Government", [])
        gov.rates = BinarySortedDict()
        gov.rates[365] = 0.0317

        mm = MertonModel(gov, gr)
        V, vol = mm.find_asset_vals()
        assert abs(vol - 0.15108448114640016) < TOL