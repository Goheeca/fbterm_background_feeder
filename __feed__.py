import cairo
import math
from PIL import Image

if __package__ == '':
    from util.drawing import Drawer, SubContext
else:
    from .util.drawing import Drawer, SubContext

FULL_ANGLE = 2 * math.pi


class DemoDrawer(Drawer):
    def _setup(self, ctx, w, h, _):
        self.i = 0
        self.COLORS = [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)
        ]

    def _draw(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        color = self.COLORS[self.i]
        if f % 100 == 0:
            self.i = (self.i + 1) % len(self.COLORS)
        ctx.set_source_rgb(*color)
        omega = 1 * FULL_ANGLE
        amplitude = w/8 if w/8 < h/8 else h/8
        angle = omega * t % FULL_ANGLE
        position = w/2 + amplitude * math.cos(angle), h/2 + amplitude * math.sin(angle)
        ctx.arc(position[0], position[1], 200, 0, FULL_ANGLE)
        ctx.fill()
        return 0.01

    def _last(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()


class ImageDrawer(Drawer):
    def _setup(self, ctx, w, h, argv):
        self.img = Image.open(argv[0])
        self.period = self.img.n_frames
        self.current = -1

    def _draw(self, ctx, w, h, f, t):
        delay = 0.015
        primary_color = 164/255, 24/255, 40/255
        ctx.set_source_rgb(*primary_color)
        ctx.paint()

        frame_number = int(t / delay) % self.period
        if self.current != frame_number:
            self.current = frame_number
            self.img.seek(frame_number)
            frame = self.img.convert('RGBA')
            self.fw = frame.width
            self.fh = frame.height
            self.frame_surface = cairo.ImageSurface.create_for_data(bytearray(frame.tobytes('raw', 'BGRa')), cairo.FORMAT_ARGB32, frame.width, frame.height)

        with SubContext(ctx):
            s = 0.5
            ctx.scale(s, s)
            with SubContext(ctx):
                inner_center = w/s - self.fw/2, h/s
                ctx.translate(*inner_center)
                ctx.scale(self.fw, self.fh)
                shadow_color = 133/255, 124/255, 104/255
                rg = cairo.RadialGradient(0, 0, 0.02, 0, 0, 1.5)
                rg.add_color_stop_rgba(0, *map(lambda v: v*1.5, shadow_color), 1)
                rg.add_color_stop_rgba(0.2, *shadow_color, 1)
                rg.add_color_stop_rgba(1, *primary_color, 0)
                ctx.set_source(rg)
                ctx.paint()
            ctx.translate(w/s - self.fw, h/s - self.fh)
            ctx.set_source_surface(self.frame_surface, 0, 0)
            ctx.paint()
        ctx.set_source_rgba(0, 0, 0, 0.8)
        ctx.paint()
        return delay

    def _last(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()


__drawer__ = ImageDrawer
