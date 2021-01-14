#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, getopt, re, os.path, configparser, random
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

class MapSeedBot:
    """Save previous seed and change to new random seed on periodic basis
       Check day is always first Thursday of the month
       """
    def __init__(self, configPath = '', configSection = 'SERVER1', serverSeedConfigPath = ''):
        configSectionUpper = configSection.upper()
        self.modify_configuration(configPath, configSectionUpper)
        confsec = self.config[configSectionUpper]
        self.lastWipe = confsec['last_wipe']
        self.configPath = configPath
        self.configSection = configSection
        self.serverSeedConfigPath = serverSeedConfigPath
        print(self.lastWipe)

    def modify_configuration(self, configPath, configSection, saveSeed = False, newSeed = '1'):
        """Read seed INI file. Write new wipe date and new seed if saveSeed = True.
           last wipe will be current time. Pass new seed to be written to seed INI file"""
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
                for key,value in userconfig._sections[configSection].items():
                    if key != 'last_wipe':
                        config[configSection][key] = value
                if saveSeed:
                    config[configSection][str(wipeDateTime)] = newSeed
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

    def change_seed(self, newSeed):
        #TODO: Change to write the seed and not read and print it.
        with open(self.serverSeedConfigPath, 'r', encoding='utf-8') as configfile:
            for line in configfile:
                if "seed" in line:
                    match = re.findall(pattern, line)
                    if len(match) != 0:
                            print(re.sub(pattern, 'seed="'+str(newSeed), line))

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

