from flask import Flask,render_template, redirect, request
import numpy as np
import tweepy 
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import re

app = Flask(__name__)

@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    userid = request.form.get('userid')


    #======================Insert Twitter API Here==========================
    consumerKey = "iBnbpKXoe6QqgEtddULWZrtfR"
    consumerSecret = "OUtn0OdYwzo6piGD9hv4jYPhaoWrIuqPXZGp4KSsI4vZgO18vz"
    accessToken = "2247094207-DNHVzUZO8Slx1BYxxJDDy9nuuGu65KBGkN6fSK1"
    accessTokenSecret = "UvvVx3z7KAUJ1uai3r8Ok8cA9CzTaSEENgpQHhCtXsMxk"
    #======================Insert Twitter API End===========================
    
    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)

    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity
    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    post = api.user_timeline(screen_name=userid, count = 500, lang ="en", tweet_mode="extended")
    twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])
    twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)
    twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
    twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)
    twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
    positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
    negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
    neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]
    positive_per = round((positive.shape[0]/twitter.shape[0])*100, 1)
    negative_per = round((negative.shape[0]/twitter.shape[0])*100, 1)
    neutral_per = round((neutral.shape[0]/twitter.shape[0])*100, 1)
    return render_template('sentiment.html', name=userid,positive=positive_per,negative=negative_per,neutral=neutral_per)

@app.route('/')
def home():
    return render_template('index.html')

app.run(debug=True)
