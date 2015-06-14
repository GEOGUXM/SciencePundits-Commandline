# from rauth import OAuth1Service

# # Get a real consumer key & secret from https://dev.twitter.com/apps/new
# twitter = OAuth1Service(
#     name='twitter',
#     consumer_key='J8MoJG4bQ9gcmGh8H7XhMg',
#     consumer_secret='7WAscbSy65GmiVOvMU5EBYn5z80fhQkcFWSLMJJu4',
#     request_token_url='https://api.twitter.com/oauth/request_token',
#     access_token_url='https://api.twitter.com/oauth/access_token',
#     authorize_url='https://api.twitter.com/oauth/authorize',
#     base_url='https://api.twitter.com/1/')

# request_token, request_token_secret = twitter.get_request_token()

# authorize_url = twitter.get_authorize_url(request_token)

# print 'Visit this URL in your browser: ' + authorize_url
# pin = raw_input('Enter PIN from browser: ')

# session = twitter.get_auth_session(request_token,
#                                    request_token_secret,
#                                    method='POST',
#                                    data={'oauth_verifier': pin})

# params = {'screen_name': 'github',  # User to pull Tweets from
#           'include_rts': 1,         # Include retweets
#           'count': 10}              # 10 tweets

# r = session.get('statuses/user_timeline.json', params=params)

# for i, tweet in enumerate(r.json(), 1):
#     handle = tweet['user']['screen_name'].encode('utf-8')
#     text = tweet['text'].encode('utf-8')
#     print '{0}. @{1} - {2}'.format(i, handle, text)



from TwitterSearch import *

# twitter_consumer_key =   'dkW3o9o2CqajnKKPxyFffv5TX'
# twitter_consumer_secret =  'DLftXCc8yfW1wcw9DWcmFnrYnQSXeJHI8gEatQ5pmiSgDMXw9M'
# twitter_access_token =  '88552398-1P8aP3FMnTXKYdaKE6kxRCmbyJxS7Lz4mgjf42msv'
# twitter_access_token_secret = 'xp0AKe2gnSmk7iHDW3xq5J3IQJcogucY9EKpm2BOCltcI'

twitter_consumer_key = 'pLMifOjrm1SN2IvOYrbsTNhtn'
twitter_consumer_secret = 'wyCYugnH2PkqgwJ0Dg94tQczZotBtHCmDiJM0ojUsxV4dYR4dr'
twitter_access_token = '88552398-7jILK2yxbt1X7fJINklrhO1AgbEv7v66JVzTYIIry'
twitter_access_token_secret = 'uyYj0Hogk7uqIFhrTclJatEyt3lsXQeMuhkBp05joshFX'

try:
    tuo = TwitterUserOrder('BillNye') # create a TwitterUserOrder

    # it's about time to create TwitterSearch object again
    ts = TwitterSearch(
        consumer_key = 'twitter_consumer_key',
        consumer_secret = 'twitter_consumer_secret',
        access_token = 'twitter_access_token',
        access_token_secret = 'twitter_access_token_secret'
    )

    # start asking Twitter about the timeline
    for tweet in ts.search_tweets_iterable(tuo):
        print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )

except TwitterSearchException as e: # catch all those ugly errors
    print(e)