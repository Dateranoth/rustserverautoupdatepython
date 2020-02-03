# Auto Update an Oxide Rust Server. Can be used with any server, but designed around using LGSM.

This program was written to allow automatically updating Oxide when a new version is detected. It also allows for notification messages to be sent via Discord and RCON.

This application does not require any input to run, but it will default to creating a configuration file in the same directory it is executed from.
To change this directory, please specify on the command line. rusterverautoupdate.py /myconfig/path/ SERVER1
SERVER1 is optional, but can be used to run mutliple instances using the same configuration. Each instance should have unique settings placed in their section.
rustserverautoupdate.ini will be created on first run, and updated if any new options are added or removed.

REQUIRES: packages: requests, websockets


*oxide_log_dir
	* Directory of the oxide log files. 
	* DEFAULT: ~/serverfiles/oxide/logs
*oxide_git_url
	* URL of Oxide GIT. This is used to check for the latest release. Has not been tested against non-default repositories.
	* DEFAULT: https://api.github.com/repositories/94599577/releases/latest
*oxide_check_time_in_min
	* How long to wait between update checks in minutes.
	* DEFAULT: 15
*oxide_auto_update
	* Enable auto updates. If enabled. bash command below is ran after last notification.
	* DEFAULT: no
*bash_get_update_command
	* Commands to run after update detected and last notification has been sent.
	* DEFAULT: ~/./rustserver stop | ~/./rustserver mods-update | ~/./rustserver start
*use_rcon
	* Use RCON to send notification to server before updating.
	* DEFAULT: yes
*use_discord
	* Use Discord to send notification to channel before updating.
	* DEFAULT: no
*rcon_ip
	* RCON IP
	* DEFAULT: 127.0.0.1
*rcon_port
	* RCON Port
	* DEFAULT: 28016
*rcon_pass
	* RCON Password
	* DEFAULT: CHANGE_ME
*discord_webhook
	* Webhook from Discord Bot Setup.
	* DEFAULT: 
*discord_bot_name
	* Bot Name to Display to Discord
	* DEFAULT: RustPythonBot
*discord_bot_avatar_url
	* Bot Avatar Image URL
	* DEFAULT:
*discord_msg_game_name
	* Discord Message: Game Name to Display.
	* DEFAULT: My Rust Game
*discord_msg_server_name
	* Discord Message: Name of Server
	* DEFAULT: My Server
*discord_msg_server_ip_port
	* Discord Message SERVER IP:PORT to Display.
	* DEFAULT: 127.0.0.1:28015
*discord_msg_server_host_name
	* Discord Message: Host Name to Display.
	* DEFAULT:
*discord_msg_title
	* Discord Message: Title to Display.
	* DEFAULT: 🚧 ALERT
*send_15min_warn
	* Send 15 Minute Warning Before Update.
	* DEFAULT: yes
*send_10min_warn
	* Send 10 Minute Warning Before Update.
	* DEFAULT: yes
*send_5min_warn
	* Send 5 Minute Warning Before Update.
	* DEFAULT: yes
*send_1min_warn
	* Send 1 Minute Warning Before Update.
	* DEFAULT: yes
*15min_msg
	* Message to be displayed for 15 minute warning.
	* DEFAULT: Oxide Update Detected. Server will restart in 15 minutes for update.
*10min_msg
	* Message to be displayed for 10 minute warning.
	* DEFAULT: Oxide Update Scheduled. Server will restart in 10 minutes for update.
*5min_msg
	* Message to be displayed for 5 minute warning.
	* DEFAULT: Oxide Update Scheduled. Server will restart in 5 minutes for update.
*1min_msg
	* Message to be displayed for 1 minute warning.
	* DEFAULT: FINAL WARNING! SERVER RESTARTING FOR OXIDE UPDATE IN 1 MINUTE!!