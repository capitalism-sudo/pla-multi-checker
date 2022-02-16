from tkinter import Widget
from tkinter.ttk import Treeview

class DataGridView(Treeview):
    def __init__(self,*args,sizes=[],**kwargs):
        super().__init__(*args,**kwargs)
        self.sizes = sizes
        self.set_columns()
    
    def set_columns(self):
        i = 0
        for column in self['columns']:
            self.heading(column,text=column)
            self.column(column,width=self.sizes[i])
            i += 1
        self['show'] = 'headings'
    
    def clear(self):
        for item in self.get_children():
            self.delete(item)