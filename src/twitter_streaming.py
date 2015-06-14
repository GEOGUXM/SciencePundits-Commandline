from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
import pandas as pd
import matplotlib.pyplot as plt
import time 

#Variables that contains the user credentials to access Twitter API 
access_token = "88552398-7jILK2yxbt1X7fJINklrhO1AgbEv7v66JVzTYIIry"
access_token_secret = "uyYj0Hogk7uqIFhrTclJatEyt3lsXQeMuhkBp05joshFX"
consumer_key = "pLMifOjrm1SN2IvOYrbsTNhtn"
consumer_secret = "wyCYugnH2PkqgwJ0Dg94tQczZotBtHCmDiJM0ojUsxV4dYR4dr"


def check_keywords(timeline, keywords):
    tweets = []
    #keywords = [k['keyword'] for k in keywords]
    for tweet in timeline:
        score = 0
        for kw in keywords:
            if kw.lower() in tweet.text.lower():
                score += 1
        if score > 0:
            tweets.append({
                'tweet': tweet.text,
                'score': score})
    tweets = sorted(tweets, key = lambda x: x['score'], reverse=True)
    return tweets

# def get_timeline(): 

# 	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# 	auth.set_access_token(access_token, access_token_secret)
# 	client = tweepy.API(auth)
	
# 	tweets2 = []	
# 	user = client.get_user(screen_name='BillNye')
# 	timeline = user.timeline(count = 200)
# 	#tweets = [] 
# 	keywords = ['circuit','Sail']
# 	if timeline is not None:
# 		# print "not none"
# 	    # closed.append(user['id'])
# 	    tweets = check_keywords(timeline, keywords)
# 	    if len(tweets) != 0:
# 			for x in tweets:
# 				print x 
# 				tweets2.append(x) 
# 	return tweets2

# Takes the user list to look pundits 
def get_timeline2(user_list,keywords): 

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	client = tweepy.API(auth)
	
	tweets2 = []	
	#tweets = [] 
	for x in user_list: 
		user = client.get_user(screen_name=x)
		# print '#######', user.screen_name 
		timeline = user.timeline(count = 50)
		#tweets = [] 
		#keywords = ['circuit','Sail']
		if timeline is not None:
			# print "not none"
		    # closed.append(user['id'])
		    tweets = check_keywords(timeline, keywords)
		    i = 0 
		    if len(tweets) != 0:
				for x in tweets:
					print x 
					tweets2.append({'screen_name' : user.screen_name, 'tweet': tweets[i]['tweet'], 'score': tweets[i]['score']}) 
					i = i+1
	return tweets2

# check if each tweet is greater that 1 print only that 

def print_tweets(users,keywords): 
	tweets2 = get_timeline2(users,keywords) 
	for tweet in tweets2: 
		if(tweet['score'] == 1): 
			print(tweet['tweet'])
			#import time
			time.sleep(2)

users = ['@BillNye','@neiltyson']

keywords = ['circuit','Sail']
#abc = get_timeline2(users,keywords)
print_tweets(users,keywords)

