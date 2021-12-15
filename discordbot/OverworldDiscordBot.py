import asyncio
import discord
import itertools
import io
import json
import os.path
import platform
import pokebase as pb
import socket
import sys
from datetime import datetime
from discord.ext import commands
from discord.utils import get
from distutils.util import strtobool
from enum import Enum
from functools import lru_cache
from PIL import Image
from threading import Thread
from time import sleep, time


sys.path.append('../')
from lookups import Util
from nxreader import SWSHReader
from structure.PK8Overworld import PK8

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

class Config:
    def __init__(self, path):
        self.json = json.load(open(path))
        self.path = path
    
    def save(self):
        json.dump(self.json, open(self.path,"w"), indent=4)
    
    def __getitem__(self,key):
        return self.json[key]
    
    def __setitem__(self,key,value):
        self.json[key] = value
        self.save()

class Statistics:
    def __init__(self):
        self.total_count = 0
        self.shiny_count = 0
        self.brilliant_count = 0
        self.total_mark_count = 0
        self.rare_mark_count = 0
        self.personality_mark_count = 0
        self.time_mark_count = 0
        self.weather_mark_count = 0
        self.pokemon = {}
        self.start_time = time()
        self.encounter_cache = b''
        self.save_file_name = datetime.now().strftime('%Y%m%d%H%M%S')

    @property
    def run_time(self):
        return time() - self.start_time

    def percent(self,stat):
        if self.total_count != 0:
            return round((stat/self.total_count)*100,2)
        else:
            return 0

    def __str__(self):
        newline = '\n'
        sorted_pokemon = dict(sorted(self.pokemon.items(), key=lambda item: item[1], reverse=True))
        first_ten = dict(itertools.islice(sorted_pokemon.items(), 10))
        
        return f"""Time Running: {round(self.run_time,2)}s
        Shiny Count: {self.shiny_count} {self.percent(self.shiny_count)}%
        Brilliant Count: {self.brilliant_count} {self.percent(self.brilliant_count)}%
        Total Mark Count: {self.total_mark_count} {self.percent(self.total_mark_count)}%
        Rare Mark Count: {self.rare_mark_count} {self.percent(self.rare_mark_count)}%
        Personality Mark Count: {self.personality_mark_count} {self.percent(self.personality_mark_count)}%
        Time Mark Count: {self.time_mark_count} {self.percent(self.time_mark_count)}%
        Weather Mark Count: {self.weather_mark_count} {self.percent(self.weather_mark_count)}%
        {newline.join([(f'{Util.STRINGS.species[index]} {self.pokemon[index]} {self.percent(self.pokemon[index])}%') for index in first_ten])}
        Total Encounters: {self.total_count}
        """.replace("        ","")
    
    def save(self):
        with open(self.save_file_name + ".encounters", "ab+") as f:
            f.write(self.encounter_cache)
        self.encounter_cache = b''

    def add_pkm(self, pkm, save = True):
        self.total_count += 1
        if self.is_pkm_shiny(pkm):
            self.shiny_count += 1
        if self.is_pkm_brilliant(pkm):
            self.brilliant_count += 1
        if self.is_pkm_marked(pkm):
            self.total_mark_count += 1
        if self.is_pkm_rare_marked(pkm):
            self.total_mark_count += 1
            self.rare_mark_count += 1
        if self.is_pkm_personality_marked(pkm):
            self.personality_mark_count += 1
        if self.is_pkm_time_marked(pkm):
            self.time_mark_count += 1
        if self.is_pkm_weather_marked(pkm):
            self.weather_mark_count += 1
        if pkm.species in self.pokemon:
            self.pokemon[pkm.species] += 1
        else:
            self.pokemon[pkm.species] = 1
        if save:
            self.encounter_cache += bytes(pkm.data)
            if len(self.encounter_cache) >= 56*100:
                self.save()
    
    @staticmethod
    def is_pkm_shiny(pkm):
        return pkm.shinyType != 0
    
    @staticmethod
    def is_pkm_brilliant(pkm):
        return pkm.brilliant
    
    @staticmethod
    def is_pkm_marked(pkm):
        return pkm.mark != 255 and pkm.mark != 69
    
    @staticmethod
    def is_pkm_personality_marked(pkm):
        return pkm.mark != 255 and pkm.mark >= 70
    
    @staticmethod
    def is_pkm_time_marked(pkm):
        return pkm.mark <= 56
    
    @staticmethod
    def is_pkm_weather_marked(pkm):
        return pkm.mark >= 57 and pkm.mark <= 64
    
    @staticmethod
    def is_pkm_rare_marked(pkm):
        return pkm.mark == 69

class OverworldDiscordBot(commands.Bot):
    def __init__(self, config_path):
        # we do this to avoid "RuntimeError: Event loop is closed" on shutdown
        if platform.system() == 'Windows':
	        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # Default values for variables as to not throw errors.
        self.thread = None
        self.thread_running = False
        self.reader = None
        self.config = Config(config_path)
        self.stats = Statistics()
        super().__init__(command_prefix=self.config["DiscordBotPrefix"])

        # function to run when the bot is "ready"
        @self.event
        async def on_ready():
            # tell user in console that the bot is ready
            message = "Discord Bot has started."
            await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
            # change bot presence to "Watching some ram for shinies"
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="some ram for shinies"))

        # function to run whenever the configure command is called
        @self.command()
        async def configure(ctx, key, value):
            try:
                self.config[key] = value
                message = f"Config[\"{key}\"] = \"{value}\""
                await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
            except Exception as e:
                message = f"Unable to set value, ```{e}```"
                await self.send_discord_msg(message, Channels.NotificationChannelForInfo)

        # function to run whenever the start command is called
        @self.command()
        async def start(ctx):
            # create reader object
            try:
                self.reader = SWSHReader(self.config["IP"],usb_connection=self.config["USB"])
                # create and start a thread for reading from the switch
                self.thread_running = True
                self.thread = Thread(target=self.reader_func,args=(ctx,))
                self.thread.start()
                message = "Reader has started."
                await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
            except socket.timeout:
                message = f"Unable to connect to IP {self.config['IP']}. Check that the Switch is available."
                await self.send_discord_msg(message, Channels.NotificationChannelForInfo)

        # function to run whenever the ping command is called
        @self.command()
        async def ping(ctx):
            # say the bots latency in discord channel
            await ctx.send(f'Pong! {round(self.latency, 3)}')
        
        # function to run whenever shutdown command is called, stops reader and discord bot
        @self.command()
        async def shutdown(ctx,):
            message = "Discord Bot is shutting down..."
            await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
            # stop reader
            await stop(ctx)
            # wait for thread to catch up
            sleep(2)
            # close discord bot
            await self.close()

        # function to run whenever stop command is called, stops reader but keeps discord bot alive
        @self.command()
        async def stop(ctx):
            self.stats.save()
            # tell user in console that we are now stopping
            message = "Reader is stopping..."
            await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
            # if reader was started then close it
            try:
                self.reader.close(False)
            except:
                print("Failure to close the reader as it is already closed. Ignoring.")
            # tell reader thread that we are done
            self.thread_running = False
            message = "Reader has stopped."
            await self.send_discord_msg(message, Channels.NotificationChannelForInfo)

        # function to run whenever restart command is called, restarts reader but keeps discord bot alive
        @self.command()
        async def restart(ctx):
            # tell user in console that we are now restarting
            message = "Reader is restarting..."
            await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
            await stop(ctx)
            await start(ctx)
        
        # function to run whenever download_emoji command is called, adds all mark emojis to the current server
        @self.command()
        async def download_emoji(ctx):
            # color for the line on the side of the embed, 0xfad1ff is pink
            embed_color = 0xfad1ff
            embed=discord.Embed(color=embed_color)
            embed.add_field(name = "Download Emojis", value = "Download the mark zip attached and drag and drop them into your emojis", inline = False)
            await self.send_discord_event(embed, discord.File("../resources/marks.zip"), ctx.channel.id)
        
        # function to run whenever stats command is called, displays statistics
        @self.command()
        async def stats(ctx):
            # color for the line on the side of the embed, 0xfad1ff is pink
            embed_color = 0xfad1ff
            embed=discord.Embed(color=embed_color)
            embed.add_field(name = "Statistics", value = str(self.stats), inline = False)
            await self.send_discord_event(embed, None, ctx.channel.id)
        
        # function to run whenever save_stats command is called, saves current stats
        @self.command()
        async def save_stats(ctx):
            self.stats.save()
            message = "Stats Saved."
            await self.send_discord_msg(message, Channels.NotificationChannelForInfo)
        
        # function to run whenever list_stats command is called, lists all .encounter files
        @self.command()
        async def list_stats(ctx):
            embed_color = 0xfad1ff
            embed=discord.Embed(color=embed_color)
            list_str = "----------------------------------------------------------------"
            for file in os.listdir(os.path.join(os.path.dirname(__file__),"../tests/")):
                if file.endswith(".encounters"):
                    list_str += f"\n{os.path.getsize(os.path.join(os.path.dirname(__file__),f'../tests/{file}'))//56} Encounters, {file}"
            embed.add_field(name = "Backups", value = list_str, inline = False)
            await self.send_discord_event(embed, None, ctx.channel.id)
        
        # function to run whenever load_stats command is called, replaces self.stats with backup
        @self.command()
        async def load_stats(ctx,filename):
            if not self.thread_running:
                await self.send_discord_msg("No reader connected", Channels.NotificationChannelForInfo)
                return
            await self.send_discord_msg("Loading stats...", Channels.NotificationChannelForInfo)
            self.stats = Statistics()
            self.stats.save_file_name = filename.split(".encounters")[0]
            with open(os.path.join(os.path.dirname(__file__),f"../tests/{filename}"), "rb") as backup:
                i = 0
                total = os.path.getsize(os.path.join(os.path.dirname(__file__),f'../tests/{filename}'))
                while i < total:
                    pkm = PK8(list(backup.read(56)),0,0)
                    self.stats.add_pkm(pkm,False)
                    i += 56
            await self.send_discord_msg("Stats Loaded.", Channels.NotificationChannelForInfo)

    async def send_discord_event(self, embed, file, channel_id):
        channel = self.get_channel(int(channel_id))
        return await channel.send(embed=embed,file=file)

    async def send_discord_msg(self, message, destination=Channels.NoChannel):
        channel_id = None
        if destination == Channels.NotificationChannelForInfo:
            channel_id = self.config["NotificationChannelForInfo"]
        elif destination == Channels.EventNotificationChannelIdForShiny:
            channel_id = self.config["EventNotificationChannelIdForShiny"]
        elif destination == Channels.EventNotificationChannelIdForBrilliant:
            channel_id = self.config["EventNotificationChannelIdForBrilliant"]
        elif destination == Channels.EventNotificationChannelIdForMark:
            channel_id = self.config["EventNotificationChannelIdForMark"]
        elif destination == Channels.EventNotificationChannelIdForRareMark:
            channel_id = self.config["EventNotificationChannelIdForRareMark"]
        elif destination == Channels.TextNotificationChannelIdForShiny:
            channel_id = self.config["TextNotificationChannelIdForShiny"]
        elif destination == Channels.TextNotificationChannelIdForBrilliant:
            channel_id = self.config["TextNotificationChannelIdForBrilliant"]
        elif destination == Channels.TextNotificationChannelIdForMark:
            channel_id = self.config["TextNotificationChannelIdForMark"]
        elif destination == Channels.TextNotificationChannelIdForRareMark:
            channel_id = self.config["TextNotificationChannelIdForRareMark"]
        if channel_id:
            channel = self.get_channel(int(channel_id.replace("<#","").replace(">","")))
            print(f"{channel.name}: {message}")
            return await channel.send(message)
        else:
            print(f"LocalOnly: {message}")

    # function to be run in the new thread after start is called
    def reader_func(self,ctx):
        # config to refactor out later
        # color for the line on the side of the embed, 0xfad1ff is pink
        embed_color = 0xfad1ff
        # used to verify that the read mons are new
        last_check = []
        while True:
            # check if we are supposed to be running
            if not self.thread_running:
                break
            # refresh KCoords block
            pkms = None
            try:
                self.reader.KCoordinates.refresh()
                # read pokemon
                pkms = self.reader.KCoordinates.ReadOwPokemonFromBlock()
            # if an exception happened the connection to the switch has likely been severed
            except Exception:
                # if we are supposed to be running then log that a disconnect happened
                if self.thread_running:
                    self.thread_running = False
                    print(f"No connection to Switch at IP {self.config['IP']}. Check that the Switch is available.")
                break
            # check if the read pokemon are different
            if len(pkms) > 0 and [pkm.ec for pkm in pkms] != last_check:
                # for each pkm check for filter
                for pkm in pkms:
                    # check if pokemon is new
                    if not pkm.ec in last_check:
                        # add it to the statistics
                        self.stats.add_pkm(pkm)
                        # Determine if the pokemon info should be an event notification, and where it routes to. Send text notifications inline.
                        channels_to_notify = []
                        if Statistics.is_pkm_shiny(pkm):
                            eventchannel_id = self.config["EventNotificationChannelIdForShiny"]
                            if len(eventchannel_id) > 0:
                                channels_to_notify.append(eventchannel_id)
                            textchannel_id = self.config["TextNotificationChannelIdForShiny"]
                            if len(textchannel_id) > 0:
                                message = f"Shiny {get_pkm_species_string(pkm)} detected!"
                                asyncio.run_coroutine_threadsafe(self.send_discord_msg(message, Channels.TextNotificationChannelIdForShiny),self.loop)
                        if Statistics.is_pkm_brilliant(pkm):
                            eventchannel_id = self.config["EventNotificationChannelIdForBrilliant"]
                            if len(eventchannel_id) > 0:
                                channels_to_notify.append(eventchannel_id)
                            textchannel_id = self.config["TextNotificationChannelIdForBrilliant"]
                            if len(textchannel_id) > 0:
                                message = f"Brilliant {get_pkm_species_string(pkm)} detected!"
                                asyncio.run_coroutine_threadsafe(self.send_discord_msg(message, Channels.TextNotificationChannelIdForBrilliant),self.loop)
                        if Statistics.is_pkm_rare_marked(pkm):
                            eventchannel_id = self.config["EventNotificationChannelIdForRareMark"]
                            if len(eventchannel_id) > 0:
                                channels_to_notify.append(eventchannel_id)
                            textchannel_id = self.config["TextNotificationChannelIdForRareMark"]
                            if len(textchannel_id) > 0:
                                message = f"Rare Mark {get_pkm_species_string(pkm)} detected!"
                                asyncio.run_coroutine_threadsafe(self.send_discord_msg(message, Channels.TextNotificationChannelIdForRareMark),self.loop)
                        if Statistics.is_pkm_marked(pkm):
                            eventchannel_id = self.config["EventNotificationChannelIdForMark"]
                            if len(eventchannel_id) > 0:
                                channels_to_notify.append(eventchannel_id)
                            textchannel_id = self.config["TextNotificationChannelIdForMark"]
                            if len(textchannel_id) > 0:
                                message = f"{get_pkm_mark_string(pkm)} Mark {get_pkm_species_string(pkm)} detected!"
                                asyncio.run_coroutine_threadsafe(self.send_discord_msg(message, Channels.TextNotificationChannelIdForMark),self.loop)
                        
                        # Remove duplicate channel IDs from the list.
                        channels_to_notify = list(set(channels_to_notify))
                        if channels_to_notify and strtobool(self.config["EnableDebugLogging"]):
                            print(f"DEBUG: Channels to notify are: {channels_to_notify}")

                        # If we are notifying at least one channel ...
                        if channels_to_notify:
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
                            for channel_id in channels_to_notify:
                                asyncio.run_coroutine_threadsafe(self.send_discord_event(embed, file, channel_id),self.loop)
                # print a line to show that new pokemon have just been read
                message = f"{len(pkms)} Pokemon Observed"
                asyncio.run_coroutine_threadsafe(self.send_discord_msg(message, Channels.NotificationChannelForInfo),self.loop)
                # set last check
                last_check = [pkm.ec for pkm in pkms]
            # give the thread a break
            self.reader.pause(0.3)

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
