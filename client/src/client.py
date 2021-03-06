# vim:set sw=2 ts=2 sts=2 et:
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import sys
import time

import soundids
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

# Initialise Display and GL
SCREEN_SIZE = (1200, 800)

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
import monkey

import keymap

# End monkey imports

game_world = objectfactory.ObjectFactory.from_id(objectid.world_id)
our_monkey = None

active = True

host = 'localhost'
host_port = 8007
client_port = 9999

cancel_sound = pygame.mixer.Sound('cancel.wav')
game_music = pygame.mixer.Sound('spin.ogg')

if len(sys.argv) >= 2:
  host = sys.argv[1]
if len(sys.argv) >= 3:
  host_port = int(sys.argv[2])
if len(sys.argv) >= 4:
  client_port = int(sys.argv[3])

class ClientProtocol(DatagramProtocol):

  def datagramReceived(self, data, address):
    global game_world
    global our_monkey

    msg = data.strip().split(',')
    msg.reverse()

    client_id = int(msg.pop())

    game_world.children = []
    game_world.tree_from_network(msg)

    monkeys = game_world.children_of_type(monkey.Monkey)
    for m in monkeys:
      if m.player_id == client_id:
        our_monkey = m
        break

client = ClientProtocol()

reactor.listenUDP(client_port, client)
reactor.fireSystemEvent('startup')

fps = 30
clock = pygame.time.Clock()

sequence_number = 0

keys = keymap.KeyMap()

#try:

game_music.play(-1)

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

  if our_monkey == None:
    continue

  events = []
  for event in pygame.event.get():
    events.append(event)

    if event.type == pygame.QUIT:
      active = False
    elif event.type == pygame.KEYDOWN:
      if event.unicode == 'q':
        pygame.mixer.stop()
        cancel_sound.play()
        active = False

  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

  zoom = 0.1
  glScale(zoom, zoom, 1)

  # center camera on monkey
  mx, my = our_monkey.body.position
  glTranslate(-mx, -my, 0)

  game_world.tree_render()

  pygame.display.flip()

#except Exception as e:
  #print e

reactor.fireSystemEvent('shutdown')
pygame.quit()


