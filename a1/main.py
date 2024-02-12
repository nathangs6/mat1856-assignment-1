import src.computations as src

INFO_FILENAME = "data/bond_info.csv"
PRICE_FILENAME = "data/bond_prices.csv"
OUTPUT_FOLDER = "output/"
ISINS = ['CA135087J546',
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

if __name__ == "__main__":
    df = src.build_data(INFO_FILENAME, PRICE_FILENAME)
    df.to_csv("output/constructed_data.csv")
    df = df.sort_values(by="Date Collected", ascending=True)
    bonds = src.get_bonds(df)
    dates = df["Date Collected"].unique()
    date_strs = []
    for date in dates:
        date_strs.append(date.strftime('%Y-%m-%d'))
    # YTM Step
    print("Computing YTM")
    ytm = src.get_all_ytm(bonds, df, dates)
    src.plot_ytm(ytm, date_strs, OUTPUT_FOLDER)
    # Spot Rate Step
    print("Computing spot rates")
    sr = src.get_all_sr(bonds, df, dates, compounding_period=0)
    src.plot_sr(sr, date_strs, OUTPUT_FOLDER)

    # FR Step
    print("Computing forward rates")
    fr = src.get_all_fr(sr)
    src.plot_fr(fr, date_strs, OUTPUT_FOLDER)

    # Cov Step
    ## Compute ytm covariance metrics
    print("Computing covariance characteristics for YTM")
    year_sr = src.get_year_srs(sr)
    sr_cov = src.construct_cov(year_sr, src.daily_log_returns)
    print(src.matrix_to_latex(sr_cov))
    print(src.eval_evec_to_latex(sr_cov))
    ## Compute fr covariance metrics
    print("Computing covariance characteristics for forward rates")
    fr_cov = src.construct_cov(fr, src.daily_log_returns)
    print(src.matrix_to_latex(fr_cov))
    print(src.eval_evec_to_latex(fr_cov))
