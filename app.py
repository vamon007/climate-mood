import os
import dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime

app = dash.Dash(__name__)
server = app.server
app.title = 'Climate Mood Dashboard'

tweet_db_url = os.environ["DATABASE_URL"]

def get_df_from_db():

    engine = create_engine(tweet_db_url)

    df = pd.read_sql_table('tweets', engine)

    return df

tdf = get_df_from_db()
app.layout = html.Div(children=[
    html.H1(children='Climate Moods'),

    html.Div(children='''
             Twitter sentiment analysis on moods on climate change.
    '''),

    dcc.Graph(
        id='line',
        figure={
            'data': [
                {'x': tdf.TimeStamp, 'y': tdf["Polarity"], 
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
