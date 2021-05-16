import io
import json
import signal
import sys
import urllib
import tkinter as tk
import pokebase as pb

# Go to root of PyNXReader
sys.path.append('../../')

from nxreader import LGPEReader
from PIL import Image, ImageTk
from structure import PK7b

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config = json.load(open("../../config.json"))
        self.master = master
        self.pack()
        self.create_widgets()
        self.last_info = ""
        signal.signal(signal.SIGINT, self.signal_handler)

    def create_widgets(self):
        self.master.title("PyNXReader")
        self.type_var = tk.IntVar()
        self.connect_button = tk.Button(self, text="Connect", fg="green", command=self.connect)
        self.connect_button.grid(column=0,row=1)
        self.current_info_display = tk.Text(self,height=5)
        self.current_info_display.grid(column=3, row=2, rowspan=2)
        self.image_display = tk.Label(self)
        self.image_display.grid(column=1, row=2, columnspan=2, rowspan=3)
        self.battle_choice = tk.Radiobutton(self, text="Battle/Trade/Gift/Active", variable=self.type_var, value=1)
        self.legend_choice = tk.Radiobutton(self, text="Legend", variable=self.type_var, value=2)
        self.battle_choice.grid(column=0, row=2, columnspan=1, rowspan=1)
        self.legend_choice.grid(column=0, row=3, columnspan=1, rowspan=1)
        self.battle_choice.select()
        self.quit = tk.Button(self, text="Disconnect", fg="red", command=self.disconnect)
        self.quit.grid(column=1,row=1)

    def connect(self):
        print("Connecting to: ", self.config["IP"])
        self.LGPEReader = LGPEReader(self.config["IP"])
        self.update()

    def disconnect(self):
        print("Disconnecting")
        self.after_cancel(self.after_token)
        self.LGPEReader.close(False)
        self.LGPEReader = None
    
    def signal_handler(self, signal, frame):
        self.disconnect()
        sys.exit(0)
    
    def update(self):
        commands = [self.LGPEReader.readActive, self.LGPEReader.readLegend]
        read_func = commands[self.type_var.get()-1]

        try:
            pk7b = PK7b(read_func())
            error = False
        except Exception as e:
            print(e)
            error = True
        while error:
            try:
                pk7b = PK7b(read_func())
                error = False
            except:
                error = True
        
        if not pk7b.isValid() or pk7b.ec() == 0:
            print("Invalid or Not Present")
            self.last_info = ""
            self.image_display.config(image='')
            self.current_info_display.delete(1.0, tk.END)
        if pk7b.isValid() and pk7b.ec() != 0 and pk7b.toString() != self.last_info:
            info = pk7b.toString()
            s1 = pb.SpriteResource('pokemon', pk7b.species(), shiny=pk7b.shinyType).img_data
            im = Image.open(io.BytesIO(s1))
            image = ImageTk.PhotoImage(im)
            self.image = image
            self.image_display.config(image=image)
            self.last_info = info
            self.current_info_display.delete(1.0, tk.END)
            self.current_info_display.insert(1.0, info)
        self.after_token = self.after(1000, self.update)

root = tk.Tk()
app = Application(master=root)
app.mainloop()