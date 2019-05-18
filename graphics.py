import cairo
import info
import linuxfb
import sys


class ManagedCairoSurface(object):
    def __init__(self, *args):
        self.args = args

    def __enter__(self):
        self.surface = cairo.ImageSurface.create_for_data(*self.args)
        return self.surface

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.surface.finish()


def fb_to_cairo_format(fb_format):
    return cairo.Format.__dict__.get(fb_format, cairo.Format.INVALID)


def main(argv):
    fb_info = info.minimal_info(info.extract_info(linuxfb.get_info()))

    print(f"Resolution: {fb_info['resolution'][0]} x {fb_info['resolution'][1]}\nSize: {fb_info['size']} B\nPixel Format: {fb_info['pixel_format']}")

    print("Cairo Format: " + str(fb_to_cairo_format(fb_info['pixel_format'])))


if __name__ == '__main__':
    main(sys.argv[1:])
