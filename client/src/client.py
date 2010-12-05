# vim:set sw=2 ts=2 sts=2 et:
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

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

import keymap

# End monkey imports

monkey     = objectfactory.ObjectFactory.from_id(objectid.monkey_id)
monkey.from_network(['0', '0', '0', '0'])

game_world = objectfactory.ObjectFactory.from_id(objectid.world_id)
active = True

host = 'localhost'
host_port = 8007
client_port = 9999

if len(sys.argv) >= 2:
  host = sys.argv[1]
if len(sys.argv) >= 3:
  host_port = int(sys.argv[2])
if len(sys.argv) >= 4:
  client_port = int(sys.argv[3])

class ClientProtocol(DatagramProtocol):

  def datagramReceived(self, data, address):
    global game_world

    msg = data.strip().split(',')
    msg.reverse()

    game_world.children = []
    game_world.tree_from_network(msg)

client = ClientProtocol()

reactor.listenUDP(client_port, client)
reactor.fireSystemEvent('startup')

fps = 30
clock = pygame.time.Clock()

sequence_number = 0

keys = keymap.KeyMap()

try:
  while active:
    delta_t = clock.tick(fps)

    msg = [sequence_number]
    sequence_number += 1

    keys.read_keys(pygame.key.get_pressed())
    keys.to_network(msg)

    msg = map(str, msg)
    msg = ','.join(msg)

    client.transport.write(msg, (host, host_port))

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

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    zoom = 0.1
    glScale(zoom, zoom, 1)

    game_world.tree_render()

    pygame.display.flip()

except Exception as e:
  print e

reactor.fireSystemEvent('shutdown')
pygame.quit()


