# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import renderable
import pygame
import pymunk
from pymunk.vec2d import *

class Monkey(renderable.Renderable):

  mass       = 50.0
  elasticity = 0.8
  friction   = 1

  def __init__(self):
    renderable.Renderable.__init__(self)

    self.t = 0

  # Body
    #points = [(-0.05,0.05), (0.05,0.05), (0.05,-0.05), (-0.05,-0.05)
    points = [( 0.0923, 0.0382),( 0.0382, 0.0923),(-0.0382, 0.0923),(-0.0923, 0.0382), \
              (-0.0923,-0.0382),(-0.0382,-0.0923),( 0.0382,-0.0923),( 0.0923,-0.0382)]
    moment = pymunk.moment_for_poly(self.mass, points, (0,0))

    #moment = pymunk.moment_for_circle(self.mass, 0, 0.05, (0,0))
    body = pymunk.Body(self.mass, moment)

    self.body = pymunk.Poly(body, points)
    #self.body = pymunk.Circle(body, 0.05, (0,0))
    self.body.friction    = self.friction
    self.body.elasticity  = self.elasticity
    self.body.collision_type = 2

    self.state = 'grounded'

  def add_to_space(self, space, at):
    self.body.body.position = at
    space.add(self.body.body, self.body)

  def render(self):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(1, 0, 0)

    glBegin(GL_POLYGON)
    for (xx,yy) in self.body.get_points():
    #for (x,y) in [(-0.05,0.05), (0.05,0.05), (0.05,-0.05), (-0.05,-0.05)]:
      #xx = self.body.body.position.x + x * math.cos(self.body.body.angle) - \
                                       #y * math.sin(self.body.body.angle)
      #yy = self.body.body.position.y + x * math.sin(self.body.body.angle) + \
                                       #y * math.cos(self.body.body.angle)
      glVertex3f(xx, yy, 0)
    glEnd()

    glBegin(GL_LINES)
    #for (x,y) in self.body.get_points():
    for (x,y) in [(0.0,0.0), (0.00,0.05)]:
      xx = self.body.body.position.x + x * math.cos(self.body.body.angle) - \
                                       y * math.sin(self.body.body.angle)
      yy = self.body.body.position.y + x * math.sin(self.body.body.angle) + \
                                       y * math.cos(self.body.body.angle)
      glVertex3f(xx, yy, 0)
    glEnd()

    #glBegin(GL_POLYGON)
    #for (x,y) in [(-0.1, -0.1), (-0.1, 0.1), (0.1, 0.1), (0.1, -0.1)]:
      #x,y = 

    #glEnd()

