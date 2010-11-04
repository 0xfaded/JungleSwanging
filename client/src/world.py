# vim:set sw=2 ts=2 sts=2 et:

import renderable

class World(renderable.Renderable):
  def __init__(self):
    self.monkeys = []
    self.jungle = None

  def add_monkey(self, monkey):
    self.monkeys.append(monkey)

  def set_jungle(self, jungle):
    self.jungle = jungle

  def render(self):
    self.jungle.render()

    for monkey in self.monkeys:
      monkey.render()

