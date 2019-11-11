import logging
import tkinter as tk
import tkinter.ttk as ttk

from tol_stack.gui._base import BaseFrame
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
        PartsFrame(self)\
            .grid(row=1, column=1, sticky='new')

        self.mainloop()


class TitleFrame(BaseFrame):
    def __init__(self, parent, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        tk.Label(self, text='Tolerance Analysis for Mortals', font=self.font_heading)\
            .grid(row=0, column=0, sticky='new')


class StackupFrame(BaseFrame):
    def __init__(self, parent, on_change_callback: callable = None, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        path_types = StackPath.retrieve_stackup_path_types()
        self._on_change_callback = on_change_callback

        r = 0
        tk.Label(self, text='Stackup', font=self.font_heading)\
            .grid(row=r, column=0, columnspan=2, sticky='new')

        r += 1
        self._stack_type_var = tk.StringVar()
        self._stack_type_var.set(path_types[0])
        self._stack_type_var.trace('w', callback=self._on_change)

        tk.Label(self, text='Select Stack Type:').grid(row=r, column=0, sticky='w')
        self._stack_type_cb = ttk.Combobox(self, textvariable=self._stack_type_var, values=path_types)
        self._stack_type_cb.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Samples', font=self.font).grid(row=r, column=0, sticky='e')
        self._size_entry = tk.Entry(self)
        self._size_entry.grid(row=r, column=1, sticky='ew')
        self._size_entry.insert(0, '100000')

        self._size_entry.bind('<Return>', self._on_change)

    def _on_change(self, *args):
        path_type = self._stack_type_var.get()
        size = int(self._size_entry.get())

        self._logger.info(f'Data changed; path_type="{path_type}", size={size}')

        if self._on_change_callback is not None:
            self._on_change_callback(
                path_type=path_type,
                size=size
            )


class PartsFrame(BaseFrame):
    def __init__(self, parent, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        self._parts_label = None
        self._add_part_btn = None
        self._part_frames = []

        self.redraw()

    def redraw(self):
        for c in self.winfo_children():
            c.grid_forget()

        r = 0
        if self._parts_label is None:
            self._parts_label = tk.Label(self, text='Parts', font=self.font_heading)
        self._parts_label.grid(row=r, column=0, sticky='new')

        for frame in self._part_frames:
            if not frame.removed:
                r += 1
                frame.grid(row=r, column=0, sticky='ew')

        r += 1
        if self._add_part_btn is None:
            self._add_part_btn = tk.Button(self, text='Add Part...', command=self._add_part, font=self.font)
        self._add_part_btn.grid(row=r, column=0, sticky='ew')

    def _add_part(self):
        self._part_frames.append(
            PartFrame(self)
        )
        self.redraw()


class PartFrame(BaseFrame):
    def __init__(self, parent, on_update_callback: callable = None, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        self._on_update_callback = on_update_callback
        self.removed = False

        c = 0
        self._name_entry = tk.Entry(self)
        self._name_entry.grid(row=0, column=c, sticky='ew')

        c += 1
        self._dist_cb = ttk.Combobox(self)
        self._dist_cb.grid(row=0, column=c, sticky='ew')

        c += 1
        self._nominal_entry = tk.Entry(self)
        self._nominal_entry.grid(row=0, column=c, sticky='ew')

        c += 1
        self._tolerance_entry = tk.Entry(self)
        self._tolerance_entry.grid(row=0, column=c, sticky='ew')

        c += 1
        self._maximum_entry = tk.Entry(self)
        self._maximum_entry.grid(row=0, column=c, sticky='ew')

        c += 1
        self._minimum_entry = tk.Entry(self)
        self._minimum_entry.grid(row=0, column=c, sticky='ew')

        c += 1
        self._remove_btn = tk.Button(self, text='-', command=self._remove)
        self._remove_btn.grid(row=0, column=c, sticky='ew')

    def _remove(self):
        self.removed = True

    def _on_update(self, *args):
        if self._on_update_callback is not None:
            self._on_update_callback()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Application()
