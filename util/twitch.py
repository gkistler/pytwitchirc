# Twisted Twitch

from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log


class BBMTwitchBot(IRCClient):
	"""BBM"""

	def sendLine(self, line):
		IRCClient.sendLine(self, line)
		print 'Out:: ' + line

	def lineReceived(self, line):
		IRCClient.lineReceived(self, line)
		print 'In:: ' + line

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
		nick = prefix.split('!')[0]
		channel = params[-1]

	def irc_PART(self, prefix, params):
		"""
		Called when a user leaves a channel.
		"""
		IRCClient.irc_PART(self, prefix, params)
		nick = prefix.split('!')[0]
		channel = params[-1]

	def irc_QUIT(self, prefix, params):
		"""
		Called when a user has quit.
		"""
		print prefix, params
		IRCClient.irc_QUIT(self, prefix, params)
		#self.state.nukeuser(prefix.split('!')[0])
		dispatch(self, Event("userQuit", prefix, params, hostmask=prefix))

	def irc_PRIVMSG(self, prefix, params):
		"""
		This will get called when the bot receives a message.
		"""
		user = prefix
		channel = params[0]
		message = params[-1]
		self.relay("%s: %s" % (user, message))


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
		IRCClient.irc_NICK(self, prefix, params)
		kicker = prefix.split('!')[0]
		channel = params[0]
		kicked = params[1]
		message = params[-1]


	def irc_RPL_NAMREPLY(self, prefix, params):
		"""
		Called when NAMES reply is received from the server.
		"""
		print 'NAMES:', params
		channel = params[2]
		users = params[3].split(" ")

	def relay(self, message):
		communicator.relay(self, message)

	def connectionMade(self):
		IRCClient.connectionMade(self)
		log.msg("[%s] Connection made, registering." % self.network)
		communicator.register(self)
		#reset connection factory delay:
		self.factory.resetDelay()

	def connectionLost(self, reason):
		IRCClient.connectionLost(self, reason)
		log.msg("[%s] Connection lost, unregistering." % self.network)
		communicator.unregister(self)

	# callbacks for events

	def signedOn(self):
		"""Called when bot has succesfully signed on to server."""
		print "[Signed on]"
		IRCClient.signedOn(self)
		for chan in self.channels:
			print 'Joining %s' % chan
			self.join(chan)


	def sendmsg(self, channel, msg):
		#check if there's hooks, if there is, dispatch, if not, send directly
		self.msg(channel, msg)

	#overriding msg
	# need to consider dipatching this event and allow for some override somehow
	# TODO: need to do some funky UTF-8 length calculation. Most naive one would be to keep adding a
	#	character so like for char in msg: t += char if len(t.encode("utf-8")) > max: send(old) else: old = t
	#	or something... google or stackoverflow I guess WORRY ABOUT THIS LATER THOUGH
	def msg(self, user, msg, length=None):
		msg = msg.encode("utf-8")
		if length: IRCClient.msg(self, user, msg, length)
		else: IRCClient.msg(self, user, msg)


class BBMTwitchBotFactory(ReconnectingClientFactory):
	"""A factory for BBMBot.
	A new protocol instance will be created each time we connect to the server.
	"""

	# the class of the protocol to build when new connection is made
	protocol = BBMTwitchBot

	def __init__(self, serversettings):
		#reconnect settings
		self.maxDelay = 45
		self.factor = 1.6180339887498948
		self.channels = serversettings['channels']
		print 'test__init__'

	def buildProtocol(self, address):
		proto = ReconnectingClientFactory.buildProtocol(self, address)
		proto.nickname = 'testbort'
		proto.channels = self.channels
		proto.network = address
		proto.identifier = '%s@%s' % (','.join(proto.channels), proto.network)
		return proto