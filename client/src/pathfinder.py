# vim:set sw=2 ts=2 sts=2 et:

import math

from Box2D import *

from OpenGL.GL import *
from OpenGL.GLU import *


class Parabola(object):
  def __init__(self, p0, d0, t_hit, gravity):
    self.p0, self.d0 = p0, d0
    self.t_hit = t_hit
    self.gravity = gravity

  def __call__(self, t):
    x = self.p0.x + self.d0.x * t
    y = self.p0.y + self.d0.y * t - 0.5*self.gravity * t*t
    return b2Vec2(x, y)

  def d(self, t):
    x = self.d0.x
    y = self.d0.y - self.gravity * t
    return b2Vec2(x, y)

  def plot(self):

    glDisable(GL_TEXTURE_2D)
    glColor3f(1,0,0)

    glBegin(GL_LINE_STRIP)
    for t in xrange(20):
      v = self(self.t_hit * (t/20.0))
      glVertex3f(v.x, v.y, 0)

    glEnd()

  def world_trace(self, world, target_body, source_body, clearance, step=0.1):
    t = 0
    seg = b2Segment()
    while t <= self.t_hit - step:
      p1 = self(t)
      p2 = self(t+step)

      d1 = self.d(t)
      d2 = self.d(t+step)

      perp1 = b2Vec2(d1.y, -d1.x)
      perp1.Normalize()
      perp1 *= clearance
        
      perp2 = b2Vec2(d2.y, -d2.x)
      perp2.Normalize()
      perp2 *= clearance
        
      # Box2d seems to raycast backwards
      seg.p2 = p1 + perp1
      seg.p1 = p2 + perp2

      (r, n, shape) = world.RaycastOne(seg, False, None)

      if shape:
        body = shape.GetBody()
        if body.this == target_body.this:
          return True
        elif body.this != source_body.this:
          return False

      seg.p2 = p1 - perp1
      seg.p1 = p2 - perp2

      (r, n, shape) = world.RaycastOne(seg, False, None)

      if shape:
        body = shape.GetBody()
        if body.this == target_body.this:
          return True
        elif body.this != source_body.this:
          return False

      t += step

    return True

  def to_network(self, msg):
    msg.append(self.p0.x)
    msg.append(self.p0.y)
    msg.append(self.d0.x)
    msg.append(self.d0.y)
    msg.append(self.t_hit)
    msg.append(self.gravity)

  def from_network(self, msg):
    px = float(msg.pop())
    py = float(msg.pop())
    dx = float(msg.pop())
    dy = float(msg.pop())
    
    self.p0 = b2Vec2(px, py)
    self.d0 = b2Vec2(dx, dy)
    self.t_hit = float(msg.pop())
    self.gravity = float(msg.pop())


def find_parabola(world, target_body, source_body,
                  target, source, v0_max, clearance, step=0.05):
  """
  Find a clear parabola in the world between the target and source
  """

  target = b2Vec2(target)
  source = b2Vec2(source)
  gravity = abs(world.GetGravity().y)

  v0_max *= v0_max

  t = step
  d0 = _solve_d0(target, source, t, gravity)

  last_v2 = 10000000000
  v2 = d0.LengthSquared()

  while v2 > v0_max:
    t += step
    d0 = _solve_d0(target, source, t, gravity)

    last_v2 = v2
    v2 = d0.LengthSquared()

    if last_v2 < v2:
      return None

  while d0.LengthSquared() < v0_max:
    p = Parabola(source, d0, t, gravity)
    if p.world_trace(world, target_body, source_body, clearance):
      return p

    t += step
    d0 = _solve_d0(target, source, t, gravity)

  return None

def _solve_d0(target, source, t, gravity):
  """
  find dy0 parabola between source and target with dx0
  """

  p1 = target - source

  dx = p1.x / t
  dy = (p1.y + 0.5 * gravity * t*t) / t

  return b2Vec2(dx, dy)

