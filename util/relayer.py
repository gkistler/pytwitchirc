from twisted.python import log


class Relayer:

	def __init__(self):
		self.twitch_proto = None
		self.irc_proto = None
		# Twitch -> [IRC Chans]
		self.relaymap = {}
		self.twitch_to_irc = {}
		self.irc_to_twitch = {}

	def register_twitch(self, protocol):
		if self.twitch_proto is not None:
			log.msg("WARNING: Twitch protocol already registered!")
		self.twitch_proto = protocol

	def register_irc(self, protocol):
		if self.twitch_proto is not None:
			log.msg("WARNING: IRC protocol already registered!")
		self.irc_proto = protocol

	def add_relay(self, twitch_chan, irc_chan):
		if irc_chan not in self.irc_proto.state.channels:
			self.irc_proto.join(irc_chan)
		self.relaymap.setdefault(twitch_chan, []).append(irc_chan)
		self.build_relay_maps()

	def build_relay_maps(self):
		for twitch_chan, ircchans in self.relaymap.items():
			for irc_chan in ircchans:
				self.twitch_to_irc.setdefault(twitch_chan, []).append(irc_chan)
				self.irc_to_twitch[irc_chan] = twitch_chan

	def relay(self, channel, message, label):
		log.msg('%s %s %s' % (channel, message, label))
		from pprint import pprint
		pprint(self.relaymap)
		pprint(self.twitch_to_irc)
		pprint(self.irc_to_twitch)
		if label == 'twitch' and channel in self.twitch_to_irc and self.twitch_to_irc[channel]:
			for ircchan in self.twitch_to_irc[channel]:
				self.irc_proto.sendmsg(ircchan, message)
		# Twitch throttles messages heavily
		# this is a bad idea
		#elif channel in self.irc_to_twitch:
		#	self.twitchproto.sendmsg(self.irc_to_twitch[channel], message)


relayer = Relayer()
