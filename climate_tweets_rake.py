import os
import tweepy
from tweepy import OAuthHandler
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
import re
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from textblob import TextBlob

#Environment Variables to Twitter App
consumerKey = os.environ["CONSUMER_KEY"]
consumerSecret = os.environ["CONSUMER_SECRET"]
accessToken = os.environ["ACCESS_TOKEN"]
accessTokenSecret = os.environ["ACCESS_TOKEN_SECRET"]

# Declaring relevant Variables
positive = 0
negative = 0
neutral = 0
polarityVal = []
subjectivityVal = []
tweetsArray = []
timestampArray = []
utfArray = []


SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']

def tweets_to_sheet():

        # Authenticate with Google Drive API
        scope = ['https://www.googleapis.com/auth/drive']

        creds = service_account.Credentials.from_service_account_file('credentials_climate_mood.json', scopes=SCOPES)
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials_climate_mood.json', scope)
        client = gspread.authorize(creds)

        gsheet = client.open('Climate Mood').sheet1.get_all_records()

        # Authenticating the Twitter Application and creating an object to use the Twitter API
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Clear the Google Sheet
        client.open('Climate Mood').values_clear("Sheet1")
	
        #Get the tweets
        tweets = tweepy.Cursor(api.search, q='climate change').items(1000)
	
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

        # Write to Google Sheet
        set_with_dataframe(client.open('Climate Mood').sheet1, tweet_frame)
	
        pass


tweets_to_sheet()
