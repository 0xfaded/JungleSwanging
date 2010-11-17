# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *
from monkey import *

class PowerUp(GameObject):

  def __init__(self, parent, radius):
    super(PowerUp, self).__init__(parent)

    self.circleDef = b2CircleDef()
    self.circleDef.radius = radius
    self.circleDef.density = 1
    self.circleDef.friction = 1
    self.circleDef.restitution = 0.3

    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self
    self.bodyDef.fixedRotation = True

  def add_to_world(self, world, contact_listener, at):
    self.bodyDef.position = at

    self.body = world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.circleDef)

    self.body.SetMassFromShapes()

    self.callback_id = \
        contact_listener.add_callback(self.foo, 'Add', self.body, Monkey)


    self.destroyMe = False

  def update(self, world, contact_listener):
    if self.destroyMe:

      contact_listener.remove_callback(self.callback_id, 'Add')
      world.DestroyBody(self.body)

  def foo(self, contact):
    print contact

    contact.shape2.GetBody().userData.max_ground_velocity = 10

    contact.shape1.GetBody().userData.destroyMe = True
