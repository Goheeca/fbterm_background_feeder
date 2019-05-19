import os
import stat
import mmap
import time
import signal
import sys
from itertools import takewhile

import info
import graphics
import shared_memory
import cairo
import linuxfb


def main(argv):
    keepWorking = True

    def stopWorking(sig, frame):
        nonlocal keepWorking
        keepWorking = False

    background = argv[0] if len(argv) > 0 else os.getenv('FBTERM_BACKGROUND_IMAGE_PATH', '/fbterm-background-feeder.test')
    consumer = int(argv[1]) if len(argv) > 1 else None

    fb_info = info.minimal_info(info.extract_info(linuxfb.get_info()))
    width, height = fb_info['resolution']
    size = fb_info['size']
    format = graphics.fb_to_cairo_format(fb_info['pixel_format'])
    stride = cairo.ImageSurface.format_stride_for_width(format, width)

    signal.signal(signal.SIGINT, stopWorking)
    signal.signal(signal.SIGQUIT, stopWorking)
    signal.signal(signal.SIGABRT, stopWorking)
    signal.signal(signal.SIGTERM, stopWorking)

    with shared_memory.ManagedSHM(background, os.O_RDWR | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR, unlink=False) as shm:
        os.ftruncate(shm, size)
        with shared_memory.ManagedMMap(shm, size, mmap.MAP_SHARED, mmap.ACCESS_READ | mmap.ACCESS_WRITE, preserve=True) as mem:
            if consumer is None:
                pid_str = ''.join(map(chr, takewhile(lambda byte_: byte_ != 0, mem[:128])))
                if len(pid_str) <= 19:
                    try:
                        consumer = int(pid_str)
                    except ValueError:
                        pass
            with graphics.ManagedCairoSurface(mem, format, width, height, stride) as surface:
                ctx = cairo.Context(surface)
                ctx.scale(width, height)

                i = 0
                colors = [
                    (1, 0, 0),
                    (0, 1, 0),
                    (0, 0, 1)
                ]
                while keepWorking:
                    ctx.set_source_rgb(*colors[i])
                    ctx.rectangle(0, 0, 1, 1)
                    ctx.fill()
                    #surface.flush()
                    if consumer:
                        os.kill(consumer, signal.SIGIO)
                    print(colors[i])
                    i = (i + 1) % len(colors)
                    time.sleep(1)


if __name__ == '__main__':
    main(sys.argv[1:])
