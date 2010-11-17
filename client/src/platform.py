# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math
import pygame
from pygame.locals import *
from Box2D import *
from gameobject import *


class Platform(GameObject):

  points = []
#  shape
#  friction
#  bodyDef

  def __init__(self, points):
    super(Platform, self).__init__(self)

    self.shape = b2EdgeChainDef()
    self.shape.setVertices(points)
    self.shape.isALoop = True
    self.shape.friction = 0.3
    self.bodyDef = b2BodyDef()
    self.bodyDef.userData = self



  def add_to_world(self, world, contact_listener, at):
    self.bodyDef.position = at
    self.body = world.CreateBody(self.bodyDef)
    self.body.CreateShape(self.shape)

