import os
import stat
import mmap
import signal
from itertools import takewhile

import shared_memory


class FbtermFeeder(object):
    def __init__(self, name, size, double_buffer=False, consumer_pid=None):
        self.name = name
        self.size = size
        self.double_buffer = double_buffer
        self.consumer_pid = consumer_pid
        self._shm = None
        self._mmap = None

    def __enter__(self):
        self._managedSHM = shared_memory.ManagedSHM(self.name, os.O_RDWR, stat.S_IRUSR | stat.S_IWUSR, unlink=False)
        self._shm = self._managedSHM.__enter__()
        os.ftruncate(self._shm, self.size)
        self._managedMMap = shared_memory.ManagedMMap(self._shm, self.size, mmap.MAP_SHARED, mmap.ACCESS_READ | mmap.ACCESS_WRITE, preserve=True)
        self._mmap = self._managedMMap.__enter__()
        if self.consumer_pid is None:
            self._read_consumer_pid()
        return self

    def _read_consumer_pid(self):
        pid_str = ''.join(map(chr, takewhile(lambda byte_: byte_ != 0, self._mmap[:128])))
        if len(pid_str) <= 19:
            self.consumer_pid = int(pid_str)

    def get_data(self):
        return self._mmap

    def notify_consumer(self, lower_buffer):
        if self.consumer_pid:
            signo = signal.SIGIO if lower_buffer else signal.SIGURG
            os.kill(self.consumer_pid, signo)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._mmap:
            self._managedMMap.__exit__(exc_type, exc_val, exc_tb)
        self._managedSHM.__exit__(exc_type, exc_val, exc_tb)
