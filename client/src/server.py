# vim:set ts=2 sw=2 et:

#class Server(object):

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

class MonkeyProtocol(Protocol):

  def connectionMade(self):
    self.factory.active[id(self)] = self

  def connectionLost(self):
    del self.factory.active[id(self)]

     

class Server (Factory):

  protocol = MonkeyProtocol

  def __init__(self, reactor):

    self.pendingConnects = []
    self.pendingDisconnects = []
    self.active = {}

    self.reactor = reactor
    
  def iterate(self, step=0):
    self.reactor.iterate(step)

  def broadcast(self, msg):
    for connection in self.active.values():
      print connection
      connection.transport.write(msg)

# Singleton
Server = Server(reactor)
reactor.listenTCP(8007, Server)

