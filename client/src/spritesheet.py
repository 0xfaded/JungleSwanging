# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from OpenGL.GLU import *

import cairo
import rsvg

import pygame
from pygame.locals import *

import sys
import math

class SpriteSheet(object):
  def __init__(self, size):
    super(SpriteSheet, self).__init__()
    self.size = size
    self.coords = {}

    self.surface = self.make_surface(size)

  def __getitem__(self, key):
    return self.coords[key]

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

  def draw(self):
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glBindTexture(GL_TEXTURE_2D, self.texture_id)

    points = range(4)
    points = map(lambda x: (math.cos(x), math.sin(x)), points)

    tex_coords = [(0,0), (0, 1), (1, 1), (1, 0)]

    coords = zip(points, tex_coords)

    # GL_TRIANGLE
    # GL_QUAD
    # GL_POLYGON
    glBegin(GL_QUADS)

    for ((px, py), (tx, ty)) in coords:
      glTexCoord2f(tx, ty)
      glVertex3f(px, py, 0)

    glEnd()

    glDisable(GL_TEXTURE_2D)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(1, 1, 1)


    glBegin(GL_QUADS)
    for ((px, py), (tx, ty)) in coords:
      glVertex3f(px, py, 0)

    glEnd()

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

    print self.texture_id
 
  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.texture_id)

