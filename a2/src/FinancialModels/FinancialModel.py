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

    def print_stats(self) -> None:
        print(f"Government: {self.government.name}\n" + 
              f"Company: {self.company.name}\n" + 
              f"Recovery Rate: {self.company.get_recovery_rate()}\n" +
              f"Annual Default Probability: {(1 - self.get_q())*100}%")
    
    def setup(self):
        self.government.compute_rates()
        self.company.compute_rates()

    def gen_hazard_rates(self, periods: np.array) -> np.array:
        h = np.zeros_like(periods, dtype=float)
        for i in range(len(periods)):
            h[i] = self.company.rates[periods[i]] - self.government.rates[periods[i]]
        return h
    
    def get_default_probs(self, periods: np.array) -> np.array:
        R = self.company.get_recovery_rate()
        h = self.gen_hazard_rates(periods)
        
        return 1 - (np.exp(-h) - R) / (1 - R)
    
    def get_q(self):
        h = self.gen_hazard_rates([365])[0]
        R = self.company.get_recovery_rate()
        return (np.exp(-h) - R) / (1 - R)
    
    def get_annual_default_probs(self, num_years: int) -> list:
        q = self.get_q()
        A = np.array([[q, 1-q],[0,1]])
        default_probs = []
        for _ in range(num_years):
            default_probs.append(A[0,1])
            A = A @ A
        return default_probs



def volatility_equation(vs: float, V: float, S: float, delta: float) -> float:
    return vs * S * delta / V


class MertonModel(FinancialModel):
    option: Option

    def __init__(self, company: StockCompany) -> None:
        super().__init__(company)

    def print_stats(self) -> None:
        print(f"Company: {self.company.name}\n" +
              f"Assets: {self.company.assets}\n" +
              f"Equity: {self.company.equity}\n" +
              f"Debt: {self.company.debt}\n" +
              f"Stock Volatility: {100*self.company.stock.volatility}\n" +
              f"Asset Volatility: {100*self.find_asset_volatility("fixed")}")

    def setup(self, stock_price_file: str):
        self.company.compute_rates()
        self.company.stock.compute_volatility(stock_price_file)

    def _fixed_point(self, equity_vol: float):
        option = self.company.make_option(365)
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

    def find_asset_volatility(self, method: str):
        equity_vol = self.company.stock.volatility
        if method == "fixed":
            asset_volatility = self._fixed_point(equity_vol)
        else:
            raise ValueError
        return asset_volatility
    
    def get_default_probs(self, periods: list[int]) -> list[float]:
        option = self.company.make_option(365)
        asset_volatility = self.find_asset_volatility(method="fixed")
        option.volatility = asset_volatility
        default_probs = []
        for period in periods:
            option.t = period/365
            default_probs.append(1. - option.get_probability_of_exercise())
        return default_probs