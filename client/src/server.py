# vim:set ts=2 sw=2 et:

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import keymap
import monkey

class Client(object):
  def __init__(self, address):
    self.last_sequence = 0
    self.time_to_live = Server.timeout
    self.keys = keymap.KeyMap()
    self.monkey = monkey.Monkey(self.keys)

    self.address = address

class Server(DatagramProtocol):

  timeout = 30

  def __init__(self, reactor):

    self.active = {}
    self.reactor = reactor
    self.new_monkeys = []
    self.removed_monkeys = []
    
  def datagramReceived(self, data, address):
    if not self.active.has_key(address):
      new_client = Client(address)
      self.new_monkeys.append(new_client.monkey)
      self.active[address] = new_client 

    msg = data.strip().split(',')
    msg.reverse()
    sequence_number = int(msg.pop())

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
        self.removed_monkeys.append(client.monkey)
        del self.active[address]
        continue

      client_id = client.monkey.player_id
      client_tag = str(client_id)+','
      self.transport.write(client_tag + msg, address)

  def shutdown(self):
    self.reactor.fireSystemEvent('shutdown')

# Singleton
Server = Server(reactor)
reactor.listenUDP(8007, Server)
reactor.fireSystemEvent('startup')


