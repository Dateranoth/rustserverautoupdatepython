#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, sys, getopt, logging
from websocket import create_connection, _exceptions

class RCONBot:
    """Send Message to Rust RCON Using WebSocket"""
    def __init__(self, password, ip = "127.0.0.1", port = "28016", botName = "RustPythonBot"):
        self.ip = ip
        self.port = port
        self.password = password
        self.botName = botName
        self.logger = logging.getLogger(__name__)

    def send_message(self, command, identifier = "-1", timeout = 10):
        """Send Message to Rust RCON. Return reply from server.
           Example send_message('say Welcome to my Server')
           Optionally send identifer and timeout. Identifier is a return for
           certain commands to allow tracking. Timeout is how long to wait for reply."""
        jsonDict = {"Identifier": identifier,
                   "Message": command,
                   "Name": self.botName}
        self.logger.debug("Sending RCON Message: " + json.dumps(jsonDict))
        ws = create_connection("ws://" + self.ip + ":" + self.port + "/" + self.password, timeout)
        ws.send(json.dumps(jsonDict))
        reply = json.loads(ws.recv())
        # Rust wants to take forever to respond to the close. If we just abandon the socket instead of closing
        # Rust complains about it and we end up spamming the console. This is basically a cheat to start
        # the process of closing the connection without waiting for Rust to actually tell us it's closed.
        ws.close(timeout=.05)
        return reply

def argumenthelp():
    print("\nSyntax: rcon.py -p <RCON Password> -c <Command> [-i <Server IP> -o <Server RCON Port> -n <Bot Name> -t <Command Timeout in Seconds>]\n"
          "Example: rcon.py -i '127.0.0.1' -o '28016' -p 'CHANGE_ME' -c 'say Hello World' -n 'MyRustBot' -t 5\n"
          "REQUIRED INPUT:\n"
          "-w --password     RCON Password.\n"
          "-c --command      Command to be sent to Server.\n"
          "OPTIONAL INPUT:\n"          
          "-i --ip           Server RCON IP. Default: 127.0.0.1\n"
          "-o --port         Server RCON Port. Default: 28016.\n"
          "-n --botname      Bot Name. For Logging. Default: RustPythonBot\n"
          "-t --timeout      Time in Seconds before failing due to no response from server. Default: 10\n"
          "-v --verbose      Print Full response from RCON and not just Message\n")
    
def main(argv):
    password = ""
    command = ""
    ip = "127.0.0.1"
    port = "28016"
    botName = "RustPythonBot"
    timeout = 10
    verbose = False
    try:
        opts, args = getopt.getopt(argv,"hvw:c:i:o:n:t:",["help", "verbose", "password=", "command=", "ip=", "port=", "botname=", "timeout="])
    except getopt.GetoptError as err:
        print("Incorrect Syntax: -h or --help for more information")
        print("rcon.py -p <RCON Password> -c <Command> [-i <Server IP> -o <Server RCON Port> -n <Bot Name> -t <Command Timeout in Seconds>]\n")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            argumenthelp()
            sys.exit()
        elif opt in ("-w", "--password"):
            password = arg
        elif opt in ("-c", "--command"):
            command = arg
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-o", "--port"):
            port = arg
        elif opt in ("-n", "--botname"):
            botName = arg
        elif opt in ("-t", "--timeout"):
            timeout = int(arg)
        elif opt in ("-v", "--verbose"):
            verbose = True
    if not password.strip() or not command.strip():
        print("Incorrect Syntax: password and command required\n"
              "-h or --help for more information")
        sys.exit()
    try:
        bot = RCONBot(password, ip, port, botName)
        print("\n***Sending Command***\n")
        reply = bot.send_message(command, timeout)
        if verbose:
            print("VERBOSE. FULL RESPONSE: \n" + json.dumps(reply) + "\n\n")
        print(reply["Message"])
    except _exceptions.WebSocketTimeoutException as err:
        print("Timed Out while waiting on response from server for command: " + command)
if __name__ == "__main__":
   main(sys.argv[1:])