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
    dcc.Graph(id='usage_by_ip'),
    html.Div(id='usage_by_protocol'),
    dcc.Store(id='intermediate-value'),
    dcc.Store(id='bandwidth_store'),
    dcc.Interval(id='interval',
                  interval=5*1000,
                  n_intervals=1)
])

@app.callback(Output('intermediate-value', 'data'), Input('interval', 'n_intervals'))
def update_data(n_intervals):
    con = sqlite3.connect("data/database.db")
    data = pd.read_sql("SELECT * FROM NetworkTraffic", con)
    con.close()
    return data.to_json(orient='split')

@app.callback(Output('usage_by_ip', 'figure'), Input('intermediate-value', 'data'))
def usage_by_ip(data):
    df = pd.read_json(StringIO(data), orient='split', date_unit='s')
    per_ip_df = df.loc[:, ["source_address", "frame_length"]].groupby(by='source_address').sum().reset_index().sort_values("frame_length", ascending=False)
    fig = px.bar(per_ip_df,
                 x='source_address',
                 y='frame_length',
                 labels={'source_address': "Source Address",
                         'frame_length': "Frame Length"},
                 title="Usage by IP")
    return fig

@app.callback(Output('bandwidth_store', 'data'), [Input('intermediate-value', 'data'), Input('bandwidth_store', 'data')])
def calc_bandwidth(data, bandwidth_store):
    datalength = 20
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

@app.callback(Output('usage_by_protocol', 'children'), Input('intermediate-value', 'data'))
def protocol_display(data):
    display_list = []
    df = pd.read_json(StringIO(data), orient='split')
    per_protocol_df = df.loc[:, ["source_address", "frame_length", "protocols"]].groupby(by=['protocols', 'source_address']).sum().reset_index().sort_values("frame_length", ascending=False)
    for p in per_protocol_df.loc[:, "protocols"].unique():
        dfp = per_protocol_df.loc[per_protocol_df.loc[:, "protocols"] == p, ["source_address", "frame_length"]]
        fig = px.bar(dfp, x='source_address', y='frame_length', title=f"Usage by Protocol: {p}")
        display_list.append(dcc.Graph(figure=fig))
    return html.Div(display_list)

if __name__ == '__main__':
    app.run(debug=True)
