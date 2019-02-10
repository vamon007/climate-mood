import os
import tweepy
from tweepy import OAuthHandler
import pandas as pd
import re
from textblob import TextBlob
import psycopg2
from sqlalchemy import create_engine

# Environment Variables to Twitter App
consumerKey = os.environ["CONSUMER_KEY"]
consumerSecret = os.environ["CONSUMER_SECRET"]
accessToken = os.environ["ACCESS_TOKEN"]
accessTokenSecret = os.environ["ACCESS_TOKEN_SECRET"]

# Environment Variables to Database
tweet_db_url = os.environ["DATABASE_URL"]

# Declaring relevant Variables
positive = 0
negative = 0
neutral = 0
polarityVal = []
subjectivityVal = []
tweetsArray = []
timestampArray = []
utfArray = []

def tweets_to_db():

        # Authenticating the Twitter Application and creating an object to use the Twitter API
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        #Get the tweets
        tweets = tweepy.Cursor(api.search, q='climate change -filter:retweets -filter:replies', lang='en').items(10000)
	
        # Creating a list of String Tweets
        for tweet in tweets:
            tweetsArray.append(tweet.text)
            timestampArray.append(tweet.created_at)
            utfArray.append(tweet.text.encode("utf-8"))
	
        # Cleaning a Tweet String
        def cleanTweet(tweet):
            # Remove Links, Special Characters etc from tweet
            return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet).split())

        # Perform Sentiment Analysis
        for tweet in tweetsArray:
            t = cleanTweet(tweet)
            analysis = TextBlob(t)
            polarityVal.append(analysis.sentiment.polarity)
            subjectivityVal.append(analysis.sentiment.subjectivity)

        # Create pandas dataframe from arrays
        tweet_frame = pd.DataFrame({"Tweets":tweetsArray, "TimeStamp":timestampArray, "UTF Offset":utfArray, "Polarity":polarityVal, "Subjectivity":subjectivityVal}, columns=["Tweets", "TimeStamp", "UTF Offset", "Polarity", "Subjectivity"])

        # Connect to Heroku and write to db
        engine = create_engine(tweet_db_url)
        tweet_frame.to_sql('tweets', con=engine, if_exists='replace')
	
        pass


tweets_to_db()
