# AdaHack 2022 submission
# Built in a few hours! :)
# Sholto, Josh, Nikita, Amisha, Alice

# Web server that queries the Twitter API for 500 recent tweets containing keywords
# It then analyses other words appearing and returns the number of occurrences so they
# can be visualised in the front-end

from flask import Flask, request, jsonify
import tweepy
import string
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
stop_words = set(stopwords.words("english"))
twitter_bearer_token = open("bearer_token.txt", "r").read()

client = tweepy.Client(twitter_bearer_token)

@app.route('/getWordMap')
def getWordMap():
    sentiments = {}
    words = {}

    def search_twitter(search_query):
        paginator = tweepy.Paginator(client.search_recent_tweets,
                                     query=search_query, 
                                     max_results=100, 
                                     limit=5)
        for tweet in paginator.flatten(limit=500):
            build_dictionary(tweet)
            get_sentiment(tweet)


    def sanitise_word(word):
        w = word.lower()
        w = w.translate(str.maketrans('', '', string.punctuation))
        if w not in stop_words and len(w) > 1 and w != "&amp;":
            return w
        return ""
        
    def build_dictionary(tweet):
        tweet_words = [sanitise_word(t) for t in tweet.text.split(" ")]
        for word in tweet_words:
            if word not in words and word != "":
                words[word] = 1
            elif word != "":
                words[word] += 1

    def round_nearest(x, a):
        return round(round(x / a) * a, 1)
    
    def get_sentiment(tweet):
        sentiment = TextBlob(tweet.text).sentiment.polarity
        nearest_category = round_nearest(sentiment, 0.2)
        if nearest_category not in sentiments:
            sentiments[nearest_category] = 1
        else:
            sentiments[nearest_category] += 1
    
    search_term = request.args.get("word")
  
    if search_term is None:
        return "[]" # Return empty array to the client so the word map generates nothing
    
    search_query = f"({search_term}) -is:retweet lang:en"
    search_twitter(search_query)
    # Sort dictionary of words by number of mentions, where the number of mentions is greater than 10
    sorted_dict = [{"x": t, "value": words[t]} for t in dict(sorted(words.items(), key=lambda item: item[1], reverse=True)) if words[t] > 10]

    response = jsonify({"words": sorted_dict, "sentiments": sentiments})
    response.headers.add("Access-Control-Allow-Origin", "*") # Enable CORS so the front-end canc be hosted elsewhere and still can access
    return response

if __name__ == '__main__':
   app.run()