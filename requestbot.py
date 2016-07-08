import requests
from requests_oauthlib import OAuth1

import time
import random
import datetime
import csv

g = open('config.txt', 'r')
lines = g.readlines()
for i in range(len(lines)):
    lines[i] = lines[i].strip()

ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = lines
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

class LarryError(Exception):
    def __init__(self, error_msg):
        self.error_msg = msg
    def __str__(self):
        return repr(self.error_msg)

class LarryBot:

    BAG_OF_WORDS = ["RT giveaway", "RT #win", "RT chance win", "RT giving away", "RT to enter"]
    BANNED_USERS = ['competition', "bot", "safarics", "csgo", "fut", "pokemon"]
    BANNED_WORDS = ["rt @", "csgo", "dragon", "rose", "blackops", "pokemon", "cod", "header", "baby", "madden", "fifa", "funko", "uk"]
    MIN_FOLLOWERS = 1000

    ENDING = ["by", "ends", "selected", "winner", "today", "tomorrow", "closes", "picked"]

    url = "https://api.twitter.com/1.1/"

    def __init__(self):
        self.list_of_tweets = set([])
        self.session = requests.Session()
        self.session.auth = auth

    def search(self, q, count=100, locale='en'):
        search_url = "%ssearch/tweets.json" % self.url
        search_params = {'q':q, 'count':100, 'locale':locale}
        r = self.session.get(search_url, params=search_params)
        return r.json()

    def update_status(self, status):
        update_url = "%sstatuses/update.json" % self.url 
        update_params = {'status':status}
        r = self.session.post(update_url, params=update_params)
        errors = r.json()['errors']
        if errors:
             raise errors[0]['message']

    def retweet(self, tweet_id):
        retweet_url = "%sstatuses/retweet/%s.json" % (self.url, tweet_id)
        r = self.session.post(retweet_url)
        errors = r.json()['errors']
        if errors:
             raise LarryError(errors[0]['message'])

    def like(self, tweet_id):
        like_url = "%sfavorites/create.json" % self.url
        like_params = {'id':tweet_id}
        r = self.session.post(like_url, params=like_params)
        errors = r.json()['errors']
        if errors:
             print errors[0]['message']

    def add_friend(self, user_id):
        add_friend_url = "%sfriendships/create.json" % self.url
        add_friend_params = {'id':user_id}
        r = self.session.post(add_friend_url, params=add_friend_params)
        errors = r.json()['errors']
        if errors:
             print errors[0]['message']

    def find_status(self, tweet_id):
        find_url = "%sstatuses/show.json" % self.url
        find_params = {'id':tweet_id}
        r = self.session.get(find_url, params=find_params)
        return r.json()

    def find_user(self, user_id):
        find_user_url = "%susers/show.json" % self.url
        find_user_params = {'id':user_id}
        r = self.session.get(find_user_url, params=find_user_params)
        return r.json()

    def run(self):
        while True:
            for words in self.BAG_OF_WORDS:
                try:
                    r = self.search(words)
                    for data in r['statuses']:
                        in_set, tweet_id = self.get_id(data)
                        if not in_set:
                            self.tweet(tweet_id)
                except BaseException as e:
                        print "Error is:" + str(e)

    def get_id(self, data):
        # If it's a reply, we know it's not what we want.
        if data['in_reply_to_status_id']:
            return

        # Get the correct tweet to read.
        try:
            correct_tweet = data['retweeted_status']
        except KeyError:
            correct_tweet = data

        correct_id = correct_tweet['id']
        in_set = correct_id in self.list_of_tweets
        self.list_of_tweets.add(correct_id)
        return in_set, correct_id

    def tweet(self, tweet_id):
        correct_tweet = self.find_status(tweet_id)

        # Make sure user is of some status and is not reposting something.
        curr_followers = correct_tweet['user']['followers_count']
        try: 
            if curr_followers < self.MIN_FOLLOWERS or correct_tweet['entities']['urls']:
                return

            # Check whether it's something we don't want, which we specify at the top.
            screen_name = correct_tweet['user']['screen_name']
            given_name = correct_tweet['user']['name']
            tweet = correct_tweet['text']
            tweet_lower = tweet.lower()

            if not ("rt" in tweet_lower or "retweet" in tweet_lower):
                return
            for word in self.BANNED_WORDS:
                if word in tweet_lower:
                    return
            user_lower = screen_name.lower()
            given_lower = given_name.lower()
            for user in self.BANNED_USERS:
                if user in user_lower or user in given_lower:
                    return

            day_to_delete = (datetime.datetime.today() + datetime.timedelta(days=7)).day
            f = open(str(day_to_delete) + ".csv", "a")
            writer = csv.writer(f)

            # Check that this isn't an actual retweet.
            others = correct_tweet['entities']['user_mentions']
            if not others:
                pass
            for person in others:
                other_id = person['id']
                other_followers = self.find_user(other_id)['followers_count']
                if curr_followers < other_followers:
                    return
                # If asking us to follow a smaller account, we comply sometimes.
                elif len(others) == 1 and curr_followers > other_followers:
                    if random.random() < 0.3:
                        self.add_friend(other_id)
                        writer.writerow([other_id])
                    else:
                        return
        except KeyError:
            pass

        # If all pass, we retweet.
        try:
            user_id = correct_tweet['user']['id']
            if "like" in tweet_lower:
                self.like(tweet_id)
            self.add_friend(user_id)
            self.retweet(tweet_id)
            writer.writerow([user_id])
            f.close()
            print "finished"
            time.sleep(random.random() * 50)
        except BaseException as e:
            print e

if __name__ == "__main__":
    c = LarryBot()
    c.run()