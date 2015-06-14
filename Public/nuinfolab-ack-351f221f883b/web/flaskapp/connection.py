import sys
import os
import pymongo

# Get settings module

# Connect to mongo database
host = os.getenv('ACK_MONGO_HOST', '127.0.0.1')
_conn = pymongo.Connection(host, 27017)
_db = _conn['ack']

# Mongo collections
_content = _db['content']

# Ensure indicies
_content.ensure_index('url')
  
