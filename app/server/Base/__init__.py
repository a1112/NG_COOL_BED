from queue import Queue


class RollingQueue(Queue):
    def put(self, item, block=True, timeout=None):
        if self.full():
            self.get()  # 丢弃最旧的数据
        super().put(item, block, timeout)