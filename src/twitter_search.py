from TwitterSearch import *



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

c_key = 'pLMifOjrm1SN2IvOYrbsTNhtn'
c_secret = 'wyCYugnH2PkqgwJ0Dg94tQczZotBtHCmDiJM0ojUsxV4dYR4dr'
a_token = '88552398-7jILK2yxbt1X7fJINklrhO1AgbEv7v66JVzTYIIry'
a_token_secret = 'uyYj0Hogk7uqIFhrTclJatEyt3lsXQeMuhkBp05joshFX'

# try:
#     tuo = TwitterUserOrder('@BillNye') # create a TwitterUserOrder

#     tuo.set_keywords(['climate change'])
#     # it's about time to create TwitterSearch object again
#     ts = TwitterSearch(
#         consumer_key = c_key,
#         consumer_secret = c_secret,
#         access_token = a_token,
#         access_token_secret = a_token_secret
#     )

#     # start asking Twitter about the timeline
#     for tweet in ts.search_tweets_iterable(tuo):
#         print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )

# except TwitterSearchException as e: # catch all those ugly errors
#     print(e)

try:
    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.set_keywords(['climate']) # let's define all words we would like to have a look for
    tso.set_language('de') # we want to see German tweets only
    tso.set_include_entities(False) # and don't give us all those entity information

    # it's about time to create a TwitterSearch object with our secret tokens
    ts = TwitterSearch(
        consumer_key = c_key,
        consumer_secret = c_secret,
        access_token = a_token,
        access_token_secret = a_token_secret
     )

     # this is where the fun actually starts :)
    for tweet in ts.search_tweets_iterable(tso):
        #if tweet['user'] == '@BillNye':
        print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )

except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)