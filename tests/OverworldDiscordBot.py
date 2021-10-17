import sys

sys.path.append('../')
from discordbot import OverworldDiscordBot

bot = OverworldDiscordBot("../config.json")
bot.run(bot.config["DiscordToken"])
