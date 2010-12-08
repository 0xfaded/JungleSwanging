# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from Box2D import *

import gameobject

class Effect(gameobject.GameObject):

  def __init__(self, time_to_live):
    """
    Effect that renders but has no influence on the world
    Time to live in milliseconds
    """
    super(Effect, self).__init__()

    self.t = 0
    self.time_to_live = time_to_live


  def add_to_world(self, at):
    self.at = at

  def update(self, delta_t):
    self.t += delta_t
    if self.t > self.time_to_live:
      self.kill_me()

  def to_network(self, msg):
    msg.append(self.at.x)
    msg.append(self.at.y)
    msg.append(self.t)

  def from_network(self, msg):
    x = float(msg.pop())
    y = float(msg.pop())
    self.t = float(msg.pop())

    self.at = b2Vec2(x, y)

