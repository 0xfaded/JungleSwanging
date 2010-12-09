# vim:set sw=2 ts=2 sts=2 et:

import math
import random
import monkey
from Box2D import *

class SmallExplosion(object):
  # the radius of the query is calculated such that at
  # its limit min_impulse is applied. Objects that would
  # this recieve an impulse less than this are ignored
  min_impulse = 5

  # Anything that is very close to center of explosion
  # has its impulse calculated using this impluse
  min_distance  = 0.2
  min_distance2 = min_distance * min_distance

  def __init__(self, b2_world):
    self.world = b2_world

  def explode_at(self, at, impulse_at_1m):
    radius = math.sqrt(impulse_at_1m / self.min_impulse)
    corner = b2Vec2(radius, radius)
    bounds = b2AABB()
    bounds.lowerBound = -corner + at
    bounds.upperBound =  corner + at

    (n, shapes) = self.world.Query(bounds, 32)

    already_bombed = set()

    for shape in shapes:
      body = shape.GetBody()
      addr = int(body.this)
      if addr in already_bombed:
        continue

      already_bombed.add(addr)

      s = body.position - at

      length2 = s.LengthSquared()
      if length2 == 0:
        s_norm = b2Vec2(0, 1)
        length2 = self.min_distance2
      else:
        s_norm = s.copy()
        s_norm.Normalize()
        if length2 < self.min_distance2:
          length2 = self.min_distance2

      impulse = s_norm * impulse_at_1m / length2

      # Apply the impulse at a slight offset to generate some torque
      offset_x = (random.random() - 0.5) / 5
      offset_y = (random.random() - 0.5) / 5
      offset = b2Vec2(offset_x, offset_y)
      if body.userData and isinstance(body.userData, monkey.Monkey):
        # Use the specialized apply impulse which can knock the monkey
        # out of control
        body.userData.apply_impulse(impulse, offset)
      else:
        body.ApplyImpulse(impulse, offset)



