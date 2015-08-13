from twisted.python import log

class Communicator:
	def __init__(self):
		self.twitchproto = None
		self.ircproto = None

	def register(self, protocol):
		if protocol.label == 'twitch':
			if self.twitchproto is not None:
				log.msg("WARNING: Twitch protocol already registered!")
		else:
			self.ircproto = protocol

	def relay(self, protocol, message):
		if not protocol.relay_active:
			return
		for target_proto in self.instances:
			if target_proto == protocol:
				continue
			for channel in target_proto.channels:
				target_proto.sendmsg(channel, message)