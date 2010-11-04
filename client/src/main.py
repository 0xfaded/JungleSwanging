# vim:set sw=2 ts=2 sts=2 et:
import sys

import pygame
from pygame.locals import *

import pymunk
from pymunk import Vec2d

from OpenGL.GL import *
from OpenGL.GLU import *

# Monkeys Imports
from monkey import * 
from jungle import *

SCREEN_SIZE = (800, 600)

pygame.init()
pymunk.init_pymunk()

screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE|OPENGL|DOUBLEBUF)

space = pymunk.Space()
space.gravity = Vec2d(0.0, -500.0)

glViewport(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])

# GL's COORDINATE SYSTEM FOR RENDERING:
# (camera view):
#
# ^ +z      positive z is away from us (zero at top of screen)
# |
# o--> +x   x increases left to right
# |         
# v +y      positive y is down
# 
# (side view):
# o_  <--- camera
#  \
#    o--> +z
#    |
#    v +y

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
ratio = float(SCREEN_SIZE[0])/SCREEN_SIZE[1]
glOrtho(-ratio, ratio, -1, 1, 1000, -1000)

glMatrixMode(GL_MODELVIEW)

glEnable(GL_TEXTURE_2D)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL) # hmm

# discard any fragments with alpha <= 0
glEnable(GL_ALPHA_TEST)
glAlphaFunc(GL_GREATER, 0)

# set background and alpha blending
glClearColor(0,0,0,0)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

clock = pygame.time.Clock()

monkey  = Monkey()
jungle  = Jungle((2,1))

monkey.add_to_space(space, (0,0.3))
jungle.add_to_space(space, (0,0))

def crop_angle(angle):
  """Take an arbitary angle, and return that angle between pi and -pi"""
  return ((abs(angle) + math.pi) % (2 * math.pi)) - math.pi

def special_update(body, gravity, damping, dt):
  gravity = Vec2d(0, -500)
  keys = pygame.key.get_pressed()
  if keys[K_LEFT]:
    gravity += Vec2d(-1000, 0)
  elif keys[K_RIGHT]:
    gravity += Vec2d( 1000, 0)

  #body.angle = 0
  #body.angular_velocity = 0
  pymunk.Body.update_velocity(body, gravity, damping, dt)

def normal_update(body, gravity, damping, dt):
  gravity = Vec2d(0, -500)
  pymunk.Body.update_velocity(body, gravity, damping, dt)

def foo1(space, arbitor):
  if abs(crop_angle(monkey.body.body.angle)) < 0.5:
    monkey.body.body.velocity_func = special_update
  monkey.body.body.velocity_func = special_update
  return True

def foo2(space, arbitor):
  monkey.body.body.velocity_func = normal_update
  monkey.body.body.velocity_func = special_update
  return True

space.add_collision_handler(1, 2, foo1, None, None, foo2)

while 1:
  deltat = clock.tick(30)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit(0)
    elif event.type == pygame.KEYDOWN:
      if event.unicode == 'q':
        sys.exit(0)
      if event.key == K_UP:
        monkey.body.body.apply_impulse((0, 600))

  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

  # center camera on monkey
  mx, my = monkey.body.body.position
  glTranslate(-mx, -my, 0)

  space.step(0.001)

  monkey.render()
  jungle.render()

  pygame.display.flip()

