# vim:set ts=2 sw=2 et:
from renderable import *

class GameObject(Renderable):
  body = None

  def __init__(self): super(GameObject, self).__init__()

  def on_contact_add(self, contact):
    return

  def on_contact_remove(self, contact):
    return

