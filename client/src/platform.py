# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from Box2D import *

import gameobject

from objectid import *

class Platform(gameobject.GameObject):

  points = []
#  shape
#  friction
#  bodyDef

  def __init__(self, points):
    super(Platform, self).__init__()

    self.shape = b2EdgeChainDef()
    self.shape.setVertices(points)
    self.shape.isALoop = True
    self.shape.friction = 0.3
    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self



  def add_to_world(self, at):
    self.bodyDef.position = at
    self.body = self.world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.shape)

  def to_network(self, msg):
    msg.append(platform_id)

  def from_network(self, msg):
    id    = msg.pop()

  def render(self):
    """
    Platforms are all rendered in the background image
    """
    pass

