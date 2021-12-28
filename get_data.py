import pandas as pd
import json
import requests
import datetime as dt
import yfinance as yf
import numpy as np

def get_fund_nav_df(mf_dict, start_date, end_date):
    fund_nav_df = pd.DataFrame()
    for fund_name in mf_dict.keys():
        api_url = mf_dict[fund_name]
        response = requests.get(api_url)
        nav = json.loads(response.text)
        nav_val = dict()
        for nav_data in nav['data']:
            date = dt.datetime.strptime(nav_data['date'], '%d-%m-%Y').date()
            nav_val[date] = float(nav_data['nav'])
        fund_nav_df[fund_name] = pd.Series(nav_val)

    fund_nav_df = fund_nav_df[::-1]
    return fund_nav_df[start_date:end_date]

def get_index_df(index_dict, start_date, end_date):
    index_df = pd.DataFrame()
    for index, index_ticker in index_dict.items():
        index_df[index] = yf.download(index_ticker, start=start_date, end=end_date)['Adj Close']
    return index_df

def compare_fund_stats(fund_nav_df, risk_free_rate=0):
    daily_returns = fund_nav_df.pct_change()
    mean = daily_returns.mean() * 248
    std = daily_returns.std() * np.sqrt(248)
    cumu_return = (fund_nav_df.iloc[-1]/fund_nav_df.iloc[0]) - 1    
    sharpe_ratio = (mean - risk_free_rate) / std
    downside_deviation = daily_returns[daily_returns<0].dropna().std()*np.sqrt(248)
    sortino_ratio = (mean - risk_free_rate) / downside_deviation

    start_date = fund_nav_df.index[0]
    end_date = fund_nav_df.index[-1]
    duration = end_date.year - start_date.year
    abs_returns = (fund_nav_df.iloc[-1]/ fund_nav_df.iloc[0] - 1) * 100
    cagr = (np.power((fund_nav_df.iloc[-1]/ fund_nav_df.iloc[0]), (1/duration)) - 1) * 100

    cols = ['Cumulative returns', 'Standard deviation', 'Mean returns', 
    'Downside deviation', 'Sharpe ratio', 'Sortino ratio', 'Absolute Returns', 'CAGR']
    stats = [cumu_return, std, mean, downside_deviation, sharpe_ratio, sortino_ratio, abs_returns, cagr]
    fund_stat_df = pd.DataFrame()
    for col, stat in zip(cols, stats):
        fund_stat_df[col] = stat
    return fund_stat_df  

def get_rolling_returns(fund_nav_df, rolling_window=365):
    roll_start_date_list = []
    roll_end_date_list = []
    roll_return_list = []

    for roll_start_date in fund_nav_df.index:
        roll_end_date = roll_start_date + dt.timedelta(days=rolling_window)
        
        roll_date_df = fund_nav_df[fund_nav_df.index >= roll_end_date]
        if (not roll_date_df.empty):
            roll_start_date_list.append(roll_start_date)
            roll_end_date_list.append(roll_date_df.index[0])

            roll_start_date_nav = fund_nav_df[fund_nav_df.index == roll_start_date]
            roll_end_date_nav = roll_date_df.iloc[0]
            roll_end_date_return = (roll_end_date_nav / roll_start_date_nav) - 1
            
            
            roll_return_list.append(roll_end_date_return)

    roll_return_df = pd.DataFrame()
    roll_return_df['start date'] = roll_start_date_list
    roll_return_df['end date'] = roll_end_date_list

    for column in fund_nav_df.columns:
        roll_return_df[column] = [i[column].to_numpy()[0] for i in roll_return_list]
    return roll_return_df
