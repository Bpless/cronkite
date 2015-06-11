import datetime
from functools import partial
import logging
from subprocess import CalledProcessError
import shlex
import time

from tornado import httpclient, gen, ioloop, queues
import tornado.process

from tornado.gen import Task, Return, coroutine
from tornado.ioloop import IOLoop

STREAM = tornado.process.Subprocess.STREAM


class Worker(object):
    def __init__(self, work_q, results_q):
        self.work_q = work_q
        self.results_q = results_q

    @coroutine
    def call_subprocess(self):
        """
        Wrapper around subprocess call using Tornado's Subprocess class.
        """
        unit = yield self.work_q.get()

        start = time.time()
        is_timeout = False

        try:
            timeout = partial(
                tornado.gen.with_timeout,
                datetime.timedelta(seconds=unit.get('timeout', 5))
            )

            sub_process = tornado.process.Subprocess(
                unit['cmd'],
                stdin=STREAM,
                stdout=STREAM,
                stderr=STREAM,
                shell=True
            )

            yield timeout(sub_process.wait_for_exit())
        except tornado.gen.TimeoutError:
            is_timeout = True
        except CalledProcessError:
            pass
        except Exception, e:
            print e
        finally:
            if is_timeout:
                results = {
                    'job': unit['id'],
                    'is_timeout': True
                }
            else:
                def reader(data):
                    import pdb; pdb.set_trace()

                sub_process.stdout.read_bytes(4096, reader)

                output, error = yield [
                    Task(sub_process.stdout.read_until_close),
                    Task(sub_process.stderr.read_until_close)
                ]

                results = {
                    'job': unit['id'],
                    'seconds': time.time() - start,
                    'stdout': output,
                    'stderr': error,
                    'returncode': sub_process.returncode,
                }

            print results
            self.work_q.task_done()
            raise Return(results)

    @gen.coroutine
    def run(self):
        while True:
            yield self.call_subprocess()
