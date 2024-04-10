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
        """
        Computes the volatility of this stocks log interday returns.

        === Parameters ===
        - price_data: the daily historical price data for this stock.
                      Must have column "Price Date" and "Price".
        """
        if isinstance(price_data, str):
            price_data = consume_price_csv(price_data)
        df = price_data
        df = df[df["Price Date"] <= pd.to_datetime(self.date)]
        interday_returns = np.log(df["Price"] / df["Price"].shift(1))
        self.volatility = interday_returns.std(ddof=0) * np.sqrt(252)


def consume_price_csv(filename: str) -> pd.DataFrame:
    """
    Constructs a historical price dataframe using the csv file found at filename.
    """
    df = pd.read_csv(filename)
    try:
        df["Price Date"] = pd.to_datetime(df["Date"], format="%m/%d/%y")
    except ValueError:
        df["Price Date"] = pd.to_datetime(df["Date"])
    df["Price"] = df["Close"]
    df = df[["Price Date", "Price"]]
    return df
