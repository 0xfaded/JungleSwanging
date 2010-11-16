# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *
from grab import *

import copy

class Monkey(GameObject):

  category = 1
  mass       = 50.0
  elasticity = 0.8

  # Note additonal friction is calculated separately whilst on ground
  friction   = 3

  max_landing_impulse = 30
  max_knock_impulse   = 10

  max_ground_velocity = 5

  def __init__(self):
    super(Monkey, self).__init__()

    self.t = 0

  # Body consists a box with a circle at the top and bottom
    #self.points = [( 0.0923, 0.0382),( 0.0382, 0.0923), \
                   #(-0.0382, 0.0923),(-0.0923, 0.0382), \
                   #(-0.0923,-0.0382),(-0.0382,-0.0923), \
                   #( 0.0382,-0.0923),( 0.0923,-0.0382)]

    self.boxDef = b2PolygonDef()
    self.boxDef.SetAsBox(0.4, 0.4)
    self.boxDef.density = 1
    self.boxDef.friction = self.friction
    self.boxDef.restitution = 0.5

    self.circleDef = b2CircleDef()
    self.circleDef.radius = 0.41
    self.circleDef.density = 1
    self.circleDef.friction = self.friction
    self.circleDef.restitution = 0.5

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

  def add_to_world(self, world, at):
    self.bodyDef.position = at
    self.body = world.CreateBody(self.bodyDef)

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

    self.body.SetMassFromShapes()

    self.body.SetFixedRotation(True)

  def set_contact_callbacks(self, contact_listener):
    contact_listener.add_callback(self.on_platform_pre_land, 'Add',
                                  self.foot_shape, str)

    contact_listener.add_callback(self.on_platform_land, 'Result',
                                  self.foot_shape, str)

    contact_listener.add_callback(self.on_platform_leave, 'Remove',
                                  self.foot_shape, str)

    contact_listener.add_callback(self.on_hit, 'Result', self.body)

    contact_listener.add_callback(self.on_grab_touch, 'Live',
                                  self.shoulder_shape, Grab)

    contact_listener.add_callback(self.on_grab_leave, 'Remove',
                                  self.shoulder_shape, Grab)

  def on_platform_land(self, result):
    # For movement calculations, if we are in a grounded state we
    # need to store the best suiting platform contact. We choose
    # the most horizontal platform as the best suiting

    if result.normalImpulse <= self.max_landing_impulse:
      up = b2Vec2(0, 1)
      dot = b2Dot(result.normal, up)

      # Reject any platform at an angle greater than 60 degrees
      if dot > 0.5:
        if self.platform_contact == None:
          self.platform_contact = copy.copy(result)
        else:
          old_dot = b2Dot(self.platform_contact.normal, up)

          if dot > old_dot:
            self.platform_contact = copy.copy(result)

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
        isinstance(result.shape2.GetBody().userData, str):

      up = b2Vec2(0,1)
      monkey_up = b2Mul(b2Mat22(self.body.angle), up)

      max_impulse = self.max_landing_impulse * (b2Dot(monkey_up, up) + 0.1)
      impulse = result.normalImpulse
      if impulse > max_impulse:
        self.controlled = False
      else:
        self.controlled = True

    else:
      max_impulse = self.max_knock_impulse
      impulse = math.hypot(result.normalImpulse, result.tangentImpulse)

      if impulse > max_impulse:
        self.controlled = False


  def read_contacts(self, contact_listener):
    return
    best_dot = -100000
    down = b2Vec2(0, -1)


  def control(self, keys, events):
    self.keys = keys

    # Calculate the force vector to apply in the left or right direction
    force = b2Vec2(0, 0)
    impulse = b2Vec2(0, 0)

    key_basis  = b2Vec2(0,0)
    jump_basis = b2Vec2(0,0)

    # Left Right movement
    if keys[K_LEFT]:
      key_basis += b2Vec2(-1, 0)
    if keys[K_RIGHT]:
      key_basis += b2Vec2(1, 0)

    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == K_SPACE:
          self._attempt_grab()
        if event.key == K_UP:
          jump_basis += b2Vec2(0, 1)

    # Prevent ourselves from getting stuck with our feet not touching a platform
    if self.body.linearVelocity.Length() < 0.01:
      self.controlled = True

    # Check if the monkey has returned to the ground
    #   If velocity is reasonable, return to standing state
    #   Otherwise put into uncontrolled state
    if self._is_hanging():
      if self.state != 'hanging':
        self.state = 'hanging'
        self._set_controlled(True)
        print self.state

    elif self._is_grounded():
      force   += self._calc_platform_force(key_basis)  * 50
      impulse += jump_basis * 20

      if self.state != 'grounded':
        self.state = 'grounded'
        print self.state

        # _set_upright() will perserve linear velocity. This makes sense
        # if the user continues holding the key in the desired direction,
        # however if the user stops, then the monkey will land and go
        # continue sliding until frition takes over. 
        # Therefore we need to calculate the friction manually and subtract
        # it after uprighting the monkey

        if (self.controlled):
          vel_dot = b2Dot(key_basis, self.body.linearVelocity)
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
      if self.state != 'airbourne':
        self.state = 'airbourne'
        print self.state
        self._set_controlled(False)

    # Store air velocity for restoration purposes
    if not self._is_grounded():
      self.last_air_velocity = self.body.linearVelocity

    # Apply Force
    if force.Length() != 0:
      forceN = force.copy()
      forceN.Normalize()
      # TODO Max speed == 5, clean this
      if b2Dot(self.body.linearVelocity, forceN) < self.max_ground_velocity:
        self.body.ApplyForce(force, self.body.position)

    if impulse.Length() != 0:
      self.body.ApplyImpulse(impulse, self.body.position)

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
    print normal_vel
    if normal_vel.Length() < 10:
      contact.shape1.restitution = 0
    else:
      contact.shape1.restitution = 0.5

  def on_contact_remove(self, contact):
    pass

  def _calc_platform_force(self, input_force):
    """
    Scale force appropriately for the case when a monkey is standing on a
    platform
    """
    i, j = self.platform_contact.normal
    parallel = b2Vec2(-j, i)

    if input_force.Length() != 0:
      # Project the horizontal force vector onto a vector parallel
      # to the normal (slope of platform)
      input_force = parallel * b2Dot(parallel, input_force)

    # Friction is always in the direction opposite the monkeys velocity
    friction_force = -0.0 * self.body.linearVelocity

    force = input_force + friction_force

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

  def _set_controlled(self, controlled):
    if self.fixedRotation != controlled:
      print 'set', controlled
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

