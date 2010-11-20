# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *
from grab import *
from platform import *

import copy

class Monkey(GameObject):

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
      self.ground_force_x       = 50 # Ground acceleration along the x axis
      self.ground_force_y       =  0 # Ground acceleration along the y axis

      self.ground_impulse_x     =  0
      self.ground_impulse_y     = 20 # Best thought as jump

      self.air_force_x          = 10 # Air acceleration along the x axis
      self.air_force_y          = 40 # Air acceleration along the y axis

      self.air_impulse_x        =  0
      self.air_impulse_y        =  0 # Best thought as air boost

      self.hang_force_x         =  0 # Hanging acceleration along the x axis
      self.hang_force_y         =  0 # Hanging acceleration along the y axis

      self.hang_impulse_x       =  0
      self.hang_impulse_y       =  0 # Best thought as hang boost

      self.max_landing_impulse  = 35
      self.max_knock_impulse    = 20

      # if velocity < max_velocity: apply force
      self.max_ground_velocity  =  5
      self.max_air_velocity     =  2

  def __init__(self, parent):
    super(Monkey, self).__init__(parent)

    self.t = 0

    # Note we do not need to set any properties of the monkey's shapes
    # as all properties in stats are applied to the entire monkey
    # on each iteration
    self.base_stats = Monkey.Stats()
    self.stats      = self.base_stats

    self.boxDef = b2PolygonDef()
    self.boxDef.SetAsBox(0.4, 0.4)

    self.circleDef = b2CircleDef()
    self.circleDef.radius = 0.41

    # Shoulder sensor is used for determining if a grab point is in range
    self.shoulderDef = b2CircleDef()
    self.shoulderDef.radius = 0
    self.shoulderDef.isSensor = True

    self.bodyDef = b2BodyDef()
    self.bodyDef.angle = 0.0
    self.bodyDef.allowSleep = False
    self.bodyDef.userData = self

    self.platform_contact = None
    self.grab_contact = None
    self.grab_joint = None

    # Body.GetFixedRotation() is buggy, so we need to store our own
    self.fixedRotation = True
    self.controlled = True

    self.direction = 1

    self.state = 'none'

  def add_to_world(self, at):
    self.bodyDef.position = at
    self.body = self.world.CreateBody(self.bodyDef)

    self.boxShape = self.body.CreateShape(self.boxDef)
    self.boxShape = self.boxShape.asPolygon()

    self.circleDef.localPosition = (0, -0.4)

    self.foot_shape = self.body.CreateShape(self.circleDef)
    self.foot_shape = self.foot_shape.asCircle()

    self.circleDef.localPosition = (0, 0.4)

    self.head_shape = self.body.CreateShape(self.circleDef)
    self.head_shape = self.head_shape.asCircle()

    self.shoulderDef.localPosition = (0.0 * self.direction, 0.4)

    self.shoulder_shape = self.body.CreateShape(self.shoulderDef)
    self.shoulder_shape = self.shoulder_shape.asCircle()

    self._apply_stats(self.stats)

    self.body.SetMassFromShapes()

    self.body.SetFixedRotation(True)

    self._set_contact_callbacks()

  def update(self, controller, delta_t):
    keys, events = controller

    # Update the monkey with the latest stats
    stats = self.stats
    #self._apply_stats(stats)

    # Calculate the force vector to apply in the left or right direction
    force = b2Vec2(0, 0)
    impulse = b2Vec2(0, 0)

    force_basis   = b2Vec2(0,0)
    impulse_basis = b2Vec2(0,0)

    # Left Right movement
    if keys[K_LEFT]:
      force_basis += b2Vec2(-1,  0)
    if keys[K_RIGHT]:
      force_basis += b2Vec2( 1,  0)
    if keys[K_UP]:
      force_basis += b2Vec2( 0,  1)
    if keys[K_DOWN]:
      force_basis += b2Vec2( 0, -1)


    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == K_SPACE:
          self._attempt_grab()
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

      force += b2Vec2(force_basis.x, 0) * stats.hang_force_x
      force += b2Vec2(0, force_basis.y) * stats.hang_force_y

    # Check if the monkey has returned to the ground
    #   If velocity is reasonable, return to standing state
    #   Otherwise put into uncontrolled state
    if self._is_hanging():
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

  def _set_contact_callbacks(self):
    self.add_callback(self.on_platform_pre_land, 'Add',
                      self.foot_shape, Platform)

    self.add_callback(self.on_platform_land, 'Result',
                      self.foot_shape, Platform)

    self.add_callback(self.on_platform_leave, 'Remove',
                      self.foot_shape, Platform)

    self.add_callback(self.on_hit, 'Result', self.body)

    self.add_callback(self.on_grab_touch, 'Live',
                      self.shoulder_shape, Grab)

    self.add_callback(self.on_grab_leave, 'Remove',
                      self.shoulder_shape, Grab)

  def on_platform_land(self, result):
    # For movement calculations, if we are in a grounded state we
    # need to store the best suiting platform contact. We choose
    # the most horizontal platform as the best suiting

    # First reject any hard landings
    up = b2Vec2(0,1)
    monkey_up = b2Mul(b2Mat22(self.body.angle), up)

    reject_dot = (b2Dot(monkey_up, up) * 0.9 + 0.1)

    reject_dot **= 3

    print result.normalImpulse
    max_impulse = self.stats.max_landing_impulse * reject_dot

    if result.normalImpulse <= max_impulse:
      up = b2Vec2(0, 1)
      dot = b2Dot(result.normal, up)

      # Reject any platform at an angle greater than 60 degrees
      if dot > 0.5:
        # Choose best dot from either new platform or existing contact
        if self.platform_contact == None:
          self.platform_contact = copy.copy(result)
        else:
          old_dot = b2Dot(self.platform_contact.normal, up)

          if dot > old_dot:
            self.platform_contact = copy.copy(result)

        # If there is now an accepted platform, we are controlled
        self.controlled = True
        return True
    
    return False

  def on_platform_leave(self, contact):
    if self.platform_contact == None:
      return

    if contact.shape2.this == self.platform_contact.shape2.this:
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
    if result.shape1.this == self.foot_shape.this and \
        isinstance(result.shape2.GetBody().userData, Platform):

      # Platform and foot collides are handled separetly
      self.on_platform_land(result)

    else:
      max_impulse = self.stats.max_knock_impulse
      impulse = math.hypot(result.normalImpulse, result.tangentImpulse)

      if impulse > max_impulse:
        self.controlled = False

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
    normal_vel = b2Dot(contact.velocity, contact.normal) * contact.normal
    # print normal_vel
    # TODO clean this up
    contact.shape1.restitution = 0
    if normal_vel.Length() < 10:
      contact.shape1.restitution = 0
    else:
      contact.shape1.restitution = self.stats.restitution

  def on_contact_remove(self, contact):
    pass

  def _calc_platform_force(self, input_force):
    """
    Adjust force such that force is applied along platform
    """
    i, j = self.platform_contact.normal
    parallel = b2Vec2(-j, i)

    if input_force.Length() != 0:
      # Project the horizontal force vector onto a vector parallel
      # to the normal (slope of platform)
      input_force_i = b2Vec2(input_force.x, 0)
      force_parallel = parallel * b2Dot(parallel, input_force)


      # Recombine with vertical component
      force = force_parallel + b2Vec2(0, input_force.y)

    else:
      force = input_force

    return force

  def render(self):
    # Calculate rendering coords
    rot = b2Mat22(self.body.angle)
    off = self.body.position

    points = map(lambda x: b2Mul(rot,x) + off, self.points)


    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(1, 0, 0)


    glBegin(GL_POLYGON)
    for (x,y) in points:
      glVertex3f(x, y, 0)
    glEnd()

    glBegin(GL_LINES)
    points = map(lambda x: b2Mul(rot,x) + off, [b2Vec2(0,0), b2Vec2(0, 0.05)])
    for (x,y) in points:
      glVertex3f(x, y, 0)
    glEnd()

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

