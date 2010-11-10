# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *
from grab import *

class Monkey(GameObject):

  category = 1
  mass       = 50.0
  elasticity = 0.8

  # Note additonal friction is calculated separately whilst on ground
  friction   = 3

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
    self.circleDef.radius = 0.39
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

    self.last_contacts = []
    self.last_air_velocity = b2Vec2(0,0)

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

  def read_contacts(self, contact_listener):
    # Find the most horizontal platform contact and assign it to the current
    # Platform
    best_dot = -100000
    down = b2Vec2(0, -1)

    self.platform_contact = None
    for contact in contact_listener.get_live(self, str):
      print - contact.normal * contact.velocity.Length()
      dot = b2Dot(contact.normal, down)

      # Contacts are added in time order. If two contacts are equal,
      # yet one contact is more recent than the previous, use the
      # more recent one. Hence <= instead of <
      if best_dot <= dot:
        best_dot = dot
        self.platform_contact = contact

    # if contact is two steep ignore (currently at pi/3)
    if best_dot < 0.5:
      self.platform_contact = None

    # Find closest grab point
    shoulder_pos = self.body.GetWorldPoint(self.shoulder_shape.localPosition)

    self.grab_contact = None
    best_dist = 10000000
    for contact in contact_listener.get_live(self, Grab):
      if contact.shape1.this != self.shoulder_shape.this:
        continue

      dist = (shoulder_pos - contact.body2.position).Length() 
      if dist <= best_dist:
        best_dist = dist
        self.grab_contact = contact

  def control(self, keys, events):
    self.keys = keys

    # Calculate the force vector to apply in the left or right direction
    force = b2Vec2(0, 0)
    impulse = b2Vec2(0, 0)

    # Left Right movement
    if keys[K_LEFT]:
      force += b2Vec2(-1, 0)
    if keys[K_RIGHT]:
      force += b2Vec2(1, 0)

    if keys[K_UP]:
      impulse += b2Vec2(0, 1)

    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == K_SPACE:
          self._attempt_grab()

    # Check if the monkey has returned to the ground
    #   If velocity is reasonable, return to standing state
    #   Otherwise put into uncontrolled state
    if self._is_hanging():
      if self.state != 'hanging':
        self.state = 'hanging'
        print self.state
        self._set_controlled()

    elif self._is_grounded():
      if self.state != 'grounded':
        self.state = 'grounded'
        print self.state

        # Normal vector points from shape1 to shape2.
        #   shape1 = monkey
        #   shape2 = platform
        # So we reverse the normal
        uprightness = self._uprightness(-self.platform_contact.normal)
        upright_threshold = uprightness * 5 + 1
        if self.body.linearVelocity.Length() < upright_threshold:
          self._set_upright()

          # When we land hard we create a lot of friction and therefore
          # lose a lot of speed. This feels good if we want to stop, but
          # if the user has their key down in the same direction it feels
          # wrong. To combat this, after landing, if the user is holding
          # down the key in the direction restore their linear velocity

          # is the user holding down the key in the same direction`
          if b2Dot(force, self.last_air_velocity) > 0:
            print 'nooo'
            # reference vector perpendicular to normal
            (i, j) = self.platform_contact.normal
            perp = b2Vec2(-j, i)
            proj_vel = b2Dot(perp, self.last_air_velocity) * perp

            # What velocity wasn't saved must be converted to some
            # form of resistance force
            #resistance = self.last_air_velocity - proj_vel
            #proj_mag = proj_vel.Length() * self.friction
            #resistance_mag = proj_vel.Length()

            # Note, cant be zero as "force dot last_vel > 0"
            #ratio = proj_mag / (resistance_mag + proj_mag)
            ratio = 0.9
            proj_vel *= ratio

            self.body.linearVelocity = proj_vel
        else:
          self._set_uncontrolled()

    elif not self._is_grounded():
      if self.state != 'airbourne':
        self.state = 'airbourne'
        print self.state

    # Store air velocity for restoration purposes
    if not self._is_grounded():
      self.last_air_velocity = self.body.linearVelocity


    if self.platform_contact == None:
      force *= 0
      impulse *= 0
    else:
      force = self._calc_platform_force(force)
      force *= 30
      impulse *= 10

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
    jointDef.body2 = self.grab_contact.body2
    jointDef.frequencyHz = 5
    jointDef.dampingRatio = 5

    jointDef.localAnchor1 = self.shoulder_shape.localPosition
    jointDef.localAnchor2 = (0,0)

    shoulder_pos = self.body.GetWorldPoint(self.shoulder_shape.localPosition)
    disp = self.grab_contact.body2.position - shoulder_pos
    jointDef.length = disp.Length()
    jointDef.length = 2
    
    self.grab_joint = world.CreateJoint(jointDef)


  def on_contact_add(self, contact):
    if contact.velocity.Length() < 5:
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
    # If we are already in a controlled state, do nothing
    # Otherwise set the monkey in a controlled upright state

    if self._is_controlled():
      return

    # Calculate pos above current foot location
    foot_pos = self.foot_shape.localPosition
    rot_mat  = b2Mat22(self.body.angle)
    foot_pos = b2Mul(rot_mat, foot_pos)
    foot_pos += self.body.position

    body_pos = foot_pos - self.foot_shape.localPosition

    self.body.position = body_pos

    # Upright the monkey
    self.body.angle = 0

    self._set_controlled()

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

