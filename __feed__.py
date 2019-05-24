import cairo
import math
from PIL import Image
from opensimplex import OpenSimplex
import random
import numpy as np

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
        # last frame drawing
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

def seed_position():
    return (random.uniform(0, 1000), random.uniform(0, 1000)), (random.uniform(0, 1000), random.uniform(0, 1000))

def repeater(f, *args, **kwargs):
    while True:
        yield f(*args, **kwargs)

def seed_position_gen():
    return repeater(seed_position)

def seed_gen():
    return repeater(lambda: random.randint(0, 1000))

class NoiseElement(object):
    def static_circle(pos=(0, 0), amp=1.0):
        return lambda p, _=0: (pos[0] + amp * math.cos(p * FULL_ANGLE), pos[1] + amp * math.sin(p * FULL_ANGLE))

    def __init__(self, noise, curve_fn, closed=True, seed_position=seed_position()):
        self.noise = noise
        self.curve_fn = curve_fn
        self.seed_position_x, self.seed_position_y = seed_position
        self.closed = closed

    def _paths(self, roughness, wildness, amplitude):
        x = NoiseElement.static_circle(self.seed_position_x, roughness)
        y = NoiseElement.static_circle(self.seed_position_y, roughness)
        t = NoiseElement.static_circle(amp=wildness)
        return x, y, t

    def setup_paths(self, roughness, wildness, amplitude):
        self.noise_path_x, self.noise_path_y, self.time_path = self._paths(roughness, wildness, amplitude)

    def setup(self, steps, time_steps, roughness, wildness, amplitude):
        self.setup_paths(roughness, wildness, amplitude)
        self.steps = steps
        self.time_steps = time_steps

        self.displacements_x = np.zeros((self.steps, self.time_steps))
        self.displacements_y = np.zeros((self.steps, self.time_steps))

        for step in range(self.steps):
            xnx, xny = self.noise_path_x(step / self.steps)
            ynx, yny = self.noise_path_y(step / self.steps)
            for time_step in range(self.time_steps):
                tnx, tny = self.time_path(time_step / self.time_steps)
                self.displacements_x[step, time_step] = amplitude * self.noise.noise4d(xnx, xny, tnx, tny)
                self.displacements_y[step, time_step] = amplitude * self.noise.noise4d(ynx, yny, tnx, tny)

    def get(self, step, time_step):
        p = step / self.steps
        time = time_step / self.time_steps
        x, y = self.curve_fn(p, time)
        return x + self.displacements_x[step, time_step], y + self.displacements_y[step, time_step]

    def generate(self, p, time, roughness, wildness, amplitude):
        xnx, xny = self.noise_path_x(p)
        ynx, yny = self.noise_path_y(p)
        tnx, tny = self.time_path(time)
        x, y = self.curve_fn(p, time)
        return x + self.noise.noise4d(xnx, xny, tnx, tny), y + self.noise.noise4d(ynx, yny, tnx, tny)

    def draw(self, ctx, f, points=False):
        time_step = f % self.time_steps
        for step in range(self.steps):
            x, y = self.get(step, time_step)
            if points:
                ctx.move_to(x, y)
                ctx.close_path()
                ctx.stroke()
            else:
                mark = ctx.move_to if step == 0 else ctx.line_to
                mark(x, y)
        if not points:
            if self.closed:
                ctx.close_path()
            ctx.stroke()

def brahmagupta(a, b, c, d):
    s = (a + b + c + d) / 2
    return math.sqrt((s - a) * (s - b) * (s - c) * (s - d))

def dist(a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return math.sqrt(dx**2 + dy**2)

class NoiseRibbon(object):
    def __init__(self, curves, closed=True, seeds=seed_gen(), seed_positions=seed_position_gen()):
        self.closed = closed
        self.noises = [OpenSimplex(seed) for _, seed in zip(range(len(curves)), seeds)]
        self.noise_elements = [NoiseElement(noise, curve, closed, seed_position) for noise, curve, seed_position in zip(self.noises, curves, seed_positions)]

    def setup(self, steps, time_steps, roughness, wildness, amplitude):
        self.steps = steps
        self.time_steps = time_steps
        for elem in self.noise_elements:
            elem.setup(steps, time_steps, roughness, wildness, amplitude)

    def get(self, step, time_step):
        p1 = [curve.get(step, time_step) for curve in self.noise_elements]
        step = (step + 1) % self.steps
        p2 = [curve.get(step, time_step) for curve in self.noise_elements]
        return p1, p2

    def draw(self, ctx, f, brightness=1):
        time_step = f % self.time_steps
        steps = self.steps
        if not self.closed:
            steps -= 1
        for step in range(steps):
            p1, p2 = self.get(step, time_step)
            for a, b, c, d in zip(p1, p1[1:], p2[1:], p2):
                ctx.move_to(*a)
                ctx.line_to(*b)
                ctx.line_to(*c)
                ctx.line_to(*d)
                ctx.close_path()
                area = brahmagupta(dist(a, b), dist(b, c), dist(c, d), dist(d, a))
                color = (0,0,0)
                ctx.set_source_rgba(*color, math.pow(area, brightness))
                ctx.fill()

class NoiseDrawer(Drawer):
    def heart(amp=200):
        def _heart(p, t):
            p *= FULL_ANGLE
            p += t * FULL_ANGLE
            x = amp/15*16*math.sin(p)**3
            y = amp/15*(-13*math.cos(p)+5*math.cos(2*p)+2*math.cos(3*p)+math.cos(4*p))
            return x, y
        return _heart

    def _setup(self, ctx, w, h, argv):
        brightness = float(argv[0]) if len(argv) > 0 else 1/2
        self.radius = 200
        self.steps = 500
        self.period_len = 500
        roughness = 5
        wildness = 0.5
        amplitude = 100
        self.brightness = math.log(brightness, amplitude * FULL_ANGLE * self.radius / self.steps)
        self.ribbon = NoiseRibbon([NoiseDrawer.heart(self.radius), NoiseDrawer.heart(self.radius)], True)
        self.ribbon.setup(self.steps, self.period_len, roughness, wildness, amplitude)

    def _draw(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0.3, 0.3, 0.3)
        ctx.paint()
        ctx.set_source_rgba(0, 0, 0, 0.3)

        with SubContext(ctx):
            ctx.translate(w/2, h/2)
            self.ribbon.draw(ctx, f, self.brightness)

        return 1/30

    def _last(self, ctx, w, h, f, t):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()


__drawer__ = NoiseDrawer
