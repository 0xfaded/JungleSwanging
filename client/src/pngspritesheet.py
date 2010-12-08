# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *

import sys
import math

from Box2D import *

class PNGSpriteSheet(object):
  def __init__(self, name):
    super(PNGSpriteSheet, self).__init__()
    self.coords = {}

    (self.texture_id, self.size) = self.load_image(name)

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

    # discard any fragments with alpha <= 0
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0)

    # set background and alpha blending
    glClearColor(0,0,0,0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
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

  def load_svg_at(self, path, at, size = None):
    return size

  def set_texture(self):
    pass

  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.texture_id)

  def load_image(self, image):
    textureSurface = pygame.image.load(image)
    textureSurface = pygame.transform.flip(textureSurface, False, True)
 
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
 
    width = textureSurface.get_width()
    height = textureSurface.get_height()
 
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, textureData)
 
    return texture, (width, height)

