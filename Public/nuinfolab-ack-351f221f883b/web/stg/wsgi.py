"""
WSGI config for ack project.
"""
import os
import sys
import site

site.addsitedir('/home/infolab/env/ack/lib/python2.7/site-packages')
sys.path.append('/home/infolab/apps/ack')
sys.path.append('/home/infolab/apps/ack/web/flaskapp')
sys.stdout = sys.stderr

os.environ.setdefault('ACK_CONFIG', '/home/infolab/conf/etc/ack.cfg')
os.environ.setdefault('ACK_MONGO_HOST', 'localhost')

from app import application
