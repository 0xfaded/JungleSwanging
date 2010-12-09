# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

from objectid import *

import projectile
import gamesprites
import burst
import smallexplosion
import monkey
import soundids

class PinappleGrenade(projectile.Projectile):

  radius = 0.2
  sprite_name = 'pinapple'
  def __init__(self):
    super(PinappleGrenade, self).__init__(self.radius, 0.8,
                                          self.sprite_name, 0.1, 0.8);
    self.bounces = 0
    self.timeToExplode = 5000

  def add_to_world(self, at):
    super(PinappleGrenade, self).add_to_world(at)

    # Use a custom comparison function that ignores sensors
    # All projectiles will probably want to do this
    cmp = lambda x: not x.isSensor
    self.add_callback(self.on_hit, 'Add', self.body, cmp)

  def update(self, delta_t):
    super(PinappleGrenade, self).update(delta_t)

    self.timeToExplode -= delta_t

    if self.timeToExplode < 0:
      self.bounces = 1

    if self.bounces > 0:
      self.get_root().sounds |= soundids.boom_id
      effect_pos = self.body.position + b2Vec2(0,0.2)
      self.get_root().add_child(burst.Burst(), effect_pos)

      # Remove ball from simulation before explosion
      explode_at = self.body.position
      self.kill_me()

      expl = smallexplosion.SmallExplosion(self.world)
      expl.explode_at(explode_at, 30)


  def on_hit(self, contact):
    if isinstance(contact.shape2.GetBody().userData, monkey.Monkey):
      self.bounces = 1
    else:
      self.get_root().sounds |= soundids.metal_id

  def to_network(self, msg):
    msg.append(pinapple_id)
    super(PinappleGrenade, self).to_network(msg)

  def from_network(self, msg):
    id    = msg.pop()
    super(PinappleGrenade, self).from_network(msg)

