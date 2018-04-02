import os
import redis
from celery.utils.log import get_task_logger


REDIS_CLIENT = redis.Redis.from_url(
    url=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)


logger = get_task_logger('send_number')


def only_one(function=None, ikey="", timeout=None):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""

        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            # for item in kwargs.iteritems():
            #     print item
            key = kwargs.get('keytask', ikey)
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    logger.info('Lock Acquired: {0}'.format(key))
                    ret_value = run_func(*args, **kwargs)
                else:
                    print('Failed to Acquire Lock: {0}'.format(key))
                    logger.info('Failed to Acquire Lock: {0}'.format(key))
            finally:
                if have_lock:
                    logger.info('Lock Closed: {0}'.format(key))
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec