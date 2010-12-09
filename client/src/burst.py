# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from Box2D import *

import effect

from objectid import *

import gamesprites

class Burst(effect.Effect):

  def __init__(self):
    """
    Effect that renders but has no influence on the world
    Time to live in seconds
    """
    super(Burst, self).__init__(100)

  def to_network(self, msg):
    msg.append(burst_id)
    super(Burst, self).to_network(msg)

  def from_network(self, msg):
    id = msg.pop()
    super(Burst, self).from_network(msg)

  def render(self):
    gamesprites.GameSprites.render_at_center('burst', self.at, (2, 2.5), 0)

