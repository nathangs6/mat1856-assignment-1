from src.Bootstrapper.bootstrap import bootstrap
from src.FinancialInstruments.Bond import get_dated_bonds, process_bond_data, sort_bond_list, compute_spread
from src.FinancialInstruments.Stock import DatedStock
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialModels.FinancialModel import MertonModel, CreditMetricModel
import numpy as np
import matplotlib.pyplot as plt


def construct_canada() -> Company:
    gov_bonds = get_dated_bonds(process_bond_data("data/gov_bond_info.csv",
                                                  "data/gov_bond_prices.csv"))
    canada = Company("Canada", gov_bonds)
    return canada


def construct_loblaws() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/loblaws_bond_info.csv",
                                                     "data/loblaws_bond_prices.csv"))
    stock = DatedStock(310526379, "03-26-2024", 151.88)
    stock.compute_volatility("data/loblaws_stock_prices.csv")
    loblaws = StockCompany("Loblaws", bonds, stock, 37.734, 11.472, 17.555)
    return loblaws


def construct_bombardier() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/bombardier_bond_info.csv",
                                                     "data/bombardier_bond_prices.csv"))
    stock = DatedStock(98000000, "03-26-2024", 61.42)
    stock.compute_volatility("data/bombardier_stock_prices.csv")
    bombardier = StockCompany("Bombardier", bonds, stock, 12.458, -2.404, 14.862)
    return bombardier


def construct_telus() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/telus_bond_info.csv",
                                                     "data/telus_bond_prices.csv"))
    stock = DatedStock(1468000000, "03-26-2024", 21.46)
    stock.compute_volatility("data/telus_stock_prices.csv")
    telus = StockCompany("Telus", bonds, stock, 42.40, 42.40-29.33, 20.73)
    return telus


def construct_pembina() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/pembina_bond_info.csv",
                                                     "data/pembina_bond_prices.csv"))
    stock = DatedStock(549000000, "03-26-2024", 47.33)
    stock.compute_volatility("data/pembina_stock_prices.csv")
    pembina = StockCompany("Pembina Pipelines", bonds, stock, 31.038, 15.696, 11.366)
    return pembina


def construct_slate() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/slate_bond_info.csv",
                                                     "data/slate_bond_prices.csv"))
    stock = DatedStock(549000000, "03-26-2024", 0.74)
    stock.compute_volatility("data/slate_stock_prices.csv")
    slate = StockCompany("Slate Office REIT", bonds, stock, 1747.860, 515.370, 1178.734)
    return slate


def construct_ecn() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/ecn_bond_info.csv",
                                                     "data/ecn_bond_prices.csv"))
    stock = DatedStock(549000000, "03-26-2024", 0.74)
    stock.compute_volatility("data/ecn_stock_prices.csv")
    ecn = StockCompany("ECN Capital", bonds, stock, 1284.833, 209.488, 1075.345)
    return ecn


def construct_bmo() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/bmo_bond_info.csv",
                                                     "data/bmo_bond_prices.csv"))
    stock = DatedStock(549000000, "03-26-2024", 0.74)
    stock.compute_volatility("data/bmo_stock_prices.csv")
    ecn = StockCompany("BMO", bonds, stock, 1324.762, 77.279, 1247.483)
    return ecn


def construct_ct() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/ct_bond_info.csv",
                                                     "data/ct_bond_prices.csv"))
    stock = DatedStock(549000000, "03-26-2024", 0.74)
    stock.compute_volatility("data/ct_stock_prices.csv")
    ct = StockCompany("Canadian Tire", bonds, stock, 21.9783, 6.4448, 15.5335)
    return ct


def construct_dollarama() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/dollarama_bond_info.csv",
                                                     "data/dollarama_bond_prices.csv"))
    stock = DatedStock(278760000, "03-26-2024", 109.97)
    stock.compute_volatility("data/dollarama_stock_prices.csv")
    d = StockCompany("Dollarama", bonds, stock, 5263.607, 380.848, 4506.665)
    return d


def construct_sru() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/sru_bond_info.csv",
                                                     "data/sru_bond_prices.csv"))
    stock = DatedStock(278760000, "03-26-2024", 109.97)
    stock.compute_volatility("data/sru_stock_prices.csv")
    d = StockCompany("SRU", bonds, stock, 11905.422, 6359.304, 5546.118)
    return d


def construct_brookfield() -> StockCompany:
    bonds = get_dated_bonds(process_bond_data("data/brookfield_bond_info.csv",
                                                     "data/brookfield_bond_prices.csv"))
    stock = DatedStock(287.053, "04-10-2024", 30.34)
    stock.compute_volatility("data/bepun_stock_prices.csv")
    equity = stock.num_shares * stock.price
    debt = 25222
    c = StockCompany("BEP", bonds, stock, equity+debt, equity, debt)
    return c


def merton_experiment(num_years: int, com_constructor: callable) -> list[float]:
    print("=== MERTON ===")
    ### SETUP
    canada = construct_canada()
    canada.get_rates([365 * i for i in range(1, num_years+1)])
    company  = com_constructor()

    ### Merton Specific Results
    mm = MertonModel(canada, company)
    mm.print_stats()

    ### Return information needed to compare CreditMetrics and Merton
    default_probs = mm.get_default_probs(num_years)
    return default_probs


def credit_metrics_experiment(num_years: int, com_constructor: callable) -> list[float]:
    print("=== CREDIT METRICS ===")
    ### SETUP
    canada = construct_canada()
    company = com_constructor()
    company.set_recovery_rate(0.5)

    cm = CreditMetricModel(canada, company)

    ### Credit Metric Specific Results
    cm.print_stats()
    periods = np.arange(1, 6)
    gov_rates = np.array(canada.get_rates(periods*365))*100
    #rbc_rates = rbc.get_rates(periods)
    fig, ax = plt.subplots(1,1, figsize=(10,3))
    ax.set_title("Canada vs. BEP Rates")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Yield (%)")
    ax.plot(periods, gov_rates, '#209fb5', label="Canada")
    ax.plot(periods, gov_rates+cm.spread*100, '#40a02b', label=company.name)
    ax.legend()
    plt.savefig("output/yield_plot.jpg", bbox_inches="tight")

    ### Return information needed to compare CreditMetrics and Merton
    return cm.get_annual_default_probs(num_years)


if __name__ == "__main__":
    com_constructor = construct_brookfield
    num_years = 20
    periods = [i for i in range(1, num_years+1)]
    mm_default_probs = merton_experiment(num_years, com_constructor)
    print("")
    cm_default_probs = credit_metrics_experiment(num_years, com_constructor)
    print("\n=== RESULTS ===")
    for i in range(num_years):
        mm_default_probs[i] *= 100
        cm_default_probs[i] *= 100
    print(f"Merton Probs: {mm_default_probs}")
    print(f"CreditMetric Probs: {cm_default_probs}")

    fig, ax = plt.subplots(1, 1, figsize=(10,3))
    ax.set_title("BEP-UN.TO Default Probability")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Default Probability (%)")
    ax.plot(periods, cm_default_probs, '#209fb5', label="CreditMetrics")
    ax.plot(periods, mm_default_probs, '#40a02b', label="Merton")
    ax.legend()
    plt.savefig("output/default_plot.jpg", bbox_inches="tight")