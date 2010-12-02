# vim:set sw=2 ts=2 sts=2 et:
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory

import sys
import time

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

# Initialise Display and GL
SCREEN_SIZE = (800, 600)

pygame.init()
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

# Import monkey stuff after initializing opengl
import objectfactory
import objectid
# End monkey imports

monkey     = objectfactory.ObjectFactory.from_id(objectid.monkey_id)
monkey.from_network(['0', '0', '0', '0'])

game_world = None
active = True

class ClientProtocol(Protocol):
  def __init__(self):
    self.last_message = ''

  def dataReceived(self, data):
    global game_world

    msgs = self.last_message + data
    msgs = msgs.split('\n')

    self.last_msg = msgs[-1]

    latest_msg = msgs[-2].split(',')
    latest_msg.reverse()

    game_world = objectfactory.ObjectFactory.from_id(objectid.world_id)
    game_world.tree_from_network(latest_msg)

class ClientProtocolFactory(ClientFactory):
  def startedConnecting(self, connector):
    print 'Started to connect.'

  def buildProtocol(self, addr):
    print 'Connected.'
    return ClientProtocol()

  def clientConnectionLost(self, connector, reason):
    global active
    print 'Lost connection.  Reason:', reason
    active = False

  def clientConnectionFailed(self, connector, reason):
    print 'Connection failed. Reason:', reason

client = ClientProtocolFactory()
reactor.connectTCP('localhost', 8007, client)
reactor.fireSystemEvent('startup')

fps = 30
clock = pygame.time.Clock()

try:
  while active:
    delta_t = clock.tick(fps)
    reactor.iterate(0)

    if game_world == None:
      continue

    events = []
    for event in pygame.event.get():
      events.append(event)
  
      if event.type == pygame.QUIT:
        active = False
      elif event.type == pygame.KEYDOWN:
        if event.unicode == 'q':
          active = False

    #keys = pygame.key.get_pressed()

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    zoom = 0.1
    glScale(zoom, zoom, 1)

    game_world.tree_render()

    pygame.display.flip()

except:
  pass

reactor.fireSystemEvent('shutdown')
pygame.quit()


