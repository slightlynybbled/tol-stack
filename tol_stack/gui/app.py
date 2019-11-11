import logging
import tkinter as tk
import tkinter.ttk as ttk

from tol_stack.gui._base import BaseFrame
import tol_stack.gui.images as images
from tol_stack.stack import StackPath


class Application(tk.Tk):
    def __init__(self, loglevel=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        super().__init__()

        TitleFrame(self)\
            .grid(row=0, column=0, columnspan=2, sticky='new')
        StackupFrame(self)\
            .grid(row=1, column=0, sticky='new')
        PartDefinitionsFrame(self)\
            .grid(row=1, column=1, sticky='new')

        self.mainloop()


class TitleFrame(BaseFrame):
    def __init__(self, parent, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        tk.Label(self, text='Tolerance Analysis for Mortals', font=self.font_heading)\
            .grid(row=0, column=0, sticky='new')


class StackupFrame(BaseFrame):
    def __init__(self, parent, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        path_types = StackPath.retrieve_stackup_path_types()

        r = 0
        tk.Label(self, text='Stackup', font=self.font_heading)\
            .grid(row=r, column=0, columnspan=2, sticky='new')

        r += 1
        self._stack_type_var = tk.StringVar()
        self._stack_type_var.set(path_types[0])
        #self._stack_type_var.trace('w', callback=self._on_path_type_change)

        tk.Label(self, text='Select Stack Type:').grid(row=r, column=0, sticky='w')
        self._stack_type_cb = ttk.Combobox(self, textvariable=self._stack_type_var, values=path_types)
        self._stack_type_cb.grid(row=r, column=1, sticky='ew')


class PartDefinitionsFrame(BaseFrame):
    def __init__(self, parent, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        self._parts = []

        self.redraw()

    def redraw(self):
        for c in self.winfo_children():
            c.destroy()

        r = 0
        tk.Label(self, text='Parts', font=self.font_heading)\
            .grid(row=r, column=0, sticky='new')

        r += 1
        tk.Button(self, text='Add Part...', font=self.font)\
            .grid(row=r, column=0, sticky='ew')



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Application()
