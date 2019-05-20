import cairo
import math
from enum import Enum

FULL_ANGLE = 2 * math.pi


class Buffer(Enum):
    LOWER = 0
    UPPER = 1


class Drawer(object):
    def __init__(self, surface, double_buffer=False):
        self.surface = surface
        self.ctx = cairo.Context(surface)
        self.double_buffer = double_buffer
        if self.double_buffer:
            self._offset = self.surface.get_height() // 2
            self._lower = cairo.Matrix()
            self._lower.translate(0, 0)
            self._upper = cairo.Matrix()
            self._upper.translate(0, self._offset)
            self._width = self.surface.get_width()
            self._height = self.surface.get_height() // 2

    def setup(self):
        self._complete_buffer = False
        #self.ctx.translate(0, self._offset) #self._clip()
        self._setup(self.ctx, self._width, self._height)
        self.frame = 1
        self.time = 0

    def draw(self):
        self._flip()
        delay = self._draw(self.ctx, self._width, self._height, self.frame, self.time)
        #self._complete_buffer ^= self.double_buffer
        self.frame += 1
        self.time += delay
        return delay

    def last(self):
        self._flip()
        self._last(self.ctx, self._width, self._height, self.frame, self.time)
        #self._complete_buffer ^= self.double_buffer

    def complete_buffer(self):
        return Buffer.UPPER if self._complete_buffer else Buffer.LOWER

    def _flip(self):
        if self.double_buffer:
            current_composed_transform = self.ctx.get_matrix()
            #print(f'COMPOSED: {current_composed_transform}')
            from_ = self._upper if self._complete_buffer else self._lower
            to_ = self._lower if self._complete_buffer else self._upper
            #print(f'    FROM: {from_}')
            #print(f'      TO: {to_}')

            self.ctx.reset_clip()
            self.ctx.set_matrix(to_)
            self.ctx.rectangle(0, 0, self._width, self._height)
            self.ctx.clip()

            from_.invert()
            self.ctx.set_matrix(current_composed_transform * from_ * to_)
            from_.invert()

            self._complete_buffer ^= True

            #print(f'   FINAL: {self.ctx.get_matrix()}')

    def _setup(self, ctx, w, h):
        pass

    def _draw(self, ctx, w, h, f, t):
        return 1.0

    def _last(self, ctx, w, h, f, t):
        pass


class DemoDrawer(Drawer):
    def _setup(self, ctx, w, h):
        #ctx.scale(w, h)
        self.i = 0
        self.time = 0
        self.COLORS = [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)
        ]

    def _draw(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        color = self.COLORS[self.i]
        #if f % 10 == 0:
        #    self.i = (self.i + 1) % len(self.COLORS)
        self.i = int((t / 3) % len(self.COLORS))
        ctx.set_source_rgb(*color)
        omega = 1 * FULL_ANGLE
        amplitude = w/8 if w/8 < h/8 else h/8
        angle = omega * t % FULL_ANGLE
        position = w/2 + amplitude * math.cos(angle), h/2 + amplitude * math.sin(angle)
        ctx.arc(position[0], position[1], 200, 0, FULL_ANGLE)
        ctx.fill()
        #print(f'Color: {color}, Angle: {angle/FULL_ANGLE*360:06.2f}, Position: {position}, {self._complete_buffer}')
        return 0.01

    def _last(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()


__drawer__ = DemoDrawer
