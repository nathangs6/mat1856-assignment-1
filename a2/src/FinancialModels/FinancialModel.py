import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.optimize
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialInstruments.Option import Option
from src.FinancialInstruments.Bond import compute_spread


class FinancialModel:
    government: Company
    company: Company

    def __init__(self, government: Company, company: Company) -> None:
        self.company = company
        self.government = government

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
    spread: float | None

    def __init__(self, gov: Company, com: Company) -> None:
        super().__init__(gov, com)
        self.spread = self.get_spread()

    def print_stats(self) -> None:
        print(f"Government: {self.government.name}\n" + 
              f"Company: {self.company.name}\n" + 
              f"Recovery Rate: {self.company.get_recovery_rate()*100}%\n" +
              f"Spread: {round(self.spread/0.0001)}\n" +
              f"Annual Default Probability: {round((1 - self.get_q())*100,2)}%")
        
    def get_spread(self) -> float:
        c_bond = self.company.bonds[0]
        nearest_bond = None
        for bond in self.government.bonds:
            if nearest_bond is None:
                nearest_bond = bond
            if abs(bond.maturity_period - c_bond.maturity_period) < abs(nearest_bond.maturity_period - c_bond.maturity_period):
                nearest_bond = bond
        return compute_spread(nearest_bond, c_bond)
        
   
    def set_spread(self, spread: float) -> None:
        self.spread = spread
    
    def get_q(self):
        h = self.spread
        R = self.company.get_recovery_rate()
        return (np.exp(-h) - R) / (1 - R)
    
    def get_annual_default_probs(self, num_years: int) -> list:
        q = self.get_q()
        M = np.array([[q, 1-q],[0,1]])
        A = M
        default_probs = []
        for _ in range(num_years):
            default_probs.append(A[0,1])
            A = A @ M
        return default_probs



def volatility_equation(vs: float, V: float, S: float, delta: float) -> float:
    return vs * S / delta / V


class MertonModel(FinancialModel):
    option: Option

    def __init__(self, government: Company, company: StockCompany) -> None:
        super().__init__(government, company)

    def print_stats(self) -> None:
        assets, asset_volatility = self.find_asset_vals()
        print(f"Company: {self.company.name}\n" +
              f"Assets: {self.company.assets}\n" +
              f"Equity: {self.company.equity}\n" +
              f"Debt: {self.company.debt}\n" +
              f"Stock Volatility: {round(100*self.company.stock.volatility,2)}%\n" +
              f"Asset Volatility: {round(100*asset_volatility,2)}%\n" +
              f"Derived Assets: {assets}")

    def setup(self, stock_price_file: str):
        self.government.compute_rates()
        self.find_asset_volatility("fixed")
        self.company.compute_rates()
        self.company.stock.compute_volatility(stock_price_file)

    def fixed_point_equations(self, variables, sigma_S):
        V, sigma_V = variables
        option = Option(underlying_price=V,
                        strike_price=self.company.debt,
                        r=self.government.rates[365*10],
                        t=1.0,
                        volatility=sigma_V)
        E_calculated = option.price()
        sigma_V_calculated = volatility_equation(sigma_S, V, self.company.equity, option.delta())
        return [E_calculated - self.company.equity, sigma_V_calculated - sigma_V]

    def find_asset_vals(self) -> list[float]:
        initial_guesses = [self.company.assets, self.company.stock.volatility]
        return scipy.optimize.fsolve(self.fixed_point_equations, initial_guesses, self.company.stock.volatility)

    def get_default_probs(self, num_years: int) -> list[float]:
        assets, asset_volatility = self.find_asset_vals()
        option = Option(
            assets,
            self.company.debt,
            0.0,
            0.0,
            asset_volatility
        )
        survival_probs = []
        for y in range(1, num_years+1):
            option.r = self.government.rates[y*365]
            option.t = y
            survival_probs.append(option.get_probability_of_exercise())
        default_probs = []
        prod = 1
        for p in survival_probs:
            prod *= p
            default_probs.append(1. - prod)
        return default_probs