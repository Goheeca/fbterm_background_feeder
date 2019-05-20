#!/usr/bin/env python3

import os
import time
import signal
import sys
import errno

if __package__ is None:
    import util.fbdev_metainfo as fb, util.fbterm_feed as term, util.graphics as g, __feed__
else:
    from .util import fbdev_metainfo as fb, fbterm_feed as term, graphics as g
    from . import __feed__


def main(argv, feed=__feed__.__drawer__):
    keepWorking = True

    def stopWorking(sig, frame):
        nonlocal keepWorking
        keepWorking = False

    background = argv[0] if len(argv) > 0 else os.getenv('FBTERM_BACKGROUND_IMAGE_PATH')

    fb_info = fb.get()
    width, height = fb_info['resolution']
    size = fb_info['size']
    format = fb_info['pixel_format']

    signal.signal(signal.SIGINT, stopWorking)
    signal.signal(signal.SIGQUIT, stopWorking)
    signal.signal(signal.SIGABRT, stopWorking)
    signal.signal(signal.SIGTERM, stopWorking)

    try:
        with term.FbtermFeeder(background, size, None) as feeder:
            with g.ManagedCairoSurface(feeder.get_data(), format, width, height) as surface:
                drawer = feed(surface)
                drawer.setup(argv[1:])
                while keepWorking:
                    delay = drawer.draw()
                    feeder.notify_consumer()
                    time.sleep(delay)
                drawer.last()
                feeder.notify_consumer()
    except RuntimeError:
        sys.exit(errno.ENOENT)
    except ValueError:
        sys.exit(errno.EINVAL)
    except ProcessLookupError:
        sys.exit(errno.EINVAL)
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
