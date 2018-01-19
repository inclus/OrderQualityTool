import time

import pygogo
import sys

from prometheus_client import Histogram

TWO_CYCLE = "two_cycle"

IS_INTERFACE = "is_interface"

logger = pygogo.Gogo(__name__).get_structured_logger()
method_execution_time_histogram = Histogram('qdb_method_execution_time_seconds', 'Time taken to execute the method',
                                            ['method'])


def should_log_time():
    return 'test' not in sys.argv


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        duration = te - ts
        method_name = method.__name__
        method_execution_time_histogram.labels(method=method_name).observe(duration)
        if should_log_time():
            logger.info("timer",
                        extra={
                            "method": method_name,
                            "duration": "%2.5f" % duration,
                            "extra": [str(a)[:30] for a in args]})
        return result

    return timed
