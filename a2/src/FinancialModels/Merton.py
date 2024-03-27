from src.FinancialInstruments.Company import Company
from src.FinancialInstruments.Bond import DatedBond
from src.FinancialInstruments.Stock import DatedStock


class MertonModel:
    government: Company
    company: Company
    
    def __init__(self, government: Company, company: Company) -> None:
        self.government = government
        self.company = company

    def setup(self, stock_price_file: str):
        self.government.get_rates()
        self.company.get_rates()
        self.company.stock.compute_volatility(stock_price_file)

    def fixed_point_func(self, delta) -> float:
        return self.company.stock.volatility * self.company.equity / delta / self.company.assets
    