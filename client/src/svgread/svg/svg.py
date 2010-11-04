from xml.dom.minidom import parse, parseString
import xml

class SVGElementFactory(object):
  def fromDOM(self, node):
    """Read a node from a dom and return a corresponding SVGElement"""
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

    if node.tagName == SVG.tagName:
      ele = SVG()
    elif node.tagName == Group.tagName:
      ele = Group()
    else:
      return SVG.tagName
      raise NotImplementedError(node.tagName)

    print node.tagName
    ele.read(node)
    return ele

# Singleton
SVGElementFactory = SVGElementFactory()

class SVGElement(object):
  """Base class for all SVG elements"""

  _id = None
  klass = None
  style = None
  externalResourcesRequired = None
  transform = None

  children = []

  def read(self, node):
      self._set_id(node.attributes['id'].nodeValue)
      for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
          self.children.append(SVGElementFactory.fromDOM(child))

  def _set_id(self, id):
    self._id = unicode(id)
  def _get_id(self):
    return self._id

  id = property(_get_id, _set_id)



class SVG(SVGElement):
  """SVG element"""

  _width  = None
  _height = None

  tagName = 'svg'


  def read(self, node):
    if node.nodeType != node.ELEMENT_NODE or node.tagName != self.tagName:
      raise Exeption('expected <{0}> got <1>'.format(self.tagName, node))

    super(SVG, self).read(node)

    self._set_width (node.attributes['width' ].nodeValue)
    self._set_height(node.attributes['height'].nodeValue)

  def _set_width(self, width):
    self._width = float(width)
  def _get_width(self):
    return self._width

  def _set_height(self, height):
    self._height = float(height)
  def _get_height(self):
    return self._height

  width  = property(_get_width  ,_set_width )
  height = property(_get_height ,_set_height)



class Group(SVGElement):
  """The svg Group element"""
  tagName = 'g'

  def read(self, node):
    super(Group, self).read(node)
    if node.nodeType != node.ELEMENT_NODE or node.tagName != self.tagName:
      raise Exeption('expected <{0}> got <1>'.format(self.tagName, node))


class SVGShape(SVGElement):
  """Abstract class for all Shape SVG objects"""

  def read(self, node):
    super(Group, self).read(node)
    if node.nodeType != node.ELEMENT_NODE or node.tagName != self.tagName:
      raise Exeption('expected <{0}> got <1>'.format(self.tagName, node))



if __name__ == '__main__':
  svg_dom = parse('map2.svg')
  a = SVGElementFactory.fromDOM(svg_dom)

