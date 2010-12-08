# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from Box2D import *

import effect
import gamesprites

from objectid import *

class ABomb(effect.Effect):

  def __init__(self):
    """
    Effect that renders but has no influence on the world
    Time to live in seconds
    """
    super(ABomb, self).__init__(750)

  def to_network(self, msg):
    msg.append(abomb_id)
    super(ABomb, self).to_network(msg)

  def from_network(self, msg):
    id = msg.pop()
    super(ABomb, self).from_network(msg)

  def render(self):
    gamesprites.GameSprites.render_at_center('abomb', self.at, (2, 2.5), 0)

