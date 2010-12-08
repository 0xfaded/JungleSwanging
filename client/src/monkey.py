# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

import gameobject
import grab
import platform
import beachballofdeath

import gamesprites

import pathfinder


from objectid import *

import copy

# Global counter used as seed for player ids
_player_id = 1

class Monkey(gameobject.GameObject):

  shoulder_offset = (0.15, -0.2)

  class Stats(object):
    """
    These stats define how the monkey behaves in the simulation.
    At the beginning of each update, powerups will be mapped across
    the monkeys initial Stats, as defined in the below __init__(),
    and the resulting modified Stats will be used to determine the
    monkeys interaction with the simulation.
    """
    def __init__(self):
      # Box2D Properties
      self.restitution = 0.5
      self.friction    = 3
      self.density     = 1

      # Other Stats
      self.ground_force_x       = 30 # Ground acceleration along the x axis
      self.ground_force_y       =  0 # Ground acceleration along the y axis

      self.ground_impulse_x     =  0
      self.ground_impulse_y     = 10 # Best thought as jump

      self.air_force_x          =  0 # Air acceleration along the x axis
      self.air_force_y          =  0 # Air acceleration along the y axis

      self.air_impulse_x        =  0
      self.air_impulse_y        =  0 # Best thought as air boost

      self.hang_force_x         =  0 # Hanging acceleration along the x axis
      self.hang_force_y         =  0 # Hanging acceleration along the y axis

      self.hang_impulse_x       =  0
      self.hang_impulse_y       =  0 # Best thought as hang boost

      self.max_landing_speed    = 20
      self.max_knock_impulse    = 20

      # if velocity < max_velocity: apply force
      self.max_ground_velocity  =  10
      self.max_air_velocity     =  2

  def __init__(self, controller):
    global _player_id

    super(Monkey, self).__init__()

    self.t = 0
    self.controller = controller
    self.player_id = _player_id
    _player_id += 1

    # Note we do not need to set any properties of the monkey's shapes
    # as all properties in stats are applied to the entire monkey
    # on each iteration
    self.base_stats = Monkey.Stats()
    self.stats      = self.base_stats

    self.headDef = b2CircleDef()
    self.headDef.radius = 0.60
    self.headDef.filter.groupIndex = -self.player_id

    self.footDef = b2CircleDef()
    self.footDef.radius = 0.20
    self.footDef.filter.groupIndex = -self.player_id

    # Shoulder sensor is used for determining if a grab point is in range
    self.shoulderDef = b2CircleDef()
    self.shoulderDef.radius = 0
    self.shoulderDef.isSensor = True
    self.shoulderDef.filter.groupIndex = -self.player_id

    self.bodyDef = b2BodyDef()
    self.bodyDef.angle = 0.0
    self.bodyDef.allowSleep = False
    self.bodyDef.userData = self

    self.platform_contact = None
    self.grab_contact = None
    self.grab_joint = None

    # Targeting
    self.parabola = None

    # Body.GetFixedRotation() is buggy, so we need to store our own
    self.fixedRotation = True
    self.controlled = True

    self.direction = 1

    self.state = 'none'

  def add_to_world(self, at):
    self.bodyDef.position = at
    self.body = self.world.CreateBody(self.bodyDef)

    self.footDef.localPosition = (0, -0.6)

    self.foot_shape = self.body.CreateShape(self.footDef)
    self.foot_shape = self.foot_shape.asCircle()

    self.headDef.localPosition = (0, 0.2)

    self.head_shape = self.body.CreateShape(self.headDef)
    self.head_shape = self.head_shape.asCircle()

    self.shoulderDef.localPosition = (self.shoulder_offset)

    self.shoulder_shape = self.body.CreateShape(self.shoulderDef)
    self.shoulder_shape = self.shoulder_shape.asCircle()

    self._apply_stats(self.stats)

    self.body.SetMassFromShapes()

    self.body.SetFixedRotation(True)

    self._set_contact_callbacks()

  def to_network(self, msg):
    msg.append(monkey_id)
    msg.append(self.body.position.x)
    msg.append(self.body.position.y)
    msg.append(self.body.angle)

  def from_network(self, msg):
    id    = msg.pop()

    x     = float(msg.pop())
    y     = float(msg.pop())
    angle = float(msg.pop())

    # Use a dummy body as we dont run a simulation on the client
    dummy = b2BodyDef()
    dummy.position = b2Vec2(x,y)
    dummy.angle    = angle

    # This is ugly, but for our purposes a BodyDef has
    # all the attributes required for rendering, and I'm in a rush
    self.body = dummy


  def update(self, delta_t):
    keys, events = self.controller.active, self.controller.events

    # Update the monkey with the latest stats
    stats = self.stats
    #self._apply_stats(stats)

    # Find the most up to date target before trying to read input
    self._find_target()

    # Calculate the force vector to apply in the left or right direction
    force = b2Vec2(0, 0)
    impulse = b2Vec2(0, 0)

    force_basis   = b2Vec2(0,0)
    impulse_basis = b2Vec2(0,0)

    # Left Right movement
    if keys.has_key(K_LEFT):
      force_basis += b2Vec2(-1,  0)
    if keys.has_key(K_RIGHT):
      force_basis += b2Vec2( 1,  0)
    if keys.has_key(K_UP):
      force_basis += b2Vec2( 0,  1)
    if keys.has_key(K_DOWN):
      force_basis += b2Vec2( 0, -1)


    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == K_SPACE:
          self._attempt_grab()
        if event.key == K_LCTRL:
          self._attempt_fire()
        if event.key == K_LEFT:
          impulse_basis += b2Vec2(-1,  0)
        if event.key == K_RIGHT:
          impulse_basis += b2Vec2( 1,  0)
        if event.key == K_UP:
          impulse_basis += b2Vec2( 0,  1)
        if event.key == K_DOWN:
          impulse_basis += b2Vec2( 0, -1)

    # Prevent ourselves from getting stuck with our feet not touching a platform
    if self.body.linearVelocity.Length() < 0.01:
      self.controlled = True

    # Check if the monkey has returned to the ground
    #   If velocity is reasonable, return to standing state
    #   Otherwise put into uncontrolled state
    if self._is_hanging():
      force += b2Vec2(force_basis.x, 0) * stats.hang_force_x
      force += b2Vec2(0, force_basis.y) * stats.hang_force_y

      if self.state != 'hanging':
        self.state = 'hanging'
        self._set_controlled(True)

    elif self._is_grounded():
      force += self._calc_platform_force(force_basis) * stats.ground_force_x
      impulse.y += impulse_basis.y * stats.ground_impulse_y

      if self.state != 'grounded':
        self.state = 'grounded'

        # _set_upright() will perserve linear velocity. This makes sense
        # if the user continues holding the key in the desired direction,
        # however if the user stops, then the monkey will land and go
        # continue sliding until frition takes over.
        # Therefore we need to calculate the friction manually and subtract
        # it after uprighting the monkey

        if (self.controlled):
          vel_dot = b2Dot(force_basis, self.body.linearVelocity)
          if vel_dot == 0:
            vel_scale = 0.5
          elif vel_dot > 0:
            vel_scale = 1
          else:
            vel_scale = 0.25

          i, j = self.platform_contact.normal
          perp = b2Vec2(j, -i)
          perp_vel = b2Dot(self.body.linearVelocity, perp) * perp

          self._set_upright()
          self.body.linearVelocity -= (1 - vel_scale) * perp_vel

    elif not self._is_grounded():
      force += b2Vec2(force_basis.x, 0) * stats.air_force_x
      force += b2Vec2(0, force_basis.y) * stats.air_force_y

      if self.state != 'airbourne':
        self.state = 'airbourne'
        self._set_controlled(False)

    # Store air velocity for restoration purposes
    if not self._is_grounded():
      self.last_air_velocity = self.body.linearVelocity

    # Apply Force
    if force.Length() != 0:
      if not self.state == 'grounded' or \
          self.body.linearVelocity.Length() < self.stats.max_ground_velocity:
      
        force = b2Mul(b2Mat22(self.body.angle), force)
        self.body.ApplyForce(force, self.body.position)

    if impulse.Length() != 0:
      force = b2Mul(b2Mat22(self.body.angle), force)
      self.body.ApplyImpulse(impulse, self.body.position)

  def _find_target(self):
    targets = self.get_root().children_of_type(Monkey)
    targets.sort(key=lambda m: -m.body.position.y)

    source_pos  = self.body.position
    source_body = self.body
    v0_max = 5

    for target in targets:
      if target is self:
        continue

      target_pos  = target.body.position
      target_body = target.body

      parabola = pathfinder.find_parabola(self.world, target_body, source_body,
                                          target_pos, source_pos, v0_max, 0.4)

      if parabola:
        break

    self.parabola = parabola

  def _set_contact_callbacks(self):
    self.add_callback(self.on_platform_pre_land, 'Add',
                      self.foot_shape, platform.Platform)

    self.add_callback(self.on_platform_leave, 'Remove',
                      self.foot_shape, platform.Platform)

    self.add_callback(self.on_hit, 'Result', self.body)

    self.add_callback(self.on_grab_touch, 'Live',
                      self.shoulder_shape, grab.Grab)

    self.add_callback(self.on_grab_leave, 'Remove',
                      self.shoulder_shape, grab.Grab)

  def on_platform_leave(self, contact):
    # One of two things happened here, we either jumped off the platform
    # or fell off the platform. If we are running along a slightly bumpy
    # platform, we dont want slight bumps to send us airbourne.
    #
    # To counter this, if there is an adjacent edge on the platform
    # that is relatively flat, we play with the physics to ensure that
    # we keep running along it

    # Only perform the hack if the monkey did not deliberately jump and
    # was not somehow hit (by projectile or another monkey)
#    self.did_jump = False
#    self.was_hit = False
#    if not (self.did_jump or self.was_hit):
#      # Work out which side of the platform we went off
#      cur_plat = self.platform_contact.shape2.asEdge()
#      next_d   = (cur_plat.vertex2 - contact.position).LengthSquared()
#      prev_d   = (cur_plat.vertex1 - contact.position).LengthSquared()
#
#      print next_d, prev_d
#      if prev_d < next_d:
#        adj_plat = cur_plat.prev
#        dir = -1
#      else:
#        adj_plat = cur_plat.next
#        dir = 1
#
#      plat_unit = adj_plat.vertex2 - adj_plat.vertex1
#      plat_unit.Normalize()
#
#      old_vel = self.body.linearVelocity
#      print plat_unit, dir, old_vel.Length()
#      self.body.linearVelocity = plat_unit * dir * old_vel.Length()
#

    if self.platform_contact == None:
      pass

    elif contact.shape2.this == self.platform_contact.shape2.this:
      self.platform_contact = None


  def on_grab_touch(self, contact):
    # Maintain the closest grab point
    if self.grab_contact == None:
      self.grab_contact = copy.copy(contact)

    else:
      shoulder_pos = self.body.GetWorldPoint(self.shoulder_shape.localPosition)

      new_pos  = contact.shape2.GetBody().position
      old_pos  = self.grab_contact.shape2.GetBody().position

      new_dist = (shoulder_pos - new_pos).LengthSquared()
      old_dist = (shoulder_pos - old_pos).LengthSquared()
      if new_dist < old_dist:
        self.grab_contact = copy.copy(contact)

  def on_grab_leave(self, contact):
    if self.grab_contact == None:
      return

    if contact.shape2.this == self.grab_contact.shape2.this:
      self.grab_contact = None


  def on_hit(self, result):
    # Platform and foot collides are handled separetly
    if result.shape1.this == self.foot_shape.this and \
        isinstance(result.shape2.GetBody().userData, platform.Platform):
      
      if self.on_platform_land(result):
        # In the event that we landed on a platform, we are done
        return

    max_impulse = self.stats.max_knock_impulse
    impulse = math.hypot(result.normalImpulse, result.tangentImpulse)

    if impulse > max_impulse:
      self.controlled = False

  def on_platform_land(self, result):
    # For movement calculations, if we are in a grounded state we
    # need to store the best suiting platform contact. We choose
    # the most horizontal platform as the best suiting
    #
    # Return True if we handled the collision, False otherwise

    # Reject hard landings
    if self._will_land(result):
      self.platform_contact = copy.copy(result)
      self.controlled = True

      return True

    return False

  def _attempt_fire(self):
    if self.parabola:
      beachball = beachballofdeath.BeachBallOfDeath()
      beachball.set_init_velocity(self.parabola)
      self.add_child(beachball, (0,0))

  def _attempt_grab(self):
    world = self.body.GetWorld()

    if self.grab_joint != None:
      world.DestroyJoint(self.grab_joint)
      self.grab_joint = None
      return

    if self.grab_contact == None:
      return

    jointDef = b2DistanceJointDef()
    jointDef.body1 = self.body
    jointDef.body2 = self.grab_contact.shape2.GetBody()
    jointDef.frequencyHz = 5
    jointDef.dampingRatio = 5

    jointDef.localAnchor1 = self.shoulder_shape.localPosition
    jointDef.localAnchor2 = (0,0)

    jointDef.length = 2

    self.grab_joint = world.CreateJoint(jointDef)


  def on_platform_pre_land(self, contact):
    if self._will_land(contact):
      contact.shape1.restitution = 0
    else:
      contact.shape1.restitution = self.stats.restitution

  def on_contact_remove(self, contact):
    pass

  def _calc_platform_force(self, input_force):
    """
    Adjust force such that force is applied along platform
    """

    if input_force.LengthSquared() == 0:
      return input_force

    # Applying a force along the platfrom has one slight problem
    #
    #    o   o
    # ___^___^
    #        \   o
    #         \  ^
    #
    # Here the monkey goes air bourne. This is expected behaviour
    # If the edge is very steep, however when going over slight bumps
    # this is very bad. 
    #
    # The solution is to interperlate the angle force vector between
    # the current platfrom and the next platform

    # Divide the current platform at its midpoint. If we are closest to
    # the point on the left, interperlate with it. Same for right
#    v_contact = self.platform_contact.position
#
#    plat = self.platform_contact.shape2.asEdge()
#    plat_c = (plat.vertex1 + plat.vertex2) * 0.5
#
#    next_d = (v_contact - plat.vertex2).LengthSquared()
#    prev_d = (v_contact - plat.vertex1).LengthSquared()
#
#    if next_d < prev_d:
#      inter_plat = plat.next
#      v_common = inter_plat.vertex1
#    else:
#      inter_plat = plat.prev
#      v_common = inter_plat.vertex2
#
#    # Only interperlate if the interplatform slope is less than 60 degrees
#    inter_plat_unit = inter_plat.vertex2 - inter_plat.vertex1
#    inter_plat_unit.Normalize()
#    inter_plat_norm = b2Vec2(inter_plat_unit.y, -inter_plat_unit.x)
#    horiz = b2Vec2(-1,0)
#    print b2Dot(inter_plat_unit, horiz)
#    if b2Dot(inter_plat_unit, horiz) > 0.5:
#      # Interperlate with the normal of the adjacent platform
#      inter_plat_norm = b2Vec2(inter_plat_unit.y, -inter_plat_unit.x)
#      plat_norm = self.platform_contact.normal
#
#      # Do a linear the interperlation
#      plat_d  = (plat_c - v_contact).Length()
#      inter_d = (v_common - v_contact).Length()
#      sum_d = plat_d + inter_d
#
#      norm = inter_plat_norm * (plat_d / sum_d) + plat_norm * (inter_d / sum_d)
#      norm.Normalize()
#    else:
#      norm = self.platform_contact.normal


    # Project the horizontal force vector onto a vector parallel
    # to the normal (slope of platform)

    # This line undoes the interp stuff
    norm = self.platform_contact.normal

    parallel = b2Vec2(norm.y, -norm.x)

    input_force_i = b2Vec2(input_force.x, 0)
    force_parallel = parallel * b2Dot(parallel, input_force)

    # Recombine with vertical component
    force = force_parallel + b2Vec2(0, input_force.y)

    return force

  def render(self):
    if self.parabola:
      self.parabola.plot()

    # Calculate rendering coords
    rot = self.body.angle
    off = self.body.position
    shoulder_offset = b2Vec2(self.shoulder_offset)

    # Body
    gamesprites.GameSprites.render_at_center('monkey', off, (1.6, 1.6), rot)

    # Grab Arm 
    if self.grab_joint:
      grab_hand_pos = self.grab_joint.body2.position
    else:
      grab_hand_pos = b2Vec2(0.2, -0.2) + shoulder_offset
      grab_hand_pos = self.body.GetWorldPoint(grab_hand_pos)
    
    grab_shoulder_pos = self.body.GetWorldPoint(shoulder_offset)
    grab_arm = grab_hand_pos - grab_shoulder_pos
    points = self._render_fatten_vector(grab_arm, 0.05)
    points = map(lambda x: x + grab_shoulder_pos, points)

    gamesprites.GameSprites.render_points('monkey_arm', points)

    # Item Arm
    shoulder_offset.x = -shoulder_offset.x

    item_hand_pos = b2Vec2(-0.2, -0.2) + shoulder_offset
    item_hand_pos = self.body.GetWorldPoint(item_hand_pos)

    item_shoulder_pos = self.body.GetWorldPoint(shoulder_offset)
    item_arm = item_hand_pos - item_shoulder_pos
    points = self._render_fatten_vector(item_arm, 0.05)
    points = map(lambda x: x + item_shoulder_pos, points)

    gamesprites.GameSprites.render_points('monkey_arm', points)

  def _render_fatten_vector(self, vector, fatness):
    unit = vector.copy()
    unit.Normalize()
    unit *= fatness
    perp = (unit.y, -unit.x) 

    points = []

    points.append(-unit - perp)
    points.append(-unit + perp)

    points.append(vector + unit + perp)
    points.append(vector + unit - perp)

    return points

  def _apply_stats(self, stats):
    for shape in self.body.shapeList:
      if shape.isSensor:
        continue

      shape.density     = stats.density
      shape.friction    = stats.friction
      shape.restitution = stats.restitution

    #self.body.SetMassFromShapes()

  def _set_controlled(self, controlled):
    if self.fixedRotation != controlled:
      self.body.SetFixedRotation(controlled)
      self.fixedRotation = controlled

  def _set_upright(self):
    # Note: Do not mess with the engine until the end. Doing so will
    #       trigger callbacks, destroying the integrety of our state
    # Calculate pos above current foot location
    foot_pos = self.foot_shape.localPosition
    rot_mat  = b2Mat22(self.body.angle)
    foot_pos = b2Mul(rot_mat, foot_pos)
    foot_pos += self.body.position

    body_pos = foot_pos - self.foot_shape.localPosition

    # Remove velocity perpendicular to platform
    perp_vel = b2Dot(self.platform_contact.normal, self.body.linearVelocity)   
    perp_vel *= self.platform_contact.normal

    # Update the engine
    self.body.position = body_pos
    self.body.linearVelocity -= perp_vel

    # Upright the monkey
    self.body.angle = 0


    self._set_controlled(True)

  def _is_grounded(self):
    return self.platform_contact != None

  def _is_controlled(self):
    return self.fixedRotation

  def _is_hanging(self):
    return self.grab_joint != None

  def _uprightness(self, reference):
    """
    Return a measure of how upright the monkey is. The measure we use
    is the dot product between a unit reference vector and the direction
    vector of the monkey
    """

    rot_mat = b2Mat22(self.body.angle)
    up = b2Vec2(0,1)
    d_vec   = b2Mul(rot_mat, up)

    return b2Dot(d_vec, reference)

  def _will_land(self, platform_contact):
    """
    Calculate whether the monkey is in a stable enough state as to land
    upright when he hits a platform
    """
    uprightness = self._uprightness(b2Vec2(0,1))

    platform_dot = b2Dot(platform_contact.normal, b2Vec2(0,1)) 

    # Reject any platform at an angle greater than 60 degrees
    if platform_dot < 0.5:
      return False

    
    score = uprightness * self.body.linearVelocity.Length()

    # Only consider score component perpendictular to the platform
    score *= platform_dot

    return score < self.stats.max_landing_speed

