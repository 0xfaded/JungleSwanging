# vim:set ts=2 sw=2 et:
from renderable import *

class GameObject(Renderable):
  body = None
  parent = None
  x_init = 0
  y_init = 0

  def __init__(self, parent):
    super(GameObject, self).__init__()
    self.parent = parent

  def set_start(self, coords):
    self.x_init, self.y_init = coords

  def get_start(self):
    return (self.x_init,self.y_init)

  def add_to_world(self, world, contact_listener, at):
    return

  def remove_to_world(self, world, contact_listener):
    return

  def update(self, world, contact_listener):
    return
