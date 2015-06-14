import collections
import ConfigParser
import os
import re
import sys
from os.path import expanduser

ACK_CONFIG_ENV_VAR = 'ACK_CONFIG'
DEFAULT_CONFIG_DIR = expanduser('~')
DEFAULT_CONFIG_FILE = 'ack.cfg'
#INTERNAL_CONFIG_DIR = 'config'
#INTERNAL_CONFIG_FILE = 'ack.cfg'
CONFIG_LIST_REGEX = re.compile(r'[, \s]+')


_config = None
def configuration():
    global _config
    if _config is None:
        _config = ConfigParser.SafeConfigParser()
        path = config_file_path()
        with open(path) as f:
            _config.readfp(f)
    return _config



def config_file_path():
    return os.getenv(ACK_CONFIG_ENV_VAR,
        os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE))


def get_section_data(section='ack'):
    config = configuration()
    d = {}
    for name, value in config.items(section):
        d[name] = value
    return d
    
def get_twitter_keys(section='ack'):
    config = configuration()
    TwitterKeys = collections.namedtuple('TwitterKeys', [
        'consumer_key',
        'consumer_secret',
        'access_token',
        'access_token_secret'])
    k = TwitterKeys(
        config.get(section, 'twitter_consumer_key'),
        config.get(section, 'twitter_consumer_secret'),
        config.get(section, 'twitter_access_token'),
        config.get(section, 'twitter_access_token_secret'))
    return k


def get_named_stoplist(name):
    config = configuration()
    stoplist = config.get('stoplists', name)
    return [s.strip() for s in CONFIG_LIST_REGEX.split(stoplist) if s.strip()]


def get_stoplist_names():
    config = configuration()
    return [name for name, value in config.items('stoplists')]


def get_category_pundits(category):
    config = configuration()
    pundit_panel = config.get('punditpanels', category)
    return [s.strip() for s in CONFIG_LIST_REGEX.split(pundit_panel) if s.strip()]
      
      
def get_pundit_categories():
    config = configuration()
    return [category for category, value in config.items('punditpanels')]
