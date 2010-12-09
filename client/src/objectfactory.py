# vim:set ts=2 sw=2 et:

from objectid import *

import grab
import powerup
import world
import monkey
import platform

import beachballofdeath
import abomb

import powerup

import gameobject

class ObjectFactory(object):
  def __init__(self): super(ObjectFactory, self).__init__()

  def from_id(self, obj_id):
    # None item
    if obj_id == null_id:
      return None

    # Core Objects
    elif obj_id == monkey_id:
      ret = object.__new__(monkey.Monkey)
    elif obj_id == platform_id:
      ret = object.__new__(platform.Platform)
    elif obj_id == grab_id:
      ret = object.__new__(grab.Grab)
    elif obj_id == world_id:
      ret = object.__new__(world.World)

    # Projectiles
    elif obj_id == beachball_id:
      ret = object.__new__(beachballofdeath.BeachBallOfDeath)

    # Effects
    elif obj_id == abomb_id:
      ret = object.__new__(abomb.ABomb)

    # PowerUps
    elif obj_id == powerup_id:
      ret = object.__new__(powerup.PowerUp)

    else:
      raise Exception('Undefiened objectid {0}'.format(obj_id))

    gameobject.GameObject.__init__(ret)

    return ret

  def to_id(self, obj):
    # None item
    if obj == None:
      ret = null_id

    # Core Objects
    elif isinstance(obj, monkey.Monkey):
      ret = monkey_id
    elif isinstance(obj, platform.Platform):
      ret = platform_id
    elif isinstance(obj, grab.Grab):
      ret = grab_id
    elif isinstance(obj, world.World):
      ret = world_id

    # Projectiles
    elif isinstance(obj, beachballofdeath.BeachBallOfDeath):
      ret = beachball_id

    # Effects
    elif isinstance(obj, abomb.ABomb):
      ret = abomb_id

    # PowerUps
    elif isinstance(obj, powerup.PowerUp):
      ret = powerup_id

    else:
      raise Exception('Undefiened object type {0}'.format(obj))

    return ret

# Singleton
ObjectFactory = ObjectFactory()

