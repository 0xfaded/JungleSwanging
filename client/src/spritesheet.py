# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from OpenGL.GLU import *

import cairo
import rsvg

import pygame
from pygame.locals import *

import sys
import math

from Box2D import *

class SpriteSheet(object):
  def __init__(self, size):
    super(SpriteSheet, self).__init__()
    self.size = size
    self.coords = {}

    self.surface = self.make_surface(size)
    self.texture_id = None

  #def __del__(self):
    #if self.texture_id != None:
      #glDeleteTextures(self.texture_id)

    #super(SpriteSheet, self).__del__()

  def __getitem__(self, key):
    return self.coords[key]

  def render_at_center(self, name, center, size, rot):
    """Render sprite at given center with rotation"""
    center = tuple(center)
    size   = tuple(size)

    size = (size[0] / 2.0, size[1] / 2.0)
    points = [(-size[0],  size[1]),
              (-size[0], -size[1]),
              ( size[0], -size[1]),
              ( size[0],  size[1])]

    rot = b2Mat22(rot)
    points = map(lambda x: b2Mul(rot,x) + center, points)
    
    self.render_points(name, points)

  def render_at(self, name, at, size):
    at   = tuple(at)
    size = tuple(size)

    """Render at given offset"""
    points = [(at[0]          , at[1] + size[1]),
              (at[0]          , at[1]          ),
              (at[0] + size[0], at[1]          ),
              (at[0] + size[0], at[1] + size[1])]

    self.render_points(name, points)

  def render_points(self, name, points):
    """Render sprite at given points"""
    points = map(lambda x: tuple(x), points)

    tex_coords = self[name]

    points = zip(points, tex_coords)

    glColor3f(1,1,1)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_TEXTURE_2D)

    self.bind()

    glBegin(GL_POLYGON)

    for ((px,py), (tx, ty)) in points:
      glTexCoord2f(tx, ty)
      glVertex3f(px, py, 0)
    glEnd()

  def add_sprite(self, name, path, at, size = None):
    size = self.load_svg_at(path, at, size)

    tex_coords = [(at[0]          , at[1]          ),
                  (at[0]          , at[1] + size[1]),
                  (at[0] + size[0], at[1] + size[1]),
                  (at[0] + size[0], at[1]          )]

    w,h = self.size
    tex_coords = map(lambda (x,y): (float(x)/w, float(y)/h), tex_coords)

    self.coords[name] = tex_coords

    return size

  def make_surface(self, (width, height)):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    
    cr.save()

    # Clear everything
    cr.set_source_rgba(0, 0, 0, 0)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.paint()

    cr.restore()

    return surface

  def load_svg_at(self, path, at, size = None):

    svg = rsvg.Handle(path)

    cr = cairo.Context(self.surface)
    cr.translate(*at)

    if size != None:
      xscale = float(size[0]) / svg.props.width
      yscale = float(size[1]) / svg.props.height
      cr.scale(xscale, yscale)

    else:
      size = (svg.props.width, svg.props.height)

    svg.render_cairo(cr)

    return size

  def set_texture(self):
    self.texture_id = glGenTextures(1)

    width = self.surface.get_width()
    height = self.surface.get_height()
 
    data = str(self.surface.get_data())

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, self.texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA,
        GL_UNSIGNED_BYTE, data)

  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.texture_id)

