import traceback
import urllib
import requests
from functools import wraps
from birdy.twitter import UserClient, TwitterAuthError
from ack.config import get_twitter_keys, get_named_stoplist
from ack.classifier import classify_text
from ack.content import get_article
from ack.entities import extract_entities, collapse_entities
from ack.keywords import get_keywords
from ack.twitter import search, find_stakeholder_twitter_users, \
    stakeholder_tweets, form_query, search_recent, dedupe_tweets, \
    filter_tweets_by_stoplist, group_tweets_by_text, \
    group_tweets_by_screen_name, pundit_tweets
from flask import Flask, render_template, request, jsonify, session, url_for, redirect, abort

app = Flask(__name__)


from werkzeug.wsgi import DispatcherMiddleware


app.secret_key = '\xba\xc6\xcf\xc7/\x93:\xa7\x9a\xaf\xc2}\xf47y>\xa6\xad\xce*\xe5\xa2\xd80'

application = DispatcherMiddleware(app, {
    '/context':     app
})

from connection import _content
import bson


class InvalidRequest(Exception):
    status_code = 400


def render(data, template=None):
    if all([
        template is not None,
        'application/json' not in request.headers['Accept'],
        request.args.get('_format') != 'json'
    ]):
        return render_template(template, **data)
    else:
        return jsonify(data)


def twitter_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except TwitterAuthError:
            return url_for(auth_check)
    return wrapper


def content_identifier_required(f):
    """Enforces url query parameter on a route."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        content_id = kwargs.get('content_id')
        if content_id is None:
            content_id = request.args.get('id')
        if not 'url' in request.args and content_id is None:
            if 'application/json' not in request.headers['Accept'] and \
                    request.args.get('_format') != 'json':
                return redirect(url_for('url_required') + \
                    '?next=%s' % request.script_root + request.path)
            else:
                raise InvalidRequest('url parameter is required')
        if content_id:
            r = cached_content(content_id=content_id)
        else:
            url = request.args.get('url')
            if not url:
                raise InvalidRequest('URL or content ID required.')
            r = cached_content(url=url)
        if not r:
            raise Exception('Could not find article content')
        request.content = r
        return f(*args, **kwargs)
    return wrapper


@app.route('/url-required', methods=('POST', 'GET'))
def url_required():
    if request.method == 'POST':
        url = request.form['url']
        next_ = request.form['next']
        if url and next_:
            return redirect('%s?url=%s' % (next_, url))
    return render_template('url_required.jinja2', next=request.args.get('next'))

#
# per-app session management
#


def session_get(app, key):
    return session.get(app+'-'+key)


def session_set(app, key, value):
    session.permanent = True # Safari seems to need this
    session[app+'-'+key] = value


def session_pop(app, key):
    app_key = app+'-'+key
    if app_key in session:
        session.pop(app_key)
    

def session_pop_list(app, key_list):
    for k in key_list:
        app_key = app+'-'+k      
        if app_key in session:
            session.pop(app_key)


def remove_session_credentials(app):
    session_pop_list(app,
        ['auth_token', 'auth_token_secret', 'auth_redirect',
         'access_token', 'access_token_secret'])
    

@app.route('/auth/clear/<app>')
def auth_clear(app):
    remove_session_credentials(app)
    return jsonify({ 'status': 'OK' })


@app.route('/session')
def session_show():
    return jsonify({ k:v for k,v in session.iteritems() })

#
# authorization
# 

def get_twitter_credentials(app):
    access_token = session_get(app, 'access_token')
    access_token_secret = session_get(app, 'access_token_secret')
    if not (access_token and access_token_secret):     
        raise TwitterAuthError('User is not authorized')
    return {
        'access_token': access_token, 
        'access_token_secret': access_token_secret
    }


@app.route('/auth/check/<app>/')
def auth_check(app):
    """
    Check authorization.  Get signin token and auth_url, if needed.
    <app> = application identifier
    
    @redirect = redirect to this url post-authorization verification
    """
    try:
        access_token = session_get(app, 'access_token')
        access_token_secret = session_get(app, 'access_token_secret')

        if access_token and access_token_secret:        
            tk = get_twitter_keys(app)
            client = UserClient(
                tk.consumer_key,
                tk.consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret)                    
            """
            We need to make a call to verify_credentials in case the user
            has revoked access for this application. This is a rate-limited
            call and so this approach might not be ideal. If we end up
            having rate-limiting problems, we might try giving each user
            a unique application ID that is kept in local storage and used
            as a lookup for Twitter creds (vs. session data which is domain-
            specific and thus problematic for our extension-approach). This
            might allow us to consolidate Twitter creds per user rather than
            storing them for each domain visited."""
            verif = client.api.account.verify_credentials.get()
            if verif.headers['status'].split()[0] == '200':
                return jsonify({'is_auth': 1})
            else:
                # possibly revoked access, although this will probably
                # get handled by the TwitterAuthError catch
                remove_session_credentials('stakeholder')
                return jsonify({'is_auth': 0})
            
        tk = get_twitter_keys(app)
        client = UserClient(tk.consumer_key, tk.consumer_secret)

        callback = 'http://'+request.host+url_for('auth_verify', app=app)
        print 'getting auth token for callback:', callback
        token = client.get_authorize_token(callback)
                
        session_set(app, 'auth_token', token.oauth_token)
        session_set(app, 'auth_token_secret', token.oauth_token_secret)        
        session_set(app, 'auth_redirect', request.args.get('redirect') or '')

        # START DEBUG
        print 'AUTH_CHECK', app
        for k, v in session.iteritems():
            print k, v
        # END DEBUG
        if 'html' in request.headers['Accept'] and request.args.get('_format') != 'json':
            print 'redirecting', token.auth_url
            return redirect(token.auth_url)
        else:
            data = {'is_auth': 0, 'auth_url': token.auth_url}
            return jsonify(data)
    except TwitterAuthError:
        remove_session_credentials(app)
        return jsonify({'is_auth': 0})
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
             

@app.route('/auth/verify/<app>/')
def auth_verify(app):
    """
    Get final access token and secret, redirect   
    <app> = application identifier
    
    @oauth_verifier = parameter from auth_url callback (see above)  
    """
    try:
        # START DEBUG
        # if session values are in the AUTH CHECK but not here - be sure
        # to check cookie settings. Note: Firefox let's you select
        # "Accept Cookies" even when in "Always use private mode" -- however
        # cookies do not work in this mode.
        print 'AUTH_VERIFY', app
        for k, v in session.iteritems():
            print k, v
        # END DEBUG

        oauth_verifier = request.args.get('oauth_verifier')
        if not oauth_verifier:
            raise Exception('expected oauth_verifier parameter')

        auth_token = session_get(app, 'auth_token')
        auth_token_secret = session_get(app, 'auth_token_secret')    
        auth_redirect = session_get(app, 'auth_redirect')

        if not (auth_token and auth_token_secret):
            raise Exception('Authorization credentials not found in session')
    
        tk = get_twitter_keys()
        client = UserClient(tk.consumer_key, tk.consumer_secret,
                    auth_token, auth_token_secret)                    
        token = client.get_access_token(oauth_verifier)
        
        session_set(app, 'access_token', token.oauth_token)
        session_set(app, 'access_token_secret', token.oauth_token_secret)    
        session_pop_list(app, ['auth_token', 'auth_token_secret', 'auth_redirect'])
        
        if auth_redirect:
            return redirect(auth_redirect)
        else:
            return redirect(url_for('home'))
    except Exception, e:
        traceback.print_exc()
        return redirect(auth_redirect)


#
# api
#

BROWSER_EXTENSIONS = (
    {   'name': 'Qwotd',
        'basename': 'qwotd',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': "Stakeholders' Tweetback",
        'basename': 'stakeholder',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': 'TweetTalk',
        'basename': 'tweettalk',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': 'Readdit',
        'basename': 'readdit',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': 'Pundits',
        'basename': 'pundits',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' }

)

def browser_extensions():
    ext_url = \
        'http://context.infolabprojects.com/static/browser-extensions/%s_%s.%s'
    return [ {
        'name': e['name'],
        'chrome': ext_url % (e['basename'], e['chrome'], 'crx'),
        'firefox': ext_url % (e['basename'], e['firefox'], 'xpi'),
        'safari': ext_url % (e['basename'], e['safari'], 'safariextension.zip'),
     } for e in BROWSER_EXTENSIONS ]


@app.route("/api")
@app.route("/")
def home():
    data = {
        'ack': 'OK',
        'notes': [
            'While Firefox extensions appear to be installable via direct link, they should be installed by downloading first. We are seeing different behaviors for these modes of installation, likely due to security policies in Firefox.',
            'Chrome extensions should be downloaded and copied locally into the Extensions window (Window > Extensions).',
            'Safari exensions should be downloaded, unzipped, and installed via the Extension Builder (Develop > Show Extension Builder)',
        ],
        'resources': {
            'browser_extensions': browser_extensions()
        }
    }
    if request.url_rule.rule == '/api':
        return jsonify(data)
    else:
        return render_template('home.jinja2', **data)

  
@app.route('/url')
@app.route('/url/<app>/')
@content_identifier_required
def url_(app='qwotd'):
    """
    Search for tweets by url
    <app> = application identifier

    @url = url to search for
    """    
    try:
        url = request.args.get('url')
        if not url:
            raise Exception('Expected url parameter')
          
        try:
            credentials = get_twitter_credentials(app)
            params = {'q': url, 'count': 200}       
            tweets = search_recent(params, section=app, credentials=credentials)
        except TwitterAuthError:
            # User not authenticated. Re-initiating Twitter auth.
            if 'html' in request.headers['Accept'] and \
                    request.args.get('_format') != 'json':
                return redirect(url_for('auth_check', app=app)) 
            session_pop(app, 'access_token')
            session_pop(app, 'access_token_secret')
            return url_(app)
            
        # De-dupe retweets
        tweets = dedupe_tweets(tweets)
        
        # Group by text
        grouped = group_tweets_by_text(tweets)
        
        # Sort tweets within groups
        for k, tweet_list in grouped.iteritems():
            grouped[k].sort(key=lambda t: (t.retweet_count, t.created_at),
                reverse=True)
        
        # Sort groups by count, text
        groups = sorted(grouped.items(), key=lambda t: (-1*len(t[1]), t[0]))
                            
        data = {'error': '', 'tweets': groups}
        return render(data, template='url.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})        


def cached_content(url=None, content_id=None):
    """Retrieve content from the cache or fetch it and cache it. Replaces
    Mongo's _id with id."""
    if url:
        r = _content.find_one({'url': url})
    elif content_id:
        r = _content.find_one({'_id': bson.ObjectId(content_id)})
    else:
        raise Exception('No Content Identifier') 
    if not r:
        data = get_article(url)
        r = {
            'url': url,
            'title': data['title'],
            'text': data['text']
        }
        _content.insert(r, manipulate=True)  # so id is set
    r['id'] = str(r['_id'])
    del r['_id']
    return r

def content_keywords(content):
    if not 'keywords' in content:
        content['keywords'] = [x for x in get_keywords(content['text'])
            if x['count'] > 2]      
        _content.save(content)
    return content['keywords']

def content_entities(content):
    if not 'entities' in content:
        content['entities'] = extract_entities(content['text'])   
        _content.save(content)
    return content['entities']

def content_categories(content):
    if not 'categories' in content:
        content['categories'] = classify_text(content['text'])
        _content.save(content)
    return content['categories']

def content_stakeholders(content, app='stakeholder'):
    if not 'stakeholders' in content:
        entities = content_entities(content)
        kwargs = {
            'section': app,
            'credentials': get_twitter_credentials(app)
        }
        stakeholder_list = find_stakeholder_twitter_users(
            content['text'], entities, **kwargs)
        content['stakeholders'] = stakeholder_list
        _content.save(content)
    return content['stakeholders']


@app.route('/content/')
@content_identifier_required
def content():
    """
    Retrieve and cache content @ url
    """
    try:
        url = request.args.get('url')
        if not url:
            raise Exception('Expected url parameter')
        return render(cached_content(url=url), template='content.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})        

    
@app.route('/keywords')
@app.route('/keywords/<content_id>/')
@content_identifier_required
def keywords(content_id=None):
    """
    Retrieve and cache keywords for article with <id>.
    Automatically prune keywords with count < 2
    """
    try:
        data = content_keywords(request.content)
        return render({ 'keywords': data }, template='keywords.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
            

@app.route('/entities')
@app.route('/entities/<content_id>/')
@content_identifier_required
def entities(content_id=None):
    """
    Retrieve and cache entities for article with <content_id>. Alternatively
    accepts url or id in query params.
    """
    try:
        data = {'entities': content_entities(request.content)}
        return render(data, template='entities.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/categories')
@app.route('/categories/<content_id>/')
@content_identifier_required
def categories(content_id=None):
    """
    Retrieve and cache categories for article with <content_id>/  Alternatively
    accepts or url or id in query params.
    """
    try:
        data = {'categories': content_categories(request.content)}
        return render(data, template='categories.jinja2')    
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
        

@app.route('/stakeholders')
@app.route('/stakeholders/<app>/<content_id>/')
@content_identifier_required
def stakeholders(app='stakeholder', content_id=None):
    """Retrieve and cache stakeholders for article with <id>
    """
    try:
        content = request.content
        data = content_stakeholders(content, app=app)
        return render({ 'stakeholders': data },
            template='stakeholders.jinja2')
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})    


@app.route('/stakeholdertweets')
@app.route('/stakeholdertweets/<app>/<content_id>/')
@content_identifier_required
def stakeholdertweets(app='stakeholder', content_id=None):
    """
    Retrieve stakeholder tweets for article with <id>
    """
    try:
        content = request.content
        keywords = content_keywords(content)
        stakeholders = content_stakeholders(content, app=app)
        stakeholders = stakeholders[:request.args.get('limit', 10)]
        credentials = get_twitter_credentials(app)
        result = stakeholder_tweets(
            stakeholders,
            keywords,
            section=app,
            credentials=credentials)
        d = group_tweets_by_screen_name([d['tweet'] for d in result])
        return render({'tweets': d.items()}, template='stakeholdertweets.jinja2')     
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
        

@app.route('/pundittweets')
@app.route('/pundittweets/<app>/<content_id>/')
@content_identifier_required
def pundittweets(app='pundits', content_id=None):
    """
    Retrieve pundit tweets for article with <id>
    """
    try:
        content = request.content
        keywords = content_keywords(content)
                  
        categories = content_categories(content)      
        if not categories:
            raise Exception('No categories found for article')    
        category = categories[0][0]
        
        credentials = get_twitter_credentials(app)
        
        tweets = pundit_tweets(
            category,
            keywords,
            section=app,
            credentials=credentials)
        tweets = dedupe_tweets(tweets)
        return render({'tweets': tweets}, template='pundittweets.jinja2')            
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})

    
@app.route('/topic')
@app.route('/topic/<app>/<content_id>/')
@content_identifier_required
def topic(app='tweettalk', content_id=None):
    """
    Search for tweets related to the topic of article with <id>
    """
    try:
        q = form_query(content_keywords(request.content),
            content_entities(request.content))        
        credentials = get_twitter_credentials(app)
        params = {'q': q, 'count': 100, 'result_type': 'mixed'}
        result = search(params, section=app, credentials=credentials)  
        tweets = filter_tweets_by_stoplist(result.statuses, 'media')
        return render( {'tweets': tweets }, template='topic.jinja2')
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})


def _reddit_search(query):
    """
    Send query to Reddit search
    """
    reddits = []   
    if query:
        headers = {'User-Agent' : 'Mozilla/5.0'}
        params = {
            'q': query,
            'limit': 10,
            'sort': 'relevance',
            't': 'month'
        }
        r = requests.get('http://www.reddit.com/search.json', params=params,
            headers=headers)
        d = r.json()
        if 'error' in d:
            if d['error'] == 429:
                raise Exception('You are being rate limited by Reddit')
            else:
                raise Exception(d['error'])       
        if 'data' in d and 'children' in d['data']:
            for r in d['data']['children']:
                reddits.append({
                    'id': r['data']['id'],
                    'title': r['data']['title'],
                    'permalink': 'http://www.reddit.com'+r['data']['permalink']
                })   
    return reddits
    
@app.route('/reddits')
@app.route('/reddits/<app>/<content_id>/')
@content_identifier_required
def reddits(app='readdit', content_id=None):
    """
    Search for reddits related to the topic of article with <id>
    https://www.reddit.com/dev/api#GET_search
    
    The extension performs these functions on the client side due to 
    rate limiting, but the website needs this.
    """
    try:
        # Search by url
        reddits = _reddit_search(request.content['url'])
                    
        # Search by keyword
        keywords = content_keywords(request.content)        
        q = '+'.join(x['keyword'] for x in keywords[:3])        
        more_reddits = _reddit_search(q)
            
        # De-dupe
        for i in xrange(len(more_reddits) - 1, -1 -1):
            id = more_reddits[i]['data']['id']
            for r in reddits:
                if id == r['id']:
                    del more_reddits[i]
        
        reddits.extend(more_reddits)
                           
        return render({'reddits': reddits}, template='reddits.jinja2')    
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
                        

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
