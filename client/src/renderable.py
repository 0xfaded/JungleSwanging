# vim:set ts=2 sw=2 et:
class Renderable(object):
  def __init__(self):
    super(Renderable, self).__init__()
  def render(self):
    raise NotImplementedError()
