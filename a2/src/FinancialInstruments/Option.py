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

    def _d_vals(self) -> tuple[float, float]:
        """
        Computes d1 and d2 used in the the Black-Scholes formula.
        """
        A = self.strike_price * np.exp(-self.r * self.t)
        V = self.underlying_price
        v = self.volatility
        t = self.t
        a = np.log(V/A)
        b = 0.5 * v**2 * t
        c = v * np.sqrt(t)
        d1 = (a + b) / c
        return d1, d1 - v*np.sqrt(t)

    def price(self) -> float:
        """
        Computes the price of this option.
        """
        A = self.strike_price * np.exp(-self.r * self.t)
        V = self.underlying_price
        d1, d2 = self._d_vals()
        return V * N(d1) - A * N(d2)
    
    def delta(self) -> float:
        """
        Computes the delta of this option.
        """
        d1 = self._d_vals()[0]
        return N(d1)
    
    def get_probability_of_exercise(self) -> float:
        """
        Computes the probability of exercising this option.
        """
        d2 = self._d_vals()[1]
        return N(d2)
