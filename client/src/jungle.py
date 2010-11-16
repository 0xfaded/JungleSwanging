# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *

import renderable
import pygame

from Box2D import *


class Jungle(renderable.Renderable):

  floor_friction = 0.8
  floor_elasticity = 0.5

  wall_friction = 0.3
  wall_elasticity = 0.6

  def __init__(self, size):
    renderable.Renderable.__init__(self)

    self.size = b2Vec2(size)
    w, h = self.size

    self.floor_points = [(w/2,-h/2),(-w/2,-h/2)]

    self.floorShapeDef = b2EdgeChainDef()
    self.floorShapeDef.setVertices(self.floor_points)
    self.floorShapeDef.isALoop = False

    self.floor = None

    
  def add_to_world(self, world, at):
    bodyDef = b2BodyDef()
    bodyDef.position = at
    bodyDef.userData = 'abc'

    self.floor = world.CreateBody(bodyDef)
    self.floor.CreateShape(self.floorShapeDef)

  def render(self):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(0, 1, 0)

    # Calculate rendering coords
    rot = b2Mat22(self.floor.angle)
    off = self.floor.position

    points = map(lambda x: b2Mul(rot,x) + off, self.floor_points)

    glBegin(GL_LINES)
    for (x, y) in points:

      glVertex3f(x, y, 0)

    glEnd()

    rot = b2Mat22(self.test.angle)
    off = self.test.position

    points = map(lambda x: b2Mul(rot,x) + off, self.test_points)

    glBegin(GL_POLYGON)
    for (x, y) in points:

      glVertex3f(x, y, 0)

    glEnd()

