import newspaper
import urllib2
from .extract import ArticleExtractor
try:
    from goose import Goose
except ImportError:
    Goose = None


def opener():
    return urllib2.build_opener(urllib2.HTTPCookieProcessor())


def fetch(url):
    return opener().open(url).read()
    

def extract_with_goose(html):
    a = Goose().extract(raw_html=html)
    return {
        'html': html,
        'title': a.title,
        'text': a.cleaned_text
    }


def fetch_extract_with_newspaper(url):
    a = newspaper.Article(url)
    a.download()
    a.parse()
    return {
        'url': url,
        'html': a.html,
        'title': a.title,
        'text': a.text
    }


def get_article(url):        
    #extractor = ArticleExtractor(url=url)
    #text = ' '.join(extractor.get_article_text())
    #if text.strip() != '':
    #    return {
    #        'url': url,
    #        'title': extractor.title,
    #        'text': text,
    #        'html': extractor.html
    #    }
    newspaper_article = fetch_extract_with_newspaper(url)
    if newspaper_article['text']:
        return newspaper_article
    article = { 'url': url }
    if newspaper_article['html']:
        article['html'] = newspaper_article['html']
    else:
        article['html'] = fetch(url)
    if Goose is not None:
        goose = extract_with_goose(article['html'])
        article['title'] = goose['title']
        article['text'] = goose['text']
    else:
        article['title'] = ''
        article['text'] = ''
    return article
