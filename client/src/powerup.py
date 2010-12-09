# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

import gameobject
import monkey

import beachballofdeath
import gamesprites

from objectid import *

class PowerUp(gameobject.GameObject):

  def __init__(self, radius, cooldown, sprite_name, weapon):
    super(PowerUp, self).__init__()

    self.weapon = weapon

    self.circleDef = b2CircleDef()
    self.circleDef.radius = radius
    self.circleDef.isSensor = True

    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self
    self.bodyDef.fixedRotation = True

    self.cooldown = cooldown
    self.sprite_name = sprite_name
    self.radius = radius
    self.t = 0

  def add_to_world(self, at):
    self.bodyDef.position = at

    self.body = self.world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.circleDef)

    self.body.SetMassFromShapes()

    self.add_callback(self.on_touch, 'Live', self.body, monkey.Monkey)


    self.destroyMe = False

  def to_network(self, msg):
    msg.append(powerup_id)
    msg.append(self.body.position.x)
    msg.append(self.body.position.y)
    msg.append(self.radius)
    msg.append(self.t)
    msg.append(self.sprite_name)

  def from_network(self, msg):
    id    = msg.pop()

    x     = float(msg.pop())
    y     = float(msg.pop())

    self.body = b2BodyDef()
    self.body.position = b2Vec2(x, y)

    self.radius = float(msg.pop())
    self.t      = float(msg.pop())

    self.sprite_name = msg.pop()

    # Use a dummy body as we dont run a simulation on the client
    dummy = b2BodyDef()
    dummy.position = b2Vec2(x,y)

    # This is ugly, but for our purposes a BodyDef has
    # all the attributes required for rendering, and I'm in a rush
    self.body = dummy


  def update(self, delta_t):
    if self.t >= 0:
      self.t -= delta_t

  def on_touch(self, contact):
    if self.t <= 0:
      self.update_monkey(contact)
      self.t = self.cooldown

  def update_monkey(self, contact):
    monk = contact.shape2.GetBody().userData
    monk.set_weapon(self.weapon())

  def render(self):
    if self.t >= 0:
      return

    rot = self.body.angle
    off = self.body.position
    
    w = self.radius * 2
    h = self.radius * 2
    gamesprites.GameSprites.render_at_center(self.sprite_name,off, (w,h), rot)

