import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.optimize
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialInstruments.Option import Option


class FinancialModel:
    company: Company

    def __init__(self, company: Company) -> None:
        self.company = company

    def get_default_probs(self, periods: np.array) -> np.array:
        raise NotImplementedError
    
    def plot_default_probs(self, periods: np.array, probs: np.array, save_file: str) -> None:
        import os
        curr_dir = os.path.dirname(__file__)
        filename = os.path.join(curr_dir, '..', '..', 'output', save_file)
        fig, ax = plt.subplots(1, 1)
        ax.plot(periods/365, probs*100.0)
        ax.set_title(f"Probability of {self.company.name} Defaulting")
        ax.set_xlabel("Time (years)")
        ax.set_ylabel("Probability of Default (%)")
        fig.savefig(filename)
        plt.close(fig)


class CreditMetricModel(FinancialModel):
    government: Company

    def __init__(self, gov: Company, com: Company) -> None:
        super().__init__(com)
        self.government = gov
    
    def setup(self):
        self.government.get_rates()
        self.company.get_rates()

    def gen_hazard_rates(self, periods: np.array) -> np.array:
        h = np.zeros_like(periods, dtype=float)
        for i in range(len(periods)):
            h[i] = self.company.rates[periods[i]] - self.government.rates[periods[i]]
        return h
    
    def get_default_probs(self, periods: np.array) -> np.array:
        R = self.company.get_recovery_rate()
        h = self.gen_hazard_rates(periods)
        
        return 1 - (np.exp(-h) - R) / (1 - R)


def volatility_equation(vs: float, V: float, S: float, delta: float) -> float:
    return vs * S * delta / V


class MertonModel(FinancialModel):
    option: Option

    def __init__(self, company: StockCompany) -> None:
        super().__init__(company)

    def setup(self, stock_price_file: str):
        self.company.get_rates()
        self.company.stock.compute_volatility(stock_price_file)

    def fixed_point(self, period: int, equity_vol: float):
        option = self.company.make_option(period)
        S = self.company.equity
        V = self.company.assets
        tol = 1e-9
        new_vol = equity_vol
        option.volatility = np.inf
        i, max_iter = 0, 1000
        while abs(new_vol - option.volatility) > tol and i < max_iter:
            option.volatility = new_vol
            delta = option.delta()
            new_vol = volatility_equation(equity_vol, V, S, delta)
            i += 1
        if i == max_iter:
            print(f"Fixed point iteration did not converge in {max_iter} steps!")
        return option.volatility

    def find_asset_volatility(self, period: int, method: str):
        equity_vol = self.company.stock.volatility
        if method == "fixed":
            asset_volatility = self.fixed_point(period, equity_vol)
        else:
            raise ValueError
        return asset_volatility