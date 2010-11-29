# vim:set ts=2 sw=2 et:

from objectid import *

import grab
import powerup
import world
import monkey
import platform

class ObjectFactory(object):
  def __init__(self): super(ObjectFactory, self).__init__()

  def from_id(self, obj_id):
    if obj_id == monkey_id:
      return object.__new__(monkey.Monkey)
    elif obj_id == platform_id:
      return object.__new__(platform.Platform)
    elif obj_id == grab_id:
      return object.__new__(grab.Grab)
    elif obj_id == world_id:
      return object.__new__(map.Map)
    elif obj_id == powerup_id:
      return object.__new__(powerup.Powerup)
    elif obj_id == projectile_id:
      return object.__new__(powerup.Projectile)

# Singleton
ObjectFactory = ObjectFactory()

