#!/usr/bin/env python3

import os
import time
import signal
import sys
import errno

import fbdev_metainfo
import fbterm_feed
import graphics
import drawing


def main(argv):
    keepWorking = True

    def stopWorking(sig, frame):
        nonlocal keepWorking
        keepWorking = False

    background = argv[0] if len(argv) > 0 else os.getenv('FBTERM_BACKGROUND_IMAGE_PATH')
    consumer = int(argv[1]) if len(argv) > 1 else None

    fb_info = fbdev_metainfo.get()
    width, height = fb_info['resolution']
    size = fb_info['size']
    format = fb_info['pixel_format']

    signal.signal(signal.SIGINT, stopWorking)
    signal.signal(signal.SIGQUIT, stopWorking)
    signal.signal(signal.SIGABRT, stopWorking)
    signal.signal(signal.SIGTERM, stopWorking)

    double_buffer = True

    if double_buffer:
        size *= 2
        height *= 2

    try:
        with fbterm_feed.FbtermFeeder(background, size, consumer) as feeder:
            with graphics.ManagedCairoSurface(feeder.get_data(), format, width, height) as surface:
                drawer = drawing.__drawer__(surface, double_buffer)
                drawer.setup()
                while keepWorking:
                    delay = drawer.draw()
                    #surface.flush()
                    feeder.notify_consumer(drawer.complete_buffer() == drawing.Buffer.LOWER)
                    time.sleep(delay)
                drawer.last()
                #surface.flush()
                feeder.notify_consumer(drawer.complete_buffer() == drawing.Buffer.LOWER)
    except RuntimeError:
        sys.exit(errno.ENOENT)
    except ValueError:
        sys.exit(errno.EINVAL)
    except ProcessLookupError:
        sys.exit(errno.EINVAL)
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
