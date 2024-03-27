from src.FinancialInstruments.Bond import Bond, DatedBond, sort_bond_list
from src.FinancialInstruments.Stock import Stock, DatedStock
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
from src.Bootstrapper.bootstrap import bootstrap
import numpy as np


class Company:
    name: str
    stock: DatedStock
    bonds: list[DatedBond]
    rates: BinarySortedDict
    assets: float
    equity: float
    debt: float
    
    def __init__(self, name: str, stock: DatedStock, bonds: list[Bond],
                 liability: float, debt: float) -> None:
        self.name = name
        self.stock = stock
        self.bonds = bonds
        print(stock.num_shares, stock.price, stock.num_shares * stock.price)
        self.equity = (stock.num_shares * stock.price) / 1e9
        self.assets = self.equity + liability
        self.debt = debt 

    def add_bonds(self, bonds: Bond|list[Bond]) -> None:
        if isinstance(bonds, Bond):
            self.bonds.append(bonds)
        else:
            self.bonds.extend(bonds)
        self.bonds = sort_bond_list(self.bonds)

    def get_rates(self):
        self.rates = bootstrap(self.bonds)

    def print_stats(self, period: int) -> None:
        if self.rates is None:
            self.get_rates()
        print(f"Company: {self.name}, Period={period}\n" + 
              f"Assets: {self.assets}\n" +
              f"Equity: {self.equity}\n" + 
              f"Strike: {self.debt * np.exp(self.rates[period] * period/365)}\n" + 
              f"Volatility: {round(100*self.stock.volatility, 2)}%\n" + 
              f"Rate: {round(self.rates[period], 2)}%")