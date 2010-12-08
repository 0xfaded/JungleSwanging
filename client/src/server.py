# vim:set ts=2 sw=2 et:

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import keymap

class Client(object):
  def __init__(self, address):
    self.last_sequence = 0
    self.time_to_live = Server.timeout
    self.keys = keymap.KeyMap()

    self.address = address

class Server(DatagramProtocol):

  timeout = 30

  def __init__(self, reactor):

    self.active = {}
    self.reactor = reactor
    
  def datagramReceived(self, data, address):
    if not self.active.has_key(address):
      self.active[address] = Client(address)

    msg = data.strip().split(',')
    msg.reverse()
    sequence_number = msg.pop()

    client = self.active[address]

    if sequence_number > client.last_sequence:
      client.last_sequence = sequence_number
      client.time_to_live = self.timeout

      client.keys.from_network(msg)


  def iterate(self, step=0):
    self.reactor.iterate(step)

  def broadcast(self, msg):
    for address in list(self.active):
      client = self.active[address]
      client.time_to_live -= 1

      if client.time_to_live == 0:
        del self.active[address]
        continue

      self.transport.write(msg, address)

  def shutdown(self):
    self.reactor.fireSystemEvent('shutdown')

# Singleton
Server = Server(reactor)
reactor.listenUDP(8007, Server)
reactor.fireSystemEvent('startup')


