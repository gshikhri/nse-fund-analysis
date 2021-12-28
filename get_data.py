import pandas as pd
import json
import requests
import datetime as dt
import yfinance as yf

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
