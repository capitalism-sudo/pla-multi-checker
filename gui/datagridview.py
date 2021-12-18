from tkinter import Widget
from tkinter.ttk import Treeview

class DataGridView(Treeview):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_columns()
    
    def set_columns(self):
        for column in self['columns']:
            self.heading(column,text=column)
            self.column(column,width=100)
        self['show'] = 'headings'
    
    def clear(self):
        for item in self.get_children():
            self.delete(item)