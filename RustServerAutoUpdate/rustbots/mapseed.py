#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, getopt, re, os.path, configparser, random
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

#TODO: Clean up code. Add if __name__ == "__main__": to run standalone.
class MapSeedBot:
    """Save previous seed and change to new random seed on periodic basis
       Check day is always first Thursday of the month"""
    def __init__(self, configPath = '', configSection = 'SERVER1', serverSeedConfigPath = '/home/rustserver/lgsm/config-lgsm/rustserver/rustserver.cfg'):
        """configPath: Path where the rusterserverseedlog.ini should be saved
           configSection: [SECTION] for this instance. Usually Server Name. Default: SERVER1
           serverSeedConfigPath: Full path to INI containing seed= Default: '/home/rustserver/lgsm/config-lgsm/rustserver/rustserver.cfg'. """
        self.configSection = configSection.upper()
        self.configPath = configPath
        self.serverSeedConfigPath = serverSeedConfigPath
        self.modify_configuration(self.configPath, self.configSection)

    def modify_configuration(self, configPath, configSection, saveSeed = False, newSeed = '1'):
        """Read seed INI file. Write new wipe date and newSeed if saveSeed = True.
           last wipe will be current time. Pass newSeed to be written to seed INI file
           Will set self.lastWipe to what was read from INI or what was just written"""
        timeZN = timezone(timedelta(hours=0))
        wipeDateTime = datetime.now(timeZN)
        confComments = OrderedDict({'DEFAULT': {'# This is the Default section.': None,
                                                '# This section will only contain the last_wipe key as a fallback.': None,
                                                '# Individual instances will contain the last wipe and previous seeds.': None},
                                    configSection   : {'# Last Wipe Time and Seeds for '+ configSection +' Here.': None}})
        confDefaults = OrderedDict({'DEFAULT': {'last_wipe':  str(wipeDateTime)},
                                    configSection:    {'last_wipe':  str(wipeDateTime)}})

        configFile = os.path.join(configPath, "rustserverseedlog.ini")
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
            self.modify_configuration(self.configPath, self.configSection)
            previousdatetime = datetime.strptime(str(self.lastWipe), '%Y-%m-%d %H:%M:%S.%f%z')
            minDaysBetweenWipe = timedelta(days=27)
            if datetime.now(timeZN) >= (previousdatetime + minDaysBetweenWipe):
                newSeed = random.randrange(1, 2147483647, 1)
                self.change_seed(newSeed)
                self.modify_configuration(self.configPath, self.configSection, True, newSeed)
                print('Seed Updated to : ' + str(newSeed) + ' at Time: ' + self.lastWipe)
                return True
            else:
                print('Not been enough days')
                return False
        else:
            print('Not the 1st Thursday of the Month')
            return False

