import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.optimize
from src.FinancialEntity.Company import Company, StockCompany
from src.FinancialInstruments.Option import Option
from src.FinancialInstruments.Bond import compute_spread


class FinancialModel:
    """
    An abstract credit risk model.

    === Attributes ===
    - government: the government the company of interest is in
    - company: the company of interest
    """
    government: Company
    company: Company

    def __init__(self, government: Company, company: Company) -> None:
        self.company = company
        self.government = government

    def get_default_probs(self, periods: np.array) -> np.array:
        raise NotImplementedError


class CreditMetricsModel(FinancialModel):
    """
    A class representing the CreditMetrics model.

    === Attributes ===
    - spread: the spread of the company from the government.
    """
    spread: float | None

    def __init__(self, gov: Company, com: Company) -> None:
        super().__init__(gov, com)
        self.spread = self.get_spread()

    def print_stats(self) -> None:
        """
        Print some stats relevant to the CreditMetrics model.
        """
        print(f"Government: {self.government.name}\n" + 
              f"Company: {self.company.name}\n" + 
              f"Recovery Rate: {self.company.get_recovery_rate()*100}%\n" +
              f"Spread: {round(self.spread/0.0001)}\n" +
              f"Annual Default Probability: {round((1 - self.get_q())*100,2)}%")
        
    def get_spread(self) -> float:
        """
        Gets the spread of this company according to the government.
        """
        c_bond = self.company.bonds[0]
        nearest_bond = None
        for bond in self.government.bonds:
            if nearest_bond is None:
                nearest_bond = bond
            if abs(bond.maturity_period - c_bond.maturity_period) < abs(nearest_bond.maturity_period - c_bond.maturity_period):
                nearest_bond = bond
        return compute_spread(nearest_bond, c_bond)
    
    def get_q(self):
        """
        Gets the probability of solvency for this company.
        """
        h = self.spread
        R = self.company.get_recovery_rate()
        return (np.exp(-h) - R) / (1 - R)
    
    def get_annual_default_probs(self, num_years: int) -> list:
        """
        Gets the annual default probability for each year in [1, num_years].
        """
        q = self.get_q()
        M = np.array([[q, 1-q],[0,1]])
        A = M
        default_probs = []
        for _ in range(num_years):
            default_probs.append(A[0,1])
            A = A @ M
        return default_probs



def volatility_equation(vs: float, V: float, S: float, delta: float) -> float:
    """
    The fixed point volatility equation. With 
    - v_X = volatility of X,
    - S = equity
    - V = assets
    - delta = option delta
    v_v = v_S * S / delta / V
    """
    return vs * S / delta / V


def cumulative_probability(X_probs: list[float]) -> list[float]:
    """
    Given two states, X and Y, with probability q, 1 - q of each at each period,
    returns the probability that you are in state Y at each period.
    """
    cumulative_Y_probs = []
    prod = 1
    for q in X_probs:
        prod *= q
        cumulative_Y_probs.append(1. - prod)
    return cumulative_Y_probs

class MertonModel(FinancialModel):
    """
    A class representing the Merton model for credit risk.
    """
    def __init__(self, government: Company, company: StockCompany) -> None:
        super().__init__(government, company)

    def print_stats(self) -> None:
        """
        Prints some relevant stats for the Merton model.
        """
        assets, asset_volatility = self.find_asset_vals()
        print(f"Company: {self.company.name}\n" +
              f"Assets: {self.company.assets}\n" +
              f"Equity: {self.company.equity}\n" +
              f"Debt: {self.company.debt}\n" +
              f"Stock Volatility: {round(100*self.company.stock.volatility,2)}%\n" +
              f"Asset Volatility: {round(100*asset_volatility,2)}%\n" +
              f"Derived Assets: {assets}")

    def fixed_point_equations(self, variables, sigma_S):
        """
        The fixed point equations for this company/governement.

        Seeing a company's equity (S) as a call option (C) on its assets (V),
        the two equations are:
        - v_V = v_S * S / delta / V
        - S = price(C)
        """
        V, sigma_V = variables
        option = Option(underlying_price=V,
                        strike_price=self.company.debt,
                        r=self.government.rates[365*10],
                        t=1.0,
                        volatility=sigma_V)
        S_calculated = option.price()
        sigma_V_calculated = volatility_equation(sigma_S, V, self.company.equity, option.delta())
        return [S_calculated - self.company.equity, sigma_V_calculated - sigma_V]

    def find_asset_vals(self) -> list[float]:
        """
        Computes the asset values for this company by simultaneously solving
        the fixed point equations.
        """
        initial_guesses = [self.company.assets, self.company.stock.volatility]
        return scipy.optimize.fsolve(self.fixed_point_equations, initial_guesses, self.company.stock.volatility)

    def get_default_probs(self, num_years: int) -> list[float]:
        """
        Get the default probability of this company for each year in [1, num_years].
        """
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
        default_probs = cumulative_probability(survival_probs)
        return default_probs