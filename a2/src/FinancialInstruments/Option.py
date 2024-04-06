import numpy as np
import scipy


def N(x: float) -> float:
    """
    Returns the normal CDF at x.
    """
    return scipy.stats.norm.cdf(x)


class Option:
    """
    A class for representing options.

    === Attributes ===
    - underlying_price: the price of the underlying instrument
    - strike_price: the strike price of the option
    - r: the risk-free interest rate
    - t: the time to exercise
    - volatility: the volatility of the underlying asset
    """
    underlying_price: float
    strike_price: float
    r: float
    t: float
    volatility: float

    def __init__(self, underlying_price: float, strike_price: float,
                 r: float, t: float, volatility: float) -> None:
        self.underlying_price = underlying_price
        self.strike_price = strike_price
        self.r = r
        self.t = t
        self.volatility = volatility

    def price(self) -> float:
        A = self.strike_price * np.exp(-self.r * self.t)
        V = self.underlying_price
        v = self.volatility
        t = self.t
        a = np.log(V / A)
        b = 0.5 * v**2 * t
        c = v * np.sqrt(t)
        d1 = (a + b) / c
        d2 = d1 - v * np.sqrt(t)
        return V * N(d1) - A * N(d2)
    
    def delta(self) -> float:
        V = self.underlying_price
        A = self.strike_price * np.exp(-self.r * self.t)
        v = self.volatility
        t = self.t
        a = np.log(V/A)
        b = v**2 * t / 2
        c = v * np.sqrt(t)
        return N((a + b) / c)
    
    def get_probability_of_exercise(self) -> float:
        A = self.strike_price * np.exp(-self.r * self.t)
        V = self.underlying_price
        v = self.volatility
        t = self.t
        a = np.log(V / A)
        b = 0.5 * v**2 * t
        c = v * np.sqrt(t)
        d1 = (a + b) / c
        d2 = d1 - v * np.sqrt(t)
        return N(d2)
