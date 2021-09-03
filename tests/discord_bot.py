# Example of using discord.py with pynx
# needs a discord bot account and a server with all the mark ids as emojis

import asyncio
import discord
import io
import json
import pokebase as pb
import sys
from discord.ext import commands
from discord.utils import get
from functools import lru_cache
from PIL import Image
from threading import Thread
from time import sleep

sys.path.append('../')
from lookups import Util
from nxreader import SWSHReader


# config

# put your discord bot's token here
TOKEN = ""
# color for the line on the side of the embed, 0xfad1ff is pink
embed_color = 0xfad1ff
# prefix for bot commands
bot_prefix = "$"

# function that determines whether or not to send a pkm to your discord channel
def pkm_filter(pkm):
    # if pkm is shiny
    if pkm.shinyType != 0:
        return True
    # or if it has rare mark (internal id 69)
    if pkm.mark == 69:
        return True
    # or if it has a brilliant aura
    if pkm.brilliant:
        return True
    # if none of the above are true return false
    return False

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
    mark_string = 'No Mark' if pkm.mark == 255 else pkm.Ribbons[pkm.mark]
    # Nature string (Jolly,Adamant,Timid,etc.)
    nature_string = Util.STRINGS.natures[pkm.nature]
    #  /⋆/◇
    shiny_string = '' if pkm.shinyType == 0 else '⋆ ' if pkm.shinyType == 1 else '◇ '
    # Species-Form Number (Articuno-1 for GCuno)
    species_string = Util.STRINGS.species[pkm.species] + (('-' + str(pkm.altForm)) if pkm.altForm > 0 else '')

    # format of the title
    title = f"{mark_emoji}{gender_emoji} {shiny_string} {species_string}"
    # format of the description
    description = f"{nature_string} {ability_string}\n{ivs_string}\n{mark_string}\n{brilliant_string}"

    return title, description

# config end

# function to pull pokemon images from pokebase, has a cache since the same pokemon tend to spawn in an area
@lru_cache(maxsize=32)
def get_pokemon(species,shiny):
    image_bytes = pb.SpriteResource('pokemon', species, shiny=shiny).img_data
    im = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    return im

# class for the bot, inherits from commands.Bot
class Bot(commands.Bot):
    def __init__(self):
        # set up commands.Bot with specified prefix
        super().__init__(command_prefix=bot_prefix)
        # default values for variables as to not throw errors
        self.thread = None
        self.thread_running = True
        self.reader = None
        # function to run when the bot is "ready"
        @self.event
        async def on_ready():
            # tell user in console that the bot is ready
            print("Logged in!")
            # change bot presence to "Watching some ram for shinies"
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="some ram for shinies"))
        # function to run whenever the start command is called
        @self.command()
        async def start(ctx):
            # create reader object
            config = json.load(open("../config.json"))
            self.reader = SWSHReader(config["IP"])
            # create and start a thread for reading from the switch
            self.thread = Thread(target=self.reader_func,args=(ctx,))
            self.thread.start()
        # function to run whenever the ping command is called
        @self.command()
        async def ping(ctx):
            # say the bots latency in discord channel
            await ctx.send(f'Pong! {round(self.latency, 3)}')
        # function to run whenever stop command is called, stops reader and discord bot
        @self.command()
        async def stop(ctx):
            # tell user in console that we are now stopping
            print("Stopping")
            # if reader was started then close it
            if self.reader != None:
                self.reader.close()
            # tell reader thread that we are done
            self.thread_running = False
            # wait for thread to catch up
            sleep(2)
            # close discord bot
            await self.close()
            print("Stopped.")
    # function to be run in the new thread after start is called
    def reader_func(self,ctx):
        # used to verify that the read mons are new
        last_check = 0
        while True:
            # check if we are supposed to be running
            if not self.thread_running:
                exit()
            # refresh KCoords block
            self.reader.KCoordinates.refresh()
            # read pokemon
            pkms = self.reader.KCoordinates.ReadOwPokemonFromBlock()
            # check if the read pokemon are different
            if len(pkms) > 0 and pkms[-1].ec != last_check:
                # set last check
                last_check = pkms[-1].ec
                # for each pkm check for filter
                for pkm in pkms:
                    # check if pkm matches our definied filter
                    if pkm_filter(pkm):
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
                        asyncio.run_coroutine_threadsafe(ctx.send(embed=embed,file=file),self.loop)
                # print a line to show that new pokemon have just been read
                print("-------------------------------")
            # give the thread a break
            self.reader.pause(0.3)

# start bot
bot = Bot()
bot.run(TOKEN)
