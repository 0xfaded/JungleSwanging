from xml.dom.minidom import parse
import xml

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
          print path.attributes['d'].nodeValue


if __name__ == '__main__':
  a = Map()
  a.read('map2.svg')

