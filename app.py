import dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import tweepy
import re
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
from textblob import TextBlob

app = dash.Dash(__name__)

# Declaring relevant Variables
polarityVal = []
positive = 0
negative = 0
neutral = 0 
subjectivityVal = []
tweetsArray = []

#Environment Variables to Twitter App
consumerKey = CONSUMER_KEY
consumerSecret = CONSUMER_SECRET
accessToken = ACCESS_TOKEN
accessTokenSecret = ACCESS_TOKEN_SECRET

# Authenticating the Twitter Application and creating an object to use the Twitter API
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Storing the tweets
tweets = tweepy.Cursor(api.search, q='climate change').items(1000)

# Creating a list of String Tweets
for tweet in tweets:
    tweetsArray.append(tweet.text)

# Cleaning a Tweet String
def cleanTweet(tweet):
    # Remove Links, Special Characters etc from tweet
    return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet).split())

# Performing Sentiment Analysis
for tweet in tweetsArray:
    t = cleanTweet(tweet)
    analysis = TextBlob(t)
    polarityVal.append(analysis.sentiment.polarity)
    subjectivityVal.append(analysis.sentiment.subjectivity)

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
    ),

    dcc.Graph(
        id='line',
        figure={
            'data': [
                {'y': subjectivityVal,
                 'type': 'basic-line',},
            ],
            'layout': {
                'title': 'Subjectivity Trend of the Tweets'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
