# vim:set ts=2 sw=2 et:
from renderable import *

class GameObject(Renderable):
  body = None

  def __init__(self): super(GameObject, self).__init__()

  def add_to_world(self, world, contact_listener, at):
    return

  def update(self, world, contact_listener):
    return
