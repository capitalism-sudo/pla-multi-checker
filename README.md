# PyNXReader
 Python Lib for reading information from Pokemon Sword and Shield and LGPE

 This library is more focused on reading information for hunting/overlays/just knowing the info as opposed to botting.

 This is a fork of PyNXBot by [wwwwwwzx](https://github.com/wwwwwwzx) so credit to them and other who worked on the original project!

## Warning
 I won't be liable if your Switch get damaged or banned. Use at your own risk.

## Images
 ![PyNXReader](./PyNXReader_Screenshot.png)
 ![OverworldReader](./OverworldReader_Screenshot.png)
 ![DenReader](./DenReader_Screenshot.png)
 ![LGPEReader](./LGPEReader_Screenshot.png)

## Features
 * Check Den info
 * Check Wild Pokémon info
 * Check Legendary Pokémon info
 * Check Calyrex Fusion Pokémon info
 * Check Party Pokémon info
 * Check Box Pokémon info
 * Check Save info
 * Check Overworld Pokémon info
 * Check LGPE Battle/Trade/Gift/Legendary/Active (Summary Screen, etc.) Pokémon info

## Requirements
* [Python](https://www.python.org/downloads/)
	* Install z3-solver, pyserial, pillow, and pokebase via [pip](https://pip.pypa.io/en/stable/) if `ImportError` happens.
	   `pip install z3-solver` 
	   `pip install pyserial`
	   `pip install pillow`
	   `pip install pokebase`
* CFW
* Internet Connection
* [sys-botbase](https://github.com/olliz0r/sys-botbase)
* [joycon-sys-botbase](https://github.com/Manu098vm/sys-botbase) For LGPE
* [ldn_mitm](https://github.com/spacemeowx2/ldn_mitm)

## Usage
* The scripts to run are contained in the ./scripts/ folder
* Use [CaptureSight](https://github.com/zaksabeast/CaptureSight/)/CheckDen script to check your Den id for the Den scripts
* Scripts labeled "Check'name'.py" will display info on that type of encounter in the console
* "GUIReader.py" Is the script you need to run if you want GUI reading of Wild/Legendary/Fusion Pokémon for SWSH or Battle/Trade/Gift/Legendary/Active Pokémon for LGPE.
* "GUIOverworld.py" Is the script you need to run if you want GUI reading of Overworld Pokémon
* The other scripts are for dumping info and can be mostly ignored for the average person

### Usage: Overworld Scanner Discord Bot
Prerequisite of a discord bot account and a discord server with all the mark ids as emojis.

In order to run the bot do the following:
1. Copy *config.template.json* to *config.json*
1. Fill out *config.json* with appropriate values.
1. Execute *tests/OverworldDiscordBot.py*
1. From the discord server, run the *$start* command to start the bot's main scanner thread.

## Credits:
* olliz0r for his great [sys-botbase](https://github.com/olliz0r/sys-botbase) which let open sockets on the Nintendo Switch
* spacemeowx2 for his livesafer [sys-module](https://github.com/spacemeowx2/ldn_mitm). It avoids Switch to disconnect from wifi once game is opened
* Admiral-Fish for his great app [RaidFinder](https://github.com/Admiral-Fish/RaidFinder) always up to date
* zaksabeast for his great SwSh Switch tool [CaptureSight](https://github.com/zaksabeast/CaptureSight/) (many addresses/checks are taken from there)
* Leanny for his great plugin [PKHeX_Raid_Plugin](https://github.com/Leanny/PKHeX_Raid_Plugin/tree/master/PKHeX_Raid_Plugin) (many addresses/checks are taken from there)
* Kurt for his great app [SysBot.NET](https://github.com/kwsch/SysBot.NET) (many addresses/checks are taken from there)
* [wwwwwwzx](https://github.com/wwwwwwzx) for creating and working on the original project
* [Real96](https://github.com/Real96) for working on the original project
* [Manu098](https://github.com/Manu098vm/) for Sys-EncounterBot (many addresses/checks are taken from there)

## Possible Future Improvements
* Expand discord bot readme section to include a comprehensive guide
* Cleanup: Set embed_color via config file.
* Cleanup: Set bot_prefix via config file.
* Cleanup: Migrate non-class utility functions to a utility class.
* Feature: Update the configuration and reload it via discord command
* Feature: Bot command to install emoji pack in a discord server
* Feature: Add a filtering class to enable complex filters instead of a set of flags
* Feature: Save statistics and display aggregate stats. Examples include: pokemon encounters, mark #s, shiny #s, etc.
* Feature: Use the bot "activity" to update how many overworld pokemon have been scanned
* Feature: include watchers to ping alongside filters. Is this useful for a bot attached to a single switch?
* Feature: Make changing the formatting on the event cards easy for non-technical users.