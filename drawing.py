import cairo


class Drawer(object):
    def __init__(self, surface):
        self.surface = surface
        self.ctx = cairo.Context(surface)

    def setup(self):
        self._setup(self.ctx, self.surface.get_width(), self.surface.get_height())

    def draw(self):
        return self._draw(self.ctx, self.surface.get_width(), self.surface.get_height())

    def _setup(self, ctx, w, h):
        pass

    def _draw(self, ctx, w, h):
        return 1.0


class DemoDrawer(Drawer):
    def _setup(self, ctx, w, h):
        ctx.scale(w, h)
        self.i = 0
        self.COLORS = [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)
        ]

    def _draw(self, ctx, w, h):
        color = self.COLORS[self.i]
        ctx.set_source_rgb(*color)
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()
        print(color)
        self.i = (self.i + 1) % len(self.COLORS)
        return 1.0


__drawer__ = DemoDrawer
