from src.FinancialInstruments.Bond import Bond, DatedBond, sort_bond_list
from src.FinancialInstruments.Stock import DatedStock
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
from src.Bootstrapper.bootstrap import bootstrap
import numpy as np
import scipy


class Company:
    name: str
    bonds: list[DatedBond]
    rates: BinarySortedDict | None
    recovery_rate: float | None
    def __init__(self, name: str, bonds: list[Bond]) -> None:
        self.name = name
        self.bonds = bonds
        self.rates = None
        self.recovery_rate = None

    def get_recovery_rate(self) -> float:
        if self.recovery_rate is None or \
            self.recovery_rate < 0 or \
            self.recovery_rate > 1:
            raise AttributeError("Please ensure the recovery rate is between 0 and 1!")
        return self.recovery_rate

    def set_recovery_rate(self, r: float) -> None:
        self.recovery_rate = r

    def add_bonds(self, bonds: Bond|list[Bond]) -> None:
        if isinstance(bonds, Bond):
            self.bonds.append(bonds)
        else:
            self.bonds.extend(bonds)
        self.bonds = sort_bond_list(self.bonds)
    
    def get_rates(self):
        self.rates = bootstrap(self.bonds)


class StockCompany(Company):
    stock: DatedStock
    assets: float
    equity: float
    debt: float
    
    def __init__(self, name: str, bonds: list[Bond], stock: DatedStock,
                 liability: float, debt: float) -> None:
        self.name = name
        self.stock = stock
        self.bonds = bonds
        self.equity = (stock.num_shares * stock.price) / 1e9
        self.assets = self.equity + liability
        self.debt = debt 

    def add_bonds(self, bonds: Bond|list[Bond]) -> None:
        if isinstance(bonds, Bond):
            self.bonds.append(bonds)
        else:
            self.bonds.extend(bonds)
        self.bonds = sort_bond_list(self.bonds)
    
    def get_strike(self) -> None:
        return self.debt

    def get_discounted_strike(self, period: int) -> None:
        if self.rates is None:
            self.get_rates()
        t = period/365
        r = self.rates[period]
        return self.get_strike() * np.exp(-r*t)

    @staticmethod
    def N(x):
        return scipy.stats.norm.cdf(x)

    def get_option_price(self, period: int, vol: float=None, V: float=None):
        if vol is None:
            vol = self.stock.volatility
        if S is None:
            S = self.assets
        A = self.get_discounted_strike(period)
        t = period/365
        a = np.log(S / A)
        b = 0.5 * vol**2 * t
        c = vol * np.sqrt(t)
        d1 = (a + b) / c
        d2 = d1 - vol * np.sqrt(t)
        return V * self.N(d1) - A * self.N(d2)

    def get_delta(self, period, vol, dv=1/1e9) -> float:
        t = period/365
        V = self.assets
        A = self.get_discounted_strike(period)
        a = np.log(V/A)
        b = vol**2 * t / 2
        c = vol * np.sqrt(t)
        return scipy.stats.norm.cdf((a + b) / c)
        #V = self.assets
        #S1 = self.get_option_price(period, vol, V+dv)
        #S2 = self.get_option_price(period, vol, V-dv)
        #return (S1 - S2) / (2*dv)

    def print_stats(self, period: int) -> None:
        if self.rates is None:
            self.get_rates()
        print(f"Company: {self.name}, Period={period}\n" + 
              f"Assets: {self.assets}\n" +
              f"Equity: {self.equity}\n" + 
              f"Strike: {self.get_strike()}\n" + 
              f"Volatility: {round(100*self.stock.volatility, 2)}%\n" + 
              f"Rate: {round(self.rates[period]*100, 2)}%")
        
    def print_black_scholes(self, period: int, vol: float=None) -> None:
        if self.rates is None:
            self.get_rates()
        print(f"C={round(self.get_option_price(period, vol, self.assets), 3)}," +
              f"S={round(self.assets, 3)}," +
              f"A={round(self.get_discounted_strike(period), 3)}," +
              f"delta={round(self.get_delta(period, vol), 3)}")