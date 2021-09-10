import json
import sys

sys.path.append('../')
from discordbot import OverworldDiscordBot

bot = OverworldDiscordBot()
bot.configure(json.load(open("../config.json")))
bot.run(bot.config["DiscordToken"])
