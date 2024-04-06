from src.Bootstrapper.bootstrap import bootstrap
from src.FinancialInstruments.Bond import get_dated_bonds, process_bond_data
from src.FinancialInstruments.Stock import DatedStock
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialModels.FinancialModel import MertonModel, CreditMetricModel
import numpy as np


def merton_experiment():
    bond_data = process_bond_data("data/gov_bond_info.csv", "data/gov_bond_prices.csv", "data/gov_bond_processed.csv")
    bonds = get_dated_bonds(bond_data)
    stock = DatedStock(1408257000, "03-26-2024", 135.16)
    stock.compute_volatility("data/rbc_stock_prices.csv")
    #rbc = Company("RBC", stock, bonds, 1857.917, 1241.168)
    rbc = StockCompany("RBC", bonds, stock, 1857.917, 1857.917)
    rbc.equity = 1500
    rbc.get_rates()
    rbc.print_stats()
    mm = MertonModel(rbc)
    av = mm.find_asset_volatility(method="fixed")
    print(f"Asset volatility = {av*100}%")
    periods = [365*i for i in range(1, 10)]
    default_probs = mm.get_default_probs(periods)
    print([str(x*100)+"%" for x in default_probs])



def credit_metrics_experiment():
    gov_bonds = get_dated_bonds(process_bond_data("data/gov_bond_info.csv",
                                                  "data/gov_bond_prices.csv"))
    rbc_bonds = get_dated_bonds(process_bond_data("data/rbc_bond_info.csv",
                                                  "data/rbc_bond_prices.csv"))
    canada = Company("Canada", gov_bonds)
    rbc = Company("RBC", rbc_bonds)
    rbc.set_recovery_rate(0.5)

    cm = CreditMetricModel(canada, rbc)
    cm.setup()
    periods = np.array([1, 2, 3, 4, 5]) * 365
    default_probs = cm.get_default_probs(periods)
    print([str(x*100)+"%" for x in default_probs])
    #cm.plot_default_probs(periods, default_probs, "rbc_cm_defaults.pdf")


if __name__ == "__main__":
    #merton_experiment()
    credit_metrics_experiment()