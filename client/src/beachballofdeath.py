# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

from Box2D import *

from objectid import *

import projectile
import gamesprites
import abomb

class BeachBallOfDeath(projectile.Projectile):
  max_bounces = 5

  def __init__(self):
    super(BeachBallOfDeath, self).__init__(0.5, 1, 0.1, 0.8);
    self.bounces = 0

  def add_to_world(self, at):
    super(BeachBallOfDeath, self).add_to_world(at)
    self.add_callback(self.on_hit, 'Add', self.body)

  def update(self, delta_t):
    super(BeachBallOfDeath, self).update(delta_t)

    if self.bounces > 3:
      self.get_root().add_child(abomb.ABomb(), self.body.position)
      self.kill_me()

  def on_hit(self, contact):
    if self.bounces == 0:
      self.body.linearVelocity *= 3
    elif self.bounces == 1:
      self.body.linearVelocity *= 1

    self.bounces += 1

  def to_network(self, msg):
    msg.append(100)
    super(BeachBallOfDeath, self).to_network(msg)

  def from_network(self, msg):
    id    = msg.pop()
    super(BeachBallOfDeath, self).to_from(msg)

  def render(self):
    rot = self.body.angle
    off = self.body.position
    w = self.radius * 2
    h = self.radius * 2
    gamesprites.GameSprites.render_at_center('beachball',off, (w,h), rot)
