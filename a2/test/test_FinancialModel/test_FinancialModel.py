from src.FinancialModels.FinancialModel import MertonModel, CreditMetricModel
from src.FinancialEntity.Company import StockCompany
from src.FinancialInstruments.Stock import DatedStock
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
TOL = 1e-6


class TestMerton:
    def test_goodrich(self):
        gr_stock = DatedStock(117540000,"01-03-2003",17.76)
        gr_stock.volatility = 0.4959
        gr = StockCompany("Goodrich", [], gr_stock, 0, 0)
        gr.debt = 4.759
        gr.assets = 6.826
        gr.rates = BinarySortedDict()
        gr.rates[365] = 0.0317
        gr.print_stats(365)

        mm = MertonModel(gr)
        vol = mm.find_asset_volatility(365, "fixed")
        assert abs(vol - 0.15108448114640016) < TOL