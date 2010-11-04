# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *

import renderable
import pygame
import pymunk


class Jungle(renderable.Renderable):

  floor_friction = 0.8
  floor_elasticity = 0.5

  wall_friction = 0.3
  wall_elasticity = 0.6

  def __init__(self, size):
    renderable.Renderable.__init__(self)

    self.size = (float(size[0]), float(size[1]))
    w, h = self.size

    f_body = pymunk.Body(pymunk.inf, pymunk.inf)
    self.floor = pymunk.Segment(f_body, (-w/2, 0), (w/2, 0), 0.0)
    self.floor.friction   = self.floor_friction
    self.floor.elasticity = self.floor_elasticity
    self.floor.collision_type = 1

    lw_body = pymunk.Body(pymunk.inf, pymunk.inf)
    self.l_wall = pymunk.Segment(lw_body, (-w/2, h), (-w/2, 0), 0.0)
    self.l_wall.friction   = self.wall_friction
    self.l_wall.elasticity = self.wall_elasticity

    rw_body = pymunk.Body(pymunk.inf, pymunk.inf)
    self.r_wall = pymunk.Segment(rw_body, (w/2, h), (w/2, 0), 0.0)
    self.r_wall.friction   = self.wall_friction
    self.r_wall.elasticity = self.wall_elasticity

  def add_to_space(self, space, at):
    space.add_static(self.floor)
    space.add_static(self.l_wall)
    space.add_static(self.r_wall)

  def render(self):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(0, 1, 0)

    for shape in [self.r_wall, self.l_wall, self.floor]:

      body = shape.body
      pv1 = body.position + shape.a.cpvrotate(body.rotation_vector)
      pv2 = body.position + shape.b.cpvrotate(body.rotation_vector)

      glBegin(GL_LINES)

      glVertex3f(pv1.x, pv1.y, 0)
      glVertex3f(pv2.x, pv2.y, 0)

      glEnd()

