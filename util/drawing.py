import cairo


class SubContext(object):
    def __init__(self, ctx):
        self.ctx = ctx

    def __enter__(self):
        self.ctx.save()

    def __exit__(self, *args):
        self.ctx.restore()


class Drawer(object):
    def __init__(self, surface):
        self.surface = surface
        self.ctx = cairo.Context(surface)

    def setup(self, argv):
        self._setup(self.ctx, self.surface.get_width(), self.surface.get_height(), argv)
        self.frame = 1
        self.time = 0

    def draw(self):
        delay = self._draw(self.ctx, self.surface.get_width(), self.surface.get_height(), self.frame, self.time)
        self.frame += 1
        self.time += delay
        return delay

    def last(self):
        self._last(self.ctx, self.surface.get_width(), self.surface.get_height(), self.frame, self.time)

    def _setup(self, ctx, w, h, argv):
        pass

    def _draw(self, ctx, w, h, f, t):
        return 1.0

    def _last(self, ctx, w, h, f, t):
        pass
