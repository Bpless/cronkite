from datetime import timedelta
import logging
import time

from tornado import httpclient, gen, ioloop, queues
import tornado.process

from tornado.gen import Task, Return, coroutine
from tornado.ioloop import IOLoop

from transport import SyncTransport

STREAM = tornado.process.Subprocess.STREAM

concurrency = 10


class ProducerTransport(SyncTransport):
    EXCHANGE_NAME = 'cmd_to_run'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'text'
    ROUTING_KEY = 'example.text'


conn = ProducerTransport('127.0.0.1')
conn.publish({'cmd': 'ls', 'id': 1})
conn.publish({'cmd': 'fake zz', 'id': 3})
conn.publish({'cmd': 'sleep 10; pwd', 'id': 2})
