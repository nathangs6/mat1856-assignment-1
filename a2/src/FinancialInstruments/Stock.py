import pandas as pd
import numpy as np


class Stock:
    num_shares: float

    def __init__(self, num_shares: float) -> None:
        self.num_shares = num_shares


class DatedStock(Stock):
    price: float
    date: str
    volatility: float | None

    def __init__(self, num_shares: float, date: str, price: float) -> None:
        super().__init__(num_shares)
        self.price = price
        self.date = date
        self.volatility = None

    def compute_volatility(self, price_data: pd.DataFrame|str) -> None:
        if isinstance(price_data, str):
            price_data = consume_price_csv(price_data)
        df = price_data
        #df = df[df["Price Date"] <= pd.to_datetime(self.date)]
        df["Interday Return"] = np.log(df["Price"] / df["Price"].shift(1))
        self.volatility = df["Interday Return"].std(ddof=0) * np.sqrt(252)


def consume_price_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    try:
        df["Price Date"] = pd.to_datetime(df["Date"], format="%m/%d/%y")
    except ValueError:
        df["Price Date"] = pd.to_datetime(df["Date"])
    df["Price"] = df["Close"]
    df = df[["Price Date", "Price"]]
    return df


if __name__ == "__main__":
    import os
    curr_dir = os.path.dirname(__file__)
    filename = os.path.join(curr_dir, '..', '..', 'data', 'rbc_stock_prices.csv')
    price_data = consume_price_csv(filename)
    stock = DatedStock(1408257000, "03/25/2024", 99.42)
    stock.compute_volatility(price_data)
    print(stock.volatility)