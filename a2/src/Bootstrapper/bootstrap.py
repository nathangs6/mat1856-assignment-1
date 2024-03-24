import numpy as np
from src.BinarySortedDict.BinarySortedDict import BinarySortedDict
from src.FinancialInstruments.Bond import DatedBond


def bootstrap(bonds: list[DatedBond]):
    r = BinarySortedDict()
    for bond in bonds:
        dirty_price = bond.price
        coupon_periods = bond.coupon_periods
        maturity_period = bond.maturity_period

        discounted_cf = 0
        for period in coupon_periods:
            if period not in r:  # interpolate
                r[period] = r.linearly_interpolate(period)
            discounted_cf += bond.coupon_payment * continuous_time_period(r[period], period/365)
        r[maturity_period] = continuous_yield(dirty_price - discounted_cf, bond.notional, maturity_period/365)
    return r


def continuous_time_period(r,t):
    return np.exp(-r*t)


def continuous_yield(num,den,t):
    return -np.log(num/den) / t