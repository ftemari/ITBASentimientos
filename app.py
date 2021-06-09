from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions
import json
import os
import tweepy
import time

app = Flask(__name__)
app.config["DEBUG"] = True
api = Api(app)

# Local variables
consumer_key = "dATweJ6Kk5PoYVnwARz0Utfh9"
consumer_secret = "Ku39okApA0evSqqPuHhrfAhhCeqCvzAE6vbDIbzBcLr7tRHgSv"

# Father class for any kind of tweet
class Tweet:
  def __init__(self, date, text, sentiment, score):
    self.date = date
    self.text = text
    self.sentiment = sentiment
    self.score = score 

  # def __str__(self):
    # return "Tweet Date:" % (self.date, self.b)

class PositiveTweet(Tweet):
  pass

class NegativeTweet(Tweet):
  pass

class NeutralTweet(Tweet):
  pass
 
_negativeTweets = []
_positiveTweets = []
_neutralTweets = []

data = {
    "foo": 3,
    "bar": {
        "x": 1,
        "y": 2
    }
}

@app.route('/', methods=['GET'])
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')


class Sentiments(Resource):
    def get(self):
        userName = "fedetemari" #@param {type:"string"}
        NumberOfTweets =  50 #@param {type:"integer"}
        language = "es" #@param {type:"string"}
        # set authorization for IBM NLU System
        authenticator = IAMAuthenticator('NolDkpvHtyofSQqeZJBkWbW6cnO_tbtg_XraTmEO_GD7')
        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2020-08-01', authenticator=authenticator)
        natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/d1fc640a-e327-45a5-b3d1-fd86a7263a8e')

        # Set authorization for tweepy library
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)


        api = tweepy.API(auth)


        for tweet in tweepy.Cursor(api.user_timeline, screen_name=userName, tweet_mode="extended").items(NumberOfTweets):

            response = natural_language_understanding.analyze(
            text=tweet.full_text,
            language= language,
            features=Features(sentiment=SentimentOptions())).get_result()
            if response["sentiment"]["document"]["label"] == "negative":
                #print("Negativo")
                _negativeTweets.append(NegativeTweet("malo", tweet.full_text, response["sentiment"]["document"]["label"] , response["sentiment"]["document"]["score"] ))
            elif response["sentiment"]["document"]["label"] == "neutral":
                _neutralTweets.append(NegativeTweet("malo", tweet.full_text, response["sentiment"]["document"]["label"] , response["sentiment"]["document"]["score"] ))
            else:
                # print("Positivo")
                _positiveTweets.append(PositiveTweet("bueno", tweet.full_text, response["sentiment"]["document"]["label"] , response["sentiment"]["document"]["score"] ))

        print("Comienza lista negativa con ", len(_negativeTweets), "tweets") 
        for negative in _negativeTweets:
            print(negative.__dict__)

        print("Termina Lista negativa")
        print("Comienza lista positiva con ", len(_positiveTweets), "tweets")
        # print(_negativeTweets)
        for positive in _positiveTweets:
            print(positive.__dict__)
            # print(_positiveTweets)
        print("Termina lista positiva")
        print("Comienza lista neutral con ", len(_positiveTweets), "tweets")
        # print(_negativeTweets)
        for neutral in _neutralTweets:
            print(neutral.__dict__)
        # print(_positiveTweets)
        print("Termina lista neutral")

        # parser = reqparse.RequestParser()
        # parser.add_argument('text', required=True)
        # args = parser.parse_args()
        # authenticator = IAMAuthenticator(
        #     'NolDkpvHtyofSQqeZJBkWbW6cnO_tbtg_XraTmEO_GD7')
        # natural_language_understanding = NaturalLanguageUnderstandingV1(
        #     version='2020-08-01',
        #     authenticator=authenticator)

        # natural_language_understanding.set_service_url(
        #     'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/d1fc640a-e327-45a5-b3d1-fd86a7263a8e')

        # response = natural_language_understanding.analyze(
        #     text=args['text'],
        #     language='en',
        #     features=Features(sentiment=SentimentOptions())).get_result()

        # # print(json.dumps(response, indent=2))
        
        # # return our data and 200 OK HTTP code
        
        return {'data': data}, 200

api.add_resource(Sentiments, '/sentiments')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
