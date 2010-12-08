# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

import gameobject
import random

from objectid import *

class Projectile(gameobject.GameObject):
  def __init__(self, radius, mass, friction=1, restitution=0.3):
    super(Projectile, self).__init__();
    self.mass   = float(mass)
    self.radius = radius

    self.circleDef = b2CircleDef()
    self.circleDef.radius = radius
    self.circleDef.density = mass / (radius * radius * math.pi)

    self.circleDef.friction = friction
    self.circleDef.restitution = restitution

    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self

  def set_init_velocity(self, parabola):
    self.init_v = parabola.d(0)

  def max_velocity_from_max_impulse(self, max_impulse):
    return self.mass / max_impulse

  def add_to_world(self, at):
    self.bodyDef.position = at
    self.body = self.world.CreateBody(self.bodyDef)

    # Dont collide with throwing monkey
    self.circleDef.filter.groupIndex = -self.parent.player_id

    self.body.CreateShape(self.circleDef)
    self.body.SetMassFromShapes()

    self.body.linearVelocity = self.init_v
    self.body.angularVelocity = random.random() * math.pi / 3

    self.parent_contact = True
    self.parent_watch_id = self.add_callback(self.watch_parent, 'Live',
                                             self.body, self.parent.body)

  def watch_parent(self, contact):
    self.parent_contact = True

  def update(self, delta_t):
    # Do we still collide with the monkey? If not, allow the projectile
    # to collide with its parent again
    if not self.parent_contact and self.parent_watch_id:
      for shape in self.body.GetShapeList():
        shape.filter.groupIndex = 0

      self.remove_callback(self.parent_watch_id)
      self.parent_watch_id = None

    self.parent_contact = False

  def to_network(self, msg):
    msg.append(self.body.position.x)
    msg.append(self.body.position.y)
    msg.append(self.body.angle)

  def from_network(self, msg):
    x     = float(msg.pop())
    y     = float(msg.pop())
    angle = float(msg.pop())

    self.body = b2BodyDef()
    self.body.position = (x,y)
    self.body.angle = angle

