import sys, getopt, re, glob, os.path, configparser
from rustbots import discord, rcon, oxide
from collections import OrderedDict

class RustMonitor:
    def __init__(self, configPath = ""):
        self.confComments = OrderedDict({'DEFAULT': {'# This is the Default configuration.': None,
                                                     '# New options will be added here on upgrade.': None,
                                                     '# Copy to USER section below and update as necessary.': None},
                                         'USER'   : {'# Enter User Settings Here.': None}})
        self.confDefaults = OrderedDict({'DEFAULT': {'oxide_log_dir':  '~/serverfiles/oxide/logs',
                                                     'oxide_git_url': 'https://api.github.com/repositories/94599577/releases/latest',
                                                     'oxide_check_time_in_min': '15',
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
                                         'USER':    {}})
        self.configFile = os.path.join(configPath, "RustServerAutoUpdate.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.configFile, encoding='utf-8')
        if len(self.config.defaults()) != len(self.confDefaults['DEFAULT']):            
            self.writeDefaultConfig()
            self.config = configparser.ConfigParser()
            self.config.read(self.configFile, encoding='utf-8')
    
        #To preserve comments. Load defaults first, then load user values. Then write file. Then read file directly again without allow_no_value to have clean input to work with.
        #subprocess.run for running shell commands
    def writeDefaultConfig(self):
        """Update INI with default values. Overwrite Defaults, but leave User values in place if they exist"""
        self.config = configparser.ConfigParser(allow_no_value=True)
        userconfig = configparser.ConfigParser()
        userconfig.read(self.configFile, encoding='utf-8')
        self.config.read_dict(self.confComments)
        self.config.read_dict(self.confDefaults)

        if userconfig.has_section('USER'):
            for key,value in userconfig._sections['USER'].items():
                if self.config.has_option('USER', key):
                    self.config['USER'][key] = value
        for (key,value) in userconfig.defaults().items():
            if self.config.has_option(self.config.default_section, key):
                self.config[self.config.default_section][key] = value

        with open(self.configFile, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

#sin = discord.ServerInformation("myGame", "MyServer", "1.1.1.1", "gamercide.org")
#bot = discord.DiscordBot("https://discordapp.com/api/webhooks/280900899868639234/PDlN_4fHnMHhUnolguOR62Ms70IXjRl3Jjdy8SskObE6FA_BIAjpb_eB_C7_kdoDH1Rz", "Botty")
#bot.send_message(sin, "Test from inside Visual Studio")

#rconbot = rcon.RCONBot("abc123", "127.0.0.1", "28016", "Botty")
#rconbot.send_message("say This is a Test from a New bot")