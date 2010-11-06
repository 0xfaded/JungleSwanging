from xml.dom.minidom import parse
from pymunk import Vec2d
import xml

class ParseError(Exception):
  pass

def _parse_point(d):
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

  point = Vec2d(float(digits[0]), float(digits[1]))

  return t, point

def _parse_number(d):
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

def _parse_arc(d):
  tail, r               = _parse_point(d)
  tail, x_axis_rotation = _parse_number(tail)
  tail, large_arc_flag  = _parse_point(tail)
  tail, center          = _parse_point(tail)
  tail, sweep_flag      = _parse_number(tail)
  tail, p               = _parse_point(tail)

  return tail, ArcDef(r, x_axis_rotation, large_arg_flag, center, sweep_flag, p)

def _parse_points(d):
  points = []
  while len(d) > 0 and (not d[0][0].isalpha()):
    d, point = _parse_point(d)
    points.append(point)

  return d, points

def _parse_numbers(d):
  numbers = []
  while len(d) > 0 and (not d[0][0].isalpha()):
    d, number = _parse_number(d)
    numbers.append(number)

  return tail, numbers

def _parse_arcs(d):
  arcs = []
  while len(d) > 0 and (not d[0][0].isalpha()):
    d, arc = _parse_arc(d)
    arcs.append(arc)

  return d, arcs

def _parse_command(d):
  command = d[0][0]
  # If the command is its own distinct token, eg m 1,1, remove the command
  # Otherwise if it is attached to an argument, separate it. eg m1,2
  if command == d[0]:
    tail = d[1:]
  else:
    d[0] = d[0][1:]
    tail = d

  if command.lower() in ['m', 'l', 'q', 't', 'c', 's']:
    tail, args = _parse_points(tail)
  elif command.lower() in ['h', 'v']:
    tail, args = _parse_numbers(tail)
  elif command.lower() in ['a']:
    tail, args = _parse_arcs(tail)
  elif command.lower() in ['z']:
    args = []
  else:
    raise ParseError('Invalid Command: ' + command)

  return tail, (d[0], args)

def _d_string_to_commands(d):
  tokens = d.split() # split on whitespace

  commands = []
  while len(tokens) > 0:
    tokens, command = _parse_command(tokens)
    commands.append(command)

  return commands

class Map(object):
  def read(self, node):
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


    # Find groups for each type of game object
    platforms, grabpoints, bananas = None, None, None
    for g in node.getElementsByTagName('g'):
      if g.attributes['id'].nodeValue == 'platform':
        for path in g.getElementsByTagName('path'):
          print _d_string_to_commands(path.attributes['d'].nodeValue)


if __name__ == '__main__':
  a = Map()
  a.read('map2.svg')

