# -*- coding: utf-8 -*-
import codecs
import os
import unittest
from ack.extract import *

cwd = os.path.dirname(os.path.realpath(__file__))

def path(relpath):
    return os.path.join(cwd, relpath)

ARTICLES = [ {
    'path': path('data/web_pages/nytimes.com.2014.08.07.tiger-woods.html'),
    'title': 'Tiger Woods Is Center of Attention at P.G.A. Championship Course',
    'author': 'BILL PENNINGTON',
    'text_start': 'LOUISVILLE, Ky.',
    'text_end': ' Weekley said.',
  }, {
    'path': path('data/web_pages/voanews.com.2014.08.07.2406146.html'),
    'title': "White House 'Gravely Concerned' for Trapped Iraqis",
    'author': None,
    'text_start': 'News / Middle East White House',
    'text_end': 'Bernard Shusman reports from Brooklyn on the New York City program.'
  }, {
    'path': path('data/web_pages/usatoday.com.2014.08.07.13710265.html'),
    'title': 'White House weighing air support for Iraq',
    'author': 'David Jackson and Jim Michaels, USA TODAY',
    'text_start': 'Soldiers of the Kurdish Peshmerga forces',
    'text_end': 'Lewis said, referring to the militants.'
  }, {
    'path': path('data/web_pages/cbsnews.com.2014.08.07.pentagon-considers-air-drops.html'),
    'title': 'Pentagon considers air drops to 15,000 Iraq refugees fleeing ISIS',
    'author': None,
    'text_start': 'The Pentagon is looking at conducting',
    'text_end': 'ISIS militants with little apparent success.',
  }, {
    'path': path('data/web_pages/pcworld.com.2014.08.07.smartphone-killswitch.html'),
    'title': 'Smartphone kill-switch bill passes California assembly',
    'author': 'Martyn Williams',
    'text_start': 'A bill requiring that all smartphones sold',
    'text_end': 'updates to their respective smartphone operating systems.'
  }, {
    'path': path('data/web_pages/narrativescience.com.2014.08.07.democratization-data.html'),
    'title': 'The Democratization of Data',
    'author': 'Kris Hammond',
    'text_start': 'While attending the Aspen Ideas Festival',
    'text_end': 'free us from the limitations of data.'
  },
]

class ExtractTestCase(unittest.TestCase):

    def test_is_attribution(self):
        self.assertFalse(is_attribution('foo'))
        self.assertTrue(is_attribution('by Bob Dylan'))
        self.assertTrue(is_attribution('BY JACK WHITE'))
        self.assertTrue(is_attribution('By Kurt Vonnegut Jr.'))
        self.assertTrue(is_attribution('By J.K. Rowling'))

    def test_article_extractions(self):
        for article in ARTICLES:
            page = codecs.open(article['path'], encoding='utf-8').read()
        extractor = ArticleExtractor(html=page)
        self.assertEqual(extractor.title, article['title'])
        self.assertEqual(extractor.author, article['author'])
        text = extractor.get_article_text()
        self.assertTrue(text[0].startswith(article['text_start']))
        self.assertTrue(text[-1].endswith(article['text_end']))
