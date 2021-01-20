#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests, json, sys, getopt, logging

class ServerInformation:
    def __init__(self, gameName, serverName, serverIP, serverHostName = ""):
        """Information on the Server when sending message
           These items can all be empty strings, but they provide
           detailed information about the server for display on Discord."""
        self.gameName = gameName
        self.serverName = serverName
        self.serverIP = serverIP
        self.serverHostName = serverHostName

class DiscordBot:
    """Bot to Send Message to Discord Server Using Webhook"""
    def __init__(self, webHook, botName, botAvatar = ""):
        """Setup reusable bot information
        webHook from Discord Bot Setup. Should be URL.
        botName is not required, but will be displayed as user on Discord.
        botAvatar allows custom user icon to be displayed. URL."""
        self.logger = logging.getLogger(__name__)
        self.webHook = webHook
        self.botName = botName
        self.botAvatar = botAvatar
    def send_message(self, ServerInformation, message, title = "🚧 ALERT"):
        """Send message and title to discord server
        ServerInformation comes from class and is required.
        message is what should be said by discord bot.
        title can be anything, but is used as an indicator for type of message."""
        headers = {"Content-Type" : "application/json"}
        jsonDict = {"username": self.botName,
                  "avatar_url": self.botAvatar,
                  "file": "content",
                  "embeds": [{"color": "2067276",
                            "author": {"name": title, "icon_url": self.botAvatar},
                            "title": "",
                            "description": message,
                            "url": "",
                            "type": "content",
                            "thumbnail": {},
                            "footer": {"text": "Hostname: " + ServerInformation.serverHostName, "icon_url": ""},
                            "fields": [{
                                            "name": "Game",
                                            "value": ServerInformation.gameName,
                                            "inline": True,
                                        },
                                        {
                                            "name": "Server IP",
                                            "value": ServerInformation.serverIP,
                                            "inline": True
                                        },
                                        {
                                            "name": "Server Name",
                                            "value": ServerInformation.serverName,
                                            "inline": True
                                        }
                            ]
                  }]
        }
        self.logger.debug("Sending Message to Discord: Header: " + str(headers) + " Message: " + json.dumps(jsonDict))
        r = requests.post(self.webHook + "?wait=true", headers=headers, data=json.dumps(jsonDict))
        return r.text
        
def argumenthelp():
    print("\nSyntax: discord.py -w <webhook> -b <BotName> -m <Message> [-a <botAvatar> -t <Message Title> -g <gameName> -s <serverName> -i <serverIP> -n <serverHostName>]\n"
          "Example: discord.py -w https://discordapp.com/api/webhooks/#####/###XXX### -b 'My Discord Bot' -m 'Hello World'\n"
          "REQUIRED INPUT:\n"
          "-w --webhook      Webhook URL from Discord.\n"
          "-b --botname      BotName to Use for Message.\n"
          "-m --message      Message to be sent to server.\n"
          "OPTIONAL INPUT:\n"          
          "-a --avatar       Bot Avatar Image URL.\n"
          "-t --title        Message Title. Default 🚧 ALERT.\n"
          "-g --gamename     Game Name.\n"
          "-s --servername   Server Name.\n"
          "-i --ip           Server IP.\n"
          "-n --hostname     Server Hostname.\n"
          "-h --help         This help.\n")
    
def main(argv):
    webHook = ""
    botName = ""
    message = ""
    botAvatar = ""
    title = "🚧 ALERT"
    gameName = "Unknown"
    serverName = "Unknown"
    serverIP = "Unknown"
    serverHostName = "Unknown"
    try:
        opts, args = getopt.getopt(argv,"ha:t:g:s:i:n:w:b:m:",["help", "avatar=", "title=", "gamename=", "servername=", "ip=", "hostname=","webhook=","botname=","message="])
    except getopt.GetoptError as err:
        print("Incorrect Syntax: -h or --help for more information")
        print("discord.py -w <webhook> -b <BotName> -m <Message> [-a <botAvatar> -t <Message Title> -g <gameName> -s <serverName> -i <serverIP> -n <serverHostName>]")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            argumenthelp()
            sys.exit()
        elif opt in ("-w", "--webhook"):
            webHook = arg
        elif opt in ("-b", "--botname"):
            botName = arg
        elif opt in ("-m", "--message"):
            message = arg
        elif opt in ("-a", "--avatar"):
            botAvatar = arg
        elif opt in ("-t", "--title"):
            title = arg
        elif opt in ("-g", "--gamename"):
            gameName = arg
        elif opt in ("-s", "--servername"):
            serverName = arg
        elif opt in ("-i", "--ip"):
            serverIP = arg
        elif opt in ("-n", "--hostname"):
            serverHostName = arg
    if not webHook.strip() or not botName.strip() or not message.strip():
        print("Incorrect Syntax: webhook, botname, and message required\n"
              "-h or --help for more information")
        sys.exit()

    sInfo = ServerInformation(gameName, serverName, serverIP, serverHostName)
    bot = DiscordBot(webHook, botName, botAvatar)
    reply = bot.send_message(sInfo, message, title)
    print(reply)
    
if __name__ == "__main__":
   main(sys.argv[1:])
