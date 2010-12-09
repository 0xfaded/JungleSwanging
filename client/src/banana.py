# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

import gameobject
import monkey

import gamesprites

from objectid import *

class Banana(gameobject.GameObject):

  def __init__(self, radius):
    super(Banana, self).__init__()

    self.circleDef = b2CircleDef()
    self.circleDef.radius = radius
    self.circleDef.isSensor = True

    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self
    self.bodyDef.fixedRotation = True

    self.radius = radius

    self.winner = None

  def get_winner(self):
    return self.winner

  def add_to_world(self, at):
    self.bodyDef.position = at

    self.body = self.world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.circleDef)

    self.add_callback(self.on_touch, 'Live', self.body, monkey.Monkey)

  def to_network(self, msg):
    msg.append(banana_id)
    msg.append(self.body.position.x)
    msg.append(self.body.position.y)
    msg.append(self.radius)

  def from_network(self, msg):
    id    = msg.pop()

    x     = float(msg.pop())
    y     = float(msg.pop())

    self.body = b2BodyDef()
    self.body.position = b2Vec2(x, y)

    self.radius = float(msg.pop())

  def on_touch(self, contact):
    if not self.winner:
      self.winner = contact.shape2.GetBody().userData

  def render(self):
    off = self.body.position
    
    w = self.radius * 2
    h = self.radius * 2
    gamesprites.GameSprites.render_at_center('banana',off, (w,h), 0)

