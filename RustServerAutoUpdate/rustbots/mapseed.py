#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, getopt, re, configparser, random, os.path, glob, logging
from os import remove
from shutil import copy2
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

#TODO: Clean up code. Put in checks for file in use.
class MapSeedBot:
    """Save previous seed and change to new random seed on periodic basis
       Check day is always first Thursday of the month"""
    def __init__(self, configPath, configName, serverSeedConfigPath, configSection = 'SERVER1'):
        """configPath: Path where the seed log INI should be saved
           configName: Name of seed log cfg file. Example: mapseed.ini
           configSection: [SECTION] for this instance. Usually Server Name. Default: SERVER1
           serverSeedConfigPath: Full path to INI containing seed= Default for LinuxGSM: '/home/rustserver/lgsm/config-lgsm/rustserver/rustserver.cfg'. """        

        self.logger = logging.getLogger(__name__)
        try:
            import rustbots.files
            self.fileManage = rustbots.files.ManageFiles()
        except ImportError:
            self.logger.warning("Missing rustbots.files. Configurations will not be backed up before writing.")
            self.fileManage = None

        self.configPath = configPath
        self.configName = configName
        self.serverSeedConfigPath = serverSeedConfigPath
        self.configSection = configSection.upper()        
        self.modify_configuration()

    def modify_configuration(self, saveSeed = False, newSeed = '1'):
        """Read seed INI file. Write new wipe date and newSeed if saveSeed = True.
           last wipe will be current time. Pass newSeed to be written to seed INI file
           Will set self.lastWipe to what was read from INI or what was just written"""
        configPath = self.configPath
        configName = self.configName
        configSection = self.configSection
        timeZN = timezone(timedelta(hours=0))
        wipeDateTime = datetime.now(timeZN)
        confComments = OrderedDict({'DEFAULT': {'# This is the Default section.': None,
                                                '# This section will only contain the last_wipe key as a fallback.': None,
                                                '# Individual instances will contain the last wipe and previous seeds.': None},
                                    configSection   : {'# Last Wipe Time and Seeds for '+ configSection +' Here.': None}})
        confDefaults = OrderedDict({'DEFAULT': {'last_wipe':  str(wipeDateTime)},
                                    configSection:    {'last_wipe':  str(wipeDateTime)}})

        configFile = os.path.join(configPath, configName)
        userconfig = configparser.ConfigParser(delimiters=('='))
        userconfig.read(configFile, encoding='utf-8')

        if (len(userconfig.defaults()) != len(confDefaults['DEFAULT'])) or saveSeed or not userconfig.has_section(configSection):
            config = configparser.ConfigParser(delimiters=('='), allow_no_value=True)            
            config.read_dict(confComments)
            config.read_dict(confDefaults)

            if userconfig.has_section(configSection):
                if saveSeed or not userconfig.has_option(configSection, 'last_wipe'):
                    config[configSection]['last_wipe'] = str(wipeDateTime)
                    config[configSection][str(wipeDateTime)] = str(newSeed).strip()
                for key,value in userconfig._sections[configSection].items():
                    if key != 'last_wipe':
                        config[configSection][key] = value
            for section in userconfig.sections():
                if section != configSection:
                    config.add_section(section)
                    config[section]['# Last Wipe Time and Seeds for '+ configSection +' Here.'] = None
                    for (key,value) in userconfig._sections[section].items():
                        config[section][key] = value
            for (key,value) in userconfig.defaults().items():
                if config.has_option(config.default_section, key):
                    config[config.default_section][key] = value
            if saveSeed:
                config[config.default_section]['last_wipe'] = str(wipeDateTime)

            #Backup seed log if possible then write the configuration.
            if not (self.fileManage is None):
                self.fileManage.backup_file(configPath, configName, 2)
            with open(configFile, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        self.config = configparser.ConfigParser(delimiters=('='))
        self.config.read_dict(confDefaults)
        self.config.read(configFile, encoding='utf-8')
        confsec = self.config[configSection]
        self.lastWipe = confsec['last_wipe']

    def change_seed(self, newSeed):
        linelist = list
        with open(self.serverSeedConfigPath, 'r', encoding='utf-8') as configfileread:
            linelist = configfileread.readlines()
        with open(self.serverSeedConfigPath, 'w', encoding='utf-8') as configfilewrite:
            pattern = '^\s*seed\s*=\s*\"?(\d+)\"?'
            seedUpdated = False
            for line in linelist:
                if "seed" in line.lower():
                    match = re.findall(pattern, line)
                    if len(match) != 0:
                        line = re.sub(pattern, 'seed="'+str(newSeed)+'"', line)
                        seedUpdated = True                        
                configfilewrite.write(line)
            if not seedUpdated:
                configfilewrite.write('\n')
                configfilewrite.write('seed="'+str(newSeed)+'" # default random; range : 1 to 2147483647 ; used to change or reproduce a procedural map')
                
    def wipe_check(self):
        timeZN = timezone(timedelta(hours=0))
        tm = datetime.now(timeZN).timetuple()
        if tm.tm_mday <= 7 and tm.tm_wday == 3:
            #Update the last wipe variable from the INI. We should do this each time to make sure it is up to date.
            self.modify_configuration()
            previousdatetime = datetime.strptime(str(self.lastWipe), '%Y-%m-%d %H:%M:%S.%f%z')
            minDaysBetweenWipe = timedelta(days=27)
            if datetime.now(timeZN) >= (previousdatetime + minDaysBetweenWipe):
                newSeed = random.randrange(1, 2147483647, 1)
                self.change_seed(newSeed)
                self.modify_configuration(True, newSeed)
                return (True, str(newSeed), self.lastWipe)
                
            else:
                return (False, "Not enough days have passed since last wipe.", self.lastWipe)
        else:
            return (False, "Not the first Thursday of the Month", self.lastWipe)


    def backup_file(self, filePath, fileName, quantity = 10, extension = ".bak"):
        timeZN = timezone(timedelta(hours=0))
        tm = datetime.now(timeZN)
        timeStamp =  tm.strftime("-%Y-%m-%d_%H.%M.%S%z")
        wildcard = "*"
        sourceFilePath = os.path.join(filePath, fileName)
        backupFilePath = os.path.join(filePath, fileName + timeStamp + extension)
        oldFileSearchPath = os.path.join(filePath, fileName + wildcard + extension)
        print("Source: " + sourceFilePath + " Dest: " + backupFilePath + " OldBackups: " + oldFileSearchPath)
        oldBackupFiles = sorted(glob.glob(oldFileSearchPath))
        if len(oldBackupFiles) >= quantity:
            remove(oldBackupFiles[0])
            print("Removed Backup File: " + oldBackupFiles[0])
        #with open(fileNamePath, 'r', encoding='utf-8') as backupSource, open(backupFilePath, 'w', encoding='utf-8') as backupDesination:
        #    for line in backupSource:
        #        backupDesination.write(line)
        copy2(sourceFilePath, backupFilePath)

        
        
def argumenthelp():
    print("\nSyntax: mapseed.py -c <Path to Server Seed Configuration File>\n"
          "Example: mapseed.py -c /home/rustserver/lgsm/config-lgsm/rustserver/rustserver.cfg"
          "\n"
          "On first run logs current date as last wipe. Each additional run will check for first day of the month and update seed after a minimum of 27 days since last wipe.\n\n"
          "REQUIRED INPUT:\n"
          "-c --configpath    Path where Seed Configuration File is Located. MUST HAVE WRITE PERMISSION.\n"          
          "OPTIONAL INPUT:\n"
          "-f --forcewipe     Immediately changes the seed and logs current time as last wipe. Pass custom seed (range : 1 to 2147483647) or 0 for random\n"
          "-p --pathINI       Path to store seed log and last wipe time. Default: Path mapseed.py is located in.\n"
          "-n --iniName       File Name to wrie seed logs and last wipe date. Default mapseed.ini"
          "-s --section       Section Name for configuration. This allows for multiple instances to be ran from same configuration. Default: SERVER1\n")
def main(argv):
    serverConfigPath = ""
    seedLogName = ""
    seedLogPath = ""
    sectionName = ""
    forceWipe = False
    try:
        opts, args = getopt.getopt(argv,"hc:f:p:n:s:",["help", "configPath=", "forcewipe=", "pathINI=", "iniName=", "section="])
    except getopt.GetoptError as err:
        print("Incorrect Syntax: -h or --help for more information")
        print("\nSyntax: mapseed.py -c <Path to Server Seed Configuration File>\n")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            argumenthelp()
            sys.exit()
        elif opt in ("-c", "--configpath"):
            serverConfigPath = arg.strip()        
        elif opt in ("-f", "--forcewipe"):
            forceWipe = True
            if arg.isnumeric:
                seed = int(arg.strip())
            else:
                print("Incorrect Syntax: seed must be numeric between 1 and 2147483647\n"
                      "-h or --help for more information")
                print('first')
                sys.exit()
            if seed == 0:
                seed = random.randrange(1, 2147483647, 1)
            elif seed < 0:
                seed = 1
            elif seed > 2147483647:
                seed = 2147483647
        elif opt in ("-p", "pathINI"):
            seedLogPath = arg.strip()
        elif opt in ("-n", "--iniName"):
            seedLogName = arg.strip()
        elif opt in ("-s", "--section"):
            sectionName = arg.strip()
    if not serverConfigPath:
        print("Incorrect Syntax: configpath and configname required\n"
              "-h or --help for more information")
        sys.exit()

    logPath, fileName = os.path.split(os.path.realpath(__file__))    
    if not seedLogPath:
        seedLogPath = logPath
    if not seedLogName:
        seedLogName = fileName.replace('.py', '')
    if not sectionName:
        sectionName = "SERVER1"

    msb = MapSeedBot(seedLogPath, seedLogName, serverConfigPath, sectionName)
    if forceWipe:
        msb.change_seed(seed)
        msb.modify_configuration(True, seed)
        print('Seed Updated to : ' + str(seed) + ' at Time: ' + msb.lastWipe)
    else:
        reply = msb.wipe_check()
        if reply[0]:
            print('Seed Updated to : ' + str(reply[1]) + ' at Time: ' + str(reply[2]))
        else:
            print(str(reply[1]) + ' Last Updated: ' + str(reply[2]))
if __name__ == "__main__":
    main(sys.argv[1:])