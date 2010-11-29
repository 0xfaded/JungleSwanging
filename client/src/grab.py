# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *
from objectid import *

class Grab(GameObject):

  def __init__(self, radius):
    super(Grab, self).__init__()

    self.circleDef = b2CircleDef()
    self.circleDef.isSensor = True
    self.circleDef.radius = radius

    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self

  def add_to_world(self, at):
    self.bodyDef.position = at

    self.body = self.world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.circleDef)

  def to_network(self, msg):
    msg.append(grab_id)

  def from_network(self, msg):
    id = msg.pop()

  def render(self):
    """
    Platforms are all rendered in the background image
    The highlighting is done here
    """
    pass

