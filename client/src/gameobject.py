# vim:set ts=2 sw=2 et:

from Box2D import b2XForm, b2Mul

class GameObject(object):
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
        break

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

  def update_tree(self, delta_t):
    for child in self.children:
      child.update_tree(delta_t)
      child.update(delta_t)

  def update(self, delta_t):
    pass

  def get_root(self):
    root = self
    while root.parent != None:
      root = root.parent

    return root

  def children_of_type(self, class_type):
    ret = []
    for child in self.children:
      if isinstance(child, class_type):
        ret.append(child)

    for child in self.children:
      ret += child.children_of_type(class_type)

    return ret

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
      child = objectfactory.ObjectFactory.from_id(obj_id)
      child.tree_from_network(msg)
      self.children.append(child)

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
      child.tree_render()

  def render(self):
    pass
  
  def GetWorldPoint(self, point):
    """
    A slower version of b2Body.GetWorldPoint(), however this doesnt require
    the body to be a real body. Useful for rendering
    """
    xform = b2XForm()
    xform.R.Set(self.body.angle)
    xform.position = self.body.position
    p = b2Mul(xform, point)
    return p

# Avoid circular imports. Game object must be defined before
# importing object factory
import objectfactory

