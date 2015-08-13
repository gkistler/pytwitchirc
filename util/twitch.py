# Twisted IRC

from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log
from relayer import Relayer
from helpers import process_hostmask


relayer = Relayer()


class BBMIRCBot(IRCClient):
	"""BBM"""

	def sendLine(self, line):
		IRCClient.sendLine(self, line)
		if self.debug: log.msg('Out:: ' + line)

	def lineReceived(self, line):
		IRCClient.lineReceived(self, line)
		if self.debug: log.msg('In:: ' + line)

	def irc_RPL_WELCOME(self, prefix, params):
		"""
		Called when we have received the welcome from the server.
		"""
		IRCClient.irc_RPL_WELCOME(self, prefix, params)

	def irc_JOIN(self, prefix, params):
		"""
		Called when a user joins a channel.
		"""
		IRCClient.irc_JOIN(self, prefix, params)
		nick, ident, host = process_hostmask(prefix)
		channel = params[0]
		if nick == self.nickname:
			self.state.channels.add(channel)

	def irc_PART(self, prefix, params):
		"""
		Called when a user leaves a channel.
		"""
		IRCClient.irc_PART(self, prefix, params)
		nick, ident, host = process_hostmask(prefix)
		channel = params[0]
		if nick == self.nickname:
			self.state.channels.remove(channel)

	def irc_QUIT(self, prefix, params):
		"""
		Called when a user has quit.
		"""
		IRCClient.irc_QUIT(self, prefix, params)
		#self.state.nukeuser(prefix.split('!')[0])

	def irc_PRIVMSG(self, prefix, params):
		"""
		This will get called when the bot receives a message.
		"""
		nick, ident, host = process_hostmask(prefix)
		channel = params[0]
		message = params[-1]
		print 'PRIVMSG (%s): [[%s]] [[%s]]' % (self.host, nick, message)
		if nick in self.admins and message.startswith('!'):
			cmd = message[1:].split(' ', 1)[0]
			if cmd == 'startrelay':
				if self.state.relay_active:
					self.msg(channel, '%s: Relay already on!' % nick)
					return

				self.msg(channel, '%s: Relay activated.' % nick)
				self.state.relay_active = True
			elif cmd == 'stoprelay':
				if not self.state.relay_active:
					self.msg(channel, '%s: Relay already off!' % nick)
					return
				self.msg(channel, '%s: Relay deactivated.' % nick)
				self.state.relay_active = False
			elif cmd == 'addrelay':
				x = message.split(' ')
				relayer.add_relay(x[1], x[2])
				self.msg(channel, 'Here we go.')
			# Don't relay admin commands
			return
		self.relay(channel, "%s: %s" % (nick, message))


	def irc_NOTICE(self, prefix, params):
		"""
		Called when the bot has received a notice from a user directed to it or a channel.
		"""
		IRCClient.irc_NOTICE(self, prefix, params)
		user = prefix
		channel = params[0]
		message = params[-1]


	def irc_NICK(self, prefix, params):
		"""
		Called when a user changes their nickname.
		"""
		IRCClient.irc_NICK(self, prefix, params)
		nick = prefix.split('!', 1)[0]

	def irc_KICK(self, prefix, params):
		"""
		Called when a user is kicked from a channel.
		"""
		kicker = prefix.split('!')[0]
		channel = params[0]
		kicked = params[1]
		message = params[-1]
		if kicked.lower() == self.nickname.lower():
			self.state.channels.remove(channel)

	def irc_RPL_NAMREPLY(self, prefix, params):
		"""
		Called when NAMES reply is received from the server.
		"""
		print 'NAMES:', params
		channel = params[2]
		users = params[3].split(" ")

	def relay(self, channel, message):
		relayer.relay(channel, message, self.label)

	def connectionMade(self):
		IRCClient.connectionMade(self)
		#reset connection factory delay:
		self.factory.resetDelay()

	def connectionLost(self, reason):
		IRCClient.connectionLost(self, reason)
		log.msg("[%s] Connection lost, unregistering." % self.host)
		relayer.unregister(self)

	# callbacks for events
	def signedOn(self):
		"""Called when bot has succesfully signed on to server."""
		print "[Signed on]"
		IRCClient.signedOn(self)
		for chan in self.channels:
			print 'Joining %s' % chan
			self.join(chan)
		log.msg("[%s] Connection made and all channels joined, registering." % self.label)
		relayer.register(self)

	def sendmsg(self, channel, msg):
		#check if there's hooks, if there is, dispatch, if not, send directly
		self.msg(channel, msg)

	def msg(self, user, msg, length=None):
		msg = msg.encode("utf-8")
		if length:
			IRCClient.msg(self, user, msg, length)
		else:
			IRCClient.msg(self, user, msg)


class BBMTwitchBotFactory(ReconnectingClientFactory):
	"""A factory for BBMBot.
	A new protocol instance will be created each time we connect to the server.
	"""

	# the class of the protocol to build when new connection is made
	protocol = BBMIRCBot

	def __init__(self, label, conf, state):
		#reconnect settings
		self.maxDelay = 45
		self.factor = 1.6180339887498948
		self.channels = conf['channels']
		self.label = label
		self.admins = conf['admins']
		if not isinstance(self.channels, (tuple, list)):
			self.channels = [self.channels]
		self.host = conf['host']
		self.nickname = conf['nickname']
		self.password = None
		self.state = state
		if 'password' in conf:
			self.password = conf['password']

	def buildProtocol(self, address):
		proto = ReconnectingClientFactory.buildProtocol(self, address)
		proto.label = self.label
		proto.nickname = self.nickname
		proto.password = self.password
		proto.channels = self.channels
		proto.admins = self.admins
		proto.network = address
		proto.host = self.host
		proto.relay_active = True
		proto.debug = True
		proto.state = self.state
		proto.identifier = '%s@%s' % (','.join(proto.channels), proto.host)
		return proto