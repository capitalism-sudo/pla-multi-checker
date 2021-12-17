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
        self.encounters = json.load(open("SWSH_Encounters.json"))
        self.personal = json.load(open("SWSH_Personal.json"))
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

        self.shiny_charm_var = tk.IntVar()
        self.mark_charm_var = tk.IntVar()
        self.weather_active_var = tk.IntVar()
        self.is_static_var = tk.IntVar()
        self.is_fishing_var = tk.IntVar()
        self.diff_held_item_var = tk.IntVar()
        self.forced_ability_var = tk.IntVar()
        self.is_shiny_locked_var = tk.IntVar()
        self.brilliant_var = tk.IntVar()

        column = 0

        self.connect_button = ttk.Button(self, text="Connect", style="Connect.TButton", command=self.connect, width=15)
        self.connect_button.grid(column=column,row=1)
        ttk.Label(self,text="Game:").grid(column=column,row=2)
        ttk.Label(self,text="Encounter Type:").grid(column=column,row=3)
        ttk.Label(self,text="Location:").grid(column=column,row=4)
        ttk.Label(self,text="Weather/Type:").grid(column=column,row=5)
        ttk.Label(self,text="Species:").grid(column=column,row=6)
        ttk.Label(self, text="Level:").grid(column=column,row=7)
        ttk.Label(self,text="Init:").grid(column=column,row=8)
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.grid(column=column,row=9,columnspan=15)

        column += 1
        self.quit = ttk.Button(self, text="Disconnect", style="Disconnect.TButton", command=self.disconnect, width=15)
        self.quit.grid(column=column,row=1,columnspan=1)
        self.game = ttk.Combobox(self,values=["Sword", "Shield"],width=40,state='readonly')
        self.game.bind('<<ComboboxSelected>>',self.reset_slots)
        self.game.grid(column=column,row=2,columnspan=4)
        self.type = ttk.Combobox(self,values=["Symbol", "Hidden", "Static"],width=40,state='readonly')
        self.type.bind('<<ComboboxSelected>>',self.populate_location)
        self.type.grid(column=column,row=3,columnspan=4)
        self.location = ttk.Combobox(self,values=[],width=40,state='readonly')
        self.location.bind('<<ComboboxSelected>>',self.populate_weather)
        self.location.grid(column=column,row=4,columnspan=4)
        self.weather = ttk.Combobox(self,values=[],width=40,state='readonly')
        self.weather.grid(column=column,row=5,columnspan=4)
        self.weather.bind('<<ComboboxSelected>>',self.populate_species)
        self.species = ttk.Combobox(self,values=[],width=40,state='readonly')
        self.species.grid(column=column,row=6,columnspan=4)
        self.species.bind('<<ComboboxSelected>>',self.autofill)
        self.min_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.min_level_var.grid(column=column,row=7)
        self.initial_display = ttk.Entry(self,width=40)
        self.initial_display.grid(column=column,row=8,columnspan=4)

        column += 2
        self.generate_button = ttk.Button(self, text="Generate", command=self.generate, width=26)
        self.generate_button.grid(column=column,row=1,columnspan=3)

        column += 1
        self.max_level_var = tk.Spinbox(self, from_= 1, to = 100, width = 5)
        self.max_level_var.grid(column=column,row=7)

        column += 2
        ttk.Label(self,text="Settings").grid(column=column,row=1,columnspan=4)
        self.shiny_charm = ttk.Checkbutton(self, text="Shiny Charm", variable=self.shiny_charm_var)
        self.shiny_charm.grid(column=column,row=2,columnspan=2)
        self.is_static = ttk.Checkbutton(self, text="Is Static", variable=self.is_static_var, command=self.toggle_static)
        self.is_static.grid(column=column,row=3,columnspan=2)
        self.forced_ability = ttk.Checkbutton(self, text="Forced Ability", variable=self.forced_ability_var)
        self.forced_ability.grid(column=column,row=4,columnspan=4)
        self.weather_active = ttk.Checkbutton(self, text="Weather Active", variable=self.weather_active_var)
        self.weather_active.grid(column=column,row=5,columnspan=2)
        ttk.Label(self, text="EM Count:").grid(column=column,row=6)
        self.is_shiny_locked = ttk.Checkbutton(self, text="Is Shiny Locked", variable=self.is_shiny_locked_var)
        self.is_shiny_locked.grid(column=column,row=7,columnspan=2)
        self.adv_label = ttk.Label(self,text="Adv:")
        self.adv_label.grid(column=column,row=8)
        self.adv_label.bind('<Double-Button-1>', self.toggle_min_advances)

        column += 1
        self.em_count_var = tk.Spinbox(self, from_= 0, to = 100, width = 5)
        self.em_count_var.grid(column=column,row=6)
        self.advances_track = ttk.Label(self,text="0 +")
        self.advances_track.grid(column=column,row=8)
        self.min_advance_var = tk.Spinbox(self, value=0, from_= 0, to = 99999999, width = 20)
        self.min_advance_var.grid(column=column,row=8)
        self.min_advance_var.grid_remove()

        column += 1
        self.mark_charm = ttk.Checkbutton(self, text="Mark Charm", variable=self.mark_charm_var)
        self.mark_charm.grid(column=column,row=2,columnspan=2)
        ttk.Label(self,text="Flawless IVs:").grid(column=column,row=3)
        self.is_fishing = ttk.Checkbutton(self, text="Is Fishing", variable=self.is_fishing_var)
        self.is_fishing.grid(column=column,row=5,columnspan=2)
        ttk.Label(self, text="KOs:").grid(column=column,row=6)
        self.diff_held_item = ttk.Checkbutton(self, text="Rand Held Item", variable=self.diff_held_item_var)
        self.diff_held_item.grid(column=column,row=7,columnspan=2)
        self.max_advance_var = tk.Spinbox(self, value=99999, from_= 0, to = 99999999, width = 20)
        self.max_advance_var.grid(column=column,row=8,columnspan=2)

        column += 1
        self.flawless_ivs_var = tk.Spinbox(self, value=0, from_= 0, to = 3, width = 5)
        self.flawless_ivs_var.grid(column=column,row=3)
        self.kos_var = tk.Spinbox(self, from_= 0, to = 500, width = 5)
        self.kos_var.grid(column=column,row=6)

        column += 3
        ttk.Label(self,text="Shininess").grid(column=column,row=2,columnspan=1)
        ttk.Label(self,text="Mark").grid(column=column,row=3,columnspan=1)
        self.slot_filter_var = tk.IntVar()
        self.slot_filter = ttk.Checkbutton(self, text="Slot", variable=self.slot_filter_var)
        self.slot_filter.grid(column=column,row=6)
        self.briliant = ttk.Checkbutton(self, text="Brilliant", variable=self.brilliant_var)
        self.briliant.grid(column=column,row=7,columnspan=4)
        
        column += 1
        ttk.Label(self,text="Filter").grid(column=column,row=1,columnspan=6)
        self.shiny_filter = ttk.Combobox(self,state='readonly',values=["Any","Star","Square","Star/Square"])
        self.shiny_filter.grid(column=column,row=2,columnspan=3)
        self.shiny_filter.set("Any")
        self.mark_var = ChecklistCombobox(self,state='readonly',values=["Rare","Uncommon","Weather","Time","Fishing"]+OverworldRNG.personality_marks)
        self.mark_var.grid(column=column,row=3,columnspan=3)

        column += 1
        self.all_mark_button = ttk.Button(self,text="All",width=20//3,command=lambda: self.mark_var.set(["Rare","Uncommon","Weather","Time","Fishing"]+OverworldRNG.personality_marks))
        self.all_mark_button.grid(column=column,row=4,columnspan=1)
        self.min_slot_var = tk.Spinbox(self, from_= 0, to = 99, width = 5)
        self.min_slot_var.grid(column=column,row=6)

        column += 1
        self.all_mark_button = ttk.Button(self,text="None",width=20//3,command=lambda: self.mark_var.set([]))
        self.all_mark_button.grid(column=column,row=4,columnspan=1)
        self.max_slot_var = tk.Spinbox(self, from_= 0, to = 99, width = 5)
        self.max_slot_var.grid(column=column,row=6)

        column += 1
        ttk.Label(self,text=" HP ").grid(column=column,row=2)
        ttk.Label(self,text=" Atk ").grid(column=column,row=3)
        ttk.Label(self,text=" Def ").grid(column=column,row=4)
        ttk.Label(self,text=" SpA ").grid(column=column,row=5)
        ttk.Label(self,text=" SpD ").grid(column=column,row=6)
        ttk.Label(self,text=" Spe ").grid(column=column,row=7)

        column += 1
        self.hp_min = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.hp_min.grid(column=column,row=2)
        self.atk_min = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.atk_min.grid(column=column,row=3)
        self.def_min = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.def_min.grid(column=column,row=4)
        self.spa_min = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.spa_min.grid(column=column,row=5)
        self.spd_min = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.spd_min.grid(column=column,row=6)
        self.spe_min = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.spe_min.grid(column=column,row=7)

        column += 1
        self.hp_max = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.hp_max.grid(column=column,row=2)
        self.hp_max['value'] = 31
        self.atk_max = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.atk_max.grid(column=column,row=3)
        self.atk_max['value'] = 31
        self.def_max = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.def_max.grid(column=column,row=4)
        self.def_max['value'] = 31
        self.spa_max = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.spa_max.grid(column=column,row=5)
        self.spa_max['value'] = 31
        self.spd_max = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.spd_max.grid(column=column,row=6)
        self.spd_max['value'] = 31
        self.spe_max = tk.Spinbox(self, from_= 0, to = 31, width = 5)
        self.spe_max.grid(column=column,row=7)
        self.spe_max['value'] = 31

        self.toggle_static()
    
    def toggle_static(self):
        static = self.is_static_var.get()
        if not static:
            self.is_fishing['state'] = tk.NORMAL
            self.diff_held_item['state'] = tk.NORMAL
            self.em_count_var['state'] = tk.NORMAL
            self.kos_var['state'] = tk.NORMAL
            self.slot_filter['state'] = tk.NORMAL
            self.min_slot_var['state'] = tk.NORMAL
            self.max_slot_var['state'] = tk.NORMAL
            self.max_level_var['state'] = tk.NORMAL
        else:
            self.is_fishing_var.set(0)
            self.diff_held_item_var.set(0)
            self.slot_filter_var.set(0)
            self.max_level_var['value'] = self.min_level_var.get()
            self.min_slot_var['value'] = 0
            self.max_slot_var['value'] = 0
            self.em_count_var['value'] = 0
            self.kos_var['value'] = 0

            self.is_fishing['state'] = tk.DISABLED
            self.diff_held_item['state'] = tk.DISABLED
            self.em_count_var['state'] = tk.DISABLED
            self.kos_var['state'] = tk.DISABLED
            self.slot_filter['state'] = tk.DISABLED
            self.min_slot_var['state'] = tk.DISABLED
            self.max_slot_var['state'] = tk.DISABLED
            self.max_level_var['state'] = tk.DISABLED

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
        static = self.type.get() == "Static"
        self.is_static_var.set(static)
        self.slot_filter_var.set(not static)
        self.toggle_static()

        self.location['values'] = [l for l in self.encounters[self.game.get()][self.type.get()]]
        self.weather['values'] = []
        self.species['values'] = []
        self.location.set("")
        self.weather.set("")
        self.species.set("")

    def populate_weather(self,event):
        self.weather['values'] = [w for w in self.encounters[self.game.get()][self.type.get()][self.location.get()]]
        self.species['values'] = []
        self.weather.set("")
        self.species.set("")
    
    def populate_species(self,event):
        weather = self.weather.get()
        if not weather in ["All Weather","Fishing","Shaking Trees"]:
            self.weather_active_var.set(1)
        if weather in ["Normal Weather","Normal"]:
            self.weather_active_var.set(0)
        if weather == "Fishing":
            self.is_fishing_var.set(1)

        pull = self.encounters[self.game.get()][self.type.get()][self.location.get()][self.weather.get()]
        if self.type.get() != "Static":
            pull = pull["Slots"]
        self.species['values'] = [s for s in pull]

        self.species.set("")
    
    def autofill(self,event):
        weather = self.weather.get()
        species = self.species.get()
        static = self.type.get() == "Static"
        if not static and self.personal[species]["Item"]:
            self.diff_held_item_var.set(1)
        else:
            self.diff_held_item_var.set(0)
        if not static:
            self.em_count_var["value"] = len(self.personal[species]["Egg_Moves"])
        min_level = max_level = 0
        if not static:
            min_level,max_level = self.encounters[self.game.get()][self.type.get()][self.location.get()][weather]["Level"]
        else:
            min_level = max_level = self.encounters[self.game.get()][self.type.get()][self.location.get()][weather][species]["Level"]
            self.forced_ability_var.set(not self.encounters[self.game.get()][self.type.get()][self.location.get()][weather][species]["Ability"] == -1)
        self.min_level_var.delete(0,"end")
        self.min_level_var.insert(0,min_level)
        self.max_level_var.delete(0,"end")
        self.max_level_var.insert(0,max_level)
        if not static:
            min_slot,max_slot = self.encounters[self.game.get()][self.type.get()][self.location.get()][weather]["Slots"][species]
            self.min_slot_var.delete(0,"end")
            self.min_slot_var.insert(0,min_slot)
            self.max_slot_var.delete(0,"end")
            self.max_slot_var.insert(0,max_slot)
            self.flawless_ivs_var['value'] = 0
        else:
            self.flawless_ivs_var['value'] = self.encounters[self.game.get()][self.type.get()][self.location.get()][weather][species]["GuaranteedIVs"]
        if species in ["Articuno-1","Zapdos-1","Moltres-1","Keldeo-1"]:
            self.is_shiny_locked_var.set(1)
        else:
            self.is_shiny_locked_var.set(0)
        self.toggle_static()

    def generate(self):
        mark_filter = None
        selected = self.mark_var.get()
        if selected != "":
            if type(selected) == type(""):
                selected = [selected]
            mark_filter = selected
        min_slot = max_slot = None
        if int(self.slot_filter_var.get()):
            min_slot = int(self.min_slot_var.get())
            max_slot = int(self.max_slot_var.get())
        
        iv_min = [
            int(self.hp_min.get()),
            int(self.atk_min.get()),
            int(self.def_min.get()),
            int(self.spa_min.get()),
            int(self.spd_min.get()),
            int(self.spe_min.get()),
        ]
        iv_max = [
            int(self.hp_max.get()),
            int(self.atk_max.get()),
            int(self.def_max.get()),
            int(self.spa_max.get()),
            int(self.spd_max.get()),
            int(self.spe_max.get()),
        ]
        if iv_min == [0,0,0,0,0,0] and iv_max == [31,31,31,31,31,31]:
            iv_min = iv_max = None

        filter = Filter(
            shininess=self.shiny_filter.get() if self.shiny_filter.get() != "Any" else None,
            marks=mark_filter,
            slot_min=min_slot,
            slot_max=max_slot,
            brilliant=self.brilliant_var.get(),
            iv_min=iv_min,
            iv_max=iv_max
            )
        self.predict = OverworldRNG(
            seed = self.initial if self.min_shown else self.rng.state,
            tid = self.SWSHReader.TID,
            sid = self.SWSHReader.SID,
            shiny_charm = int(self.shiny_charm_var.get()),
            mark_charm = int(self.mark_charm_var.get()),
            weather_active = int(self.weather_active_var.get()),
            is_fishing = int(self.is_fishing_var.get()),
            is_static = int(self.is_static_var.get()),
            is_shiny_locked = int(self.is_shiny_locked_var.get()),
            min_level = int(self.min_level_var.get()),
            max_level = int(self.max_level_var.get()),
            flawless_ivs = int(self.flawless_ivs_var.get()),
            forced_ability = int(self.forced_ability_var.get()),
            diff_held_item = int(self.diff_held_item_var.get()),
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
        print("Connecting to: "+(self.config["IP"] if not self.config["USB"] else "USB"))
        self.SWSHReader = SWSHReader(self.config["IP"],usb_connection=self.config["USB"])
        seed = self.SWSHReader.readRNG()
        self.rng = XOROSHIRO(int.from_bytes(seed[0:8],"little"),int.from_bytes(seed[8:16],"little"))
        self.initial = self.rng.state
        self.initial_display.delete(0,"end")
        self.initial_display.insert(0,hex(self.initial))
        self.advances = 0
        self.advances_track['text'] = str(self.advances) + " +"
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
            read = int.from_bytes(self.SWSHReader.readRNG(),"little")
            while self.rng.state != read:
                if not self.tracking:
                    return
                self.rng.next()
                self.advances += 1
                if self.rng.state == read:
                    self.advances_track['text'] = str(self.advances) + " +"
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