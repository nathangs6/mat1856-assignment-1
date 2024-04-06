import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.optimize
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

    def get_asset_vol(self, vol: float, V: float, S: float, delta: float) -> float:
        return vol * S * delta / V

    def non_simul(self, period: int, vol_equity: float):
        vol = vol_equity
        S = self.company.equity
        V = self.company.assets
        delta = self.company.get_delta(period, vol)
        return self.get_asset_vol(vol, V, S, delta)
    
    def simul(self, period: int, vol_equity: float):
        V = self.company.assets
        def equation(x: np.array) -> np.array:
            """
            Returns the asset volatility.

            === Parameters ===
            - x[0]: the current prediction for asset volatility
            - x[1]: the current prediction of option price
            """
            delta = self.company.get_delta(period, x[0])
            return x[0] - self.get_asset_vol(x[0], V, x[1], delta), 0.
        x0 = np.array([vol_equity, self.company.equity])
        scipy.optimize.fsolve(equation, x0)

    def find_asset_volatility(self, period: int):
        vol_equity = self.company.stock.volatility
        asset_volatility = self.simul(period, vol_equity)
        print(f"Simul: {asset_volatility}")
        asset_volatility = self.non_simul(period, vol_equity)
        print(f"Non-simul: {100*asset_volatility}%")