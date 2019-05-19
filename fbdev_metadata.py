import os
import ctypes
import fcntl

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602


class ManagedFd(object):
    def __init__(self, *args):
        self.args = args

    def __enter__(self):
        self.fd = os.open(*self.args)
        return self.fd

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.close(self.fd)


class FixScreenInfo(ctypes.Structure):
    _fields_ = [
        ('id_name', ctypes.c_char * 16),
        ('smem_start', ctypes.c_ulong),
        ('smem_len', ctypes.c_uint32),
        ('type', ctypes.c_uint32),
        ('type_aux', ctypes.c_uint32),
        ('visual', ctypes.c_uint32),
        ('xpanstep', ctypes.c_uint16),
        ('ypanstep', ctypes.c_uint16),
        ('ywrapstep', ctypes.c_uint16),
        ('line_length', ctypes.c_uint32),
        ('mmio_start', ctypes.c_ulong),
        ('mmio_len', ctypes.c_uint32),
        ('accel', ctypes.c_uint32),
        ('reserved', ctypes.c_uint16 * 3),
    ]


class FbBitField(ctypes.Structure):
    _fields_ = [
        ('offset', ctypes.c_uint32),
        ('length', ctypes.c_uint32),
        ('msb_right', ctypes.c_uint32),
    ]


class VarScreenInfo(ctypes.Structure):
    _fields_ = [
        ('xres', ctypes.c_uint32),
        ('yres', ctypes.c_uint32),
        ('xres_virtual', ctypes.c_uint32),
        ('yres_virtual', ctypes.c_uint32),
        ('xoffset', ctypes.c_uint32),
        ('yoffset', ctypes.c_uint32),

        ('bits_per_pixel', ctypes.c_uint32),
        ('grayscale', ctypes.c_uint32),

        ('red', FbBitField),
        ('green', FbBitField),
        ('blue', FbBitField),
        ('transp', FbBitField),
    ]


def get_fix_info(fd):
    fix_info = FixScreenInfo()
    fcntl.ioctl(fd, FBIOGET_FSCREENINFO, fix_info)
    return fix_info


def get_var_info(fd):
    var_info = VarScreenInfo()
    fcntl.ioctl(fd, FBIOGET_VSCREENINFO, var_info)
    return var_info


def get(fbdev=None):
    dev = fbdev or os.getenv('FRAMEBUFFER', '/dev/fb0')
    with ManagedFd(dev, os.O_RDWR) as fd:
        fix_info = get_fix_info(fd)
        var_info = get_var_info(fd)
        return fix_info, var_info
