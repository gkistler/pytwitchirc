import yaml

# twisted imports
import argparse
from util.irc import BBMIRCBotFactory
from util.twitch import BBMTwitchBotFactory
from util.configparser import load_config
from util.state import State
from twisted.internet import reactor
import os
import os.path
from sys import exit, stdout
from twisted.python import log


if __name__ == '__main__':
	state = State()
	cwdu = os.getcwdu()
	logpath = os.path.join(cwdu, 'logs')
	if not os.path.exists(logpath):
		os.mkdir(logpath)
	logfile = os.path.join(logpath, "twitch_relayer.log")
	parser = argparse.ArgumentParser(prog='pytwitchrelay')
	parser.add_argument("-c", "--config", type=str, help="primary config file location",
						default="config/twitch_relayer.yml")
	args = parser.parse_args()
	log.startLogging(stdout)
	log.addObserver(log.FileLogObserver(open(logfile, 'a')).emit)

	log.msg("Starting relayBort, logging to: '%s'" % logfile)

	conf = load_config(args.config)
	log.msg("Successfully loaded config file '%s'!" % args.config)

	log.msg('Initiating connection to twitch, channels (%s)' % conf['twitch']['channels'])
	reactor.connectTCP(conf['twitch']['host'], conf['twitch']['port'], BBMTwitchBotFactory('twitch', conf['twitch'], state))

	for label, config in conf['ircservers'].items():
		log.msg('Initiating IRC server connection (%s - %s:%s (%s))' % (label, config['host'], config['port'], ','.join(config['channels'])))
		reactor.connectTCP(config['host'], config['port'], BBMIRCBotFactory(label, config, state))
	log.msg('???')
	reactor.run()
