import json
import signal
import sys
import time
import tkinter as tk
import threading
from tkinter import ttk

# Go to root of PyNXReader
sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO,OverworldRNG,Filter
from gui import ChecklistCombobox,setup_styles

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config = json.load(open("../config.json"))
        self.locations = json.load(open("SWSH_Encounter_Slots.json"))
        self.held_items = json.load(open("SWSH_Held_Items.json"))
        self.master = master
        self.pack()
        self.advances = 0
        self.current_gen = 0
        self.generating = False
        self.tracking = False
        self.min_shown = False
        self.create_widgets()
        signal.signal(signal.SIGINT, self.signal_handler)

    def create_widgets(self):
        setup_styles()
        self.master.title("Overworld RNG")
        self.connect_button = ttk.Button(self, text="Connect", style="Connect.TButton", command=self.connect)
        self.connect_button.grid(column=0,row=1)
        self.quit = ttk.Button(self, text="Disconnect", style="Disconnect.TButton", command=self.disconnect)
        self.quit.grid(column=1,row=1)
        self.generate_button = ttk.Button(self, text="Generate", command=self.generate,width=20)
        self.generate_button.grid(column=2,row=1,columnspan=2)
        self.shiny_charm_var = tk.IntVar()
        self.mark_charm_var = tk.IntVar()
        self.weather_active_var = tk.IntVar()
        self.is_static_var = tk.IntVar()
        self.is_fishing_var = tk.IntVar()
        self.diff_held_item_var = tk.IntVar()
        self.double_mark_gen_var = tk.IntVar()
        self.is_legendary_var = tk.IntVar()
        self.is_shiny_locked_var = tk.IntVar()
        ttk.Checkbutton(self, text="Shiny Charm", variable=self.shiny_charm_var).grid(column=0,row=2,columnspan=2)
        ttk.Checkbutton(self, text="Mark Charm", variable=self.mark_charm_var).grid(column=2,row=2,columnspan=2)
        ttk.Checkbutton(self, text="Is Static", variable=self.is_static_var).grid(column=0,row=3,columnspan=2)
        ttk.Checkbutton(self, text="Is Legendary", variable=self.is_legendary_var).grid(column=2,row=3,columnspan=2)
        ttk.Checkbutton(self, text="Weather Active", variable=self.weather_active_var).grid(column=0,row=4,columnspan=2)
        ttk.Checkbutton(self, text="Is Fishing", variable=self.is_fishing_var).grid(column=2,row=4,columnspan=2)
        ttk.Checkbutton(self, text="Rand Held Item", variable=self.diff_held_item_var).grid(column=0,row=5,columnspan=2)
        ttk.Checkbutton(self, text="Double Mark Gen", variable=self.double_mark_gen_var).grid(column=2,row=5,columnspan=2)
        ttk.Checkbutton(self, text="Is Shiny Locked", variable=self.is_shiny_locked_var).grid(column=0,row=6,columnspan=4)
        ttk.Label(self, text="EM Count:").grid(column=0,row=10)
        self.em_count_var = tk.Spinbox(self, from_= 0, to = 100, width = 5)
        self.em_count_var.grid(column=1,row=10)
        ttk.Label(self, text="KOs:").grid(column=2,row=10)
        self.kos_var = tk.Spinbox(self, from_= 0, to = 500, width = 5)
        self.kos_var.grid(column=3,row=10)
        ttk.Label(self, text="Level:").grid(column=0,row=11)
        self.min_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.max_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.min_level_var.grid(column=1,row=11)
        self.max_level_var.grid(column=2,row=11)
        ttk.Label(self,text="Filter").grid(column=5,row=1,columnspan=3)
        ttk.Label(self,text="Shininess").grid(column=4,row=2,columnspan=1)
        self.shiny_filter = ttk.Combobox(self,state='readonly',values=["Any","Star","Square","Star/Square"])
        self.shiny_filter.grid(column=5,row=2,columnspan=3)
        self.shiny_filter.set("Any")
        ttk.Label(self,text="Mark").grid(column=4,row=3,columnspan=1)
        self.mark_var = ChecklistCombobox(self,state='readonly',values=["Rare","Uncommon","Weather","Time","Fishing"]+OverworldRNG.personality_marks)
        self.mark_var.grid(column=5,row=3,columnspan=3)
        self.all_mark_button = ttk.Button(self,text="All",width=20//3,command=lambda: self.mark_var.set(["Rare","Uncommon","Weather","Time","Fishing"]+OverworldRNG.personality_marks))
        self.all_mark_button.grid(column=6,row=4,columnspan=1)
        self.all_mark_button = ttk.Button(self,text="None",width=20//3,command=lambda: self.mark_var.set([]))
        self.all_mark_button.grid(column=7,row=4,columnspan=1)
        self.slot_filter = tk.IntVar()
        ttk.Checkbutton(self, text="Slot", variable=self.slot_filter).grid(column=4,row=6)
        self.min_slot_var = tk.Spinbox(self, from_= 0, to = 99, width = 5)
        self.max_slot_var = tk.Spinbox(self, from_= 0, to = 99, width = 5)
        self.min_slot_var.grid(column=6,row=6)
        self.max_slot_var.grid(column=7,row=6)
        self.adv_label = ttk.Label(self,text="Adv:")
        self.adv_label.grid(column=3,row=11)
        self.adv_label.bind('<Double-Button-1>', self.toggle_min_advances)
        self.advances_track = ttk.Label(self,text="0")
        self.advances_track.grid(column=4,row=11)
        self.min_advance_var = tk.Spinbox(self, value=0, from_= 0, to = 99999999, width = 20)
        self.min_advance_var.grid(column=4,row=11)
        self.min_advance_var.grid_remove()
        ttk.Label(self,text="+").grid(column=5,row=11)
        self.max_advance_var = tk.Spinbox(self, value=99999, from_= 0, to = 99999999, width = 20)
        self.max_advance_var.grid(column=6,row=11,columnspan=2)
        self.autofill = ttk.Button(self,text="Auto Fill Encounter Info",command=self.autofill_info)
        self.autofill.grid(column=9,row=1)
        ttk.Label(self,text="Game:").grid(column=8,row=2)
        self.game = ttk.Combobox(self,values=["Sword", "Shield"],width=40,state='readonly')
        self.game.bind('<<ComboboxSelected>>',self.reset_slots)
        self.game.grid(column=9,row=2)
        ttk.Label(self,text="Encounter Type:").grid(column=8,row=3)
        self.type = ttk.Combobox(self,values=["Symbol", "Hidden"],width=40,state='readonly')
        self.type.bind('<<ComboboxSelected>>',self.populate_location)
        self.type.grid(column=9,row=3)
        ttk.Label(self,text="Location:").grid(column=8,row=4)
        self.location = ttk.Combobox(self,values=[],width=40,state='readonly')
        self.location.bind('<<ComboboxSelected>>',self.populate_weather)
        self.location.grid(column=9,row=4)
        ttk.Label(self,text="Weather/Type:").grid(column=8,row=5)
        self.weather = ttk.Combobox(self,values=[],width=40,state='readonly')
        self.weather.grid(column=9,row=5)
        ttk.Label(self,text="Species:").grid(column=8,row=6)
        self.weather.bind('<<ComboboxSelected>>',self.populate_species)
        self.species = ttk.Combobox(self,values=[],width=40,state='readonly')
        self.species.grid(column=9,row=6)
        ttk.Label(self,text="Init:").grid(column=8,row=11)
        self.initial_display = ttk.Entry(self,width=40)
        self.initial_display.grid(column=9,row=11)
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.grid(column=0,row=12,columnspan=10)
    
    def toggle_min_advances(self,event):
        if not self.min_shown:
            self.advances_track.grid_remove()
            self.min_advance_var.grid()
            self.min_shown = True
            self.min_advance_var['value'] = self.advances
        else:
            self.advances_track.grid()
            self.min_advance_var.grid_remove()
            self.min_shown = False

    def reset_slots(self,event):
        self.location['values'] = []
        self.weather['values'] = []
        self.species['values'] = []
        self.location.set("")
        self.weather.set("")
        self.species.set("")

    def populate_location(self,event):
        self.location['values'] = [l for l in self.locations[self.game.get()][self.type.get()]]
        self.weather['values'] = []
        self.species['values'] = []
        self.location.set("")
        self.weather.set("")
        self.species.set("")

    def populate_weather(self,event):
        self.weather['values'] = [w for w in self.locations[self.game.get()][self.type.get()][self.location.get()]]
        self.species['values'] = []
        self.weather.set("")
        self.species.set("")
    
    def populate_species(self,event):
        self.species['values'] = [s for s in self.locations[self.game.get()][self.type.get()][self.location.get()][self.weather.get()][1]]
        self.species.set("")
    
    def autofill_info(self):
        weather = self.weather.get()
        species = self.species.get()
        self.is_static_var.set(0)
        self.slot_filter.set(1)
        if weather != "All Weather" and weather != "Fishing" and weather != "Shaking Trees":
            self.weather_active_var.set(1)
        if weather == "Normal Weather":
            self.weather_active_var.set(0)
        if weather == "Fishing":
            self.is_fishing_var.set(1)
        if self.held_items[species]:
            self.diff_held_item_var.set(1)
        else:
            self.diff_held_item_var.set(0)
        min_level,max_level = self.locations[self.game.get()][self.type.get()][self.location.get()][weather][0]
        self.min_level_var.delete(0,"end")
        self.min_level_var.insert(0,min_level)
        self.max_level_var.delete(0,"end")
        self.max_level_var.insert(0,max_level)
        min_slot,max_slot = self.locations[self.game.get()][self.type.get()][self.location.get()][weather][1][species]
        self.min_slot_var.delete(0,"end")
        self.min_slot_var.insert(0,min_slot)
        self.max_slot_var.delete(0,"end")
        self.max_slot_var.insert(0,max_slot)

    def generate(self):
        mark_filter = None
        # TODO: fix gui ew and full Filter functionality
        selected = self.mark_var.get()
        if selected != "":
            if type(selected) == type(""):
                selected = [selected]
            mark_filter = selected
        min_slot = max_slot = None
        if int(self.slot_filter.get()):
            min_slot = int(self.min_slot_var.get())
            max_slot = int(self.max_slot_var.get())
        filter = Filter(
            shininess=self.shiny_filter.get() if self.shiny_filter.get() != "Any" else None,
            marks=mark_filter,
            slot_min=min_slot,
            slot_max=max_slot
            )
        self.predict = OverworldRNG(
            seed = self.initial if self.min_shown else self.rng.state(),
            tid = self.SWSHReader.TID,
            sid = self.SWSHReader.SID,
            shiny_charm = int(self.shiny_charm_var.get()),
            mark_charm = int(self.mark_charm_var.get()),
            weather_active = int(self.weather_active_var.get()),
            is_fishing = int(self.is_fishing_var.get()),
            is_static = int(self.is_static_var.get()),
            is_legendary = int(self.is_legendary_var.get()),
            is_shiny_locked = int(self.is_shiny_locked_var.get()),
            min_level = int(self.min_level_var.get()),
            max_level = int(self.max_level_var.get()),
            diff_held_item = int(self.diff_held_item_var.get()),
            double_mark_gen = int(self.double_mark_gen_var.get()),
            egg_move_count = int(self.em_count_var.get()),
            kos = int(self.kos_var.get()),
            filter = filter,
            )
        if self.min_shown:
            self.predict.advance_fast(int(self.min_advance_var.get()))
        else:
            self.predict.advance += self.advances
        self.generating = True
        self.generating_thread=threading.Thread(target=self.generating_work)
        self.generating_thread.daemon = True
        self.generating_thread.start()
        self.generate_button['text'] = "Stop Generating"
        self.generate_button['command'] = self.stop_generating_work

    def connect(self):
        print("Connecting to: ", self.config["IP"])
        self.SWSHReader = SWSHReader(self.config["IP"])
        self.rng = XOROSHIRO(int.from_bytes(self.SWSHReader.read(0x4C2AAC18,8),"little"),int.from_bytes(self.SWSHReader.read(0x4C2AAC18+8,8),"little"))
        self.initial = self.rng.state()
        self.initial_display.delete(0,"end")
        self.initial_display.insert(0,hex(self.initial))
        self.advances = 0
        self.advances_track['text'] = str(self.advances)
        self.start_tracking_thread()

    def disconnect(self):
        print("Disconnecting")
        self.tracking = False
        self.SWSHReader.close(False)
        self.SWSHReader = None
    
    def signal_handler(self, signal, frame):
        self.tracking = False
        self.generating = False
        self.disconnect()
        sys.exit(0)
    
    def start_tracking_thread(self):
        self.tracking = True
        self.tracking_thread=threading.Thread(target=self.tracking_work)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
    
    def tracking_work(self):
        while self.tracking:
            read = int.from_bytes(self.SWSHReader.read(0x4C2AAC18,16),"little")
            while self.rng.state() != read:
                if not self.tracking:
                    return
                self.rng.next()
                self.advances += 1
                if self.rng.state() == read:
                    self.advances_track['text'] = str(self.advances)
            time.sleep(0.1)
    
    def generating_work(self):
        self.progress_thread=threading.Thread(target=self.progress_work)
        self.progress_thread.daemon = True
        self.progress_thread.start()
        for self.current_gen in range(int(self.max_advance_var.get())+1):
            if not self.generating:
                break
            state = self.predict.generate()
            if state:
                print(state)
        self.stop_generating_work()
    
    def progress_work(self):
        # seperate thread to not slow down generating_work
        max = int(self.max_advance_var.get())+1
        add = 1/max*100
        self.progress['value'] = 0
        while self.generating:
            self.progress['value'] = add*self.current_gen
        self.progress['value'] = 100
    
    def stop_generating_work(self):
        self.generating = False
        self.generate_button['text'] = "Generate"
        self.generate_button['command'] = self.generate

root = tk.Tk()
app = Application(master=root)
app.mainloop()