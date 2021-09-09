# Needs a discord bot account and a server with all the mark ids as emojis.

import asyncio
import io
import json
import socket
import sys
from functools import lru_cache
from threading import Thread
from time import sleep
from enum import Enum
from distutils.util import strtobool

import discord
import pokebase as pb
from discord.ext import commands
from discord.utils import get
from PIL import Image

sys.path.append('../')
from lookups import Util
from nxreader import SWSHReader
# from . import Channels

class Channels(Enum):
    NoChannel = 0
    EventNotificationChannelIdForShiny = 1
    EventNotificationChannelIdForBrilliant = 2
    EventNotificationChannelIdForMark = 3
    EventNotificationChannelIdForRareMark = 4
    NotificationChannelForInfo = 5
    TextNotificationChannelIdForShiny = 6
    TextNotificationChannelIdForBrilliant = 7
    TextNotificationChannelIdForMark = 8
    TextNotificationChannelIdForRareMark = 9

class OverworldDiscordBot(commands.Bot):
    def __init__(self):
        # config to refactor out later
        # prefix for bot commands
        bot_prefix = "$"
        # set up commands.Bot with specified prefix
        super().__init__(command_prefix=bot_prefix)

        # default values for variables as to not throw errors
        self.thread = None
        self.thread_running = True
        self.reader = None
        self.config = None
        self.is_configured = False

        # function to run when the bot is "ready"
        @self.event
        async def on_ready():
            # tell user in console that the bot is ready
            _message = "Overworld Discord Bot has started."
            await self.send_discord_msg(_message, Channels.NotificationChannelForInfo)
            # change bot presence to "Watching some ram for shinies"
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="some ram for shinies"))

        # function to run whenever the start command is called
        @self.command()
        async def start(ctx):
            if not self.is_configured:
                _message = "Unable to start bot due to missing configuration! Exiting."
                await self.send_discord_msg(_message, Channels.NotificationChannelForInfo)
                return
            # create reader object
            try:
                self.reader = SWSHReader(self.config["IP"])
                # create and start a thread for reading from the switch
                self.thread = Thread(target=self.reader_func,args=(ctx,))
                self.thread.start()
            except socket.timeout:
                _message = "Unable to connect to IP {}. Check that the Switch is available.".format(self.config["IP"])
                await self.send_discord_msg(_message, Channels.NotificationChannelForInfo)

        # function to run whenever the ping command is called
        @self.command()
        async def ping(ctx):
            # say the bots latency in discord channel
            await ctx.send(f'Pong! {round(self.latency, 3)}')
        
        # function to run whenever stop command is called, stops reader and discord bot
        @self.command()
        async def stop(ctx):
            # tell user in console that we are now stopping
            _message = "Overworld Discord Bot is stopping."
            await self.send_discord_msg(_message, Channels.NotificationChannelForInfo)
            # if reader was started then close it
            if self.reader != None:
                self.reader.close()
            # tell reader thread that we are done
            self.thread_running = False
            # wait for thread to catch up
            sleep(2)
            # close discord bot
            await self.close()
            _message = "Overworld Discord Bot has stopped."
            await self.send_discord_msg(_message, Channels.NotificationChannelForInfo)

    def configure(self, cfg_json):
        self.config = cfg_json
        self.is_configured = True

    async def send_discord_event(self, embed, file, channel_id):
        channel = self.get_channel(int(channel_id))
        asyncio.run_coroutine_threadsafe(channel.send(embed=embed,file=file),self.loop)

    async def send_discord_msg(self, message, destination=Channels.NoChannel):
        _channel_id = None
        if destination == Channels.NotificationChannelForInfo:
            _channel_id = self.config["NotificationChannelForInfo"]
        elif destination == Channels.EventNotificationChannelIdForShiny:
            _channel_id = self.config["EventNotificationChannelIdForShiny"]
        elif destination == Channels.EventNotificationChannelIdForBrilliant:
            _channel_id = self.config["EventNotificationChannelIdForBrilliant"]
        elif destination == Channels.EventNotificationChannelIdForMark:
            _channel_id = self.config["EventNotificationChannelIdForMark"]
        elif destination == Channels.EventNotificationChannelIdForRareMark:
            _channel_id = self.config["EventNotificationChannelIdForRareMark"]
        elif destination == Channels.TextNotificationChannelIdForShiny:
            _channel_id = self.config["TextNotificationChannelIdForShiny"]
        elif destination == Channels.TextNotificationChannelIdForBrilliant:
            _channel_id = self.config["TextNotificationChannelIdForBrilliant"]
        elif destination == Channels.TextNotificationChannelIdForMark:
            _channel_id = self.config["TextNotificationChannelIdForMark"]
        elif destination == Channels.TextNotificationChannelIdForRareMark:
            _channel_id = self.config["TextNotificationChannelIdForRareMark"]
        if _channel_id:
            channel = self.get_channel(int(_channel_id))
            print("{}: {}".format(channel.name, message))
            await channel.send(message)
        else:
            print("LocalOnly: {}".format(message))

    # function to be run in the new thread after start is called
    def reader_func(self,ctx):
        # config to refactor out later
        # color for the line on the side of the embed, 0xfad1ff is pink
        embed_color = 0xfad1ff
        # used to verify that the read mons are new
        last_check = 0
        while True:
            # check if we are supposed to be running
            if not self.thread_running:
                exit()
            # refresh KCoords block
            try:
                self.reader.KCoordinates.refresh()
            except Exception:
                print("No connection to Switch at IP {}. Check that the Switch is available.".format(self.config["IP"]))
                break
            # read pokemon
            pkms = self.reader.KCoordinates.ReadOwPokemonFromBlock()
            # check if the read pokemon are different
            if len(pkms) > 0 and pkms[-1].ec != last_check:
                # set last check
                last_check = pkms[-1].ec
                # for each pkm check for filter
                for pkm in pkms:
                    # Determine if the pokemon info should be an event notification, and where it routes to. Send text notifications inline.
                    _channels_to_notify = []
                    if is_pkm_shiny(pkm):
                        _event_channel_id = self.config["EventNotificationChannelIdForShiny"]
                        if len(_event_channel_id) > 0:
                            _channels_to_notify.append(_event_channel_id)
                        _text_channel_id = self.config["TextNotificationChannelIdForShiny"]
                        if len(_text_channel_id) > 0:
                            _message = "Shiny {} detected!".format(get_pkm_species_string(pkm))
                            asyncio.run_coroutine_threadsafe(self.send_discord_msg(_message, Channels.TextNotificationChannelIdForShiny),self.loop)
                    if is_pkm_brilliant(pkm):
                        _event_channel_id = self.config["EventNotificationChannelIdForBrilliant"]
                        if len(_event_channel_id) > 0:
                            _channels_to_notify.append(_event_channel_id)
                        _text_channel_id = self.config["TextNotificationChannelIdForBrilliant"]
                        if len(_text_channel_id) > 0:
                            _message = "Brilliant {} detected!".format(get_pkm_species_string(pkm))
                            asyncio.run_coroutine_threadsafe(self.send_discord_msg(_message, Channels.TextNotificationChannelIdForBrilliant),self.loop)
                    if is_pkm_rare(pkm):
                        _event_channel_id = self.config["EventNotificationChannelIdForRareMark"]
                        if len(_event_channel_id) > 0:
                            _channels_to_notify.append(_event_channel_id)
                        _text_channel_id = self.config["TextNotificationChannelIdForRareMark"]
                        if len(_text_channel_id) > 0:
                            _message = "Rare Mark {} detected!".format(get_pkm_species_string(pkm))
                            asyncio.run_coroutine_threadsafe(self.send_discord_msg(_message, Channels.TextNotificationChannelIdForRareMark),self.loop)
                    if is_pkm_marked(pkm):
                        _event_channel_id = self.config["EventNotificationChannelIdForMark"]
                        if len(_event_channel_id) > 0:
                            _channels_to_notify.append(_event_channel_id)
                        _text_channel_id = self.config["TextNotificationChannelIdForMark"]
                        if len(_text_channel_id) > 0:
                            _message = "{} Mark {} detected!".format(get_pkm_mark_string(pkm), get_pkm_species_string(pkm))
                            asyncio.run_coroutine_threadsafe(self.send_discord_msg(_message, Channels.TextNotificationChannelIdForMark),self.loop)
                    
                    # Remove duplicate channel IDs from the list.
                    _channels_to_notify = list(set(_channels_to_notify))
                    if _channels_to_notify and strtobool(self.config["EnableDebugLogging"]):
                        print("DEBUG: Channels to notify are: {}".format(_channels_to_notify))

                    # If we are notifying at least one channel ...
                    if _channels_to_notify:
                        # if so, format to strings
                        title, description = pkm_format(pkm, ctx)
                        # create discord embed object with the color specified
                        embed=discord.Embed(color=embed_color)
                        # add pkm strings as a field
                        embed.add_field(name = title, value = description, inline=False)
                        with io.BytesIO() as image_binary:
                            # pull pokemon image
                            get_pokemon(pkm.species, pkm.shinyType).save(image_binary, 'PNG')
                            image_binary.seek(0)
                            # save to a discord file
                            file = discord.File(fp=image_binary, filename='image.png')
                        # set embed thumbnail to the attached discord file
                        embed.set_thumbnail(url="attachment://image.png")
                        
                        # send a message in channel start was called with the infomation of the pokemon
                        # asyncio.run_coroutine_threadsafe(ctx.send(embed=embed,file=file),self.loop)
                        for channel_id in _channels_to_notify:
                            asyncio.run_coroutine_threadsafe(self.send_discord_event(embed, file, channel_id),self.loop)
                # print a line to show that new pokemon have just been read
                _message = "{} Pokemon Observed".format(len(pkms))
                asyncio.run_coroutine_threadsafe(self.send_discord_msg(_message, Channels.NotificationChannelForInfo),self.loop)
            # give the thread a break
            self.reader.pause(0.3)

def is_pkm_shiny(pkm):
    return pkm.shinyType != 0

def is_pkm_brilliant(pkm):
    return pkm.brilliant

def is_pkm_marked(pkm):
    return pkm.mark > 52 and pkm.mark < 98 and pkm.mark != 69

def is_pkm_rare(pkm):
    return pkm.mark == 69

def get_pkm_species_string(pkm):
    return Util.STRINGS.species[pkm.species] + (('-' + str(pkm.altForm)) if pkm.altForm > 0 else '')

def get_pkm_mark_string(pkm):
    return 'No Mark' if pkm.mark == 255 else pkm.Ribbons[pkm.mark]

# function that formats the pkm into a title string and a description string for discord embeds
def pkm_format(pkm, context):
    # get strings from pkm to use
    # 1/2/H
    ability_string = str(pkm.ability) if pkm.ability < 4 else 'H'
    # Brilliant/Not Brilliant
    brilliant_string = 'Brilliant' if pkm.brilliant else 'Not Brilliant'
    # ♂/♀/-
    gender_emoji = Util.GenderSymbol[pkm.gender-1]
    # X/X/X/X/X/X
    ivs_string = '/'.join(str(x) for x in pkm.ivs)
    # pulls an emoji from the current server with the id of the mark as its name
    # will throw an error unless you have all the marks as emojis
    mark_emoji = (str(get(context.message.guild.emojis, name=str(pkm.mark))) + ' ') if pkm.mark != 255 else ''
    # No Mark/Mark Name
    mark_string = get_pkm_mark_string(pkm)
    # Nature string (Jolly,Adamant,Timid,etc.)
    nature_string = Util.STRINGS.natures[pkm.nature]
    #  /⋆/◇
    shiny_string = '' if pkm.shinyType == 0 else '⋆ ' if pkm.shinyType == 1 else '◇ '
    # Species-Form Number (Articuno-1 for GCuno)
    species_string = get_pkm_species_string(pkm)

    # format of the title
    title = f"{mark_emoji}{gender_emoji} {shiny_string} {species_string}"
    # format of the description
    description = f"{nature_string} {ability_string}\n{ivs_string}\n{mark_string}\n{brilliant_string}"

    return title, description

# function to pull pokemon images from pokebase, has a cache since the same pokemon tend to spawn in an area
@lru_cache(maxsize=32)
def get_pokemon(species,shiny):
    image_bytes = pb.SpriteResource('pokemon', species, shiny=shiny).img_data
    im = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    return im
