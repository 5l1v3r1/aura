from functools import partial
import os

import tqdm


class QueueProgressBar(tqdm.tqdm):
    def __init__(self, *, queue, **kwargs):
        super().__init__(disable=disable(), **kwargs)
        queue.put = partial(self.put_queue, progress=self, func=queue.put)
        self._track_queue = queue
        self._queue_total = 0


    def _update_queue(self):
        if not self.disable:
            self.reset(self._queue_total)
            self.n = self._queue_total - self._track_queue.qsize()
            self.refresh()

    @staticmethod
    def put_queue(*args, progress, func, **kwargs):
        progress._queue_total += 1
        progress._update_queue()
        return func(*args, **kwargs)


def disable():
    return ("AURA_NO_PROGRESS" in os.environ)
