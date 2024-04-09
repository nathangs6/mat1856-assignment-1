from src.Bootstrapper.bootstrap import bootstrap
from src.FinancialInstruments.Bond import get_dated_bonds, process_bond_data
from src.FinancialInstruments.Stock import DatedStock
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialModels.FinancialModel import MertonModel, CreditMetricModel
import numpy as np
import matplotlib.pyplot as plt


def merton_experiment(num_years: int) -> list[float]:
    print("=== MERTON ===")
    ### SETUP
    bond_data = process_bond_data("data/gov_bond_info.csv", "data/gov_bond_prices.csv", "data/gov_bond_processed.csv")
    bonds = get_dated_bonds(bond_data)
    stock = DatedStock(1408257000, "03-26-2024", 135.16)
    stock.compute_volatility("data/rbc_stock_prices.csv")
    rbc = StockCompany("RBC", bonds, stock, 1857.917, 1857.917)
    rbc.compute_rates()

    ### Merton Specific Results
    mm = MertonModel(rbc)
    mm.print_stats()

    ### Return information needed to compare CreditMetrics and Merton
    periods = [365*i for i in range(1, num_years+1)]
    default_probs = mm.get_default_probs(periods)
    return default_probs


def credit_metrics_experiment(num_years: int) -> list[float]:
    print("=== CREDIT METRICS ===")
    ### SETUP
    gov_bonds = get_dated_bonds(process_bond_data("data/gov_bond_info.csv",
                                                  "data/gov_bond_prices.csv"))
    rbc_bonds = get_dated_bonds(process_bond_data("data/rbc_bond_info.csv",
                                                  "data/rbc_bond_prices.csv"))
    canada = Company("Canada", gov_bonds)
    rbc = Company("RBC", rbc_bonds)
    rbc.set_recovery_rate(0.5)

    cm = CreditMetricModel(canada, rbc)
    cm.setup()

    ### Credit Metric Specific Results
    cm.print_stats()
    periods = np.array([365 * i for i in range(1, num_years+1)])
    gov_rates = canada.get_rates(periods)
    rbc_rates = rbc.get_rates(periods)
    fig, ax = plt.subplots(1,1)
    ax.set_title("Canada vs. RBC Rates")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Yield")
    ax.plot(periods/365, gov_rates, label="Canada")
    ax.plot(periods/365, rbc_rates, label="RBC")
    ax.legend()
    plt.savefig("output/yield_plot.pdf", bbox_inches="tight")

    ### Return information needed to compare CreditMetrics and Merton
    return cm.get_annual_default_probs(num_years)


if __name__ == "__main__":
    num_years = 5
    periods = [i for i in range(1, num_years+1)]
    mm_default_probs = merton_experiment(num_years)
    print("")
    cm_default_probs = credit_metrics_experiment(num_years)
    for i in range(num_years):
        mm_default_probs[i] *= 100
        cm_default_probs[i] *= 100
    print(f"Merton Probs: {mm_default_probs}")
    print(f"CreditMetric Probs: {cm_default_probs}")

    fig, ax = plt.subplots(1,1)
    ax.set_title("RBC Default Probability")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Default Probability (%)")
    ax.plot(periods, cm_default_probs, label="CreditMetrics")
    ax.plot(periods, mm_default_probs, label="Merton")
    ax.legend()
    plt.savefig("output/default_plot.pdf", bbox_inches="tight")