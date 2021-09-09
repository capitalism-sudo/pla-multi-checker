# Needs a discord bot account and a server with all the mark ids as emojis

import asyncio
import io
import json
import sys
from functools import lru_cache
from threading import Thread
from time import sleep

import discord
import pokebase as pb
from discord.ext import commands
from discord.utils import get
from PIL import Image

sys.path.append('../')
from discordbot import OverworldDiscordBot # Channels

bot = OverworldDiscordBot()
bot.configure(json.load(open("../config.json")))
bot.run("ADD-TOKEN-HERE")
