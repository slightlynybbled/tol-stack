import logging
import tkinter as tk
import tkinter.ttk as ttk

from tol_stack.gui._base import BaseFrame, BaseTop
from tol_stack.stack import Part, StackPath


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
        self._parts = []

        self.redraw()

    def redraw(self):
        r = 0
        if self._parts_label is None:
            self._parts_label = tk.Label(self, text='Parts', font=self.font_heading)
        self._parts_label.grid(row=r, column=0, sticky='new')

        # for frame in self._part_frames:
        #     r += 1
        #     frame.grid(row=r, column=0, sticky='ew')

        r += 1
        if self._add_part_btn is None:
            self._add_part_btn = tk.Button(self, text='Add Part...', command=self._add_part, font=self.font)
        self._add_part_btn.grid(row=r, column=0, sticky='ew')

    def _add_part_callback(self, part: Part):
        self._parts.append(part)

    def _add_part(self):
        PartWindow(self, on_add_callback=self._add_part_callback)
        self.redraw()


class PartWindow(BaseTop):
    def __init__(self, parent, on_add_callback: callable, loglevel=logging.INFO):
        super().__init__(parent=parent, loglevel=loglevel)

        self._on_add_callback = on_add_callback

        r = 0
        tk.Label(self, text='Name:', font=self.font)\
            .grid(row=r, column=0, sticky='e')
        self._name_entry = tk.Entry(self)
        self._name_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Distribution:', font=self.font)\
            .grid(row=r, column=0, sticky='e')
        self._dist_cb = ttk.Combobox(self, values=Part.retrieve_distributions())
        self._dist_cb.grid(row=r, column=1, sticky='ew')
        self._dist_cb.set('norm')

        r += 1
        tk.Label(self, text='Nominal Value:', font=self.font)\
            .grid(row=r, column=0, sticky='e')
        self._nominal_entry = tk.Entry(self)
        self._nominal_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Tolerance:', font=self.font)\
            .grid(row=r, column=0, sticky='e')
        self._tolerance_entry = tk.Entry(self)
        self._tolerance_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Upper Limit:', font=self.font)\
            .grid(row=r, column=0, sticky='e')
        self._upper_limit_entry = tk.Entry(self)
        self._upper_limit_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Lower Limit:', font=self.font)\
            .grid(row=r, column=0, sticky='e')
        self._lower_limit_entry = tk.Entry(self)
        self._lower_limit_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Button(self, text='Add Part', command=self._add_part)\
            .grid(row=r, column=0, columnspan=2, sticky='ew')

        r += 1
        tk.Button(self, text='Cancel', command=self._cancel)\
            .grid(row=r, column=0, columnspan=2, sticky='ew')

    def _add_part(self):
        name_str = self._name_entry.get().strip()
        dist_str = self._dist_cb.get().strip()
        nominal_str = self._nominal_entry.get().strip()
        tolerance_str = self._nominal_entry.get().strip()
        upper_limit_str = self._upper_limit_entry.get().strip()
        lower_limit_str = self._upper_limit_entry.get().strip()

        if upper_limit_str and lower_limit_str:
            limits = (float(upper_limit_str), float(lower_limit_str))
        elif upper_limit_str:
            limits = float(upper_limit_str)
        else:
            limits = None

        part = Part(
            name=name_str,
            distribution=dist_str,
            nominal_value=float(nominal_str),
            tolerance=float(tolerance_str),
            size=1000,
            limits=limits
        )

        if self._on_add_callback is not None:
            self._on_add_callback(part)

        self.destroy()

    def _cancel(self):
        self.destroy()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Application()
