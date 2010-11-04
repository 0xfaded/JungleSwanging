class Foo(object):
  def __new__(cls, a):
    if a == 0:
      return 'zero'
    else:
      return super(Foo, cls).__new__(cls, a)

  def __init__(self, a):
    self.a = a

  def __str__(self):
    return str(self.a)

print Foo(0)
print Foo(1)
