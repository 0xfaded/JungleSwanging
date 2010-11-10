# vim:set sw=2 ts=2 sts=2 et:
import sys
import time

import pygame
from pygame.locals import *

from Box2D import *

from OpenGL.GL import *
from OpenGL.GLU import *

# Monkeys Imports
from monkey import * 
from jungle import *
from grab import *

from contactlistener import *

# Temporary debugging stuff
import gldebugdraw
from settings import Settings

# Initialise Display and GL
SCREEN_SIZE = (800, 600)

screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE|OPENGL|DOUBLEBUF)

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

# Set up Box2d World

# Bounding Box for the world
worldAABB = b2AABB()
worldAABB.lowerBound = (-100, -100)
worldAABB.upperBound = ( 100,  100)

# Define the gravity vector.
gravity = b2Vec2(0, -10)
 
# Do we want to let bodies sleep?
doSleep = True
 
# Construct a world object, which will hold and simulate the rigid bodies.
world = b2World(worldAABB, gravity, doSleep)

# Simple graphics for now

debugdraw = gldebugdraw.glDebugDraw()
# Set the flags based on what the settings show (uses a bitwise or mask)
flags = 0
if Settings.drawShapes:     flags |= b2DebugDraw.e_shapeBit
if Settings.drawJoints:     flags |= b2DebugDraw.e_jointBit
if Settings.drawControllers:flags |= b2DebugDraw.e_controllerBit
if Settings.drawCoreShapes: flags |= b2DebugDraw.e_coreShapeBit
if Settings.drawAABBs:      flags |= b2DebugDraw.e_aabbBit
if Settings.drawOBBs:       flags |= b2DebugDraw.e_obbBit
if Settings.drawPairs:      flags |= b2DebugDraw.e_pairBit
if Settings.drawCOMs:       flags |= b2DebugDraw.e_centerOfMassBit
debugdraw.SetFlags(flags)

world.SetDebugDraw(debugdraw)

# Set the contact listener
contact_listener = ContactListener()
world.SetContactListener(contact_listener)

clock = pygame.time.Clock()

monkey  = Monkey()
jungle  = Jungle((20,10))

grab1   = Grab(3)
grab2   = Grab(3)
grab3   = Grab(3)


jungle.add_to_world(world, (0,0))
monkey.add_to_world(world, (0,3))

grab1.add_to_world(world, (-10,1))
grab2.add_to_world(world, (5,-1))

def crop_angle(angle):
  """Take an arbitary angle, and return that angle between pi and -pi"""
  return ((abs(angle) + math.pi) % (2 * math.pi)) - math.pi

fps = 30
while 1:
  deltat = clock.tick(fps)

  events = []
  for event in pygame.event.get():
    events.append(event)

    if event.type == pygame.QUIT:
      sys.exit(0)
    elif event.type == pygame.KEYDOWN:
      if event.unicode == 'q':
        sys.exit(0)
      
  keys = pygame.key.get_pressed()

  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

  zoom = 0.1
  glScale(zoom, zoom, 1)

  # center camera on monkey
  #mx, my = monkey.body.body.position
  #glTranslate(-mx, -my, 0)

  debugdraw.init_draw()

  world.Step(1.0/fps, 10, 8)

  # Read contact information, and then clear the buffers. Contacts can be
  # Produced by world updates through functions like SetFixedRotation.
  # Therefore we clear the contacts immediatly after reading.
  monkey.read_contacts(contact_listener)
  contact_listener.clear_buffer()

  monkey.control(keys, events)

  debugdraw.draw()

  dir(world)


  #monkey.render()
  #jungle.render()

  pygame.display.flip()

