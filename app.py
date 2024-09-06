from dash import Dash, html, dcc, callback, Output, Input
import sqlite3
import plotly.express as px
import pandas as pd
import json
from io import StringIO
from datetime import datetime
from utils.data_processor import *

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Network Traffic Analyser'),
    dcc.Graph(id='bandwidth_usage'),
    dcc.Input(id='top_n_results',
              value=10,
              placeholder='Top n results',
              type='number'),
    dcc.Graph(id='usage_by_ip'),
    dcc.Dropdown(id='protocol_filter', multi=True),
    html.Div(id='usage_by_protocol'),
    dcc.Store(id='intermediate-value'),
    dcc.Store(id='bandwidth_store'),
    dcc.Store(id='unique_protocols'),
    dcc.Store(id='selected_protocols'),
    dcc.Interval(id='interval',
                  interval=1*1000,
                  n_intervals=1)
])

@app.callback(Output('intermediate-value', 'data'), Input('interval', 'n_intervals'))
def update_data(n_intervals):
    con = sqlite3.connect("data/database.db")
    data = pd.read_sql("SELECT * FROM NetworkTraffic", con)
    con.close()
    return data.to_json(orient='split')

@app.callback(Output('usage_by_ip', 'figure'), [Input('intermediate-value', 'data'), Input('top_n_results', 'value')])
def usage_by_ip(data, top_n):
    df = pd.read_json(StringIO(data), orient='split', date_unit='s')
    per_ip_df = df.loc[:, ["source_address", "frame_length"]].groupby(by='source_address').sum().reset_index().sort_values("frame_length", ascending=False)
    if top_n is not None:
        per_ip_df = per_ip_df.head(top_n)
    fig = px.bar(per_ip_df,
                 x='source_address',
                 y='frame_length',
                 labels={'source_address': "Source Address",
                         'frame_length': "Total Bytes"},
                 title="Usage by IP")
    return fig

@app.callback(Output('bandwidth_store', 'data'), [Input('intermediate-value', 'data'), Input('bandwidth_store', 'data')])
def calc_bandwidth(data, bandwidth_store):
    datalength = 30
    df = pd.read_json(StringIO(data), orient='split', date_unit='s')
    if bandwidth_store is None:
        bandwidth_store = {'index':[], 'columns':["time", "bandwidth_usage"], 'data':[]}
    else:
        bandwidth_store = json.loads(bandwidth_store)
    new_bandwidth = calculate_bandwidth(df)
    new_data_point = [datetime.now().ctime().split(" ")[-2], new_bandwidth]
    bandwidth_store["data"].append(new_data_point)
    while (len(bandwidth_store["data"]) > datalength):
        bandwidth_store["data"].pop(0)
    bandwidth_store['index'] = [i for i in range(len(bandwidth_store["data"]))]
    return json.dumps(bandwidth_store)

@app.callback(Output('bandwidth_usage', 'figure'), Input('bandwidth_store', 'data'))
def display_bandwidth_usage(data):
    df = pd.read_json(StringIO(data), orient='split')
    fig = px.line(df,
                  x='time',
                  y='bandwidth_usage',
                  labels={'time': "Time",
                          'bandwidth_usage': "Bandwidth Usage (bytes/s)"},
                  title='Bandwidth Usage')
    return fig

@app.callback(Output('unique_protocols', 'data'), Input('intermediate-value', 'data'))
def get_unique_protocols(data):
    df = pd.read_json(StringIO(data), orient='split')
    unique_protocols = list(df.loc[:, "protocols"].unique())
    return json.dumps(unique_protocols)

@app.callback(Output('protocol_filter', 'options'), [Input('unique_protocols', 'data')])
def filter_p(data):
    protocols = json.loads(data)
    return protocols

@app.callback(Output('usage_by_protocol', 'children'), [Input('intermediate-value', 'data'), Input('protocol_filter', 'value')])
def protocol_display(data, p_filter):
    display_list = []
    df = pd.read_json(StringIO(data), orient='split')
    per_protocol_df = df.loc[:, ["source_address", "frame_length", "protocols"]].groupby(by=['protocols', 'source_address']).sum().reset_index().sort_values("frame_length", ascending=False)
    if p_filter is None:
        p_filter = []
    if len(p_filter) > 0:
        iterating_list = p_filter
    else:
        iterating_list = per_protocol_df.loc[:, "protocols"].unique()
    for p in iterating_list:
        dfp = per_protocol_df.loc[per_protocol_df.loc[:, "protocols"] == p, ["source_address", "frame_length"]]
        fig = px.bar(dfp,
                     x='source_address',
                     y ='frame_length',
                     labels={'source_address': 'Source Address',
                             'frame_length': 'Total Bytes'},
                     title=f"Usage by Protocol: {p}")
        display_list.append(dcc.Graph(figure=fig))
    return html.Div(display_list)

if __name__ == '__main__':
    app.run(debug=True)
