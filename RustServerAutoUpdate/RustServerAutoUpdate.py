import sys, getopt, re, glob, os.path, configparser
from rustbots import discord, rcon, oxide
#Variables needed for methods
#rcon: password, ip = "127.0.0.1", port = "28016", botName = "RustPythonBot"
#discord: webHook, botName, botAvatar = ""
#discord: gameName, serverName, serverIP, serverHostName = ""
#discord/rcon: Message, title = "🚧 ALERT" (how many, which notifications?)
#oxide: oxideLogDir, gitURL = "https://api.github.com/repositories/94599577/releases/latest"

class RustMonitor:
    def __init__(self, configPath = ""):
        self.configFile = os.path.join(configPath, "RustServerAutoUpdate.ini")
        self.config = configparser.ConfigParser(allow_no_value=True)
        if len(self.config.read(self.configFile)) == 0:
            self.writeDefaultConfig()
        self.readConfigFile()

    def writeDefaultConfig(self):
        self.config.read_dict({'DEFAULT': {'# This is the Default configuration.': None,
                                           '# New options will be added here on upgrade.': None,
                                           '# Place user options in [USER] section below.': None,
                                           'serverIP': '127.0.0.1',
                                           'rconPort': '28016'},
                               'USER'   : {'# Enter User Settings Here.': None,
                                           'serverip': '127.0.0.1',
                                           'rconport': '28016'}})
        with open(self.configFile, 'w') as configfile:
            self.config.write(configfile)

    def readConfigFile(self):
        for each_section in self.config.sections():
            for (each_key, each_val) in selif.config.items(each_section):
                print(each_key)
                print(each_val)

sin = discord.ServerInformation("myGame", "MyServer", "1.1.1.1", "gamercide.org")
bot = discord.DiscordBot("https://discordapp.com/api/webhooks/280900899868639234/PDlN_4fHnMHhUnolguOR62Ms70IXjRl3Jjdy8SskObE6FA_BIAjpb_eB_C7_kdoDH1Rz", "Botty")
bot.send_message(sin, "Test from inside Visual Studio")

rconbot = rcon.RCONBot("abc123", "127.0.0.1", "28016", "Botty")
rconbot.send_message("say This is a Test from a New bot")