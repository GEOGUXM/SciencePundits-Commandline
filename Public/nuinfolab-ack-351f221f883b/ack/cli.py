import click
import pprint
import os
import shutil
import sys
from .config import config_file_path, get_stoplist_names
from .content import get_article
from .entities import extract_entities
from .keywords import get_keywords
from .classifier import classify_text
from .twitter import search, find_twitter_users, stakeholder_tweets, \
    form_query, search_recent, group_tweets_by_text, \
    filter_tweets_by_stoplist, pundit_tweets, dedupe_tweets

pp = pprint.PrettyPrinter()


def edit_file(filename):
    editor = os.getenv('EDITOR')
    if editor is None:
        click.echo('\nPlease set the EDITOR environment variable.\n\n')
        click.echo('e.g.:\n\n   >  export EDITOR=`which vi`')
        sys.exit(0)
    os.system('%s %s' % (editor, filename))


@click.group()
def cli():
    """Ack CLI application"""
    pass


@click.command()
@click.argument('url')
def content(url):
    """Extract primary article content"""
    pp.pprint(get_article(url))


@click.command()
@click.argument('url')
def entities(url):
    """Extract named entities"""
    pp.pprint(extract_entities(get_article(url)['text']))


@click.command()
def config():
    """Configure Ack"""
    edit_file(config_file_path())


@click.command()
@click.option('--destination_file', prompt=True)
def copyconfig(destination_file):
    """Copy internal config to external file"""
    cf = config_file_path()
    if os.path.isdir(destination_file):
        destination_file = os.path.join(destination_file,
            os.path.basename(cf))
    if os.path.exists(destination_file):
        yn = raw_input('Overwrite existing file %s? (y/N)' % destination_file)
        if not yn.lower().startswith('y'):
            return
    try:
        shutil.copy2(cf, destination_file)
        click.echo('\nBe sure to set the ACK_CONFIG environment variable:')
        click.echo('\n $ export ACK_CONFIG=%s' % destination_file)
    except IOError:
        click.echo('Could not copy configuration file to destination: %s' % (
            destination_file))
        click.echo('\nBe sure you have proper write permissions, or use:')
        click.echo('\n $ sudo ack copyconfig\n')


@click.command()
@click.argument('url')
def keywords(url):
    """Extract keywords"""
    article = get_article(url)
    pp.pprint(get_keywords(article['text']))

@click.command()
@click.argument('url')
@click.option('--stoplist', type=click.Choice(get_stoplist_names()))
def stakeholders(url, stoplist):
    """Find content stakeholders"""
    users = find_twitter_users(extract_entities(get_article(url)['text']),
        named_stoplist=stoplist)
    pp.pprint(users)


@click.command()
@click.argument('url')
@click.option('--stoplist', type=click.Choice(get_stoplist_names()))
def stakeholdertweets(url, stoplist):
    """Find content stakeholders"""
    text = get_article(url)['text']
    entities = extract_entities(text)
    users = find_twitter_users(entities, stoplist)
    pp.pprint(stakeholder_tweets(users, get_keywords(text)))


@click.command()
@click.argument('url')
def urlsearch(url):
    """Find tweets by url"""
    pp.pprint(search({'q': url}))


@click.command()
@click.argument('url')
@click.option('--count', default=15, help='number of tweets')
def urlsearchrecent(url, count):
    """Find recent tweets by url, group by text"""
    tweets = search_recent({'q': url, 'count': count})
        
    d = group_tweets_by_text(tweets)
    pairs = sorted(d.items(), key=lambda t: (-1*len(t[1]), t[0]))
    for k, n in pairs:
        print len(n), k
        
    
@click.command()
@click.argument('url')
def topictweets(url):
    """Find tweets by topic"""
    # Get article
    print 'Getting article...'
    article = get_article(url)
    
    print 'Getting keywords...'
    keywords = get_keywords(article['text'])    
    
    print 'Getting entities...'
    entities = extract_entities(article['text'])

    q = form_query(keywords, entities)
    print q

    params = {'q': q, 'count': 100, 'result_type': 'mixed'}
    result = search(params)  

    print 'Processing %d tweets' % len(result.statuses)
        
    tweets = filter_tweets_by_stoplist(result.statuses, 'media')

    print 'Found %d tweets' % len(tweets)
                
    for tweet in tweets:
        print '@'+tweet.user.screen_name, tweet.text

                
@click.command()
@click.argument('url')
def reddits(url):
    """Find reddits by topic"""
    import requests
    
    print 'Getting article...'
    article = get_article(url)

    print 'Searching reddits by URL...'
    headers = {'User-Agent' : 'Mozilla/5.0'}
    params = {
        'limit': 10,
        't': 'month', # was 'week'
        'sort': 'relevance',
        'q': url          
    }
    r = requests.get('http://www.reddit.com/search.json',
        params=params, headers=headers)
    d = r.json()
    if 'data' in d and 'children' in d['data']:
        for item in d['data']['children']:
            print item['data']['title']
            print 'http://www.reddit.com'+item['data']['permalink']  
    else:
        print d     
    
    print 'Getting keywords...'
    keywords = get_keywords(article['text'])    
    
    k = []
    for item in keywords:
        if item['count'] > 1:
            k.append(item['keyword'])    
    pp.pprint(k)

    q = '+'.join(k[:3])
    print 'query =', q
    
    print 'Searching reddits by keyword...'
    headers = {'User-Agent' : 'Mozilla/5.0'}
    params = {
        'limit': 10,
        't': 'month', # was 'week'
        'sort': 'relevance',
        'q': q           
    }
    r = requests.get('http://www.reddit.com/search.json',
        params=params, headers=headers)
    d = r.json()
    
    if 'data' in d and 'children' in d['data']:
        for item in d['data']['children']:
            print item['data']['title']
            print 'http://www.reddit.com'+item['data']['permalink']       
    else:
        print d     
 
     
@click.command()
@click.argument('url')
def categories(url):
    """Get category"""
    print 'Getting article...'
    text = get_article(url)['text']
    print 'Getting categories...'
    pp.pprint(classify_text(text))


@click.command()
@click.argument('url')
def pundittweets(url):
    """Find tweets by topic from pundits in category"""
    # Get article
    print 'Getting article...'
    text = get_article(url)['text']
    
    print 'Getting keywords...'
    keywords = get_keywords(text)    

    print 'Getting categories...'
    categories = classify_text(text)
    if not categories:
        raise Exception('No categories found for article')    
    category = categories[0][0]
    
    print 'Searching for tweets...'
    tweets = pundit_tweets(category, keywords)
    tweets = dedupe_tweets(tweets)
    
    for t in tweets:
        print '@%s' % t.user.screen_name
        print t.text

#
# development code...
#
@click.command()
@click.argument('url')
@click.option('--count', default=15, help='number of tweets')
def tw_pickle(url, count):
    """Find recent tweets by url, group by text"""
    import pickle
    tweets = search_recent({'q': url, 'count': count})    
    pickle.dump(tweets, open( "tweets.p", "wb" ) )
 
@click.command()
def tw_unpickle():
    """Find recent tweets by url, group by text"""
    import pickle
    tweets = pickle.load(open( "tweets.p", "rb"))  
    
    d = group_tweets_by_text(tweets)
    pairs = sorted(d.items(), key=lambda t: (-1*len(t[1]), t[0]))
    for k, n in pairs:
        print len(n), k
    
              
cli.add_command(content)
cli.add_command(entities)
cli.add_command(keywords)
cli.add_command(config)
cli.add_command(copyconfig)
cli.add_command(stakeholders)
cli.add_command(stakeholdertweets)
cli.add_command(urlsearch)
cli.add_command(urlsearchrecent)
cli.add_command(topictweets)
cli.add_command(reddits)
cli.add_command(categories)
cli.add_command(pundittweets)

cli.add_command(tw_pickle)
cli.add_command(tw_unpickle)
