# vim:set ts=2 sw=2 et:

from objectid import *

import grab
import powerup
import world
import monkey
import platform
import gameobject

class ObjectFactory(object):
  def __init__(self): super(ObjectFactory, self).__init__()

  def from_id(self, obj_id):
    if obj_id == monkey_id:
      ret = object.__new__(monkey.Monkey)
    elif obj_id == platform_id:
      ret = object.__new__(platform.Platform)
    elif obj_id == grab_id:
      ret = object.__new__(grab.Grab)
    elif obj_id == world_id:
      ret = object.__new__(world.World)
    elif obj_id == powerup_id:
      ret = object.__new__(powerup.PowerUp)
    elif obj_id == projectile_id:
      ret = object.__new__(powerup.Projectile)
    else:
      raise Exception('Undefiened objectid {0}'.format(obj_id))

    gameobject.GameObject.__init__(ret)

    return ret

# Singleton
ObjectFactory = ObjectFactory()

