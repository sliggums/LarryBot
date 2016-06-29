from tweepy import Stream, OAuthHandler, API
from tweepy.error import TweepError
from time import sleep
from random import random


g = open('config2.txt', 'r')
lines = g.readlines()
for i in range(len(lines)):
    lines[i] = lines[i].strip()

ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = lines

def delete():
    f = open('4.csv', 'r')
    g = open('5.csv', 'r')
    users = f.readlines()
    users += g.readlines()

    for i in range(len(users)):
        users[i] = users[i][:-1]
        print users[i]

    user_id = t.me().id
    for user in t.friends_ids(user_id):
        if user not in users:
            t.destroy_friendship(user)
            print "destroyed"
            sleep(150 * random())



oauth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
t = API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
delete()