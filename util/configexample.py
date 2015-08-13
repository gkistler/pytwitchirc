

example = '''# Twitch Settings
twitch:
  channels: ['#twitch_chan1', 'twitch_chan2']
  host: irc.twitch.tv
  nickname: BotNick
  password: oauth: bot_oauth # http://twitchapps.com/tmi/
  port: 6667
  admins: ['twitchuser1', 'twitchuser2']
# IRC Servers
ircservers:
  examplenetwork:
    nickname: example
    channels: ['#example']
    host: irc.example.net
    port: 6667
    admins: ['ircnick1', 'ircnick2']

# Misc settings
relay_config: config/relays.yml
'''