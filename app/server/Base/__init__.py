from queue import Queue


class RollingQueue:
    def __init__(self, maxsize=0, queue_cls=Queue):
        self._queue = queue_cls(maxsize)
        self._maxsize = maxsize

    def put(self, item, block=True, timeout=None):
        if self.full():
            try:
                self.get(block=False)
            except Exception:
                pass
        self._queue.put(item, block, timeout)

    def put_nowait(self, item):
        return self.put(item, block=False)

    def get(self, block=True, timeout=None):
        return self._queue.get(block, timeout)

    def get_nowait(self):
        return self.get(block=False)

    def full(self):
        try:
            return self._queue.full()
        except Exception:
            if self._maxsize <= 0:
                return False
            try:
                return self._queue.qsize() >= self._maxsize
            except Exception:
                return False

    def empty(self):
        try:
            return self._queue.empty()
        except Exception:
            try:
                return self._queue.qsize() == 0
            except Exception:
                return False

    def qsize(self):
        try:
            return self._queue.qsize()
        except Exception:
            return 0

    def close(self):
        close = getattr(self._queue, "close", None)
        if callable(close):
            close()

    def join_thread(self):
        join_thread = getattr(self._queue, "join_thread", None)
        if callable(join_thread):
            join_thread()

    def cancel_join_thread(self):
        cancel_join_thread = getattr(self._queue, "cancel_join_thread", None)
        if callable(cancel_join_thread):
            cancel_join_thread()
