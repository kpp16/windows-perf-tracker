import logging
from threading import Timer

logger = logging.getLogger(__name__)

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False

    def _run(self):
        self.function(*self.args, **self.kwargs)
        if self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()

    def start(self):
        if self.is_running:
            return
        logger.info("Starting timer")
        self.is_running = True
        self._timer = Timer(self.interval, self._run)
        self._timer.start()

    def stop(self):
        if not self.is_running or not self._timer:
            return
        logger.info("Stopping timer")
        self.is_running = False
        self._timer.cancel()

