import os
import dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from numpy import arange,array,ones
from scipy import stats
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
from pandas.tseries.offsets import *

app = dash.Dash(__name__)
server = app.server
app.title = 'Climate Mood Dashboard'

tweet_db_url = os.environ['DATABASE_URL']

def get_df_from_db():

    engine = create_engine(tweet_db_url)

    df = pd.read_sql_table('tweets', engine)

    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s')
    df = df.set_index(df['TimeStamp'])
    df = df[~df.index.duplicated(keep='first')].sort_index()

    df = df.loc[df.iloc[df.index.get_loc((df.index[-1] - pd.DateOffset(hours=1)), method='nearest')]['TimeStamp']:df.index[-1]]

    return df

def mood_verbosity():

    tdf['Verbosity'] = tdf['Tweets'].str.len()

    mood_v = pd.DataFrame({'Positive': tdf[tdf['Polarity'] > 0]['Verbosity'].mean(), 
                           'Neutral': tdf[tdf['Polarity'] == 0]['Verbosity'].mean(),
                           'Negative': tdf[tdf['Polarity'] < 0]['Verbosity'].mean()
                         }, index=[0])

    return mood_v

def popular_moods():

    pop_mood = pd.DataFrame({'Positive': len(tdf[tdf['Polarity'] > 0]),
                             'Neutral': len(tdf[tdf['Polarity'] == 0]),
                             'Negative': len(tdf[tdf['Polarity'] < 0])
                           }, index=[0])

    return pop_mood

def average_subjectivity():

    mood_subj = pd.DataFrame({'Positive': tdf[tdf['Polarity'] > 0]['Subjectivity'].mean(),
                           'Negative': tdf[tdf['Polarity'] < 0]['Subjectivity'].mean()
                         }, index=[0])

    mood_subj = mood_subj.abs()

    return mood_subj

tdf = get_df_from_db()
mdf = mood_verbosity()
pdf = popular_moods()
adf = average_subjectivity()
app.layout = html.Div(children=[
    html.Div(children=[
        html.H1(children='Climate Mood'),
        html.Div(children=['''
             Twitter sentiment analysis on climate change
        ''', 

            html.A(html.Button('Source Code!'),
                href='https://github.com/aakashhdesai/climate-mood',
            )
        ], className='description'),
    ], className='navigation'),

    html.Div(children=[

        html.Div(children=[
            html.H3(children=['Tweet Sentiment vs. Time']),
            html.Div(id='tweet-content')
        ], className='senti-title'),
        dcc.Graph(
            id='sentiment-chart',
            figure={
                'data': [
                    go.Bar(
                        x=tdf.index, y=tdf['Polarity'], customdata=tdf['Polarity']
                    ),
                ],
                'layout': go.Layout(
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                    hovermode='closest',
                    legend=dict(
                        x=0,
                        y=1,
                        traceorder='normal',
                        font=dict(
                            size=12,
                            color='#000'
                        ),
                        bgcolor='#E2E2E2',
                        bordercolor='#FFFFFF',
                        borderwidth=2
                        )
                )
            }
        )
    ], className='sentiment'),

    html.Div(children=[
        html.Div(children=[
            html.H3(children=['''Mood Verbosity''']),
            html.Div(children=[
                dcc.Graph(
                    figure={
                        'data': [go.Bar(x=mdf.iloc[0],
                                        y=['Positive', 'Neutral', 'Negative'],
                                        orientation='h',
                                        text=mdf.iloc[0].round(2),
                                        textposition = 'auto',
                                        marker={'color': ['#5fbf41', '#417cbf', '#bf5241']})
                        ],
                        'layout': go.Layout(
                                  title='Avg Characters per Tweet',
                                  hovermode=False,
                                  xaxis=dict(showgrid=False, zeroline=False, ticks='', showticklabels=False),
                                  yaxis=dict(showgrid=False, zeroline=False, ticks='', showticklabels=False),
                                  margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                                  width=300,
                                  height=300
                        )
                    })
            ], className='verbosity')
        ], className = 'analysis'),

        html.Div(children=[
            html.H3(children=['''Popular Moods''']),
            html.Div(children=[
                dcc.Graph(
                    figure={
                        'data': [go.Pie(values=pdf.iloc[0],
                                        labels=['Positive', 'Neutral', 'Negative'],
                                        text=pdf.iloc[0].round(2),
                                        marker={'colors': ['#5fbf41', '#417cbf', '#bf5241']})
                        ],
                        'layout': go.Layout(
                                  title='Sum of Tweets per Mood',
                                  hovermode=False,
                                  xaxis=dict(showgrid=False, zeroline=False, ticks='', showticklabels=False),
                                  yaxis=dict(showgrid=False, zeroline=False, ticks='', showticklabels=False),
                                  margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                                  width=300,
                                  height=300,
                                  showlegend=False
                        )
                    })
            ], className='popular')
        ], className = 'analysis'),

        html.Div(children=[
            html.H3(children=['''Mood Rating''']),
            html.Div(children=[
                dcc.Graph(
                    figure={
                        'data': [go.Bar(y=adf.iloc[0],
                                        x=['Positive', 'Negative'],
                                        text=adf.iloc[0].round(2),
                                        textposition = 'auto',
                                        marker={'color': ['#49ad4b', '#ad4b49']})
                        ],
                        'layout': go.Layout(
                                  title='Avg Subjectivity per Mood',
                                  hovermode=False,
                                  xaxis=dict(showgrid=False, zeroline=False, ticks='', showticklabels=False),
                                  yaxis=dict(showgrid=False, zeroline=False, ticks='', showticklabels=False),
                                  margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                                  width=300,
                                  height=300
                        )
                    })
            ], className='mood-ratio')

        ], className = 'analysis')
    ], className='mood-stats')
])

@app.callback(
    dash.dependencies.Output('tweet-content', 'children'),
    [dash.dependencies.Input('sentiment-chart', 'hoverData')])
def update_text(hoverData):
    s = 'Hover over points to show the tweet here!' if bool(hoverData) == False else tdf[tdf['Polarity'] == hoverData['points'][0]['customdata']].iloc[0]['Tweets']
    return html.P(
        '{}'.format(s)
)

if __name__ == '__main__':
    app.run_server(debug=True)
