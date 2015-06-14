# -*- coding: utf-8 -*-
import copy
import os
import re
import urllib
import pymongo
import requests
import string
from collections import defaultdict, OrderedDict
import birdy.twitter
from .config import get_twitter_keys, get_named_stoplist, \
    get_pundit_categories, get_category_pundits
from .keywords import check_keywords
from .entities import collapse_entities
from .util import tokenize
import bs4 as BeautifulSoup
from nltk import ngrams
from nltk.corpus import stopwords

ALNUM_PAT = re.compile(r'[A-Za-z0-9]+')
URL_PAT = re.compile(r'http[^ ]+', re.I)
USER_PAT = re.compile(r'@\w{1,15}')    

LEAD_PAT = re.compile(u'^(RT)?\s*[.?!:;,\'"‘’“”—…\s]*', re.U | re.I)     
TRAIL_PAT = re.compile(u'[\s.:—…]+$', re.U)

class UserClient(birdy.twitter.UserClient):

    def __repr__(self):
        return dict(self).__repr__


_client = None
def client():
    global _client
    if _client is None:
        _client = UserClient(*get_twitter_keys())
    return _client


def compare_names(namepartsA, namepartsB):
    """Takes two twitter names (as lists of words) and returns a score."""
    complement = set(namepartsA) ^ set(namepartsB)
    intersection = set(namepartsA) & set(namepartsB)
    score = float(len(intersection))/(len(intersection)+len(complement))
    return score


def name_parts(names, flat=False):
    parts = []
    for name in names:
        n = ALNUM_PAT.findall(name)
        if flat:
            parts.extend(n)
        else:
            parts.append(n)
    return parts


def best_users(entity_names, twitter_objs):
    twitter_name_parts = name_parts([obj['name'] for obj in twitter_objs])
    entity_name_parts = name_parts(entity_names, flat=True)
    matches = map(lambda x: compare_names(entity_name_parts, x),
        twitter_name_parts)
    return sorted(zip(matches, twitter_objs), reverse=True)


def dedupe_tweets(tweet_list):
    """
    De-duplicate tweets, by throwing out retweets
    @tweet_list = list of tweets/statuses in reverse chronological order
    """
    tweets = []
    id_set = set()
    
    tweet_list.sort(key=lambda x: x['created_at'])
    for tweet in tweet_list:
        if tweet.id_str in id_set:
            continue
        id_set.add(tweet.id_str)
   
        try:
            rt_id_str = tweet.retweeted_status.id_str
            if rt_id_str in id_set:
                continue
            id_set.add(rt_id_str)
        except AttributeError:
            pass
                                            
        tweets.append(tweet)
    
    return list(reversed(tweets))    


def filter_tweets_by_stoplist(tweet_list, named_stoplist):
    """
    Filter tweets/retweets by screen_names in named_stoplist.
    Pull original tweets out of retweets.
    """
    tweets = []
    id_set = set()
    stoplist = get_named_stoplist(named_stoplist)

    for tweet in tweet_list:
        if tweet.id_str in id_set:
            continue
        id_set.add(tweet.id_str)

        if tweet.user.screen_name.lower() in stoplist:
            continue
    
        try:
            rs = tweet.retweeted_status
        
            if rs.id_str in id_set:
                continue
            id_set.add(rs.id_str)   
            
            if rs.user.screen_name.lower() in stoplist:
                continue 
        
            tweets.append(tweet.rs)
        except AttributeError:
            tweets.append(tweet)

    return tweets
    

def group_tweets_by_screen_name(tweet_list):
    """
    Group tweets by user.screen_name
    @tweet_list = list of tweets/statuses
    
    @return {screen_name: [tweets]}
    """
    d = OrderedDict()
    for tweet in tweet_list:
        screen_name = '@'+tweet.user.screen_name
        if screen_name in d:
            d[screen_name].append(tweet)
        else:
            d[screen_name] = [tweet]
    return d
            

def group_tweets_by_text(tweet_list):
    """
    Group tweets by text, merging superstrings into substring group
    @tweet_list = list of tweets/statuses
    
    @return {text: [tweets]}
    """
    d = defaultdict(list)    
    for tweet in tweet_list:
        s = USER_PAT.sub('', URL_PAT.sub(' ', tweet.text))
        s = LEAD_PAT.sub('', TRAIL_PAT.sub('', s))
        if s:
            d[s].append(tweet)  
    
    results = defaultdict(list)
    k = sorted(d.keys(), key=lambda k: len(k))
        
    while k:
        key = k.pop(0)
        results[key].extend(d[key])

        # Try to deal with in-line hashtags and trivial whitespace
        pat = '\s+'.join(
            ['#?'+x[1:] if x[0] == '#' else '#?'+x for x in key.split()])
        try:
            regex = re.compile(pat, re.I)
            for i in range(len(k) - 1, -1, -1):
                s = k[i]
                if regex.search(s):
                    results[key].extend(d[s])               
                    del k[i]       
        except Exception, e:
            pass
                                                      
    return results


def quote_query_terms(term_list):
    quoted_terms = []
    for term in term_list:
        if term.find(' ') < 0:
            quoted_terms.append(term)
        else:
            quoted_terms.append('"%s"' % term) 
    return quoted_terms

def form_query(keywords=None, entities=None):
    """
    Form a twitter query from keywords and/or entities
    """
    q_entities = []
    if entities:
        q_entities = collapse_entities(
            [d for d in entities if d['score'] > 0.01])
 
    q_keywords = []
    if keywords:
        q_keywords = [d['keyword'] for d in keywords \
            if d['count'] > 2 and d['keyword'] not in q_entities]
            
    q_keywords = quote_query_terms(q_keywords[:5])
    q_entities = quote_query_terms(q_entities[:5])   
    q = ''
    
    if q_keywords and q_entities:
        q = '(%s) AND (%s)' % \
            (' OR '.join(q_keywords), ' OR '.join(q_entities))
    elif q_keywords:
        q = q_keywords.pop(0)
        if len(q_keywords) > 1:
            q += ' AND (%s)' % ' OR '.join(q_keywords)
        elif len(q_keywords) > 0:
            q += ' AND %s' % q_keywords[0]
    elif q_entities:  
        q = q_entities.pop(0)
        if len(q_entities) > 1:
            q += ' AND (%s)' % ' OR '.join(q_entities)
        elif len(q_entities) > 0:
            q += ' AND %s' % q_entities[0]   
    return q
     
def search(params, section='ack', credentials=None):
    """
    Execute twitter search
    
    @params = dictionary of search parameters
    @section = config section
    @credentials = dictionary containing token/secret overrides
    """
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    return client.api.search.tweets.get(**params).data


def search_recent(params, section='ack', credentials=None):
    """
    Execute twitter search for most_recent tweets (allows pagination)
    @return list of tweets in reverse chronological order
   
    @params = dictionary of search parameters
    @section = config section
    @credentials = dictionary containing token/secret overrides
    """
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)

    tweets = []
       
    params['result_type'] = 'recent'
    n_tweets = 0
    n_max = params['count']    

    while n_tweets < n_max:
        params['count'] = min(100, n_max - n_tweets)        
        
        data = client.api.search.tweets.get(**params).data
        n = len(data.statuses)          
        if not n:
            break
        tweets.extend(data.statuses)
        n_tweets += n
        
        params['max_id'] = (int(data.statuses[-1].id_str) - 1)
        
    return tweets     

BING_ACCOUNT = 'knightlab@northwestern.edu'
BING_SEARCH_ACCOUNT_KEY = 'gpx6N23pHp4tnDDds3fj1VWW20JoDwsptSCYScnp0oE'
#BING_URL = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%%27news%%2Bweb%%27&$format=json&Query=%s'
BING_URL = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%%27web%%27&$format=json&Query=%s'


def search_bing(query):
    query = "'%s'" % query
    req = BING_URL % urllib.quote(query)
    if len(req) > 2047:
        raise Exception
    r = requests.get(req, auth=(BING_ACCOUNT, BING_SEARCH_ACCOUNT_KEY))
    return r.json()


def all_page_text(url):
    try:
        html = requests.get(url).text
        doc = BeautifulSoup.BeautifulSoup(html)
        return ' '.join([t for t in doc.findAll(text=True) if t.strip()])
    except requests.ConnectionError:
        return ''


TWITTER_LINK = re.compile('<a .*?href="http://twitter.com/(\w+)"')
WORD_P = re.compile('\w+')

UNAMBIGUOUS_MEDIA_NAME_TOKENS = (
    'bbc',
    'bloomberg',
    'cnn',
    'herald',
    'nbc',
    'news',
    'nytimes',
    'reuters',
    'telegram',
    'tribune',
    'tv',
)
KNOWN_MEDIA = (
    'ac360',
    'andrewsmith810',
    'bbcnewsus',
    'bybrianbennett',
    'cnn',
    'cnnbrk',   
    'glennbeck',    
    'haileybranson',
    'houseonfox',
    'joejohnscnn',
    'joelrubin',
    'keyetv'
    'larrygallup',
    'latimes',
    'latvives',
    'newsweek',
    'nytimes',
    'obamainaugural',
    'reuters',
    'sam_schaefer',
    'tpm',
    'washingtonpost',
)

def is_media(user):
    if user['screen_name'] in KNOWN_MEDIA:
        return True
    name_tokens = []
    description_tokens = []
    for token in tokenize(user['name']):
        for t in token.split('-'):
            name_tokens.append(t.lower()) 
    for token in tokenize(user['description']):
        for t in token.split('-'):
            description_tokens.append(t.lower())
    for t in UNAMBIGUOUS_MEDIA_NAME_TOKENS:
        if t in name_tokens or t in description_tokens:
            return True
    return False


SKIP_TOKENS = \
    [l for l in string.ascii_lowercase] + \
    ['mr', 'mrs', 'miss', 'ms', 'dr', 'rev', 'reverend',
    'sir', 'sr', 'jr', 'mayor', 'president', 'chief', 'gov',
    'governor', 'sen', 'senator', 'sgt', 'sargeant']
def twitter_name_passes(name, entity_name_tokens):
    entity_tokens = [t.lower() for t in entity_name_tokens]
    name_tokens = [n.lower() for n in ALNUM_PAT.findall(name)]
    for token in name_tokens:
        if token in SKIP_TOKENS:
            continue
        if token not in entity_tokens:
            return False
    return True


def score_users(content, results, entity_names, entity_name_tokens):
    """Just experimenting here with trying to extract some features.
    Nothing promising yet so please don't use this. Seems like it might
    be useful to try getting tf-idf scores on content and user pages.
    """
    stop = stopwords.words('english') 
    content_tokens = tokenize(content)
    unigrams = [t for t in ngrams(content_tokens, 1) if t not in stop]
    bigrams = [t for t in ngrams(content_tokens, 2) if t[0] not in stop and t[1] not in stop]
    trigrams = [t for t in ngrams(content_tokens, 3) if t[0] not in stop and t[2] not in stop]
    unfiltered_users = []
    for user in results:
        unfiltered_users.append(user)
        text = '%s %s %s' % (user['name'], user['screen_name'],
            user['description'])
        strong_twitter_score = 0
        weak_twitter_score = 0
        strong_page_score = 0
        weak_page_score = 0
        for name in entity_names:
            if name in text:
                strong_twitter_score += 1
        for token in entity_name_tokens:
            if token in text:
                weak_twitter_score += 1
        
        if user['url']:
            page = all_page_text(user['url'])
            for name in entity_names:
                if name in page:
                    strong_page_score += 1
            for token in entity_name_tokens:
                if token in page:
                    weak_page_score += 1
        unigram_score = 0
        bigram_score = 0
        trigram_score = 0
        content_unigram_score = 0
        content_bigram_score = 0
        content_trigram_score = 0
        if user.get('status'):
            status = user['status']['text']
            #status_tokens = WORD_P.findall(status)
            status_tokens = tokenize(status)
            status_unigrams = [t for t in ngrams(status_tokens, 1) if t not in stop]
            status_bigrams = [t for t in ngrams(status_tokens, 2) if t[0] not in stop and t[1] not in stop]
            status_trigrams = [t for t in ngrams(status_tokens, 3) if t[0] not in stop and t[2] not in stop]
            unigram_score = sum([1 if gram in unigrams else 0 for gram in status_unigrams]) 
            bigram_score = sum([1 if gram in bigrams else 0 for gram in status_bigrams]) 
            trigram_score = sum([1 if gram in trigrams else 0 for gram in status_trigrams]) 

            for url in user['status']['entities']['urls']:
                page = all_page_text(url['expanded_url'])
                page_tokens = tokenize(page)
                content_unigrams = [t for t in ngrams(page_tokens, 1) if t not in stop]
                content_bigrams = [t for t in ngrams(page_tokens, 2) if t[0] not in stop and t[1] not in stop]
                content_trigrams = [t for t in ngrams(page_tokens, 3) if t[0] not in stop and t[2] not in stop]
                content_unigram_score += sum([1 if gram in unigrams else 0 for gram in content_unigrams]) 
                content_bigram_score += sum([1 if gram in bigrams else 0 for gram in content_bigrams]) 
                content_trigram_score += sum([1 if gram in trigrams else 0 for gram in content_trigrams]) 

        print '%s (@%s) %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (
            user['name'],
            user['screen_name'],
            strong_twitter_score,
            weak_twitter_score,
            strong_page_score,
            weak_page_score,
            unigram_score,
            bigram_score,
            trigram_score,
            content_unigram_score,
            content_bigram_score,
            content_trigram_score
        )
    return unfiltered_users


def lookup_users(client, handles):
    if not handles:
        return []
    try:
        return client.api.users.lookup.post(
            screen_name=','.join(handles)).data
    except birdy.twitter.TwitterApiError, e:
        raise e
        if str(e).startswith('Invalid API resource.'):
            return lookup_users(client, handles[:-1])
        else:
            raise e


def find_twitter_users(entities, named_stoplist=None, section='ack', credentials=None):
    """
    @entities = list of entities
    @named_stoplist = screen_names stoplist (see cfg file)
    @section = config section
    @credentials = dictionary containing token/secret overrides
    """
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    users = []
    stoplist = None
    if named_stoplist is not None:
        stoplist = get_named_stoplist(named_stoplist)
    for entity in entities:
        if entity['type'] != 'PERSON':
            continue
        user_query = urllib.quote_plus(entity['name'].encode('ascii',
            'xmlcharrefreplace'))
        results = client.api.users.search.get(
            q=user_query, count=5).data
        if stoplist:
            user_holder = [user for user in results if user['verified']
                if user.screen_name.lower() not in stoplist]
        else:
            user_holder = [user for user in results if user['verified']]
        if len(user_holder) > 0:
            scores = best_users(entity['name_forms'],user_holder)
            thresh = 0.
            scores = filter(lambda s: s[0] > thresh,scores)
            if len(scores) > 0:
                matched_users = [s[1] for s in scores]
                d = copy.copy(entity)
                d.update({ 'twitter_users':
                    [u for u in matched_users]})
                users.append(dict(d))
    return users


IGNORE_ENTITIES_NF = (
    ['Universiy'],
    ['God'],
    ['Catholic'],
    ['City'],
)
           
def _discover_users_via_twitter(entity, section, credentials):
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    user_query = urllib.quote_plus(
        '"%s"' % entity['name'].encode('ascii', 'xmlcharrefreplace'))
    results = client.api.users.search.get(q=user_query).data
    if len(results) == 0:
        user_query = urllib.quote_plus(entity['name'].encode('ascii',
            'xmlcharrefreplace'))
        results = client.api.users.search.get(
            q=user_query).data
    for r in results:
        r.update({'discovered_via':'twitter'})
    return results


def _discover_users_via_bing(entity):
    r = search_bing(entity['name'])
    handles = []
    for item in r['d']['results'][0]['Web'][:10]:
        page = requests.get(item['Url']).text
        candidates = [
            s for s in list(set(TWITTER_LINK.findall(page)))
            if s != 'share']
        if len(candidates) == 1:
            if candidates[0] not in handles:
                handles.append(candidates[0])
    results = lookup_users(client, handles)
    for r in results:
        r.update({'discovered_via':'bing'})
    return results


def get_entity_name_tokens(entity):
    entity_names = set([entity['name']] + entity['name_forms'])
    entity_name_tokens = []
    for name in entity_names:
        tokens = ALNUM_PAT.findall(name)
        for token in tokens:
            if token not in entity_name_tokens:
                entity_name_tokens.append(token)
    return entity_name_tokens


def find_stakeholder_twitter_users(content, entities, section='ack',
        credentials=None):
    """
    @entities = list of entities
    @section = config section
    @credentials = dictionary containing token/secret overrides
    """
    users = []
    for entity in entities:
        if entity['type'] not in ('PERSON', 'ORGANIZATION'):
            continue
        if entity['name_forms'] in IGNORE_ENTITIES_NF:
            continue
            
        results = []
        
        host = os.getenv('ACK_MONGO_HOST', '127.0.0.1')
        _conn = pymongo.Connection(host, 27017)
        _db = _conn['ack']
        _cached = _db['cached_users']
        _cached.ensure_index('entity')
        r = _cached.find_one({'entity': entity['name']})
        found_cached = False
        entity_name_tokens = get_entity_name_tokens(entity)
        if r is not None:
            found_cached = True
            if r['users']:
                cached_results = [r for r in r['users'] if not is_media(r)
                    if r['verified']]
                cached_results = [r for r in cached_results if
                    twitter_name_passes(r['name'], entity_name_tokens)]
                results = cached_results
        if not found_cached:
            full_results = _discover_users_via_twitter(
                entity, section, credentials)
            results = [r for r in full_results if r['verified']]
            results = [r for r in results if not is_media(r)]
            results = [r for r in results if
                twitter_name_passes(r['name'], entity_name_tokens)]
            if (results) == 0:
                bing_results = _discover_users_via_bing(entity)
                full_results += bing_results
                bing_results = [r for r in bing_results if r['verified']]
                bing_results = [r for r in bing_results if not is_media(r)]
                bing_results = [r for r in results if
                    twitter_name_passes(r['name'], entity_name_tokens)]
                results += bing_results
            r = {
                'entity': entity['name'],
                'users': full_results
            }
            _cached.insert(r)
        entity_names = set([entity['name']] + entity['name_forms'])
        #results = score_users(
        #    content, results, entity_names, entity_name_tokens)
        if len(results) > 0:
            scores = best_users(entity_names, results)
            for score in scores:
                pass
                #print 'Screen Name:', score[1]['screen_name']
                #print 'Name:', score[1]['name']
                #print 'Description:', score[1]['description']
                #print 'Followers:', score[1]['followers_count']
                #print 'Verified:', score[1]['verified']
                #print 'Status:', score[1]['status']['text']
                #print 'Statuses Count:', score[1]['statuses_count']
                #print 'Friends Count:', score[1]['friends_count']
                #print 'Favourites Count:', score[1]['favourites_count'] 
                #print 'URL:', score[1]['url']
                #print 'Location:', score[1]['location']
            thresh = 0.
            scores = filter(lambda s: s[0] > thresh,scores)
            if len(scores) > 0:
                matched_users = [s[1] for s in scores]
                d = copy.copy(entity)
                d.update({ 'twitter_users':
                    [u for u in matched_users]})
                users.append(dict(d))
    return users


def get_timeline(users, keywords, section='ack', credentials=None, limit=None):
    tk = get_twitter_keys(section)._replace(**credentials or {})        
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
    return tweets


def stakeholder_tweets(users, keywords, section='ack', credentials=None,
        limit=None):
    # Throw out users that are too ambiguous
    # TODO: ideally we would try to disambiguate and use the best option
    users = [user for user in users if len(user['twitter_users']) <= 3]
    tweets = get_timeline(users, keywords, section=section, 
        credentials=credentials, limit=limit)
    return tweets
    

def chunk_iter(seq, n):
    """
    Break seq into chunks of at most n items
    """
    return (seq[pos:pos + n] for pos in xrange(0, len(seq), n))
    
def pundit_tweets(category, keywords, section='ack', credentials=None, 
    limit=None):
    """
    Do keyword search of tweets from pundits in category
    Twitter says to keep keywords and operators < 10
    """
    categories = get_pundit_categories()
    if not category in categories:
        raise Exception('No pundit panel available for category "%s"' % category)    
    
    pundits = get_category_pundits(category)
    if not pundits:
        raise Exception('No pundits available for category "%s"' % category)

    n_keywords = 4
    while True:
        q_keywords = form_query(keywords[:n_keywords])
        n_from = (10 - len(q_keywords.split())) / 2      
        if n_from > 0:
            break
        n_keywords -= 1
    
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    
    tweets = []    
    for group in chunk_iter(pundits, n_from):    
        q_from = ' OR '.join(['from:%s' % x for x in group])
        q = '(%s) AND (%s)' % (q_from, q_keywords)
        #print q
        
        params = {'q': q, 'count': 20, 'result_type': 'mixed'}
        result = search(params, section=section, credentials=credentials)          
        if len(result.statuses) != 0:
            tweets.extend(result.statuses)
    return tweets

    
        
