import io
import json
import signal
import sys
import urllib
import tkinter as tk
import pokebase as pb
from functools import lru_cache

# Go to root of PyNXReader
sys.path.append('../')

from nxreader import SWSHReader
from structure import PK8Overworld
from PIL import Image, ImageTk

@lru_cache(maxsize=32)
def get_mark(mark):
    image_bytes = urllib.request.urlopen(f"https://www.serebii.net/swordshield/ribbons/{PK8Overworld.Ribbons[mark].lower() if mark != 255 else ''}mark.png").read()
    im = Image.open(io.BytesIO(image_bytes))
    return ImageTk.PhotoImage(im)

@lru_cache(maxsize=32)
def get_pokemon(species,shiny):
    image_bytes = pb.SpriteResource('pokemon', species, shiny=shiny).img_data
    im = Image.open(io.BytesIO(image_bytes))
    return ImageTk.PhotoImage(im)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config = json.load(open("../config.json"))
        self.master = master
        self.pack()
        self.create_widgets()
        self.last_info = ""
        signal.signal(signal.SIGINT, self.signal_handler)
        self.cache = []

    def create_widgets(self):
        self.master.title("Overworld Reader")
        self.connect_button = tk.Button(self, text="Connect", fg="green", command=self.connect)
        self.connect_button.grid(column=0,row=1)
        self.displays = []
        self.quit = tk.Button(self, text="Disconnect", fg="red", command=self.disconnect)
        self.quit.grid(column=1,row=1)

    def connect(self):
        print("Connecting to: ", self.config["IP"])
        self.SWSHReader = SWSHReader(self.config["IP"])
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
        self.SWSHReader.KCoordinates.refresh()
        pkms = self.SWSHReader.KCoordinates.ReadOwPokemonFromBlock()
        info = []
        infocheck = []
        for pkm in pkms:
            info.append(pkm)
            infocheck.append(pkm.ec)
        
        if infocheck != self.last_info:
            i = 0
            for display in self.displays:
                for widget in display:
                    widget.grid_forget()
            self.displays = []
            for pkm in info:
                self.displays.append([])
                self.displays[i].append(tk.Text(self,height=5))
                self.displays[i][0].grid(column=2+(5 if i%2 else 0), row=2+int((i*3)/2), columnspan=1, rowspan=2)
                self.displays[i].append(tk.Label(self))
                self.displays[i][1].grid(column=0+(5 if i%2 else 0), row=2+int((i*3)/2), columnspan=2, rowspan=2)
                self.displays[i].append(tk.Label(self))
                self.displays[i][2].grid(column=3+(5 if i%2 else 0), row=2+int((i*3)/2), columnspan=2, rowspan=2)
                
                try:
                    mark_image = get_mark(pkm.mark)
                    self.cache.append(mark_image)
                    self.displays[i][2].config(image=mark_image)
                except Exception as e:
                    pass

                pokemon_image = get_pokemon(pkm.species, pkm.getShinyType(((pkm.sid<<16) | pkm.tid), pkm.pid))
                self.cache.append(pokemon_image)
                self.displays[i][1].config(image=pokemon_image)
                self.last_info = str(pkm)
                self.displays[i][0].delete(1.0, tk.END)
                self.displays[i][0].insert(1.0, str(pkm))
                i += 1
            self.last_info = infocheck
        self.after_token = self.after(1000, self.update)

root = tk.Tk()
app = Application(master=root)
app.mainloop()