import json
import signal
import sys
import tkinter as tk
from tkinter import ttk

# Go to root of PyNXReader
sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO,OverworldRNG

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
        tk.Checkbutton(self, text="Shiny Charm", variable=self.shiny_charm_var).grid(column=0,row=2,columnspan=3)
        tk.Checkbutton(self, text="Mark Charm", variable=self.mark_charm_var).grid(column=0,row=3,columnspan=3)
        tk.Checkbutton(self, text="Weather Active", variable=self.weather_active_var).grid(column=0,row=4,columnspan=3)
        tk.Checkbutton(self, text="Is Static", variable=self.is_static_var).grid(column=0,row=5,columnspan=3)
        tk.Checkbutton(self, text="Is Fishing", variable=self.is_fishing_var).grid(column=0,row=6,columnspan=3)
        tk.Checkbutton(self, text="Rand Held Item", variable=self.diff_held_item_var).grid(column=0,row=7,columnspan=3)
        tk.Label(self, text="Level:").grid(column=0,row=8)
        self.min_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.max_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.min_level_var.grid(column=1,row=8)
        self.max_level_var.grid(column=2,row=8)
        tk.Label(self,text="Filter").grid(column=3,row=1,columnspan=3)
        self.shiny_filter = tk.IntVar()
        tk.Checkbutton(self, text="Shiny", variable=self.shiny_filter).grid(column=3,row=2,columnspan=3)
        self.star_filter = tk.IntVar()
        tk.Checkbutton(self, text="Star", variable=self.star_filter).grid(column=3,row=3,columnspan=3)
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

    def generate(self):
        self.predict = OverworldRNG(self.rng.state(),self.SWSHReader.TID,self.SWSHReader.SID,int(self.shiny_charm_var.get()),int(self.mark_charm_var.get()),int(self.weather_active_var.get()),int(self.is_fishing_var.get()),int(self.is_static_var.get()),int(self.min_level_var.get()),int(self.max_level_var.get()),int(self.diff_held_item_var.get()))
        shiny_filter = int(self.shiny_filter.get())
        star_filter = int(self.star_filter.get())
        has_mark_filter = int(self.has_mark_filter.get())
        rare_mark_filter = int(self.rare_mark_filter.get())
        specific_mark_filter = int(self.specific_mark_filter.get())
        specific_mark = self.specific_mark.get()
        slot_filter = int(self.slot_filter.get())
        min_slot = int(self.min_slot_var.get())
        max_slot = int(self.max_slot_var.get())
        advances = self.advances
        self.predict.advances += advances
        for _ in range(int(self.max_advance_var.get())+1):
            state = self.predict.generate()
            if state.advance < self.advances:
                continue
            if shiny_filter:
                if not state.xor < 16:
                    continue
            if star_filter:
                if not 0 < state.xor < 16:
                    continue
            if has_mark_filter:
                if state.mark == None:
                    continue
            if rare_mark_filter:
                if state.mark != "Rare":
                    continue
            if specific_mark_filter:
                if state.mark != specific_mark:
                    continue
            if slot_filter:
                if not min_slot <= state.slot_rand <= max_slot:
                    continue
            print(state)

    def connect(self):
        print("Connecting to: ", self.config["IP"])
        self.SWSHReader = SWSHReader(self.config["IP"])
        self.rng = XOROSHIRO(int.from_bytes(self.SWSHReader.read(0x4C2AAC18,8),"little"),int.from_bytes(self.SWSHReader.read(0x4C2AAC18+8,8),"little"))
        self.initial = self.rng.state()
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