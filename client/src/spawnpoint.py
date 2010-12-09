# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

import gameobject
import monkey

import beachballofdeath
import gamesprites

from objectid import *

class SpawnPoint(gameobject.GameObject):

  # Ignore a slight margin around the tent to ignore
  # ground
  margin = b2Vec2(0.1, 0.1)

  def __init__(self, size):
    super(SpawnPoint, self).__init__()
    self.size = size

  def is_clear(self):
    bounds = b2AABB()
    bounds.lowerBound = self.at + self.margin
    bounds.upperBound = self.at - self.margin + self.size

    (n, shapes) = self.world.Query(bounds, 1)

    return n == 0

  def get_center(self):
    return self.at + 0.5 * self.size

  def add_to_world(self, at):
    self.at = at

  def to_network(self, msg):
    msg.append(spawnpoint_id)
    msg.append(self.at.x)
    msg.append(self.at.y)
    msg.append(self.size.x)
    msg.append(self.size.y)

  def from_network(self, msg):
    id    = msg.pop()

    x     = float(msg.pop())
    y     = float(msg.pop())

    self.at = b2Vec2(x, y)

    w     = float(msg.pop())
    h     = float(msg.pop())

    self.size = b2Vec2(w, h)

  def render(self):
    center = self.get_center()
    gamesprites.GameSprites.render_at_center('tent', center, self.size, 0)

