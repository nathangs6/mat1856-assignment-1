from src.Bootstrapper.bootstrap import bootstrap
from src.FinancialInstruments.Bond import get_dated_bonds, process_bond_data, sort_bond_list, compute_spread
from src.FinancialInstruments.Stock import DatedStock
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialModels.FinancialModel import MertonModel, CreditMetricsModel
import numpy as np
import matplotlib.pyplot as plt


def construct_canada() -> Company:
    gov_bonds = get_dated_bonds(process_bond_data("data/gov_bond_info.csv",
                                                  "data/gov_bond_prices.csv"))
    canada = Company("Canada", gov_bonds)
    canada.compute_rates()
    return canada


def construct_brookfield() -> StockCompany:
    num_shares = 287.053
    stock_price = 30.34
    bonds = get_dated_bonds(process_bond_data("data/brookfield_bond_info.csv",
                                                     "data/brookfield_bond_prices.csv"))
    stock = DatedStock(num_shares, "04-10-2024", stock_price)
    stock.compute_volatility("data/bepun_stock_prices.csv")
    equity = stock.num_shares * stock.price
    debt = 25222
    c = StockCompany("BEP", bonds, stock, equity+debt, equity, debt)
    return c


def merton_experiment(num_years: int, com_constructor: callable) -> list[float]:
    print("=== MERTON ===")
    ### SETUP
    canada = construct_canada()
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

    cm = CreditMetricsModel(canada, company)

    ### Credit Metric Specific Results
    cm.print_stats()
    periods = np.arange(1, 6)
    gov_rates = np.array(canada.get_rates(periods*365))*100

    ### Plot rates
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
    ### Get default probabilities
    com_constructor = construct_brookfield
    num_years = 20
    periods = [i for i in range(1, num_years+1)]
    mm_default_probs = merton_experiment(num_years, com_constructor)
    print("")
    cm_default_probs = credit_metrics_experiment(num_years, com_constructor)

    ### Display results
    print("\n=== RESULTS ===")
    for i in range(num_years):
        mm_default_probs[i] *= 100
        cm_default_probs[i] *= 100
    print(f"Merton Probs: {[round(p,2) for p in mm_default_probs]}")
    print(f"CreditMetric Probs: {[round(p,2) for p in cm_default_probs]}")

    ### Plot results
    fig, ax = plt.subplots(1, 1, figsize=(10,3))
    ax.set_title("BEP-UN.TO Default Probability")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Default Probability (%)")
    ax.plot(periods, cm_default_probs, '#209fb5', label="CreditMetrics")
    ax.plot(periods, mm_default_probs, '#40a02b', label="Merton")
    ax.legend()
    plt.savefig("output/default_plot.jpg", bbox_inches="tight")