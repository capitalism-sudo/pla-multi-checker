import io
import json
import signal
import sys
import urllib
import tkinter as tk
import pokebase as pb

# Go to root of PyNXReader
sys.path.append('../')

from nxreader import SWSHReader
from PIL import Image, ImageTk
from structure import PK8

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
        self.master.title("SWSHReader")
        self.type_var = tk.IntVar()
        self.connect_button = tk.Button(self, text="Connect", fg="green", command=self.connect)
        self.connect_button.grid(column=0,row=1)
        self.current_info_display = tk.Text(self,height=5)
        self.current_info_display.grid(column=3, row=2, rowspan=3)
        self.image_display = tk.Label(self)
        self.image_display.grid(column=1, row=2, columnspan=2, rowspan=3)
        self.mark_display = tk.Label(self)
        self.mark_display.grid(column=4, row=2, columnspan=2, rowspan=3)
        self.wild_choice = tk.Radiobutton(self, text="Wild", variable=self.type_var, value=1)
        self.legend_choice = tk.Radiobutton(self, text="Legend", variable=self.type_var, value=2)
        self.horse_choice = tk.Radiobutton(self, text="Horse", variable=self.type_var, value=3)
        self.wild_choice.grid(column=0, row=2, columnspan=1, rowspan=1)
        self.legend_choice.grid(column=0, row=3, columnspan=1, rowspan=1)
        self.horse_choice.grid(column=0, row=4, columnspan=1, rowspan=1)
        self.wild_choice.select()
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
        commands = [self.SWSHReader.readWild, self.SWSHReader.readLegend, self.SWSHReader.readHorse]
        read_func = commands[self.type_var.get()-1]

        try:
            pk8 = PK8(read_func())
            error = False
        except Exception as e:
            print(e)
            error = True
        while error:
            try:
                pk8 = PK8(read_func())
                error = False
            except:
                error = True
        
        if not pk8.isValid() or pk8.ec() == 0:
            print("Invalid or Not Present")
            self.last_info = ""
            self.image_display.config(image='')
            self.mark_display.config(image='')
            self.current_info_display.delete(1.0, tk.END)
        if pk8.isValid() and pk8.ec() != 0 and str(pk8) != self.last_info:
            info = str(pk8)
            # print(info)
            s1 = pb.SpriteResource('pokemon', pk8.species(), shiny=pk8.shinyType()).img_data
            if self.type_var.get()-1 == 0:
                try:
                    # print(f"https://www.serebii.net/swordshield/ribbons/{pk8.mark().lower()}mark.png")
                    s2 = urllib.request.urlopen(f"https://www.serebii.net/swordshield/ribbons/{pk8.mark().lower()}mark.png").read()
                    im2 = Image.open(io.BytesIO(s2))
                    image2 = ImageTk.PhotoImage(im2)
                    self.image2 = image2
                    self.mark_display.config(image=image2)
                    info += f"Mark: {pk8.mark()}"
                    # print(info)
                except Exception as e:
                    print(e)
            else:
                self.mark_display.config(image='')
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