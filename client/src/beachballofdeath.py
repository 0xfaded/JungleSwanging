# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

from objectid import *

import projectile
import gamesprites
import abomb
import explosion
import monkey

class BeachBallOfDeath(projectile.Projectile):
  max_bounces = 5

  def __init__(self):
    super(BeachBallOfDeath, self).__init__(0.5, 1, 'beachball', 0.1, 0.8);
    self.bounces = 0

  def add_to_world(self, at):
    super(BeachBallOfDeath, self).add_to_world(at)

    # Use a custom comparison function that ignores sensors
    # All projectiles will probably want to do this
    cmp = lambda x: not x.isSensor
    self.add_callback(self.on_hit, 'Add', self.body, cmp)

  def update(self, delta_t):
    super(BeachBallOfDeath, self).update(delta_t)

    if self.bounces > 3:
      effect_pos = self.body.position + b2Vec2(0,0.2)
      self.get_root().add_child(abomb.ABomb(), effect_pos)
      
      # Remove ball from simulation before explosion
      explode_at = self.body.position
      self.kill_me()

      expl = explosion.Explosion(self.world)
      expl.explode_at(explode_at, 10)


  def on_hit(self, contact):
    if isinstance(contact.shape2.GetBody().userData, monkey.Monkey):
      if self.bounces == 0:
        self.body.linearVelocity *= 3
      elif self.bounces == 1:
        self.body.linearVelocity *= 1.5

    self.bounces += 1

  def to_network(self, msg):
    msg.append(beachball_id)
    super(BeachBallOfDeath, self).to_network(msg)

  def from_network(self, msg):
    id    = msg.pop()
    super(BeachBallOfDeath, self).from_network(msg)

    self.radius = 0.5

