import pandas as pd
import numpy as np
from operator import attrgetter
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict

###########################
### Bond Data Structure ###
###########################
class Bond:
    """
    Class representing a bond's static information.
    The data contained in this class should not change over time.
    """
    isin: str
    fv: float
    coupon: float
    notional: float

    def __init__(self, isin: str, fv: float, coupon: float):
        self.isin = isin
        self.fv = fv
        self.coupon = coupon
        self.coupon_payment = fv*coupon
        self.notional = fv + fv*coupon


class DatedBond(Bond):
    """
    A class representing a bond at a current date.
    The data contained in this class is only valid for a specific date.
    """
    date: np.datetime64
    maturity_period: int
    coupon_periods: list[int]

    def __init__(self, isin: str, fv: float, coupon: float, 
                 date: np.datetime64, price: float,
                 maturity_period: int, coupon_periods: list[int]) -> None:
        super().__init__(isin, fv, coupon)
        self.date = date
        self.price = price
        self.maturity_period = maturity_period
        self.coupon_periods = coupon_periods
    
    def __str__(self) -> str:
        return f"{self.isin} | {self.coupon} | {self.maturity_period}"

######################
### Bond Functions ###
######################
def sort_bond_list(lst: list[DatedBond]) -> list[DatedBond]:
    """
    Sorts lst according to date.
    """
    return sorted(lst, key=attrgetter("date"))


### YTM Computations
def ytm_price(bond: DatedBond, ytm: float) -> float:
    """
    Computes the price of bond with the ytm value given.

    === Parameters ===
    - bond: the bond to compute the price of
    - ytm: the ytm to use
    """
    P = 0
    for period in bond.coupon_periods:
        t = period/365
        P += bond.coupon_payment * np.exp(-ytm*t)
    t = bond.maturity_period/365
    return P + bond.notional * np.exp(-ytm*t) - bond.price


def d_ytm_price(bond: Bond, ytm: float) -> float:
    """
    Derivative of the ytm_price function with respect to ytm.
    """
    P = 0
    for period in bond.coupon_periods:
        t = period/365
        P -= bond.coupon_payment * t * np.exp(-ytm*t)
    t = bond.maturity_period/365
    return P - bond.notional * t * np.exp(-ytm*t)


def newton_raphson_ytm(bond: Bond, max_iter: int = 1000) -> float:
    """
    Uses the Newton-Raphson method to solve for YTM.
    """
    old_ytm = np.inf
    new_ytm = 0.03
    TOL = 1e-6
    i = 0
    while i < max_iter and np.abs(new_ytm - old_ytm) > TOL:
        old_ytm = new_ytm
        new_ytm = old_ytm - ytm_price(bond, old_ytm)/d_ytm_price(bond, old_ytm)
        i += 1
    if i == max_iter:
        print("Max number of iterations reached.")
    return new_ytm


def compute_spread(gov: DatedBond, com: DatedBond) -> float:
    """
    Returns the spread in decimal between the government bond and the company bond.
    Formula: spread = company YTM - gov YTM

    === Prerequisites ===
    - gov bond and company bond mature at a similar time period
    """
    gov_ytm = newton_raphson_ytm(gov)
    com_ytm = newton_raphson_ytm(com)
    return com_ytm - gov_ytm


#############################
### Bond Data Consumption ###
#############################
def get_bonds(df: pd.DataFrame) -> list[Bond]:
    """
    Given a pandas DataFrame with the correct columns, returns a list of bonds.
    """
    bonds = []
    for _, row in df.iterrows():
        bonds.append(Bond(row["ISIN"],
                          row["FV"],
                          row["Coupon"]/2))
    return bonds


def get_dated_bonds(df: pd.DataFrame) -> list[DatedBond]:
    """
    Given a pandas DataFrame with the correct columns, returns a list of dated bonds sorted
    in order of maturity period.
    """
    df = df.sort_values("Maturity Period", ascending=True)
    bonds = []
    for _, row in df.iterrows():
        bonds.append(DatedBond(row["ISIN"],
                               row["FV"],
                               row["Coupon"]/2,
                               row["Price Date"],
                               row["Dirty Price"],
                               row["Maturity Period"],
                               row["Coupon Periods"]))
    return sort_bond_list(bonds)


def get_last_coupon_payment_date(row):
    """
    Given a row containing the first coupon date and the price date,
    returns the most recent coupon payment date.
    """
    date = row["Coupon Start Date"]
    while date + pd.DateOffset(months=6) < row["Price Date"]:
        date = date + pd.DateOffset(months=6)
    return date

def get_future_coupon_payments(row):
    date = row["Last Coupon Payment Date"] + pd.DateOffset(months=6)
    periods = []
    while date < row["Maturity Date"]:
        period = (date - row["Price Date"]).days
        periods.append(period)
        date = date + pd.DateOffset(months=6)
    return periods


def consume_info_csv(info_filename: str) -> pd.DataFrame:
    """
    Consumes the relevant csv files and builds a pandas dataframe with the bond data.
    === Parameters ===
    - info_filename: string containing the name of the CSV file 
        containing the constant information about the bonds. Requires the following columns:
        - ISIN: the ISIN of the bond
        - Coupon: the coupon in percentage format
        - FV: the face value of the bond
        - Issue Date: the date the bond was issued
        - Maturity Date: the date the bond will mature
        - Coupon Start Date: the first date on which a coupon was paid
    - price_filename: string containing the name of the CSV file containing the bond prices.
        - ISIN: the ISIN of the bond
        - Price Date: the date for that closing price
        - Price: the percentage of the notional the closing price is.
    - save_name: string containing the name of the CSV file to save the data to.
        If None is given, don't save the data.
    === Prerequisites ===
    - the two files are in CSV format
    """
    # Process info data
    info = pd.read_csv(info_filename)
    info["Coupon"] = info["Coupon"].astype(float) / 100.0
    info["FV"] = info["FV"]
    info["Issue Date"] = pd.to_datetime(info["Issue Date"])
    info["Maturity Date"] = pd.to_datetime(info["Maturity Date"])
    info["Coupon Start Date"] = pd.to_datetime(info["Coupon Start Date"])

    return info


def consume_price_csv(filename: str, bond_info: pd.DataFrame) -> pd.DataFrame:
    prices = pd.read_csv(filename)
    prices["Price Date"] = pd.to_datetime(prices["Price Date"])

    df = bond_info.merge(prices, on="ISIN", how="inner")

    # Construct needed columns
    df["Price"] = df["Price"] * df["FV"] / 100.0
    df["Last Coupon Payment Date"] = df.apply(get_last_coupon_payment_date, axis=1)
    df["Coupon Periods"] = df.apply(get_future_coupon_payments, axis=1)
    df["Dirty Price"] = df["Price"] + (df["FV"] * df["Coupon"]/2.0) * (df["Price Date"] - df["Last Coupon Payment Date"]).dt.days / (365/2)
    df["Maturity Period"] = (df["Maturity Date"] - df["Price Date"]).dt.days
    
    return df


def process_bond_data(info_filename: str, price_filename: str, save_filename: str|None=None) -> pd.DataFrame:
    info = consume_info_csv(info_filename)
    df = consume_price_csv(price_filename, info)
    if save_filename is not None:
        df.to_csv(save_filename)
    
    return df