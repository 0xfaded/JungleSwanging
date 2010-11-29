# vim:set ts=2 sw=2 et:
from renderable import *

#from objectfactory import *

from objectid import *

class GameObject(Object):
  def __init__(self):
    super(GameObject, self).__init__()
    self.parent = None;

    self.body = None
    self.parent = None
    self.children = []
    self.callbacks = set()

    self.world = None
    self.contact_listener = None


  def add_child(self, child, offset):
    # Insert into object tree
    child.parent = self
    child.world = self.world
    child.contact_listener = self.contact_listener 

    self.children.append(child)

    # Insert into b2World
    position = self.body.position + offset
    child.add_to_world(position)

  def remove_child(self, child):
    for i in xrange(len(self.children)):
      if id(self.children[i]) == id(child):
        self.children.pop(i)

  def set_root(self, world, contact_listener):
    self.parent = None
    self.world, self.contact_listener = world, contact_listener
    self.body = world.GetGroundBody()

  def add_callback(self, func, events, arg1=None, arg2=None):
    id = self.contact_listener.add_callback(func, events, arg1, arg2)
    self.callbacks.add(id)

    return id

  def remove_callback(self, id, events = None):
    self.contact_listener.remove_callback(id)
    self.callbacks.remove(id)

  def kill_me(self):
    self.parent.remove_child(self)

    for child in self.children:
      child.kill_me()

    # We cant be modifying the callback set whilst we iterate over it
    # so iterate over a copy
    callbacks = list(self.callbacks)

    for callback in callbacks:
      self.remove_callback(callback)

    if self.body != None:
      self.world.DestroyBody(self.body)

  def set_start(self, coords):
    self.x_init, self.y_init = coords

  def get_start(self):
    return (self.x_init,self.y_init)

  def add_to_world(self, at):
    pass

  def update_tree(self, controller, delta_t):
    for child in self.children:
      child.update_tree(controller, delta_t)
      child.update(controller, delta_t)

  def update(self, controller, delta_t):
    pass

  def get_root(self):
    root = self
    while root.parent != None:
      root = root.parent

    return root

  def tree_to_network(self, msg):
    """
    Write the entire tree to a network
    """
    self.to_network(msg)
    msg.append(len(self.children))
    for child in self.children:
      child.tree_to_network(msg)

  def tree_from_network(self, msg):
    """
    Read the entire tree to a network. Note this requires knowing what
    the root class is, which is always of type Map. So only directly
    call this method from a Map
    """

    self.from_network(msg)
    n_children = int(msg.pop())
    for n in xrange(n_children):
      obj_id = int(msg[-1])
      child = None #ObjectFactory.from_id(obj_id)
      child.tree_from_network(msg)
      self.children.append(child)

    """
    Creates a minimal representation containing data required for
    rendering the game object 
    """
    raise NotImplementedError()

  def to_network(self, msg):
    """
    Creates a minimal representation containing data required for
    rendering the game object 
    """
    raise NotImplementedError()

  def from_network(self, msg):
    """
    Reconstructs a minimal representation containing data required for
    rendering the game object 
    """
    raise NotImplementedError()

  def tree_render(self):
    self.render()
    for child in self.children:
      child.render()

  def render(self):
    raise NotImplementedError()


