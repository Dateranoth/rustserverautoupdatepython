import sys, getopt, re, glob, os.path, configparser
from rustbots import discord, rcon, oxide
from collections import OrderedDict

class RustMonitor:
    def __init__(self, configPath = '', configSection = 'SERVER1'):
        configSectionUpper = configSection.upper()
        self.setupConfiguration(configPath, configSectionUpper)
        confsec = self.config[configSectionUpper]
        self.oxideLogDIR = confsec['oxide_log_dir']
        self.oxideGitURL = confsec['oxide_git_url']
        self.oxideCheckTime = confsec['oxide_check_time_in_min']
        self.oxideAutoUpdate = self.config.getboolean(configSectionUpper, 'oxide_auto_update')
        self.bashCommand = confsec['bash_get_update_command']
        self.useRCON =  self.config.getboolean(configSectionUpper, 'use_rcon')
        self.useDiscord =  self.config.getboolean(configSectionUpper, 'use_discord')
        self.rconIP = confsec['rcon_ip']
        self.rconPort = confsec['rcon_port']
        self.rconPass = confsec['rcon_pass']
        self.discordWebHook = confsec['discord_webhook']
        self.discordBotName = confsec['discord_bot_name']
        self.discordBotAvatarURL = confsec['discord_bot_avatar_url']
        self.discordMsgGameName = confsec['discord_msg_game_name']
        self.discordMsgServerName = confsec['discord_msg_server_name']
        self.discordMsgServerIP = confsec['discord_msg_server_ip_port']
        self.discordMsgHostName = confsec['discord_msg_server_host_name']
        self.discordMsgTitle = confsec['discord_msg_title']
        self.send15MinWarn =  self.config.getboolean(configSectionUpper, 'send_15min_warn')
        self.send10MinWarn =  self.config.getboolean(configSectionUpper, 'send_10min_warn')
        self.send05MinWarn =  self.config.getboolean(configSectionUpper, 'send_5min_warn')
        self.send01MinWarn =  self.config.getboolean(configSectionUpper, 'send_1min_warn')
        self.msg15Min = confsec['15min_msg']
        self.msg10Min = confsec['10min_msg']
        self.msg05Min = confsec['5min_msg']
        self.msg01Min = confsec['1min_msg']
        #To preserve comments. Load defaults first, then load user values. Then write file. Then read file directly again without allow_no_value to have clean input to work with.
        #subprocess.run for running shell commands
    def setupConfiguration(self, configPath, configSection):
        """Read INI file and update with new options if necessary"""
        confComments = OrderedDict({'DEFAULT': {'# This is the Default configuration.': None,
                                                '# These settings apply to all instances.': None,
                                                '# New options will be added here on upgrade.': None,
                                                '# Copy to appropriate section below and update as necessary.': None,
                                                '# Individual instance settings will override defaults.': None},
                                    configSection   : {'# Enter '+ configSection +' Settings Here.': None}})
        confDefaults = OrderedDict({'DEFAULT': {'oxide_log_dir':  '~/serverfiles/oxide/logs',
                                                'oxide_git_url': 'https://api.github.com/repositories/94599577/releases/latest',
                                                'oxide_check_time_in_min': '15',
                                                'oxide_auto_update': 'yes',
                                                'bash_get_update_command': '~/./rustserver stop | ~/./rustserver mods-update',
                                                'use_rcon': 'yes',
                                                'use_discord': 'yes',
                                                'rcon_ip': '127.0.0.1',
                                                'rcon_port': '28016',
                                                'rcon_pass': 'CHANGE_ME',
                                                'discord_webhook': '',
                                                'discord_bot_name': 'RustPythonBot',
                                                'discord_bot_avatar_url': '',
                                                'discord_msg_game_name': 'My Rust Game',
                                                'discord_msg_server_name': 'My Server',
                                                'discord_msg_server_ip_port': '127.0.0.1:28015',
                                                'discord_msg_server_host_name': '',
                                                'discord_msg_title': '🚧 ALERT',
                                                'send_15min_warn': 'yes',
                                                'send_10min_warn': 'yes',
                                                'send_5min_warn': 'yes',
                                                'send_1min_warn': 'yes',
                                                '15min_msg': 'Oxide Update Detected. Server will restart in 15 minutes for update.',
                                                '10min_msg': 'Oxide Update Scheduled. Server will restart in 10 minutes for update.',
                                                '5min_msg':  'Oxide Update Scheduled. Server will restart in 5 minutes for update.',
                                                '1min_msg':  'FINAL WARNING! SERVER RESTARTING FOR OXIDE UPDATE IN 1 MINUTE!!'},
                                    configSection:    {}})

        configFile = os.path.join(configPath, "rustserverautoupdate.ini")
        userconfig = configparser.ConfigParser()
        userconfig.read(configFile, encoding='utf-8')

        if (len(userconfig.defaults()) != len(confDefaults['DEFAULT'])) or not userconfig.has_section(configSection):
            config = configparser.ConfigParser(allow_no_value=True)            
            config.read_dict(confComments)
            config.read_dict(confDefaults)

            if userconfig.has_section(configSection):
                for key,value in userconfig._sections[configSection].items():
                    if config.has_option(configSection, key):
                        config[configSection][key] = value
            for section in userconfig.sections():
                if section != configSection:
                    config.add_section(section)
                    config[section]['# enter ' + section + ' settings here.'] = None
                    for (key,value) in userconfig._sections[section].items():
                        if config.has_option(section, key):
                            config[section][key] = value
            for (key,value) in userconfig.defaults().items():
                if config.has_option(config.default_section, key):
                    config[config.default_section][key] = value
           
            with open(configFile, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        self.config = configparser.ConfigParser()
        self.config.read_dict(confDefaults)
        self.config.read(configFile, encoding='utf-8')

#sin = discord.ServerInformation("myGame", "MyServer", "1.1.1.1", "gamercide.org")
#bot = discord.DiscordBot("https://discordapp.com/api/webhooks/280900899868639234/PDlN_4fHnMHhUnolguOR62Ms70IXjRl3Jjdy8SskObE6FA_BIAjpb_eB_C7_kdoDH1Rz", "Botty")
#bot.send_message(sin, "Test from inside Visual Studio")

#rconbot = rcon.RCONBot("abc123", "127.0.0.1", "28016", "Botty")
#rconbot.send_message("say This is a Test from a New bot")