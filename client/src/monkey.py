# vim:set sw=2 ts=2 sts=2 et:

from OpenGL.GL import *
import math

import pygame
from pygame.locals import *

from Box2D import *

from gameobject import *

class Monkey(GameObject):

  category = 1
  mass       = 50.0
  elasticity = 0.8

  # Note additonal friction is calculated separately whilst on ground
  friction   = 0.5

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
    self.boxDef.categoryBits = Monkey.category

    self.circleDef = b2CircleDef()
    self.circleDef.radius = 0.39
    self.circleDef.density = 1
    self.circleDef.friction = self.friction
    self.circleDef.restitution = 0.5
    self.circleDef.categoryBits= Monkey.category

    self.bodyDef = b2BodyDef()
    self.bodyDef.angle = 0.0
    self.bodyDef.allowSleeping = False
    self.bodyDef.userData = self

    self.state = 'grounded'

    self.platform_contact = None

  def add_to_world(self, world, at):
    self.bodyDef.position = at
    self.body = world.CreateBody(self.bodyDef)

    self.body.CreateShape(self.boxDef)

    self.circleDef.localPosition = (0, -0.4)
    # Store the foot shape so we can do collision detection
    self.foot_shape = self.body.CreateShape(self.circleDef)

    self.circleDef.localPosition = (0, 0.4)
    self.body.CreateShape(self.circleDef)

    self.body.SetMassFromShapes()

    #self.body.SetFixedRotation(True)

  def control(self, contact_listener, keys):
    # Calculate the force vector to apply in the left or right direction
    force = b2Vec2(0, 0)
    impulse = b2Vec2(0, 0)
    if keys[K_LEFT]:
      force += b2Vec2(-1, 0)
    if keys[K_RIGHT]:
      force += b2Vec2(1, 0)

    if keys[K_UP]:
      impulse += b2Vec2(0, 1)

    # See if we lost contact with our current contact
    if self.platform_contact != None:
      for contact in contact_listener.get_separates(self, str):
        if self.platform_contact.shape2.this == contact.shape2.this:
          self.platform_contact = None
          break

    # Find the most horizontal platform contact and assign it to the current
    # Platform
    #
    # If contacts is empty, we are either not touching anything
    # or havent moved this iteration. If in the previous iteration
    # we werent touching anything, self.platform_contact will be None
    best_dot = -100000
    down = b2Vec2(0, -1)

    for contact in contact_listener.get_contacts(self, str):
      dot = b2Dot(contact.normal, down)

      # Contacts are added in time order. If two contacts are equal,
      # yet one contact is more recent than the previous, use the
      # more recent one. Hence <= instead of <
      if best_dot <= dot:
        best_dot = dot
        self.platform_contact = contact

    #print self.platform_contact
    # TODO if contact is two steep ignore

    if self.platform_contact == None:
      force *= 0
      impulse *= 0
      self._set_airbourne()
    else:
      force = self._calc_platform_force(force)
      force *= 30
      impulse *= 10
      self._set_upright()


    # Apply Force
    if force.Length() != 0:
      forceN = force.copy()
      forceN.Normalize()
      if b2Dot(self.body.linearVelocity, forceN) < 5:
        self.body.ApplyForce(force, self.body.position)

    if impulse.Length() != 0:
      self.body.ApplyImpulse(impulse, self.body.position)


  def on_contact_add(self, contact):
    if contact.velocity.Length() < 5:
      contact.shape1.restitution = 0
    else:
      contact.shape1.restitution = 0.5


  def on_contact_remove(self, contact):
    print 'post'

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

  def _set_airbourne(self):
    return
    self.body.SetFixedRotation(False)

  def _set_upright(self):
    return
    self.body.SetFixedRotation(True)
    #self.body.angle = 0
