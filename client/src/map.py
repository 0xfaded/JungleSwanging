from xml.dom.minidom import parse
from Box2D import *
import xml
from platform import *
from powerup import *
from grab import *
from monkey import *

from bezieredge import *

class ParseError(Exception):
  pass

class Map(GameObject):
  platforms = []
  powerups = []
  grabpoints = []
  monkeys = []

  def __init__(self, parent):
    super(Map, self).__init__(parent)


  def add_to_world(self, world, contact_listener, at):
    for platform in self.platforms:
      platform.add_to_world(world, contact_listener, at)
    for powerup in self.powerups:
      powerup.add_to_world(world, contact_listener, powerup.get_start())
    for grabpoint in self.grabpoints:
      grabpoint.add_to_world(world, contact_listener, grabpoint.get_start())
    for monkey in self.monkeys:
      monkey.add_to_world(world, contact_listener, monkey.get_start())


  def read(self, node):
    powerup1 = PowerUp(self,0.25)
    powerup1.set_start((1.5,6))
    self.powerups.append(powerup1)

    grab1 = Grab(self, 3)
    grab1.set_start((17,-6))
    self.grabpoints.append(grab1)

    monkey1 = Monkey(self)
    monkey1.set_start((0,3))
    self.monkeys.append(monkey1)

    """Read a map from an svg file"""
    # If we were passed a string, read it as a file
    if isinstance(node, str):
      node = parse(node)

    # If we were passed a full DOM Document instead of just
    # the an element, search for the svg element and use it
    if isinstance(node, xml.dom.minidom.Document):
      svgs = node.getElementsByTagName('svg')
      if len (svgs) != 1:
        raise Exeption('svg dom must have exactly 1 <svg> element')
      node = svgs[0]

    if node.nodeType != node.ELEMENT_NODE:
      raise Exception('Only ELEMENT_NODE\'s can be read as SVGElements')

    # Top of the transform stack. Since the scale is 1:100, start with this
    transform = b2Mat33()
    transform.SetZero()
    transform.col1.x = 0.01
    transform.col2.y = -0.01

    transform.col3.y = 10
    transform.col3.z = 1

    self.platforms.append(_make_bounds_from_svg(node, transform))

    for g in node.getElementsByTagName('g'):
      self.platforms.extend(_handle_group(g, transform))


#################################################################

def _handle_group(node, transform):
  #tmat = _parse_transform(node.attributes['transform'].value)
  #transform = _mat33mul(transform, tmat)

  ret = []
  for path in node.getElementsByTagName('path'):
    ret.append(_make_shape_from_path(path, transform))

  return ret

def _make_shape(node, transform):
  type = node.value
  print type

def _make_shape_from_path(node, transform):
  tokens = _tokenize_d(node.attributes['d'].nodeValue)
  is_loop, points = _parse_d(tokens)

  points = _apply_transform(points, transform)

  if not _is_counter_clockwise(points):
    points.reverse()

  return Platform(points)

def _make_bounds_from_svg(node, transform):
  w = float(node.attributes['width' ].value)
  h = float(node.attributes['height'].value)

  points = [b2Vec2(0,0), b2Vec2(w, 0), b2Vec2(w, h), b2Vec2(0,h)]
  points = _apply_transform(points, transform)

  # Note we want this wrapped such that we are on the inside
  if _is_counter_clockwise(points):
    points.reverse()

  return Platform(points)

def _is_counter_clockwise(points):
  # Do the wrap around first
  area = b2Cross(points[-1], points[0])
  for i in xrange(len(points) - 1):
    area += b2Cross(points[i], points[i+1])

  return area >= 0

def _parse_d(tokens):
  # First command must be M. I didnt bother checking for this
  points = []
  is_loop = False
  for command, params in tokens:
    if command.lower() == 'm':
      _parse_m(command, params, points)
    elif command.lower() == 'l':
      _parse_l(command, params, points)
    elif command.lower() == 'h':
      params = map(lambda x: b2Vec2(x, 0), params)
      _parse_l(command, params, points)
    elif command.lower() == 'v':
      params = map(lambda y: b2Vec2(0, y), params)
      _parse_l(command, params, points)
    elif command.lower() == 'c':
      _parse_c(command, params, points)
    elif command.lower() == 'z':
      is_loop = True
    else:
      raise NotImplementedError('"{0}" not implemented'.format(command))

  return is_loop, points

def _parse_m(command, params, points):
  absolute = command.isupper()
  for param in params:
    if absolute or len(points) == 0:
      points.append(param)
    else:
      points.append(points[-1] + param)

def _parse_l(command, params, points):
  absolute = command.isupper()
  for param in params:
    if absolute:
      points.append(param)
    else:
      points.append(points[-1] + param)

def _parse_c(command, params, points):
  absolute = command.isupper()
  for i in xrange(0, len(params), 3):
    # read p1~3
    p = params[i:i+3]
    if not absolute:
      p = map(lambda x: points[-1] + x, p)


    # p0 = last point
    p.insert(0, points[-1])

    b_points = calculate_bezier(p, 30)

    # Remove first point from the bezier, as it is already
    # represented in points. Then convert them into b2Vec2
    b_points = map(lambda x: b2Vec2(x), b_points[1:])

    points.extend(b_points)


def _tokenize_d(d):
  tokens = d.split() # split on whitespace

  commands = []
  while tokens:
    tokens, command = _tokenize_d_command(tokens)
    commands.append(command)

  return commands

def _tokenize_point(d):
  t = d
  digits = t[0].split(',')
  t = t[1:]

  if len(digits) == 1:
    if t[0] == ',':
      t = t[1:]
    elif t[0].startswith(','):
      t[0][0] = t[0][1:]
    else:
      raise ParseError('Invalid Point: ' + str(d))

    digits.append(t[0])
    t = t[1:]

  if len(digits) != 2:
    raise ParseError('Invalid Number: ' + str(d))

  point = b2Vec2(float(digits[0]), float(digits[1]))

  return t, point

def _tokenize_number(d):
  number = float(d[0])

  return d[1:], number

class ArcDef(object):
  def __init__(r, x_axis_rotation, large_arc_flag, center, sweep_flag, p):
    self.r               = r
    self.x_axis_rotation = x_axis_rotation
    self.large_arc_flag  = large_arc_flag
    self.center          = center
    self.sweep_flag      = sweep_flag
    self.p               = p

def _tokenize_arc(d):
  tail, r               = _tokenize_point(d)
  tail, x_axis_rotation = _tokenize_number(tail)
  tail, large_arc_flag  = _tokenize_point(tail)
  tail, center          = _tokenize_point(tail)
  tail, sweep_flag      = _tokenize_number(tail)
  tail, p               = _tokenize_point(tail)

  return tail, ArcDef(r, x_axis_rotation, large_arg_flag, center, sweep_flag, p)

def _tokenize_points(d):
  points = []
  while len(d) > 0 and (not d[0][0].isalpha()):
    d, point = _tokenize_point(d)
    points.append(point)

  return d, points

def _tokenize_numbers(d):
  numbers = []
  while len(d) > 0 and (not d[0][0].isalpha()):
    d, number = _tokenize_number(d)
    numbers.append(number)

  return tail, numbers

def _tokenize_arcs(d):
  arcs = []
  while len(d) > 0 and (not d[0][0].isalpha()):
    d, arc = _tokenize_arc(d)
    arcs.append(arc)

  return d, arcs

def _tokenize_d_command(d):
  command = d[0][0]
  # If the command is its own distinct token, eg m 1,1, remove the command
  # Otherwise if it is attached to an argument, separate it. eg m1,2
  if command == d[0]:
    tail = d[1:]
  else:
    d[0] = d[0][1:]
    tail = d

  if command.lower() in ['m', 'l', 'q', 't', 'c', 's']:
    tail, args = _tokenize_points(tail)
  elif command.lower() in ['h', 'v']:
    tail, args = _tokenize_numbers(tail)
  elif command.lower() in ['a']:
    tail, args = _tokenize_arcs(tail)
  elif command.lower() in ['z']:
    args = []
  else:
    raise ParseError('Invalid Command: ' + command)

  return tail, (d[0], args)

def _parse_transform(transform):
  # Ensure the brackets are split into individual tokens by padding spaces
  transform = transform.replace('(', ' ( ')
  transform = transform.replace(')', ' ) ')
  # Treat commas as spaces. This is so ugly
  transform = transform.replace(',', ' ')
  tokens = transform.split() # split on whitespace

  mats = []
  while tokens:
    tokens, mat = _parse_transform_command(tokens)
    mats.append(mat)

  mats.reverse() # Matrix multiplication is performed in reverese

  mat = b2Mat33()
  # mat.SetIdentity() isnt defined ??
  mat.SetZero()
  mat.col1.x, mat.col2.y, mat.col3.z = 1,1,1

  mat = reduce(lambda x,y: _mat33mul(x,y), mats, mat)

  return mat

def _parse_transform_command(tokens):
  command = tokens[0]
  if command.lower() == 'translate':
    tokens, mat = _parse_translate(tokens[1:])

  else:
    raise NotImplementedError('{0} transform not implemented'.format(d[0]))

  return tokens[1:], mat

def _parse_translate(tokens):
  print tokens
  if tokens[0] != '(':
    raise Exception('Expected ''(''')

  tokens, x = _tokenize_number(tokens[1:])

  if tokens[0] == ')':
    y = 0
  else:
    tokens, y = _tokenize_number(tokens)

  if tokens[0] != ')':
    raise Exception('Expected '')''')

  xform = b2XForm()
  xform.position.x, xform.position.y = x,y
  xform.R.SetIdentity()

  mat = _xform_to_mat33(xform)

  return tokens[1:], mat


# I dont know why box2d doesnt already have these, but I couldnt find them
def _xform_to_mat33(xform):
  ret = b2Mat33()
  ret.SetZero()
  ret.col1.x = xform.R.col1.x
  ret.col1.y = xform.R.col1.y
  ret.col2.x = xform.R.col2.x
  ret.col2.y = xform.R.col2.y

  ret.col3.x = xform.position.x
  ret.col3.y = xform.position.y

  ret.col3.z = 1

  return ret

def _mat33_to_xform(mat33):
  ret = b2XForm()

  ret.R.col1.x   = mat33.col1.x
  ret.R.col1.y   = mat33.col1.y
  ret.R.col2.x   = mat33.col2.x
  ret.R.col2.y   = mat33.col2.y

  ret.position.x = mat33.col3.x
  ret.position.y = mat33.col3.y

  return ret

def _mat33mul(m1, m2):
  r = b2Mat33()

  r.col1.x = m1.col1.x*m2.col1.x + m1.col2.x*m2.col1.y + m1.col3.x*m2.col1.z
  r.col1.y = m1.col1.y*m2.col1.x + m1.col2.y*m2.col1.y + m1.col3.y*m2.col1.z
  r.col1.z = m1.col1.z*m2.col1.x + m1.col2.z*m2.col1.y + m1.col3.z*m2.col1.z

  r.col2.x = m1.col1.x*m2.col2.x + m1.col2.x*m2.col2.y + m1.col3.x*m2.col2.z
  r.col2.y = m1.col1.y*m2.col2.x + m1.col2.y*m2.col2.y + m1.col3.y*m2.col2.z
  r.col2.z = m1.col1.z*m2.col2.x + m1.col2.z*m2.col2.y + m1.col3.z*m2.col2.z

  r.col3.x = m1.col1.x*m2.col3.x + m1.col2.x*m2.col3.y + m1.col3.x*m2.col3.z
  r.col3.y = m1.col1.y*m2.col3.x + m1.col2.y*m2.col3.y + m1.col3.y*m2.col3.z
  r.col3.z = m1.col1.z*m2.col3.x + m1.col2.z*m2.col3.y + m1.col3.z*m2.col3.z

  return r

def _apply_transform(points, mat33):
  xform = _mat33_to_xform(mat33)
  return map(lambda x: b2Mul(xform, x), points)

if __name__ == '__main__':
  a = Map()
  a.read('bezier_test_map.svg')
