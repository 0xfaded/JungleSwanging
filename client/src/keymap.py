# vim:set sw=2 ts=2 sts=2 et:

import pygame
from pygame.locals import *

class KeyMap(object):
  def __init__(self):
    super(KeyMap, self).__init__()
    self.active = {}
    self.events = []


  def __getitem__(self, key):
    return self.active[key]

  def read_keys(self, keys):
    last_active = self.active
    self.active = {}

    for k in xrange(len(keys)):
      if keys[k]:
        self.active[k] = True

    self._gen_events(last_active, self.active)

  def to_network(self, msg):
    msg.append(len(self.active))
    for k in self.active:
      msg.append(k)

  def from_network(self, msg):
    last_active = self.active
    self.active = {}

    n = int(msg.pop())
    for i in xrange(n):
      k = int(msg.pop())
      self.active[k] = True

    self._gen_events(last_active, self.active)

  def _gen_events(self, last_active, active):
    self.events = []

    for k in last_active:
      if not active.has_key(k):
        e = pygame.event.Event(pygame.KEYUP, {'unicode':unichr(k), 'key':k})
        self.events.append(e)

    for k in active:
      if not last_active.has_key(k):
        e = pygame.event.Event(pygame.KEYDOWN, {'unicode':unichr(k), 'key':k})
        self.events.append(e)

