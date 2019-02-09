import os
import dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials

app = dash.Dash(__name__)
app.title = 'Climate Mood Dashboard'

#Environment Variables to Twitter App
consumerKey = os.environ["CONSUMER_KEY"]
consumerSecret = os.environ["CONSUMER_SECRET"]
accessToken = os.environ["ACCESS_TOKEN"]
accessTokenSecret = os.environ["ACCESS_TOKEN_SECRET"]

app.layout = html.Div(children=[
    html.H1(children='Climate Moods'),

    html.Div(children='''
             Twitter sentiment analysis on moods on climate change.
    '''),

    dcc.Graph(
        id='line',
        figure={
            'data': [
                {'y': polarityVal, 
                 'type': 'basic-line',},    
            ],
            'layout': {
                'title': 'Polarity Trend of the Tweets'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
