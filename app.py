import os
import dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import gspread
from gspread_dataframe import get_as_dataframe
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials

app = dash.Dash(__name__)
server = app.server
app.title = 'Climate Mood Dashboard'

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']

def get_climate_mood_sheet():
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    scope = ['https://www.googleapis.com/auth/drive']

    creds = service_account.Credentials.from_service_account_file(
        'credentials_climate_mood.json', scopes=SCOPES)
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials_climate_mood.json', scope)
    client = gspread.authorize(creds)

    #gsheet = client.open('Climate Trends Dataset').sheet1.get_all_records()
    gsheet = get_as_dataframe(client.open('Climate Mood').sheet1)

    return gsheet

df = get_climate_mood_sheet()
app.layout = html.Div(children=[
    html.H1(children='Climate Moods'),

    html.Div(children='''
             Twitter sentiment analysis on moods on climate change.
    '''),

    dcc.Graph(
        id='line',
        figure={
            'data': [
                {'y': df["Polarity"], 
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
