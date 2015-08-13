
from twisted.python import log

import yaml
import os
from sys import exit

def load_config(config_file):
	config_dir = os.path.dirname(config_file)

	if not os.path.exists(config_file):
		if config_dir and not os.path.exists(config_dir):
			os.makedirs(config_dir)
		fh = open(config_file, 'w')
		from util.configexample import example
		fh.write(example)
		fh.close()
		log.msg("Configuration file: '%s' not found." % config_file)
		log.msg("Created example config at '%s'.  Exiting.")
		exit(1)

	conferrors = False
	try:
		conf = yaml.load(open(config_file))
	except yaml.ScannerError:
		log.msg("ERROR: Failed to parse yaml file '%s'." % config_file)
		log.err()
		conferrors = True
	except:
		log.msg("ERROR: Failed to open config file '%s'." % config_file)
		log.err()
		log.msg("Exiting.")
		exit(1)

	if 'twitch' in conf:
		conferrors, twitchconf = validate_twitch(conf['twitch'], conferrors)
		conf['twitch'] = twitchconf
	else:
		log.msg("No twitch settings found in config file '%s'!" % config_file)
		conferrors = True

	if 'ircservers' in conf:
		for name, serverconf in conf['ircservers'].items():
			conferrors, irc_conf = validate_ircserver(name, serverconf, conferrors)
			conf['ircservers'][name] = irc_conf
	else:
		log.msg("No IRC servers found in config file '%s'!" % config_file)
		conferrors = True

	if conferrors:
		log.msg("Configuration errors !!")
		log.msg("Move '%s' out of the way and run pytwitchrelay again to generate an example configuration." % config_file)
		log.msg("Exiting.")
		exit(1)

	return conf

def validate_twitch(conf, conferrors):
	if not 'nickname' in conf:
		log.msg("ERROR: Twitch configuration is missing a nickname!")
		conferrors = True

	if not 'password' in conf:
		log.msg("ERROR: Twitch configuration is missing a password!")
		conferrors = True
	elif not conf['password'].startswith('oauth:'):
		log.msg("ERROR: Twitch configuration's password is not an OAuth token!")
		log.msg("Visit http://www.twitchapps.com/tmi/ to generate an OAuth token for Twitch IRC.")
		conferrrors = True

	if not 'host' in conf:
		log.msg("WARNING: Twitch configuration is missing a host, assuming 'irc.twitch.tv'." % value)
		conf['host'] = 'irc.twitch.tv'
	if not 'port' in conf:
		log.msg("WARNING: Twitch configuration is missing a port, assuming '6667'." % value)
		conf['port'] = '6667'

	if not 'admins' in conf:
		log.msg("No Twitch admins configured, proceeding.")
	if not 'channels' in conf:
		log.msg("No Twitch channels configured, proceeding.")

	return (conferrors, conf)


def validate_ircserver(name, conf, conferrors):
	if not 'nickname' in conf:
		log.msg("ERROR: IRC server '%s' is missing a nickname!" % name)
		conferrors = True
	if not 'host' in conf:
		log.msg("ERROR: IRC server '%s' is missing a host!" % name)
		conferrors = True
	if not 'port' in conf:
		log.msg("WARNING: IRC server '%s' is missing a port, assuming '6667'." % name)
		conf['port'] = '6667'

	if not 'admins' in conf:
		log.msg("No admins configured for IRC server '%s', proceeding." % name)
	if not 'admins' in conf:
		log.msg("No channels configured for IRC server '%s', proceeding." % name)

	return (conferrors, conf)

def load_relay_config(config_file):
	try:
		conf = yaml.load(open(config_file))
	except yaml.ScannerError:
		log.msg("ERROR: Failed to parse relay yaml file '%s'." % config_file)
		log.err()
	except:
		log.msg("ERROR: Failed to open relay config file '%s'." % config_file)
		log.err()
		log.msg("Exiting.")
		exit(1)
	return conf