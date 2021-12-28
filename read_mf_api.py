import pandas as pd
import json
import requests
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import yfinance as yf



def prepare_date_fig(interval=180):
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    fig.autofmt_xdate()
    return fig, ax


def plot_rolling_returns(roll_ret_df, interval=90):
    fig, ax = prepare_date_fig(interval)
    roll_ret_df.set_index('end date').plot(ax=ax)
    ax.set_xlabel('Duration of investment')
    ax.set_ylabel('NAV')
    ax.set_title('Rolling returns')
    plt.legend()
    fig.tight_layout()
    plt.show()

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

def compare_mf_norm(fund_nav_df, initial_investment=100, interval=180):
    fig, ax = prepare_date_fig(interval)
    fund_norm_nav_df = fund_nav_df.divide(fund_nav_df.iloc[0]) * initial_investment
    fund_norm_nav_df.plot(ax=ax)
    ax.set_xlabel('Duration of investment')
    ax.set_ylabel('NAV')
    ax.set_title('Fund NAV comparison with initial investment of: {}'.format(initial_investment))
    plt.legend()
    fig.tight_layout()
    plt.show()
    
def plot_mf_nav(fund_name, mf_nav_series, interval=180):
    fig, ax = prepare_date_fig(interval)
    mf_nav_series.plot(ax=ax, label=fund_name)
    ax.set_xlabel('Duration of investment')
    ax.set_ylabel('NAV')
    ax.set_title('Historical NAV')
    plt.legend()
    fig.tight_layout()
    plt.show()
    
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


# def compare_with_index(fund_nav_df, index_df, interval=90, initial_investment=100):
#     fig, ax = prepare_date_fig(interval)
#     fund_nav = fund_nav_df['uti-nifty-index']
#     fund_norm_nav_df = fund_nav.divide(fund_nav.iloc[0]) * initial_investment
#     fund_norm_nav_df.plot(ax=ax)

#     norm_index = 

#     ax.set_xlabel('Duration of investment')
#     ax.set_ylabel('NAV')
#     ax.set_title('Fund NAV comparison with initial investment of: {}'.format(initial_investment))
#     plt.legend()
#     fig.tight_layout()
#     plt.show()


def get_fund_tracking_error(fund_nav_df, index_df, start_date, end_date):
    pass


def get_index_df(index_ticker, start_date, end_date):
    index_df = pd.DataFrame()
    index_df['nifty50'] = yf.download(index_ticker, start=start_date, end=end_date)['Adj Close']
    return index_df

mf_dict = {
    'uti-nifty-index': 'https://api.mfapi.in/mf/120717', 
    'HDFC-index-fund': 'https://api.mfapi.in/mf/101281',
    'Nippon-index-fund': 'https://api.mfapi.in/mf/118791',
    'ICICI-index-fund': 'https://api.mfapi.in/mf/141841',
    'TATA-index-fund': 'https://api.mfapi.in/mf/119287', 
    'Mirae-largecap':'https://api.mfapi.in/mf/118825'
}
index_dict = {
    'nifty50': '^NSEI'
}

end_date = dt.datetime.now().date()
start_date = end_date - dt.timedelta(days=3*365)

fund_nav_df = get_fund_nav_df(mf_dict, start_date, end_date)
index_df = get_index_df(index_dict['nifty50'], start_date, end_date)

print(compare_fund_stats(fund_nav_df))

rolling_returns = get_rolling_returns(fund_nav_df)
# plot_rolling_returns(rolling_returns)

#plotting the normalized MF with it's index
fig, ax = plt.subplots()
((fund_nav_df/fund_nav_df.iloc[0])*100).plot(ax=ax, legend=True)
((index_df['nifty50']/index_df['nifty50'].iloc[0])*100).plot(ax=ax, legend=True)
plt.show()

# plotting the difference

norm_fund_nav_df = (fund_nav_df/fund_nav_df.iloc[0])*100
norm_index_df = (index_df['nifty50']/index_df['nifty50'].iloc[0])*100

track_error_df = pd.DataFrame()
for col in norm_fund_nav_df.columns:
    track_error_df[col] = norm_fund_nav_df[col] - norm_index_df

# print(track_error_df.head())



track_error_df.hist()
plt.show()

a = 1

# compare_mf_norm(fund_nav_df)
# print(get_fund_investment_return(fund_nav_df))
# print(compare_fund_stats(fund_nav_df))

# rolling_returns = get_rolling_returns(fund_nav_df)
# rolling_returns.head()
# plot_rolling_returns(rolling_returns)
