from Box2D import *

import traceback

class Contact(object):
  def __init__(self, contact_or_shape1 = None, shape2 = None,
               normal = None, position = None, velocity = None):

    if shape2 == None:
      self.shape1 = contact_or_shape1.shape1
      self.shape2 = contact_or_shape1.shape2

      self.normal = contact_or_shape1.normal.copy()
      self.position = contact_or_shape1.position.copy()
      self.velocity = contact_or_shape1.velocity.copy()

    else:
      self.shape1 = contact_or_shape1
      self.shape2 = shape2

      self.normal = normal.copy()
      self.position = position.copy()
      self.velocity = velocity.copy()

    self.body1 = self.shape1.GetBody()
    self.body2 = self.shape2.GetBody()

  def flip(self):
    """
    Returns a new Contact with the ording of the bodies switched
    """
    return Contact(self.shape2, self.shape1,
                   self.normal * -1, self.position, self.velocity * -1)

  def id(self):
    a = int(self.shape1.this)
    b = int(self.shape2.this)

    if a < b:
      return (a,b)
    else:
      return (b,a)

  def same_shapes(self, other):
    return \
            (self.shape1.this == other.shape1.this \
         and self.shape2.this == other.shape2.this) \
      or \
            (self.shape1.this == other.shape2.this \
         and self.shape2.this == other.shape1.this)

class ContactListener(b2ContactListener):
  def __init__(self):
    super(ContactListener, self).__init__()
    self.contacts = []
    self.separates = []

    self.live = {}

  def clear_buffer(self):
    self.contacts = []
    self.separates = []

  def Add(self, contact):
    contact = Contact(contact)

    self.contacts.append(contact)
    self.live[contact.id()] = contact

    self.on_add(contact)

  def Remove(self, contact):
    contact = Contact(contact)

    self.separates.append(contact)
    self.live.pop(contact.id())

    self.on_remove(contact)

  def on_add(self, contact):
    b1 = contact.body1
    b2 = contact.body2
    if b1.userData != None and not isinstance(b1.userData, str):
      b1.userData.on_contact_add(contact)

    if b2.userData != None and not isinstance(b2.userData, str):
      b2.userData.on_contact_add(contact.flip())

  def on_remove(self, contact):
    b1 = contact.body1
    b2 = contact.body2
    if b1.userData != None and not isinstance(b1.userData, str):
      b1.userData.on_contact_remove(contact)

    if b2.userData != None and not isinstance(b2.userData, str):
      b2.userData.on_contact_remove(contact.flip())

  def get_live(self, class1 = None, class2 = None):
    """
    Returns a list of live (active) contacts
    If class1 is a type (ie a class name), then the contacts are filtered
      such that at least one body is of type class1
    if class1 is an object (eg a new style class that derives from obj),
      then the contacts will be filtered such that atleast one body IS
      class1 (eg equal pointer values)

    if class2 is defined, then the above checks are performed such that
      both class1 and class2 are present

    The resulting contacts are then reorded such that body1 is always
      of type (or instance of) class1

    If both class1 and class2 are None, a list of all buffered contacts
      is returned

    The comparisons are performed on the userData of the Box2D bodies

    class1: Type or Object
    class2: Type or Object
    """

    return self._filter(self.live.values(), class1, class2)

  def get_contacts(self, class1 = None, class2 = None):
    """
    Returns a list of buffered contacts
    If class1 is a type (ie a class name), then the contacts are filtered
      such that at least one body is of type class1
    if class1 is an object (eg a new style class that derives from obj),
      then the contacts will be filtered such that atleast one body IS
      class1 (eg equal pointer values)

    if class2 is defined, then the above checks are performed such that
      both class1 and class2 are present

    The resulting contacts are then reorded such that body1 is always
      of type (or instance of) class1

    If both class1 and class2 are None, a list of all buffered contacts
      is returned

    The comparisons are performed on the userData of the Box2D bodies

    class1: Type or Object
    class2: Type or Object
    """

    return self._filter(self.contacts, class1, class2)

  def get_separates(self, class1 = None, class2 = None):
    """
    Returns a list of buffered separates
    If class1 is a type (ie a class name), then the separates are filtered
      such that at least one body is of type class1
    if class1 is an object (eg a new style class that derives from obj),
      then the separates will be filtered such that atleast one body IS
      class1 (eg equal pointer values)

    if class2 is defined, then the above checks are performed such that
      both class1 and class2 are present

    The resulting separates are then reorded such that body1 is always
      of type (or instance of) class1

    If both class1 and class2 are None, a list of all buffered separates
      is returned

    The comparisons are performed on the userData of the Box2D bodies

    class1: Type or Object
    class2: Type or Object
    """

    return self._filter(self.separates, class1, class2)

  def _filter(self, ret, class1, class2):
    """
    Does the magic filtering for get_contacts and get_separates
    """

    if class1 != None:
      if isinstance(class1, type):
        def cmp1(x):
          return isinstance(x, class1)
      else:
        def cmp1(x): return x is class1

      if class2 == None:
        def filter_func(x):
          return cmp1(x.body1.userData) or cmp1(x.body2.userData)

      else: # class2 != None
        if isinstance(class2, type):
          def cmp2(x): return isinstance(x, class2)
        else:
          def cmp2(x): return x is class2

        def filter_func(x):
          if cmp1(x.body1.userData):
            return cmp2(x.body2.userData)

          elif cmp2(x.body1.userData):
            return cmp1(x.body2.userData)

          else:
            return False

      ret = filter(filter_func, ret)

      def flipper_func(x):
        if cmp1(x.body2.userData):
          return x.flip()
        else:
          return x

      ret = map(flipper_func, ret)

    return ret

