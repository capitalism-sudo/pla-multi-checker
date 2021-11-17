import json
import signal
import sys
import tkinter as tk
from tkinter import ttk
from tables import locations,diff_held_items

# Go to root of PyNXReader
sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO,OverworldRNG,Filter

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config = json.load(open("../config.json"))
        self.master = master
        self.pack()
        self.advances = 0
        self.create_widgets()
        signal.signal(signal.SIGINT, self.signal_handler)

    def create_widgets(self):
        self.master.title("Overworld RNG")
        self.connect_button = tk.Button(self, text="Connect", fg="green", command=self.connect)
        self.connect_button.grid(column=0,row=1)
        self.quit = tk.Button(self, text="Disconnect", fg="red", command=self.disconnect)
        self.quit.grid(column=1,row=1)
        self.generate = tk.Button(self, text="Generate", command=self.generate)
        self.generate.grid(column=2,row=1)
        self.shiny_charm_var = tk.IntVar()
        self.mark_charm_var = tk.IntVar()
        self.weather_active_var = tk.IntVar()
        self.is_static_var = tk.IntVar()
        self.is_fishing_var = tk.IntVar()
        self.diff_held_item_var = tk.IntVar()
        self.double_mark_gen_var = tk.IntVar()
        tk.Checkbutton(self, text="Shiny Charm", variable=self.shiny_charm_var).grid(column=0,row=2,columnspan=3)
        tk.Checkbutton(self, text="Mark Charm", variable=self.mark_charm_var).grid(column=0,row=3,columnspan=3)
        tk.Checkbutton(self, text="Weather Active", variable=self.weather_active_var).grid(column=0,row=4,columnspan=3)
        tk.Checkbutton(self, text="Is Static", variable=self.is_static_var).grid(column=0,row=5,columnspan=1)
        tk.Checkbutton(self, text="Double Mark Gen", variable=self.double_mark_gen_var).grid(column=1,row=5,columnspan=2)
        tk.Checkbutton(self, text="Is Fishing", variable=self.is_fishing_var).grid(column=0,row=6,columnspan=3)
        tk.Checkbutton(self, text="Rand Held Item", variable=self.diff_held_item_var).grid(column=0,row=7,columnspan=3)
        tk.Label(self, text="Level:").grid(column=0,row=8)
        self.min_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.max_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.min_level_var.grid(column=1,row=8)
        self.max_level_var.grid(column=2,row=8)
        tk.Label(self,text="Filter").grid(column=3,row=1,columnspan=3)
        tk.Label(self,text="Shininess").grid(column=3,row=2,columnspan=3)
        self.shiny_filter = ttk.Combobox(self, values=["Any","Star","Square","Star/Square"])
        self.shiny_filter.grid(column=3,row=3,columnspan=3)
        self.shiny_filter.set("Any")
        self.has_mark_filter = tk.IntVar()
        tk.Checkbutton(self, text="Has Mark", variable=self.has_mark_filter).grid(column=3,row=4,columnspan=3)
        self.rare_mark_filter = tk.IntVar()
        tk.Checkbutton(self, text="Has Rare Mark", variable=self.rare_mark_filter).grid(column=3,row=5,columnspan=3)
        self.specific_mark_filter = tk.IntVar()
        tk.Checkbutton(self, text="Specific Mark", variable=self.specific_mark_filter).grid(column=3,row=6)
        self.specific_mark = ttk.Combobox(self,values=["Rare","Uncommon","Weather","Time","Fishing"]+OverworldRNG.personality_marks)
        self.specific_mark.grid(column=4,row=6,columnspan=2)
        self.slot_filter = tk.IntVar()
        tk.Checkbutton(self, text="Slot", variable=self.slot_filter).grid(column=3,row=7)
        self.min_slot_var = tk.Spinbox(self, from_= 0, to = 99, width = 5)
        self.max_slot_var = tk.Spinbox(self, from_= 0, to = 99, width = 5)
        self.min_slot_var.grid(column=4,row=7)
        self.max_slot_var.grid(column=5,row=7)
        self.advances_track = tk.Label(self,text="0")
        self.advances_track.grid(column=3,row=8)
        tk.Label(self,text="+").grid(column=4,row=8)
        self.max_advance_var = tk.Spinbox(self, value=99999, from_= 0, to = 99999999, width = 20)
        self.max_advance_var.grid(column=5,row=8)
        self.autofill = tk.Button(self,text="Autofill",command=self.autofill_info)
        self.autofill.grid(column=7,row=1)
        self.location = ttk.Combobox(self,values=[n for n in locations],width=40)
        self.location.bind('<<ComboboxSelected>>',self.populate_weather)
        self.location.grid(column=7,row=2)
        self.weather = ttk.Combobox(self,values=[],width=40)
        self.weather.grid(column=7,row=3)
        self.weather.bind('<<ComboboxSelected>>',self.populate_species)
        self.species = ttk.Combobox(self,values=[],width=40)
        self.species.grid(column=7,row=4)
        self.initial_display = tk.Entry(self,width=40)
        self.initial_display.grid(column=7,row=8)
    
    def populate_weather(self,event):
        self.weather['values'] = [w for w in locations[self.location.get()]]
    
    def populate_species(self,event):
        self.species['values'] = [s for s in locations[self.location.get()][self.weather.get()][1]]
    
    def autofill_info(self):
        location = self.location.get()
        weather = self.weather.get()
        species = self.species.get()
        self.is_static_var.set(0)
        self.slot_filter.set(1)
        if weather != "All Weather":
            self.weather_active_var.set(1)
        if weather == "Normal Weather":
            self.weather_active_var.set(0)
        if diff_held_items[species]:
            self.diff_held_item_var.set(1)
        else:
            self.diff_held_item_var.set(0)
        min_level,max_level = locations[location][weather][0]
        self.min_level_var.delete(0,"end")
        self.min_level_var.insert(0,min_level)
        self.max_level_var.delete(0,"end")
        self.max_level_var.insert(0,max_level)
        min_slot,max_slot = locations[location][weather][1][species]
        self.min_slot_var.delete(0,"end")
        self.min_slot_var.insert(0,min_slot)
        self.max_slot_var.delete(0,"end")
        self.max_slot_var.insert(0,max_slot)

    def generate(self):
        mark_filter = None
        # TODO: fix gui ew and full Filter functionality
        if int(self.has_mark_filter.get()):
            mark_filter = ["Rare","Uncommon","Time","Weather","Fishing"]+OverworldRNG.personality_marks
        if int(self.rare_mark_filter.get()):
            mark_filter = ["Rare"]
        if int(self.specific_mark_filter.get()):
            mark_filter = [self.specific_mark.get()]
        min_slot = max_slot = None
        if int(self.slot_filter.get()):
            min_slot = int(self.min_slot_var.get())
            max_slot = int(self.max_slot_var.get())
        filter = Filter(
            shininess=self.shiny_filter.get() if self.shiny_filter.get() != "Any" else None,
            marks=mark_filter,
            slot_min=min_slot,
            slot_max=max_slot,
            )
        self.predict = OverworldRNG(
            seed = self.rng.state(),
            tid = self.SWSHReader.TID,
            sid = self.SWSHReader.SID,
            shiny_charm = int(self.shiny_charm_var.get()),
            mark_charm = int(self.mark_charm_var.get()),
            weather_active = int(self.weather_active_var.get()),
            is_fishing = int(self.is_fishing_var.get()),
            is_static = int(self.is_static_var.get()),
            min_level = int(self.min_level_var.get()),
            max_level = int(self.max_level_var.get()),
            diff_held_item = int(self.diff_held_item_var.get()),
            double_mark_gen = int(self.double_mark_gen_var.get()),
            filter = filter,
            )
        advances = self.advances
        self.predict.advance += advances
        for _ in range(int(self.max_advance_var.get())+1):
            state = self.predict.generate()
            if state:
                print(state)

    def connect(self):
        print("Connecting to: ", self.config["IP"])
        self.SWSHReader = SWSHReader(self.config["IP"])
        self.rng = XOROSHIRO(int.from_bytes(self.SWSHReader.read(0x4C2AAC18,8),"little"),int.from_bytes(self.SWSHReader.read(0x4C2AAC18+8,8),"little"))
        self.initial = self.rng.state()
        self.initial_display.delete(0,"end")
        self.initial_display.insert(0,hex(self.initial))
        self.advances = 0
        self.update()

    def disconnect(self):
        print("Disconnecting")
        self.after_cancel(self.after_token)
        self.SWSHReader.close(False)
        self.SWSHReader = None
    
    def signal_handler(self, signal, frame):
        self.disconnect()
        sys.exit(0)
    
    def update(self):
        read = int.from_bytes(self.SWSHReader.read(0x4C2AAC18,16),"little")
        while self.rng.state() != read:
            self.rng.next()
            self.advances += 1
            if self.rng.state() == read:
                self.advances_track['text'] = str(self.advances)
        self.after_token = self.after(100, self.update)

root = tk.Tk()
app = Application(master=root)
app.mainloop()