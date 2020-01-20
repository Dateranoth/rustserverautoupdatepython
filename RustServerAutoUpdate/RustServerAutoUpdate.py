from rustbots import discord, rcon
sin = discord.ServerInformation("myGame", "MyServer", "1.1.1.1", "gamercide.org")
bot = discord.DiscordBot("https://discordapp.com/api/webhooks/280900899868639234/PDlN_4fHnMHhUnolguOR62Ms70IXjRl3Jjdy8SskObE6FA_BIAjpb_eB_C7_kdoDH1Rz", "Botty")
bot.send_message(sin, "Test from inside Visual Studio")

rconbot = rcon.RCONBot("abc123", "127.0.0.1", "28016", "Botty")
rconbot.send_message("say This is a Test from a New bot")