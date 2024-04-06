import numpy as np
import scipy
import matplotlib.pyplot as plt
from src.FinancialEntity.Company import Company, StockCompany


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


class MertonModel(FinancialModel):
    fixed_point: float

    def __init__(self, company: StockCompany) -> None:
        super().__init__(company)
        self.fixed_point = None

    def setup(self, stock_price_file: str):
        self.company.get_rates()
        self.company.stock.compute_volatility(stock_price_file)

    def fixed_point_func(self, period: int, vol=None, verbose=False) -> float:
        if vol is None:
            vol = self.company.stock.volatility
        delta = self.company.get_delta(period, vol)
        if verbose:
            print(f"vol={vol}, S={self.company.equity}, delta={delta}, V={self.company.assets}")
        return vol * self.company.equity * delta / self.company.assets

    def find_fixed_point(self, period: int) -> float:
        vol = self.company.stock.volatility
        delta = self.company.get_delta(period, vol)
        print(f"Starting with vol, delta = {round(vol*100, 2), round(delta, 3)}")
        for _ in range(1):
            new_vol = self.fixed_point_func(period, vol=vol, verbose=True)
            print(f"new_vol, old_vol = {new_vol, vol}")
            vol = new_vol
        print(f"Final fixed point found: {round(vol*100, 2)}")
        self.fixed_point = vol