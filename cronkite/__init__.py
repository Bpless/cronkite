from tornado import httpclient, gen, ioloop, queues
import tornado.process
from tornado.gen import Task, Return, coroutine
from tornado.ioloop import IOLoop


from client.alt_consumer import main

if __name__ == '__main__':
    logging.basicConfig()

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_timeout(5, main)
    ioloop.start()
