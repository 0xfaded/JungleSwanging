# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *

class Grab(GameObject):

  def __init__(self, parent, radius):
    super(Grab, self).__init__(parent)

    self.circleDef = b2CircleDef()
    self.circleDef.isSensor = True
    self.circleDef.radius = radius

    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self

  def add_to_world(self, at):
    self.bodyDef.position = at

    self.body = self.world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.circleDef)

