#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests, json, sys, getopt, re, glob, os.path

class UpdateCheck:
    """Used to check local oxide version against latest release"""
    def __init__(self, oxideLogDir, gitURL = "https://api.github.com/repositories/94599577/releases/latest"):
        """Initiate by assigning directory. Optionally point to different release. Not recommended"""
        self.oxideLogDir = os.path.join("", oxideLogDir)
        self.gitURL = gitURL

    def get_json_from_api(self):
        """Query Git API for json String with Latest Update Information"""
        r = requests.get(self.gitURL)
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
        """Get running version from local logs"""
        #pattern = "(Loaded extension Rust v)([0-9]\.[0-9]\.(\d+))"
        pattern = "Loaded extension Rust v(\d+\.\d+\.\d+)"
        lastMatch = '0.0.0'
        logFileNameList = glob.glob(os.path.join(self.oxideLogDir, 'oxide*.txt'))        
        if len(logFileNameList) != 0:
            logLatestFileName = max(logFileNameList)
            with open(logLatestFileName) as rustLogFile:
                for currentLine in rustLogFile:
                    if "Rust" in currentLine:
                        currentMatch = re.findall(pattern, currentLine)
                        if len(currentMatch) != 0:
                            lastMatch = currentMatch[0]
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