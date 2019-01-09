from threading import Thread
from queue import Queue
import sys


class Generator(object):

    def __init__(self, iterator,
                 sentinel=object(),
                 queue_maxsize=0,
                 daemon=False):
        self._iterator = iterator
        self._sentinel = sentinel
        self._queue = Queue(maxsize=queue_maxsize)

        # repr函数将对象转化为供解释器读取的形式
        self._thread = Thread(
            name=repr(iterator),
            target=self._run
        )
        self._thread.daemon = daemon
        self._started = False

    '''
        重写repr  !r是对于format结果的占位符   必须和format配合用
    '''
    def __repr__(self):
        return 'thread_manager.Generator({!r})'.format(self._iterator)

    def __iter__(self):
        self._started = True
        self._thread.start()
        for value in iter(self._queue.get, self._sentinel):
            yield value
        self._thread.join()
        self._started = False

    def __next__(self):
        if not self._started:
            self._started = True
            self._thread.start()
        value = self._queue.get(timeout=30)
        if value == self._sentinel:
            raise StopIteration()
        return value

    '''
        
    '''
    def _run(self):
        try:
            for value in self._iterator:
                # 如果没有启动
                if not self._started:
                    return

                self._queue.put(value)
        finally:
            self._queue.put(self._sentinel)

    def close(self):
        self._started = False
        try:
            while True:
                self._queue.get(timeout=30)

        # 捕获用户键盘操作的异常
        except KeyboardInterrupt as e:
            raise e
        except:
            # 回溯最后的异常并打印
            info = sys.exc_info()
            print(info[0], ":", info[1])
