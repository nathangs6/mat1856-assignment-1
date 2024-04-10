from src.FinancialInstruments.Bond import Bond, DatedBond, sort_bond_list
from src.FinancialInstruments.Stock import DatedStock
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
from src.Bootstrapper.bootstrap import bootstrap
from src.FinancialInstruments.Option import Option
import numpy as np
import scipy


class Company:
    name: str
    bonds: list[DatedBond]
    rates: BinarySortedDict | None
    recovery_rate: float | None
    spread: float | None

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
    
    def compute_rates(self):
        self.rates = bootstrap(self.bonds)

    def get_rates(self, periods: list[int]) -> list[float]:
        if self.rates is None:
            self.compute_rates()
        rates = []
        for period in periods:
            rates.append(self.rates[period])
        return rates


class StockCompany(Company):
    stock: DatedStock
    assets: float
    equity: float
    debt: float
    
    def __init__(self, name: str, bonds: list[Bond], stock: DatedStock,
                 assets: float, equity: float, debt: float) -> None:
        self.name = name
        self.stock = stock
        self.bonds = bonds
        self.assets = assets
        self.equity = equity
        self.debt = debt 

    def print_stats(self) -> None:
        print(f"Company: {self.name}\n" + 
              f"Assets: {self.assets}\n" +
              f"Equity: {self.equity}\n" + 
              f"Debt: {self.debt}")