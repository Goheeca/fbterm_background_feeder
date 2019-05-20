import ctypes
import ctypes.util
import os
import mmap


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
    def __init__(self, name, oflag, mode, unlink=True):
        self.args = name, oflag, mode
        self.name = name
        self.unlink = unlink

    def __enter__(self):
        self.fd = shm_open(*self.args)
        return self.fd

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.unlink:
            shm_unlink(self.name)
        else:
            os.close(self.fd)


class ManagedMMap(object):
    def __init__(self, fd, length, flags, access, offset=0, preserve=False):
        self.args = fd, length, flags, access, offset
        self.preserve = preserve

    def __enter__(self):
        self.mem = mmap.mmap(*self.args)
        if self.preserve:
            self.data = self.mem.read(self.mem.size())
            self.mem.seek(0, os.SEEK_SET)
        return self.mem

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.preserve:
            self.mem.seek(0, os.SEEK_SET)
            self.mem.write(self.data)
            self.mem.seek(0, os.SEEK_SET)
        self.mem.close()
