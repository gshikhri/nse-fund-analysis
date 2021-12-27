import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import json
import requests
import datetime as dt
import numpy as np
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


end_date = dt.datetime.now().date()
start_date = end_date - dt.timedelta(days=3*365)

mf_dict = {
    'uti-nifty-index': 'https://api.mfapi.in/mf/120717', 
    'HDFC-index-fund': 'https://api.mfapi.in/mf/101281',
    'Nippon-index-fund': 'https://api.mfapi.in/mf/118791',
    'ICICI-index-fund': 'https://api.mfapi.in/mf/141841',
    'TATA-index-fund': 'https://api.mfapi.in/mf/119287', 
    'Mirae-largecap':'https://api.mfapi.in/mf/118825'
}

fund_nav_df = get_fund_nav_df(mf_dict, start_date, end_date)



app = Dash(__name__)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Compare Mutual funds", style={'text-align': 'center'}),

    dcc.Dropdown(id="select_mf",
                 options=[
                    {"label": "uti nifty index", "value": "uti-nifty-index"}, 
                    {"label": "HDFC index fund", "value": "HDFC-index-fund"},
                    {"label": "Nippon index fund", "value": "Nippon-index-fund"},
                    {"label": "ICICI index fund", "value": "ICICI-index-fund"},
                    {"label": "TATA index fund", "value": "TATA-index-fund"}, 
                    {"label": "Mirae largecap", "value": "Mirae-largecap", }],
                 multi=True,
                 value='uti-nifty-index',
                 style={'width': "50%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='plot_fund_nav', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='plot_fund_nav', component_property='figure')],
    [Input(component_id='select_mf', component_property='value')]
)

def update_graph(option_selected):
    print(option_selected)
    print(type(option_selected))

    container = "Funds selected: {}".format(option_selected)

    dff = fund_nav_df.copy()
    dff = dff[option_selected]

    fig = px.line(dff.divide(dff.iloc[0]) * 100)

    return container, fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)