import cairo
import math
from PIL import Image

if __package__ == '':
    from util.drawing import Drawer, SubContext
else:
    from .util.drawing import Drawer, SubContext

FULL_ANGLE = 2 * math.pi


class ZeroDrawer(Drawer):
    def _setup(self, ctx, w, h, argv):
        # once before drawing
        pass

    def _draw(self, ctx, w, h, f, t):
        delay = 0.03
        # frame drawing
        return delay

    def _last(self, ctx, w, h, f, t):
        # last frame drawing
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()


__drawer__ = ZeroDrawer
