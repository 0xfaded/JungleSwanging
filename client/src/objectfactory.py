# vim:set ts=2 sw=2 et:

from objectid import *

import grab
import powerup
import world
import monkey
import platform

import abomb
import burst

import beachballofdeath
import orange
import pinapplegrenade

import spawnpoint

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
    elif obj_id == pinapple_id:
      ret = object.__new__(pinapplegrenade.PinappleGrenade)
    elif obj_id == orange_id:
      ret = object.__new__(orange.Orange)

    # Effects
    elif obj_id == abomb_id:
      ret = object.__new__(abomb.ABomb)
    elif obj_id == burst_id:
      ret = object.__new__(burst.Burst)

    # PowerUps
    elif obj_id == powerup_id:
      ret = object.__new__(powerup.PowerUp)

    # Permanant
    elif obj_id == spawnpoint_id:
      ret = object.__new__(spawnpoint.SpawnPoint)

    else:
      raise Exception('Undefiened objectid {0}'.format(obj_id))

    gameobject.GameObject.__init__(ret)

    return ret

  def get_constructor(self, obj_id):
    # None item
    if obj_id == null_id:
      return None

    # Core Objects
    elif obj_id == monkey_id:
      ret = monkey.Monkey
    elif obj_id == platform_id:
      ret = platform.Platform
    elif obj_id == grab_id:
      ret = grab.Grab
    elif obj_id == world_id:
      ret = world.World

    # Projectiles
    elif obj_id == beachball_id:
      ret = beachballofdeath.BeachBallOfDeath
    elif obj_id == pinapple_id:
      ret = pinapplegrenade.PinappleGrenade
    elif obj_id == orange_id:
      ret = orange.Orange

    # Effects
    elif obj_id == abomb_id:
      ret = abomb.ABomb
    elif obj_id == burst_id:
      ret = burst.Burst

    # PowerUps
    elif obj_id == powerup_id:
      ret = powerup.PowerUp

    # Permanant
    elif obj_id == spawnpoint_id:
      ret = spawnpoint.SpawnPoint

    else:
      raise Exception('Undefiened objectid {0}'.format(obj_id))

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
    elif isinstance(obj, pinapplegrenade.PinappleGrenade):
      ret = pinapple_id
    elif isinstance(obj, orange.Orange):
      ret = orange_id

    # Effects
    elif isinstance(obj, abomb.ABomb):
      ret = abomb_id
    elif isinstance(obj, burst.Burst):
      ret = burst_id

    # PowerUps
    elif isinstance(obj, powerup.PowerUp):
      ret = powerup_id

    # Permanant
    elif isinstance(obj, spawnpoint.SpawnPoint):
      return spawnpoint_id

    else:
      raise Exception('Undefiened object type {0}'.format(obj))

    return ret

# Singleton
ObjectFactory = ObjectFactory()

