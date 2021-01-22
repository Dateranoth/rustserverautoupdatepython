#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests, json, sys, getopt, re, glob, os.path, logging
from datetime import datetime, timedelta, timezone

class UpdateCheck:
    """Used to check local oxide version against latest release"""
    def __init__(self, oxideLogDir, gitURL = "https://api.github.com/repositories/94599577/releases/latest"):
        """Initiate by assigning directory. Optionally point to different release. Not recommended"""
        self.logger = logging.getLogger(__name__)
        self.oxideLogDir = os.path.join("", oxideLogDir)
        self.gitURL = gitURL
        
    def get_json_from_api(self):
        """Query Git API for json String with Latest Update Information"""
        r = requests.get(self.gitURL)
        self.logger.debug("Git URL Response: (" + str(r.status_code) + ") " + r.text)
        if r.status_code == 200:
            return r.text
        else:
            raise UpdateCheckError(str(r.status_code), r.text, "Response Status Code Failure")

    def get_latest_version(self, gitJSONString = ""):
        """Get latest version from GitURL"""
        if not gitJSONString.strip():
            gitJSONString = self.get_json_from_api()
        reply = json.loads(gitJSONString)
        for x in reply:
            if x == "tag_name":
                return reply[x]
        raise UpdateCheckError("200", gitJSONString, "Could Not Find tag_name")

    def get_latest_url(self, linux = True,  gitJSONString = ""):
        """Get latest linux version download url from GitURL. Optionally retrieve windows url instead of Linux"""
        if not gitJSONString.strip():
            gitJSONString = self.get_json_from_api()
        reply = json.loads(gitJSONString)
        for x in reply:
            if x in "assets":
                for a in reply[x]:
                    for b in a:
                        if b == "browser_download_url":
                            if "linux" in a[b] and linux:
                                return a[b]
                            elif not "linux" in a[b] and not linux:
                                return a[b]
        raise UpdateCheckError("200", gitJSONString, "Could Not Find Download URL")

    def get_running_version(self):
        """Get running version from local logs. Checks the current and last month logs.
           Oxide rolls the logs over nightly, and doesn't necessarily write the latest version on roll over.
           To make sure the latest version is found, we will iterate over the past 2 months of logs.
           This was the compromise between reading every log ( could potentially be a lot ) and reading too few."""
        pattern = "Loaded extension Rust v(\d+\.\d+\.\d+)"
        lastMatch = "0.0.0"
        timeZN = timezone(timedelta(hours=0))
        tm = datetime.now(timeZN).timetuple()
        startLog = "oxide_"
        endLog = "*.txt"
        dateDivider = "-"
        thisMonthsLogsYear = int(tm.tm_year)
        thisMonthsLogsMonth = int(tm.tm_mon)

        if int(tm.tm_mon) == 1:
            lastMonthsLogsYear = thisMonthsLogsYear - 1
            lastMonthsLogsMonth = 12
        else:
            lastMonthsLogsYear = thisMonthsLogsYear
            lastMonthsLogsMonth = thisMonthsLogsMonth - 1    
        lastMonthsLogs = startLog + "{:04d}".format(lastMonthsLogsYear) + dateDivider + "{:02d}".format(lastMonthsLogsMonth) + endLog
        thisMonthsLogs = startLog + "{:04d}".format(thisMonthsLogsYear) + dateDivider + "{:02d}".format(thisMonthsLogsMonth) + endLog
        self.logger.debug("Last Month Log Search String: " + lastMonthsLogs)
        self.logger.debug("This Month Log Search String: " + thisMonthsLogs)

        #glob does not necessarily return these in order. Need to sort them to make sure the last version is the latest.
        logFileNameList = sorted(glob.glob(os.path.join(self.oxideLogDir, lastMonthsLogs)))
        logFileNameList.extend(sorted(glob.glob(os.path.join(self.oxideLogDir, thisMonthsLogs))))
        numLogFiles = len(logFileNameList)

        if numLogFiles != 0:
            for logFile in logFileNameList:
                with open(logFile) as rustLogFile:                    
                    for currentLine in rustLogFile:
                        if "Rust" in currentLine:
                            currentMatch = re.findall(pattern, currentLine)
                            if len(currentMatch) != 0:
                                lastMatch = currentMatch[0]
                                self.logger.debug("Found Version: " + lastMatch + " in Line: " + currentLine.strip() + " in File " + logFile)
            if lastMatch == '0.0.0':
                self.logger.warning('No version was found in Oxide Log Files. Assuming this is the first run. Check Oxide Log Directory setting if this message persists.')
        else:
            self.logger.warning('No Oxide Log Files Found. Assuming this is the first run. Check Oxide Log Directory setting if this message persists.')
        return lastMatch   

    def check_update(self, linux = True):
        """Check for updates. Return tuple (Boolean update required, String update url, String runningversion, String latestversion)"""
        gitJSON = self.get_json_from_api()
        runningVersion = self.get_running_version()
        latestVersion = self.get_latest_version(gitJSON)
        updateURL = self.get_latest_url(linux, gitJSON)
        if runningVersion.strip() != latestVersion.strip():            
            return (True, updateURL, runningVersion, latestVersion)
        else:
            return (False, updateURL, runningVersion, latestVersion)

class UpdateCheckError(Exception):
    def __init__(self, responsecode, detail, msg):
        self.response = responsecode
        self.text = detail
        self.msg = msg

def argumenthelp():
    print("\nSyntax: oxide.py -l <Oxide Log Dir> [-g <GitHub URL> -w]\n"
          "Example: oxide.py -l ~\serverlocation\oxide\logs\ [-g <gitURL> -w]\n"
          "Example: oxide.py -r\n"
          "\n"
          "Check for updates. Return Space Separated String Array (Boolean update url, updatestring, runningversion, latestversion)\n\n"
          "REQUIRED INPUT - CHOOSE ONE:\n"
          "-l --logdir       Directory of Oxide Logs.\n"
          "-r --retrieveurl  Only retrieve Update URL. Update Check will not be performed\n"
          "OPTIONAL INPUT:\n"          
          "-g --giturl       URL of Oxide Git Repository. Default: https://api.github.com/repositories/94599577/releases/latest\n"
          "-w --windows      Retrieve Windows URL instead of Linux.\n"
          "-h --help         This help.\n")
    
def main(argv):
    logDir = ""
    gitURL = "https://api.github.com/repositories/94599577/releases/latest"
    linux = True
    returnURLOnly = False

    try:
        opts, args = getopt.getopt(argv,"hwrl:g:",["help", "windows", "retrieveurl", "logdir=", "giturl="])
    except getopt.GetoptError as err:
        print("Incorrect Syntax: -h or --help for more information")
        print("oxide.py -l ~\serverlocation\oxide\logs [-g <gitURL> -w]")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            argumenthelp()
            sys.exit()
        elif opt in ("-l", "--logdir"):
            logDir = arg
        elif opt in ("-g", "--giturl"):
            gitURL = arg
        elif opt in ("-w", "--windows"):
            linux = False
        elif opt in ("-r", "--retrieveurl"):
            returnURLOnly = True

    if not logDir.strip() and not returnURLOnly:
        print("Incorrect Syntax: logdir required\n"
              "-h or --help for more information")
        sys.exit()
    o = UpdateCheck(logDir, gitURL)
    replyString = ""
    if returnURLOnly:
        replyString = o.get_latest_url(linux)
    else:
        reply = o.check_update(linux)    
        for item in reply:
            if str(item) == "":
                replyString += "''" + " "
            else:
                replyString += str(item) + " "
    print(replyString)
if __name__ == "__main__":
   main(sys.argv[1:])