import io
import json
import signal
import sys
import tkinter as tk
import pokebase as pb

# Go to root of PyNXReader
sys.path.append('../')

from lookups import Util
from nxreader import RaidReader
from PIL import Image, ImageTk
from rng import XOROSHIRO,Raid
from structure import Den
from gui import setup_styles
from tkinter import ttk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config = json.load(open("../config.json"))
        self.master = master
        self.pack()
        self.create_widgets()
        self.last_info = ""
        signal.signal(signal.SIGINT, self.signal_handler)

    def create_widgets(self):
        setup_styles()
        self.master.title("Den Reader")
        self.type_var = tk.IntVar()
        self.connect_button = ttk.Button(self, text="Connect", style="Connect.TButton", command=self.connect)
        self.connect_button.grid(column=0,row=1)
        self.den_input = tk.Entry(self)
        self.den_input.insert(10,"0")
        self.den_input.grid(column=0,row=5,columnspan=2)
        self.current_info_display = tk.Text(self,height=9)
        self.current_info_display.grid(column=3, row=2, rowspan=3)
        self.next_info_display = tk.Text(self,height=9)
        self.next_info_display.grid(column=3, row=5)
        self.image_display = tk.Label(self)
        self.image_display.grid(column=1, row=2, columnspan=2, rowspan=3)
        self.galar_choice = ttk.Radiobutton(self, text="Galar", variable=self.type_var, value=1)
        self.ioa_choice = ttk.Radiobutton(self, text="IOA", variable=self.type_var, value=2)
        self.ct_choice = ttk.Radiobutton(self, text="CT", variable=self.type_var, value=3)
        self.galar_choice.grid(column=0, row=2, columnspan=1, rowspan=1)
        self.ioa_choice.grid(column=0, row=3, columnspan=1, rowspan=1)
        self.ct_choice.grid(column=0, row=4, columnspan=1, rowspan=1)
        self.quit = ttk.Button(self, text="Disconnect", style="Disconnect.TButton", command=self.disconnect)
        self.quit.grid(column=1,row=1)

    def connect(self):
        print("Connecting to: "+(self.config["IP"] if not self.config["USB"] else "USB"))
        self.RaidReader = RaidReader(self.config["IP"],usb_connection=self.config["USB"])
        self.update()

    def disconnect(self):
        print("Disconnecting")
        self.after_cancel(self.after_token)
        self.RaidReader.close(False)
        self.RaidReader = None
    
    def signal_handler(self, signal, frame):
        self.disconnect()
        sys.exit(0)
    
    def update(self):
        try:
            seed = None
            IOA = self.type_var.get() == 2
            CT = self.type_var.get() == 3
            if IOA:
                add1 = 99
                add2 = 11
            elif CT:
                add1 = 189
                add2 = 32
            else:
                add1 = -1
                add2 = 0
            den = Den(self.RaidReader.readDen(add1 + int(self.den_input.get()) + add2))
            if den.isRare():
                beam = "Rare"
            elif den.isEvent():
                beam = "Event"
            else:
                beam = "Normal"
            info = f"denID: {int(self.den_input.get())}"
            spawn = den.getSpawn(denID = add1 + int(self.den_input.get()), isSword = self.RaidReader.isPlayingSword)
            currShinyLock = 0
            info += f"    {den.stars()}★    Species: {Util.STRINGS.species[spawn.Species()]}"
            if spawn.IsGigantamax():
                info += " G-Max"
            if den.isEvent():
                info += "    Event"
                currShinyLock = spawn.ShinyFlag()
            if den.isWishingPiece():
                if currShinyLock != 2:
                    info += f"    Next Shiny Frame: {Raid.getNextShinyFrame(den.seed())}"
                else:
                    info += f"    Next Shiny Frame: 0"
                seed = den.seed()
                info = "!!! " + info
                piecedSpawn = spawn
                piecedShinyLock = currShinyLock
            if info != self.last_info:
                print(info)
                r = Raid(seed = den.seed(), TID = self.RaidReader.TID, SID = self.RaidReader.SID, flawlessiv = spawn.FlawlessIVs(), shinyLock = currShinyLock, ability = spawn.Ability(), gender = spawn.Gender(), species = spawn.Species(), altform = spawn.AltForm())
                r.print()
                print(self.RaidReader.TID, self.RaidReader.SID)
                shiny_seed = den.seed()
                for _ in range(Raid.getNextShinyFrame(den.seed())):
                    rm = XOROSHIRO(shiny_seed)
                    shiny_seed = rm.next()
                rshiny = Raid(seed = shiny_seed, TID = self.RaidReader.TID, SID = self.RaidReader.SID, flawlessiv = spawn.FlawlessIVs(), shinyLock = currShinyLock, ability = spawn.Ability(), gender = spawn.Gender(), species = spawn.Species(), altform = spawn.AltForm())
                self.last_info = info
                s1 = pb.SpriteResource('pokemon', spawn.Species(), shiny=r.ShinyType != "None").img_data
                im = Image.open(io.BytesIO(s1)).convert('RGBA')
                image = ImageTk.PhotoImage(im)
                self.image = image
                self.image_display.config(image=image)
                self.current_info_display.delete(1.0, tk.END)
                self.next_info_display.delete(1.0, tk.END)
                self.current_info_display.insert(1.0, f"Pokemon: {Util.STRINGS.species[spawn.Species()]}\n{den.stars()}★\nForm: {spawn.AltForm()}\nSeed: {r.seed:016X}\nShinyType: {r.ShinyType}\nEC: {r.EC:08X}\nPID: {r.PID:08X}\nIVs: {r.IVs}\nBeam: {beam}")
                self.next_info_display.insert(1.0, f"Next Shiny Frame: {Raid.getNextShinyFrame(den.seed())}\nSeed: {rshiny.seed:016X}\nShinyType: {rshiny.ShinyType}\nEC: {rshiny.EC:08X}\nPID: {rshiny.PID:08X}\nIVs: {rshiny.IVs}") 
        except Exception as e:
            print(e)
        self.after_token = self.after(1000, self.update)

root = tk.Tk()
app = Application(master=root)
app.mainloop()