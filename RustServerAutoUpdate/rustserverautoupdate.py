#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, signal, getopt, re, glob, os.path, configparser, asyncio, random
from rustbots import discord, rcon, oxide
from collections import OrderedDict
from time import sleep
from subprocess import run
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from datetime import datetime, timedelta, timezone

class RustMonitor:
    def __init__(self, configPath = '', configSection = 'SERVER1'):
        configSectionUpper = configSection.upper()
        self.setup_configuration(configPath, configSectionUpper)
        confsec = self.config[configSectionUpper]
        self.oxideLogDIR = confsec['oxide_log_dir']
        self.oxideGitURL = confsec['oxide_git_url']
        self.oxideCheckTime = self.config.getfloat(configSectionUpper, 'oxide_check_time_in_min')
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

    def setup_configuration(self, configPath, configSection):
        """Read INI file and update with new options if necessary"""
        confComments = OrderedDict({'DEFAULT': {'# This is the Default configuration.': None,
                                                '# These settings apply to all instances.': None,
                                                '# New options will be added here on upgrade.': None,
                                                '# Copy to appropriate section below and update as necessary.': None,
                                                '# Individual instance settings will override defaults.': None},
                                    configSection   : {'# Enter '+ configSection +' Settings Here.': None}})
        confDefaults = OrderedDict({'DEFAULT': {'oxide_log_dir':  '/home/rustserver/serverfiles/oxide/logs',
                                                'oxide_git_url': 'https://api.github.com/repositories/94599577/releases/latest',
                                                'oxide_check_time_in_min': '15',
                                                'oxide_auto_update': 'yes',
                                                'bash_get_update_command': '/home/rustserver/./rustserver stop;/home/rustserver/./rustserver update;/home/rustserver/./rustserver mods-update;/home/rustserver/./rustserver start',
                                                'use_rcon': 'yes',
                                                'use_discord': 'no',
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

    def check_variables(self, case):
        """Check variables to confirm they will not cause errors.
           Fill in generic defaults if non-required variables are empty."""
        if case == 1:
            if not self.discordWebHook.strip():
                raise RustMonitorVariableError('discord_webhook', 'Discord Bot is enabled, but no webHook was provided.')
            else:
                self.disdiscordWebHook = self.discordWebHook.strip()
            if not self.discordBotName.strip():
                self.discordBotName = 'Unknown Bot'
            if not self.discordBotAvatarURL.strip():
                self.discordBotAvatarURL = ""
            if not self.discordMsgGameName.strip():
                self.discordMsgGameName = 'Unkown Game'
            if not self.discordMsgServerName.strip():
                self.discordMsgServerName = 'Unknown Server'
            if not self.discordMsgServerIP.strip():
                self.discordMsgServerIP = '127.0.0.1'
            if not self.discordMsgHostName.strip():
                self.discordMsgHostName = ""
        elif case == 2:
            if not self.rconIP.strip():
                raise RustMonitorVariableError('rcon_ip', 'RCON is Enabled, but no IP was provided')
            else:
                self.rconIP = self.rconIP.strip()
            if not self.rconPort.strip():
                raise RustMonitorVariableError('rcon_port', 'RCON is Enabled, but no Port was provided')
            else:
                self.rconPort = self.rconPort.strip()
            if not self.rconPass.strip():
                raise RustMonitorVariableError('rcon_pass', 'RCON is Enabled, but no Password was provided')
            else:
                self.rconPass = self.rconPass.strip()
            if not self.rconBotName.strip():
                self.discordBotName = 'Unknown Bot'
    def send_msgs(self, msg):
        """Containted method to send messages to both discord and RCON"""
        #TODO: Add logging to exception messages.
        if self.useDiscord:
            try:
                self.discordBot.send_message(self.serverinfo, msg, self.discordMsgTitle)
            except Exception as ex:
                print(ex)
        if self.useRCON:
            try:
                self.rconBot.send_message('say ' + msg)
            except Exception as ex:
                print(ex)
    def kick_save(self):
        """Containted method to kick players and save before restart."""
        #TODO: Add logging to exception messages.
        if self.useRCON:
            try:
                self.rconBot.send_message('kickall "" "Server Restarting"')
                self.rconBot.send_message('server.save')
            except Exception as ex:
                print(ex)

    def wipe_check(self):
        timeZN = timezone(timedelta(hours=0))
        tm = datetime.now(timeZN).timetuple()
        if tm.tm_mday <= 7 and tm.tm_wday == 3:
            #TODO: Setup INI variable for storing the previous wipe date
            lastwipedatetimestr = "2021-01-12 20:43:18.267496+00:00"
            previousdatetime = datetime.strptime(lastwipedatetimestr, '%Y-%m-%d %H:%M:%S.%f%z')
            mindaysbetweenwipe = timedelta(days=27)
            if datetime.now(timeZN) >= (previousdatetime + mindaysbetweenwipe):
                newseed = random.randrange(1, 2147483647, 1)
                currentwipedt = datetime.now(timeZN)
                #TODO: Save Current Seed. Write New Seed. Write Last wipe time. Trigger restart
                return

    async def update_loop(self):
        self.stop = False
        timeZN = timezone(timedelta(hours=0))
        loopCycleTime = timedelta(minutes=self.oxideCheckTime)
        loopStartTime = datetime.now(timeZN)
        loopStart = True
        updateNeeded = False
        while not self.stop:
            if ((datetime.now(timeZN) >= (loopStartTime + loopCycleTime)) or loopStart) and not updateNeeded:
                response = self.oxideBot.check_update()
                if response[0]:
                    print("Found New Version: " + response[3] + " Old Version: " + response[2])
                    updateNeeded = True
                else:
                    #self.send_msgs("Oxide Up to Date: " + response[2])
                    print("Oxide Up to Date: " + response[2])
                loopStartTime = datetime.now(timeZN)
                messageWaitTime = timedelta(minutes=0)
            if updateNeeded and not loopStart:
                if send15 and (datetime.now(timeZN) >= (loopStartTime + messageWaitTime)):
                    print("Sending 15 Minute Warning")
                    with ThreadPoolExecutor() as executor:
                        await self.loop.run_in_executor(executor, self.send_msgs, self.msg15Min)
                    send15 = False
                    loopStartTime = datetime.now(timeZN)
                    messageWaitTime = timedelta(minutes=15)
                elif send10 and (datetime.now(timeZN) >= (loopStartTime + (messageWaitTime - timedelta(minutes=10)))):
                    print("Sending 10 Minute Warning")
                    with ThreadPoolExecutor() as executor:
                        await self.loop.run_in_executor(executor, self.send_msgs,self.msg10Min)
                    send10 = False
                    loopStartTime = datetime.now(timeZN)
                    messageWaitTime = timedelta(minutes=10)
                elif send05 and (datetime.now(timeZN)  >= (loopStartTime + (messageWaitTime - timedelta(minutes=5)))):
                    print("Sending 5 Minute Warning")
                    with ThreadPoolExecutor() as executor:
                        await self.loop.run_in_executor(executor, self.send_msgs, self.msg05Min)
                    send05 = False
                    loopStartTime = datetime.now(timeZN)
                    messageWaitTime = timedelta(minutes=5)
                elif send01 and (datetime.now(timeZN)  >= (loopStartTime + (messageWaitTime - timedelta(minutes=1)))):
                    print("Sending 1 Minute Warning")
                    with ThreadPoolExecutor() as executor:
                        await self.loop.run_in_executor(executor, self.send_msgs, self.msg01Min)
                    send01 = False
                    loopStartTime = datetime.now(timeZN)
                    messageWaitTime = timedelta(minutes=1)
                elif autoUpdate and (datetime.now(timeZN) >= (loopStartTime + messageWaitTime)) and not (send01 or send05 or send10 or send15):
                    print("Updating Oxide")
                    with ThreadPoolExecutor() as executor:
                        print(self.bashCommand)
                        await self.loop.run_in_executor(executor, self.kick_save)
                        await self.loop.run_in_executor(executor, partial(run, self.bashCommand, shell=True, universal_newlines=True))                    
                    autoUpdate = False
                elif not (send01 or send05 or send10 or send15 or autoUpdate):
                    print("Reset Update Check")
                    updateNeeded = False
                    #Using LinuxGSM the shell will return and the game starts up in a separate thread. Need to wait for the game to start so that the logs load.
                    #Could probably do this a different way, but for now, I think this is the best option. 
                    #It's unlikely another update would come through in 20 minutes. So this will be 20 minutes + the delay set by the user.
                    loopStartTime = datetime.now(timeZN) + timedelta(minutes=20)
            else:
                if self.send15MinWarn:
                    send15 = True
                else:
                    send15 = False
                if self.send10MinWarn:
                    send10 = True
                else:
                    send10 = False
                if self.send05MinWarn:
                    send05 = True
                else:
                    send05 = False
                if self.send01MinWarn:
                    send01 = True
                else:
                    send01 = False
                if self.oxideAutoUpdate:
                    autoUpdate = True
                else:
                    autoUpdate = False
            loopStart = False
            await asyncio.sleep(1)

    def main(self):
        if not self.oxideAutoUpdate and not self.useDiscord and not self.useRCON:
            raise RustMonitorVariableError('oxide_auto_update', 'Oxide Auto Update, Discord, and RCON are all disabled. There is nothing for this program to do.')
        if self.useDiscord:
            self.check_variables(1)
            self.serverinfo = discord.ServerInformation(self.discordMsgGameName, self.discordMsgServerName, self.discordMsgServerIP, self.discordMsgHostName)
            self.discordBot = discord.DiscordBot(self.discordWebHook, self.discordBotName, self.discordBotAvatarURL)
        if self.useRCON:
            self.rconBotName = self.discordBotName
            self.check_variables(2)
            self.rconBot = rcon.RCONBot(self.rconPass, self.rconIP, self.rconPort, self.rconBotName)
        self.oxideBot = oxide.UpdateCheck(self.oxideLogDIR, self.oxideGitURL)
        self.loop = asyncio.get_event_loop()
        tasks = asyncio.gather(self.update_loop())
        try:
            self.loop.run_until_complete(tasks)
        except GracefulExit:
            self.stop = True
            tasks.add_done_callback(lambda t: self.loop.stop())
            tasks.cancel()
            while not tasks.done() and not self.loop.is_closed():
                self.loop.run_forever()
            tasks.exception()

class RustMonitorVariableError(Exception):
    def __init__(self, variable, msg):
        self.variable = variable
        self.msg = msg

class GracefulExit(Exception):
    pass

def signal_handler(signum, frame):
    print("\nStopping Rust Server Auto Update")
    raise GracefulExit()

def argumenthelp():
    print("\nSyntax: rustserverautoupdate.py -c <Path to Configuration INI> [-s <Section Name - Used for multiple instances>]\n"
          "Example: rustserverautoupdate.py -c \home\rustserver\rustserverautoupdate -s SERVER1\n"
          "\n"
          "Check for updates. Return Space Separated String Array (Boolean update url, updatestring, runningversion, latestversion)\n\n"
          "REQUIRED INPUT - CHOOSE ONE:\n"
          "-c --configpath   Path where Configuration File is Stored. MUST HAVE R.\n"
          "OPTIONAL INPUT:\n"          
          "-s --section       Section Name for configuration. This allows for multiple instances to be ran from same configuration.\n")
def main(argv):
    configPath = os.path.dirname(os.path.realpath(__file__))
    sectionName = ""
    try:
        opts, args = getopt.getopt(argv,"hc:s:",["help", "configpath=", "section="])
    except getopt.GetoptError as err:
        print("Incorrect Syntax: -h or --help for more information")
        print("rustserverautoupdate.py -c <Path to Configuration INI> [-s <Section Name - Used for multiple instances>]\n")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            argumenthelp()
            sys.exit()
        elif opt in ("-c", "--configpath"):
            configPath = arg
        elif opt in ("-s", "--section"):
            sectionName = arg
    if not configPath.strip():
        configPath = configPath.strip()
    if not sectionName.strip():
        sectionName = "SERVER1"
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    rm = RustMonitor(configPath,sectionName)
    rm.main()

if __name__ == "__main__":
    main(sys.argv[1:])
