import copy
from numbers import Number
from types import FunctionType, NoneType


from Box2D import *

class ContactListener(b2ContactListener):
  class ContactCallback(object):
    def __init__(self, func, test, flip):
      self.func = func
      self.test = test
      self.flip = flip

  def __init__(self):
    super(ContactListener, self).__init__()

    self.callbacks = {}
    self.callbacks['Add'    ] = {}
    self.callbacks['Remove' ] = {}
    self.callbacks['Persist'] = {}
    self.callbacks['Result' ] = {}

  def add_callback(self, func, events, arg1, arg2 = None):
    """
    func: callback function

    Events in ['Add', 'Remove', 'Persist', 'Result', 'Live']

    'Live' is a special event that listens to both 'Add' and 'Persist'

    Creates a callback to be called if arg1 and arg2 match the
    shapes involved in the collision

    An arg can be one of several types

    b2Shape
      Return True if shape is present in collision
    b2Body
      Return True if body is present in collision
    python type (new style class object)
      Return True if body userdata is of this type
    None
      If second arg is None, then we don't consider it for the test
    function
      A user defined function that takes a shape as an argument

    The return is a tuple of tests. The first tests checks for
    the presence of arg1 and arg2. The second checks whether
    or not arg1 and arg2 are in order. If arg1 and arg2 are out
    of order, the contact will be flipped with all vectors directions
    reversed
    """

    if isinstance(events, str):
      events = [events]

    # Filter for duplicates
    events = set(events)
    if 'Live' in events:
      events = events | set(['Add', 'Persist'])
      events.remove('Live')

    callback = self.ContactCallback(func, *self._create_test(arg1, arg2))
    for event in events:
      self.callbacks[event][id(callback)] = callback

    return id(callback)
  
  def remove_callback(self, callback_id, events = None):

    if events == None:
      events = ['Add', 'Persist', 'Remove', 'Result']

    if isinstance(events, str):
      events = [events]

    # Filter for duplicates
    events = set(events)
    if 'Live' in events:
      events = events | set(['Add', 'Persist'])
      events.remove('Live')

    for event in events:
      if self.callbacks[event].has_key(callback_id):
        self.callbacks[event].pop(callback_id)

  def Add(self, contact):
    self._callback(self.callbacks['Add'], contact)

  def Remove(self, contact):
    self._callback(self.callbacks['Remove'], contact)

  def Persist(self, contact):
    self._callback(self.callbacks['Persist'], contact)

  def Result(self, contactResult):
    self._callback(self.callbacks['Result'], contactResult)

  def _callback(self, callbacks, contact):
    flipped = self._flip_contact(contact)
    for callback in callbacks.values():
      if callback.test(contact):
        if callback.flip(contact):
          callback.func(flipped)
        else:
          callback.func(contact)

  def _flip_contact(self, contact):
    # XXX Turns out this function was broken. If we do anything here,
    # well mess up the entire simulation. Epic TODO. The shape swap
    # is still required though

    # Careful, this is a shallow copy
    flipped = copy.copy(contact)

    tmp = flipped.shape1
    flipped.shape1 = flipped.shape2
    flipped.shape2 = tmp

    return flipped

    if isinstance(contact, b2ContactPoint):
      flipped.normal     = -flipped.normal
      flipped.separation = -flipped.separation
      flipped.velocity   = -flipped.velocity
    elif isinstance(contact, b2ContactResult):
      flipped.normal            = -flipped.normal

    return flipped


  def _create_test(self, arg1, arg2 = None):
    cmp1 = self._create_cmp(arg1)
    cmp2 = self._create_cmp(arg2)


    def filter_func(contact):
      if cmp1(contact.shape1):
        return cmp2(contact.shape2)

      elif cmp1(contact.shape2):
        return cmp2(contact.shape1)

      else:
        return False

    def flipper_func(contact):
      return not cmp1(contact.shape1)

    return (filter_func, flipper_func)

  def _create_cmp(self, arg):

    if isinstance(arg, FunctionType):
      return arg

    if isinstance(arg, b2Shape):
      def cmp(contact_shape):
        return arg.this == contact_shape.this
    
    elif isinstance(arg, b2Body):
      def cmp(contact_shape):
        return arg.this == contact_shape.GetBody().this

    elif isinstance(arg, type):
      def cmp(contact_shape):
        return isinstance(contact_shape.GetBody().userData, arg)

    elif isinstance(arg, NoneType):
      def cmp(contact_shape):
        return True

    return cmp

