from tweepy import OAuthHandler, API
from time import sleep
from random import random
import datetime


g = open('config2.txt', 'r')
lines = g.readlines()
for i in range(len(lines)):
    lines[i] = lines[i].strip()

ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = lines

def delete():
    day_to_delete = (datetime.datetime.today() + datetime.timedelta(days=7)).day
    f = open(str(day_to_delete) + ".csv", "a")
    users = f.readlines()

    for i in range(len(users)):
        users[i] = users[i][:-1]

    user_id = t.me().id
    for user in t.friends_ids(user_id):
        t.destroy_friendship(user)
        print "destroyed"
        sleep(60 + 50 * random())

    print "Done, exiting."
    time.sleep(60 * 60 * 6)

oauth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
t = API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

while True:
    delete()
