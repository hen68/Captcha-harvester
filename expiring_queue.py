from queue import Queue, SimpleQueue
from threading import Timer
from typing import Any


class ExpiringQueue(Queue):
    def __init__(self, timeout: int, maxsize=0):
        super().__init__(maxsize)
        self.timeout = timeout
        self.timer: 'SimpleQueue[Timer]' = SimpleQueue()

    def put(self, item) -> Any:
        thread = Timer(self.timeout, self.expire)
        thread.start()
        self.timer.put(thread)
        super().put(item)

    def get(self, block=True, timeout=None) -> Any:
        thread = self.timer.get(block, timeout)
        thread.cancel()
        return super().get()

    def expire(self):
        self.get()

    def is_empty(self):
        return super().empty()

    def get_list(self):
        return list(self.queue)



