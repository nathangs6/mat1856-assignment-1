import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from BinarySortedDict import BinarySortedDict


info_filename = "data/bond_info.csv"
price_filename = "data/bond_prices.csv"
output_folder = "output/"
FV = 100.0


class Bond:
    isin: str
    fv: float
    coupon: float
    notional: float
    maturity_period: int
    coupon_periods: list[int]

    def __init__(self, isin: str, fv: float, coupon: float, maturity_period: int, coupon_periods: list):
        self.isin = isin
        self.fv = fv
        self.coupon = coupon
        self.coupon_payment = fv*coupon
        self.notional = fv + fv*coupon
        self.maturity_period = maturity_period
        self.coupon_periods = coupon_periods


#########################
### Data Constructing ###
#########################
def get_bonds(df: pd.DataFrame) -> list[Bond]:
    df = df.drop_duplicates(subset=["ISIN"])
    df = df.sort_values("Maturity Period", ascending=True)
    bonds = []
    for index, row in df.iterrows():
        bonds.append(Bond(row["ISIN"],
                          FV,
                          row["Coupon"]/2,
                          row["Maturity Period"],
                          row["Coupon Periods"]))
        print("\item CAN " + str(round(row["Coupon"] * 100.0,2)) + " " + row["Maturity Date"].strftime('%b %y'))
    return bonds


def get_last_coupon_payment_date(row):
    date = row["Coupon Start Date"]
    while date + pd.DateOffset(months=6) < row["Date Collected"]:
        date = date + pd.DateOffset(months=6)
    return date

def get_future_coupon_payments(row):
    date = row["Last Coupon Payment Date"] + pd.DateOffset(months=6)
    periods = []
    while date < row["Maturity Date"]:
        period = (date - row["Date Collected"]).days
        periods.append(period)
        date = date + pd.DateOffset(months=6)
    return periods


def build_data():
    # Process info data
    info = pd.read_csv(info_filename)
    info["Coupon"] = info["Coupon"].astype(float) / 100.0
    info["Issue Date"] = pd.to_datetime(info["Issue Date"])
    info["Maturity Date"] = pd.to_datetime(info["Maturity Date"])
    info["Coupon Start Date"] = pd.to_datetime(info["Coupon Start Date"])
    # Process prices data
    prices = pd.read_csv(price_filename)
    prices["Date Collected"] = pd.to_datetime(prices["Date Collected"])
    prices["Price"] = prices["Price"] * FV / 100.0
    # Merge data and construct needed columns
    df = info.merge(prices, on="ISIN", how="inner")
    ### TEMPORARY
    df = df[df["ISIN"] != "CA135087Q988"]
    ### TEMPORARY
    df["Last Coupon Payment Date"] = df.apply(get_last_coupon_payment_date, axis=1)
    df["Coupon Periods"] = df.apply(get_future_coupon_payments, axis=1)
    df["Dirty Price"] = df["Price"] + (FV * df["Coupon"]/2.0) * (df["Date Collected"] - df["Last Coupon Payment Date"]).dt.days / (365/2)
    df["Maturity Period"] = (df["Maturity Date"] - df["Date Collected"]).dt.days
    return df


########################
### YTM Computations ###
########################
def continuous_ytm(bond: Bond, price: float, ytm: float) -> float:
    P = 0
    for period in bond.coupon_periods:
        P += bond.coupon_payment * np.exp(-ytm*period/365)
    return P + bond.notional * np.exp(-ytm*bond.maturity_period/365) - price

def d_continuous_ytm(bond: Bond, ytm: float) -> float:
    P = 0
    for period in bond.coupon_periods:
        P -= bond.coupon_payment * (period/365) * np.exp(-ytm*period/365)
    return P - bond.notional * (bond.maturity_period/365) * np.exp(-ytm*bond.maturity_period/365)


def newton_raphson_ytm(P: float, bond: Bond) -> float:
    old_ytm = 10.0
    ytm = 0.03
    TOL = 1e-6
    num_iter = 100
    i = 0
    while i < num_iter and np.abs(ytm - old_ytm) > TOL:
        old_ytm = ytm
        ytm = old_ytm - continuous_ytm(bond, P, ytm)/d_continuous_ytm(bond, ytm)
        i += 1
    if i == num_iter:
        print("Max number of iterations reached.")
    return ytm


def compute_ytm(bonds: list, df: pd.DataFrame) -> BinarySortedDict:
    ytm = BinarySortedDict()
    for bond in bonds:
        dirty_price = df[df["ISIN"] == bond.isin].iloc[0]["Dirty Price"]
        ytm[bond.maturity_period] = newton_raphson_ytm(dirty_price, bond)
    return ytm


def get_all_ytm(bonds: list, df: pd.DataFrame, dates: list) -> list:
    ytm = []
    for date in dates:
        ytm.append(compute_ytm(bonds, df[df["Date Collected"] == date]))
    return ytm


def plot_ytm(ytm, dates) -> None:
    fig, ax = plt.subplots(1)
    for i in range(len(ytm)):
        x, y = ytm[i].sorted_key_vals()
        ax.plot(x, np.array(y)*100.0, label=dates[i])
    ax.set_title("YTM Curve")
    ax.set_xlabel("Day Count from Date Collected")
    ax.set_ylabel("YTM %")
    ax.legend()
    fig.savefig(output_folder + "ytm.pdf")

##############################
### Spot Rate Computations ###
##############################
def bootstrap(bonds, df, compounding_period=0):
    r = BinarySortedDict()
    for bond in bonds:
        dirty_price = df[df["ISIN"] == bond.isin].iloc[0]["Dirty Price"]

        discounted_cf = 0
        for period in bond.coupon_periods:
            if period not in r:  # interpolate
                r[period] = r.linearly_interpolate(period)
            if compounding_period == 0:
                discounted_cf += bond.coupon_payment * continuous_time_period(r[period], period/365)
            elif compounding_period == 1:
                discounted_cf += bond.coupon_payment * annual_time_period(r[period], period/365)
        if compounding_period == 0:
            r[bond.maturity_period] = continuous_yield(dirty_price - discounted_cf, bond.notional, bond.maturity_period/365)
        elif compounding_period == 1:
            r[bond.maturity_period] = annual_yield(bond.notional, dirty_price - discounted_cf, bond.maturity_period/365)
    return r

def continuous_time_period(r,t):
    return np.exp(-r*t)

def continuous_yield(num,den,t):
    return -np.log(num/den) / t

def annual_time_period(r, t):
    return 1 / (1+r)**t

def annual_yield(num,den,t):
    return (num/den)**(1/t) - 1


def get_all_sr(bonds, df, dates, compounding_period=0):
    r = []
    for date in dates:
        r.append(bootstrap(bonds, df[df["Date Collected"] == date], compounding_period=compounding_period))
    return r


def plot_sr(rates, dates) -> None:
    fig, ax = plt.subplots(1)
    for i in range(len(rates)):
        x, y = rates[i].sorted_key_vals()
        ax.plot(x, np.array(y)*100.0, label=dates[i])
    ax.set_title("Spot Curve")
    ax.set_xlabel("Day Count from Date Collected")
    ax.set_ylabel("Spot %")
    ax.legend()
    fig.savefig(output_folder + "spots.pdf")

#################################
### Forward Rate Computations ###
#################################
def interpolate_to_years(r):
    for period in [365*x for x in range(1,6)]:
        r[period] = r.linearly_interpolate(period)


def compute_forward_rates(r):
    rates = []
    initial_period = 365
    for period in [365*x for x in range(2,6)]:
        rate = (r[period] * (period) - r[initial_period] * (initial_period))/(period-initial_period)
        rates.append(rate)
    return rates


def get_all_fr(ytms):
    forward_vals = []
    for r in ytms:
        interpolate_to_years(r)
        forward_rates = compute_forward_rates(r)
        forward_vals.append(forward_rates)
    return forward_vals


def plot_fr(fr, dates):
    fr_fig, fr_ax = plt.subplots(1)
    for i in range(len(fr)):
        fr_ax.plot([1, 2, 3, 4], np.array(fr[i])*100.0, label=dates[i])
    fr_ax.set_title("Forward Rates")
    fr_ax.set_xlabel("Year Count from Future One Year")
    fr_ax.set_ylabel("Forward Rate")
    fr_ax.legend()
    fr_fig.savefig(output_folder + "fr.pdf")


########################################
### Covariance Matrices Computations ###
########################################
def construct_cov(data, rv_func):
    num_vars = len(data[0])
    num_days = len(data)
    rvs = np.zeros(shape=(num_vars, num_days))
    for i in range(num_vars):
        for j in range(num_days-1):
            rvs[i][j] = rv_func(data[j][i], data[j+1][i])
    return np.cov(rvs)


def daily_log_returns(val0, val1):
    return np.log(val1/val0)


def display_cov_evs(cov):
    eigvals, eigvecs = np.linalg.eig(cov)
    trace = np.trace(cov)
    for i in range(len(eigvals)):
        print(f"Eigenvalue {i}: {eigvals[i]} constituting {100*eigvals[i]/trace}% of trace")
        print(f"Eigenvector: {eigvecs[i]}")

def eval_evec_to_latex(cov):
    eigvals, eigvecs = np.linalg.eig(cov)
    trace = np.trace(cov)
    ret = "\t\t\t\\hline\n\t\t\t"
    for i in range(len(eigvals)):
        ret += f"$\\lambda_{i}$ & "
    ret = ret[:-2] + "\\\\\n\t\t\t\\hline\n\t\t\t"
    for i in range(len(eigvals)):
        ret += f"${round(100*eigvals[i]/trace,4)}\%$ & "
    ret = ret[:-2] + "\\\\\n\t\t\t\\hline\n\t\t\t"
    for i in range(len(eigvals)):
        ret += f"${round(eigvals[i],6)}$ & "
    ret = ret[:-2] + "\\\\\n\t\t\t\\hline\n\t\t\t"
    for i in range(cov.shape[0]):
        for j in range(len(eigvecs)):
            ret += f"${round(eigvecs[j][i],6)}$ & "
        ret = ret[:-2] + "\\\\\n\t\t\t"
    return ret


def get_year_srs(sr):
    year_srs = []
    for day_sr in sr:
        year_sr = [day_sr[n] for n in [365*x for x in range(1,6)]]
        year_srs.append(year_sr)
    return year_srs


def matrix_to_latex(m):
    ret = ""
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ret += str(round(m[i][j], 8)) + " & "
        ret = ret[:-2] + "\\\\\n"
    return ret[:-4]


##################
### Main Block ###
##################
if __name__ == "__main__":
    isins = ['CA135087J546',
             'CA135087J967',
             'CA135087K528',
             'CA135087K940',
             'CA135087L518',
             'CA135087L930',
             'CA135087M847',
             'CA135087N837',
             'CA135087P576',
             'CA135087Q491',
             'CA135087Q988']
    df = build_data()
    df.to_csv("output/constructed_data.csv")
    df = df.sort_values(by="Date Collected", ascending=True)
    bonds = get_bonds(df)
    dates = df["Date Collected"].unique()
    date_strs = []
    for date in dates:
        date_strs.append(date.strftime('%Y-%m-%d'))
    # YTM Step
    print("Computing YTM")
    ytm = get_all_ytm(bonds, df, dates)
    plot_ytm(ytm, date_strs)
    # Spot Rate Step
    print("Computing spot rates")
    sr = get_all_sr(bonds, df, dates, compounding_period=1)
    plot_sr(sr, date_strs)

    # FR Step
    print("Computing forward rates")
    fr = get_all_fr(sr)
    plot_fr(fr, date_strs)

    # Cov Step
    ## Compute ytm covariance metrics
    print("Computing covariance characteristics for YTM")
    year_sr = get_year_srs(sr)
    sr_cov = construct_cov(year_sr, daily_log_returns)
    print(matrix_to_latex(sr_cov))
    #display_cov_evs(sr_cov)
    print(eval_evec_to_latex(sr_cov))
    ## Compute fr covariance metrics
    print("Computing covariance characteristics for forward rates")
    fr_cov = construct_cov(fr, daily_log_returns)
    print(matrix_to_latex(fr_cov))
    display_cov_evs(fr_cov)
