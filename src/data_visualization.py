import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

bond_data_filename = "data/all_bond_data.csv"
output_folder = "output/"
today = pd.to_datetime("today")

def print_sorted_bond_dates_0_5():
    df = pd.read_csv("data/all_bond_data.csv")
    df = df.drop_duplicates(subset=['ISIN', 'Maturity Date'])
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])
    df['Issue Date'] = pd.to_datetime(df['Issue Date'])
    df['Coupon'] = df['Coupon'].str.rstrip("%").astype(float)
    date = pd.to_datetime("2030-01-01")
    df = df[df["Maturity Date"] < date]
    #df = df[(df["Coupon"] >= 2.0) & (df["Coupon"] <= 4.0)]
    print(df[["ISIN", "Issue Date", "Coupon", "Maturity Date"]].sort_values(by="Maturity Date", ascending=True))

def plot_coupon_date():
    df = pd.read_csv("data/all_bond_data.csv")
    df = df.drop_duplicates(subset=['ISIN', 'Maturity Date'])
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])
    date = pd.to_datetime("2030-01-01")
    df = df[df["Maturity Date"] < date]
    df = df.sort_values(by="Maturity Date", ascending=True)
    print(df)
    plt.figure()
    plt.scatter(df["Maturity Date"].dt.year, df["Coupon"].str.rstrip("%").astype(float))
    plt.savefig("bond_dates.pdf")

def plot_date_date():
    df = pd.read_csv("data/all_bond_data.csv")
    df = df.drop_duplicates(subset=['ISIN', 'Maturity Date'])
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])
    df['Issue Date'] = pd.to_datetime(df['Issue Date'])
    date = pd.to_datetime("2030-01-01")
    df = df[df["Maturity Date"] < date]
    date = pd.to_datetime("2010-01-01")
    df = df[df["Issue Date"] > date]
    plt.figure()
    plt.scatter(df["Maturity Date"].dt.year, df["Issue Date"].dt.year)
    plt.savefig("date_date.pdf")


print_sorted_bond_dates_0_5()
#plot_coupon_date()
#plot_date_date()
