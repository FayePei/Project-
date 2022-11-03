import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    keys = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])

    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    tweets = api.user_timeline(
        screen_name=name, 
        count=100,
        include_rts = False,
    )
    tweets2 = []
    result = {
        "user": name,
        "count": len(tweets),
        "tweets": tweets2,
    }
    sid_obj = SentimentIntensityAnalyzer()
    for tweet in tweets:
        try:
            text = str(tweet.text)
        except Exception:
            text = tweet.text.encode("ascii", "ignore").decode()
        tweets2.append({
            "id": tweet.id,
            "created": tweet.created_at,
            "retweeted": tweet.retweet_count,
            "text": text,
            "hashtags": [x["text"] for x in tweet.entities["hashtags"]],
            "urls": [x["url"] for x in tweet.entities["urls"]],
            "mentions": [x["screen_name"] for x in tweet.entities["user_mentions"]],
            "score": sid_obj.polarity_scores(text)["compound"],
        })
    return result


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get the list of User objects back from friends();
    get a maximum of 100 results. Pull the appropriate values from
    the User objects and put them into a dictionary for each friend.
    """
    friends = api.get_friends(screen_name=name, count=100)
    results = []
    for friend in friends:
        results.append({
            "name": friend.name,
            "screen_name": friend.screen_name,
            "followers": friend.followers_count,
            "created": friend.created_at.date(),
            "image": friend.profile_image_url,
        })
    return results
