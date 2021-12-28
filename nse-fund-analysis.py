import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import datetime as dt
from get_data import get_fund_nav_df, get_index_df, get_rolling_returns
from fund_keys import mf_dict, index_dict

end_date = dt.datetime.now().date()
start_date = end_date - dt.timedelta(days=3*365)

fund_nav_df = get_fund_nav_df(mf_dict, start_date, end_date)
index_df = get_index_df(index_dict, start_date, end_date)

rolling_returns = get_rolling_returns(fund_nav_df)

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
    dcc.Dropdown(id="select_index",
                 options=[
                    {"label": "Nifty 50", "value": "nifty50"}, 
                    {"label": "Sensex 30", "value": "sensex30"}],
                 multi=True,
                 value='nifty50',
                 style={'width': "50%"}
                 ),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='plot_fund_nav', figure={}), 
    dcc.Graph(id='plot_rolling_returns', figure={})
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'), 
    Output(component_id='plot_fund_nav', component_property='figure'), 
    Output(component_id='plot_rolling_returns', component_property='figure')],
    [Input(component_id='select_mf', component_property='value'), 
    Input(component_id='select_index', component_property='value')]
)

def update_graph(fund_selected, index_selected):
    container = "Funds selected: {}, Benchmark selected: {}".format(fund_selected, index_selected)

    nav_df = fund_nav_df.copy()
    nav_df = nav_df[fund_selected]

    ind_df = index_df.copy()
    ind_df = ind_df[index_selected]

    merge_df = pd.merge(left=nav_df, right=ind_df, left_index=True, right_index=True)

    nav_fig = px.line(merge_df.divide(merge_df.iloc[0]) * 100, \
        title='Fund NAV comparison (initial investment Rs 100)', \
            template='ggplot2')

    roll_ret_df = rolling_returns.copy()
    roll_ret_df = roll_ret_df[fund_selected]
    roll_ret_fig = px.line(roll_ret_df, \
        title='Rolling returns (Rolling window=365 days)', \
            template='ggplot2')

    return container, nav_fig, roll_ret_fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)