from datetime import timedelta
import logging
import time

from tornado import httpclient, gen, ioloop, queues
import tornado.process

from tornado.gen import Task, Return, coroutine
from tornado.ioloop import IOLoop

from transport import AsyncTransport
from worker import Worker

STREAM = tornado.process.Subprocess.STREAM

concurrency = 10


class ConsumerTransport(AsyncTransport):
    EXCHANGE_NAME = 'cmd_to_run'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'text'
    ROUTING_KEY = 'example.text'


@gen.coroutine
def main():
    work_q = queues.Queue()
    results_q = queues.Queue()

    ConsumerTransport('127.0.0.1', work_q, results_q)

    # Start workers, then wait for the work queue to be empty.
    for _ in range(concurrency):
        Worker(work_q, results_q).run()


if __name__ == '__main__':
    logging.basicConfig()

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(main)
    ioloop.start()
