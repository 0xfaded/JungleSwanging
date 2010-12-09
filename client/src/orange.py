# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

from objectid import *

import projectile
import gamesprites
import monkey

class Orange(projectile.Projectile):

  radius = 0.4
  sprite_name = 'orange'

  def __init__(self):
    super(Orange, self).__init__(self.radius, 3, self.sprite_name, 1, 0.1);
    self.timeToRemove = 10000

  def add_to_world(self, at):
    super(Orange, self).add_to_world(at)

    # Use a custom comparison function that ignores sensors
    # All projectiles will probably want to do this
    cmp = lambda x: not x.isSensor

  def max_velocity_from_max_impulse(self, max_impulse):
    return 5 * max_impulse / self.mass

  def update(self, delta_t):
    super(Orange, self).update(delta_t)

    self.timeToRemove -= delta_t

    if self.timeToRemove < 0:
      self.kill_me()

  def to_network(self, msg):
    msg.append(orange_id)
    super(Orange, self).to_network(msg)

  def from_network(self, msg):
    id    = msg.pop()
    super(Orange, self).from_network(msg)

