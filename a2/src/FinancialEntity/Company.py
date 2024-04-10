from src.FinancialInstruments.Bond import Bond, DatedBond, sort_bond_list
from src.FinancialInstruments.Stock import DatedStock
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
from src.Bootstrapper.bootstrap import bootstrap


class Company:
    """
    Class representing a company.

    === Attributes ===
    - name: the name of this company
    - bonds: a sorted list of bonds this company has
    - rates: the interest rates for this company
    - recovery_rate: this companies recovery rate, defaults to 50%
    """
    name: str
    bonds: list[DatedBond]
    rates: BinarySortedDict | None
    recovery_rate: float | None

    def __init__(self, name: str, bonds: list[DatedBond], recovery_rate: float=0.5) -> None:
        self.name = name
        self.bonds = sort_bond_list(bonds)
        self.rates = None
        self.recovery_rate = recovery_rate

    def get_recovery_rate(self) -> float:
        return self.recovery_rate

    def set_recovery_rate(self, r: float) -> None:
        """
        Sets the recovery rate for this company.

        === Prerequisites ===
        - 0 <= r <= 1
        """
        if not isinstance(r, float):
            raise ValueError("r must be a float!")
        if r <= 0 or r >= 1:
            raise ValueError("r must lie in [0, 1]")
        self.recovery_rate = r
    
    def compute_rates(self):
        """
        Computes the rates for this company by bootstrapping its bonds.
        """
        self.rates = bootstrap(self.bonds)

    def get_rates(self, periods: list[int]) -> list[float]:
        """
        Gets the rates for reach period in periods.

        Periods should be in units of days.
        """
        if self.rates is None:
            self.compute_rates()
        rates = []
        for period in periods:
            if period < 0:
                raise ValueError("Please provide a non-negative integer!")
            rates.append(self.rates[period])
        return rates


class StockCompany(Company):
    """
    A class representing a company with a stock.

    === Attributes ===
    stock: the Stock associated with this company.
    assets: the reported assets this company has
    equity: the equity this company has
    debt: the debt this company has
    """
    stock: DatedStock
    assets: float
    equity: float
    debt: float
    
    def __init__(self, name: str, bonds: list[Bond], stock: DatedStock,
                 assets: float, equity: float, debt: float, recovery_rate: float=0.5) -> None:
        super().__init__(name, bonds, recovery_rate)
        self.stock = stock
        self.assets = assets
        self.equity = equity
        self.debt = debt
