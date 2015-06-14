import collections
import ConfigParser
import os
import re
import sys
from os.path import expanduser


import copy
import urllib
import requests
import string
from collections import defaultdict, OrderedDict
import birdy.twitter
from birdy.twitter import TwitterAuthError
# from ..config import get_twitter_keys, get_named_stoplist
# from ..content import all_page_text
# from ..nlp.keywords import check_keywords
# from ..nlp.entities import collapse_entities
# from ..nlp.util import tokenize, compare_names, name_parts, ALNUM_PAT
from nltk import ngrams
from nltk.corpus import stopwords

twitter_consumer_key = 'pLMifOjrm1SN2IvOYrbsTNhtn'
twitter_consumer_secret = 'wyCYugnH2PkqgwJ0Dg94tQczZotBtHCmDiJM0ojUsxV4dYR4dr'
twitter_access_token = '88552398-7jILK2yxbt1X7fJINklrhO1AgbEv7v66JVzTYIIry'
twitter_access_token_secret = 'uyYj0Hogk7uqIFhrTclJatEyt3lsXQeMuhkBp05joshFX'


# def filterdict(dict, str):
#     results = {}
#     for key, value in dict.items():
#         for k in str: 
#           if str in value:
#               results[key] = value
#     return results

class UserClient(birdy.twitter.UserClient):
    """Twitter UserClient"""
    def __repr__(self):
        return dict(self).__repr__


_client = None
def client():
    """Get Twitter UserClient"""
    global _client
    if _client is None:
        _client = UserClient(*get_twitter_keys())
    return _client


def get_twitter_keys():
    """Return namedtuple of Twitter config data"""
    #config = configuration()
    TwitterKeys = collections.namedtuple('TwitterKeys', [
        'consumer_key',
        'consumer_secret',
        'access_token',
        'access_token_secret'])
    k = TwitterKeys(twitter_consumer_key,
        twitter_consumer_secret,
        twitter_access_token,
        twitter_access_token_secret)
    return k


def check_keywords(timeline, keywords):
    tweets = []
    keywords = [k['keyword'] for k in keywords]
    for tweet in timeline:
        score = 0
        for kw in keywords:
            if kw.lower() in tweet.text.lower():
                score += 1
        if score > 0:
            tweets.append({
                'tweet': tweet,
                'score': score})
    tweets = sorted(tweets, key = lambda x: x['score'], reverse=True)
    return tweets


def get_timeline(users, keywords, credentials=None, limit=None):
    tk = get_twitter_keys()   
    print tk     
    client = UserClient(*tk)
    tweets = []
    closed = []
    for i, user in enumerate(users):
        if limit is not None and i >= limit:
            break 
        for user in user['twitter_users']:
            if user['id'] not in closed:
                timeline = client.api.statuses.user_timeline.get(
                    count=200, user_id=user['id']).data
                if timeline is not None:
                    closed.append(user['id'])
                    twits = check_keywords(timeline, keywords)
                    if len(twits) != 0:
                        tweets.extend(twits)
    print tweets

users = ['@BillNye','@mckeay']
keywords = ['climate']
x = get_twitter_keys()
#get_timeline()
get_timeline(users, keywords, credentials=None, limit=None)

#get_timeline(users, keywords, section='context', credentials=None, limit=None)
# #do a quick test to make sure the function works
# mydict = {'a': 'just a test',
#           'b': 'some',
#           'c': 'more',
#           'd': 'test',
#           'e': 'entries',
#           'f': 'test me more!'}

# print filterdict(mydict, 'test')