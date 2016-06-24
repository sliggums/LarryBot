from tweepy import Stream, OAuthHandler, API
from tweepy.streaming import StreamListener
from tweepy.error import TweepError
#from twitter import OAuth, Twitter
import json
import time
import random
import datetime
import re
import csv

ACCESS_TOKEN = raw_input()
ACCESS_SECRET = raw_input()
CONSUMER_KEY = raw_input()
CONSUMER_SECRET = raw_input()

BAG_OF_WORDS = ["RT giveaway", "RT #win", "RT chance win", "RT giving away", "RT to enter"]
BANNED_USERS = ['competition', "bot", "safarics", "csgo", "fut", "pokemon"]
BANNED_WORDS = ["rt@", "csgo", "dragon", "rose", "blackops", "pokemon", "cod", "header", "baby", "madden", "fifa"]
MIN_FOLLOWERS = 3000
ENDING = ["by", "ends", "selected", "winner", "today", "tomorrow", "closes", "picked"]
#current idea: try to infer the tweet's date and place them into files.

def tweet(data):
    formatted = json.loads(data)
    # If it's a reply, we know it's not what we want.
    if formatted['in_reply_to_status_id']:
        return

    # Get the correct tweet to read.
    try:
        correct_tweet = formatted['retweeted_status']
    except KeyError:
        correct_tweet = formatted

    # Make sure user is of some status and is not reposting something.
    curr_followers = correct_tweet['user']['followers_count']
    if curr_followers < MIN_FOLLOWERS or correct_tweet['entities']['urls']:
        return

    # Check whether it's something we don't want, which we specify at the top.
    screen_name = correct_tweet['user']['screen_name']
    tweet = correct_tweet['text']
    tweet_lower = tweet.lower().replace(" ", "")
    for word in BANNED_WORDS:
        if word in tweet_lower:
            return
    user_lower = screen_name.lower()
    for user in BANNED_USERS:
        if user in user_lower:
            return

    # Check that this isn't an actual retweet.
    try:
        others = correct_tweet['entities']['user_mentions']
        for person in others:
            other = int(person['id'])
            other_followers = t.get_user(other).followers_count
            if curr_followers < other_followers:
                return
            # If asking us to follow a smaller account, we comply sometimes.
            elif len(others) == 1 and curr_followers > other_followers:
                if random.random() > 0.3:
                    t.create_friendship(user_id=other)
                    writer.writerow([other])
    except KeyError:
        pass

    # If all pass, we retweet.
    try:
        tweet_id = correct_tweet['id']
        user_id = correct_tweet['user']['id']
        if "like" in tweet_lower:
            t.create_favorite(tweet_id)
        t.retweet(tweet_id)
        t.create_friendship(user_id=user_id)
        writer.writerow([user_id])
        print "finished"
        time.sleep(random.random() * 50)
    except TweepError as e:
        pass

class WinStreamListener(StreamListener):
    def on_data(self, data):
        tweet(data)

oauth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
t = API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

today = (datetime.datetime.today() + datetime.timedelta(days=7)).day
f = open(str(today) + ".csv", "a")
writer = csv.writer(f)

# def search_twitter():
#     print twit.search.tweets(q=BAG_OF_WORDS[1])['statuses']
# twit = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
# search_twitter()

stream = Stream(oauth, WinStreamListener(), async=True, languages=['en'])
while True:
    try:
        stream.filter(track=BAG_OF_WORDS, stall_warnings=True)
    except BaseException as e:
        print e