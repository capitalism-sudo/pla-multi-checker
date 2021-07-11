# PyNXReader
 Python Lib for reading information from Pokemon Sword and Shield and LGPE as well as sending inputs to the switch (to play with a different controller etc.)

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
* [sys-botbase](https://github.com/olliz0r/sys-botbase) 1.5
* [ldn_mitm](https://github.com/spacemeowx2/ldn_mitm)
* [joycon-sys-botbase](https://github.com/Manu098vm/sys-botbase) If you want to control LGPE

## Usage
* Use [CaptureSight](https://github.com/zaksabeast/CaptureSight/)/CheckDen script to check your Den id for the Den scripts
* Scripts labeled "Check<name>.py" will display info on that type of encounter in the console
* "GUIReader.py" Is the script you need to run if you want GUI reading of Wild/Legendary/Fusion Pokémon for SWSH or Battle/Trade/Gift/Legendary/Active Pokémon for LGPE.
* "OverworldReader.py" Is the script you need to run if you want GUI reading of Overworld Pokémon
* The other scripts are for dumping info and can be mostly ignored for the average person

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
