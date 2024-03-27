from src.Bootstrapper.bootstrap import bootstrap
from src.FinancialInstruments.Bond import DatedBond, get_dated_bonds, process_bond_data
from src.FinancialInstruments.Stock import DatedStock
from src.FinancialInstruments.Company import Company
from src.FinancialModels.Merton import MertonModel


if __name__ == "__main__":
    bond_data = process_bond_data("data/gov_bond_info.csv", "data/gov_bond_prices.csv", "data/gov_bond_processed.csv")
    bonds = get_dated_bonds(bond_data)
    stock = DatedStock(1408257000, "03-26-2024", 135.16)
    stock.compute_volatility("data/rbc_stock_prices.csv")
    #rbc = Company("RBC", stock, bonds, 1857.917, 1241.168)
    rbc = Company("RBC", stock, bonds, 1857.917, 1857.917)
    rbc.get_rates()
    rbc.print_stats(365)
    d1 = 0.802
    mm = MertonModel(None, rbc)
    print(f"{round(mm.fixed_point_func(d1)*100, 2)}%")
    d2 = 1.0
    print(f"{round(mm.fixed_point_func(d2)*100, 2)}%")
    d3 = 1.0
    print(f"{round(mm.fixed_point_func(d3)*100, 2)}%")