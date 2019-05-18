import ctypes
import ctypes.util
import os
import mmap


try:
    unicode
except NameError:
    unicode = str

libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("c"))
librt = ctypes.util.find_library("rt")
if librt:
    librt = ctypes.cdll.LoadLibrary(librt)

# On Linux these are in `librt`. Otherwise use `libc`.
if librt:
    _shm_open = librt.shm_open
    _shm_unlink = librt.shm_unlink
else:
    _shm_open = libc.shm_open
    _shm_unlink = libc.shm_unlink


def shm_open(name, oflag, mode):
    bname = name.encode('utf-8')

    result = _shm_open(
        ctypes.c_char_p(bname),
        ctypes.c_int(oflag),
        ctypes.c_ushort(mode)
    )

    if result == -1:
        raise RuntimeError(os.strerror(ctypes.get_errno()))

    return result


def shm_unlink(name):
    bname = name.encode('utf-8')

    result = _shm_unlink(ctypes.c_char_p(bname))

    if result == -1:
        raise RuntimeError(os.strerror(ctypes.get_errno()))


class ManagedSHM(object):
    def __init__(self, name, oflag, mode):
        self.args = name, oflag, mode
        self.name = name

    def __enter__(self):
        self.fd = shm_open(*self.args)
        return self.fd

    def __exit__(self, exc_type, exc_val, exc_tb):
        shm_unlink(self.name)


class ManagedMMap(object):
    def __init__(self, fd, length, flags, access, offset=0):
        self.args = fd, length, flags, access, offset

    def __enter__(self):
        self.mem = mmap.mmap(*self.args)
        return self.mem

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mem.close()
