import cairo


def fb_to_cairo_format(fb_format):
    return cairo.Format.__dict__.get(fb_format, cairo.Format.INVALID)


class ManagedCairoSurface(object):
    def __init__(self, mem, format, width, height):
        format = fb_to_cairo_format(format)
        stride = cairo.ImageSurface.format_stride_for_width(format, width)
        self.args = mem, format, width, height, stride

    def __enter__(self):
        self.surface = cairo.ImageSurface.create_for_data(*self.args)
        return self.surface

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.surface.finish()
