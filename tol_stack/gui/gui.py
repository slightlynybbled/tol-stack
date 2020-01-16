import tkinter as tk
from tkinter.messagebox import showerror

from tol_stack.stack import Part


class _BaseFrame(tk.Frame):
    _font = 'Arial', 14
    _heading = 'Arial', 16, 'bold'

    def __init__(self, parent, **kwargs):
        self._parent = parent
        super().__init__(self._parent, **kwargs)


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        MainFrame(self).grid(row=0, column=0)

        self.mainloop()


class MainFrame(_BaseFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        r = 0
        tk.Label(self, text='Tolerance Stack Analysis', font=self._heading)\
            .grid(row=r, column=0, columnspan=3, sticky='ew')

        r += 1
        self._pf = PartsFrame(self)
        AddPartFrame(self, on_add_callback=self._pf.add_part)\
            .grid(row=r, column=0, sticky='news')
        tk.Label(self, text='==>', font=self._heading)\
            .grid(row=r, column=1, sticky='ew')
        self._pf.grid(row=r, column=2, sticky='news')


class AddPartFrame(_BaseFrame):
    def __init__(self, parent, on_add_callback: callable, **kwargs):
        super().__init__(parent, **kwargs)

        self._on_add_callback = on_add_callback

        r = 0

        tk.Label(self, text='Part Name', font=self._font)\
            .grid(row=r, column=0, sticky='e')
        self._name_entry = tk.Entry(self)
        self._name_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Distribution', font=self._font)\
            .grid(row=r, column=0, sticky='e')
        self._dist_var = tk.StringVar()
        self._dist_var.set(Part.retrieve_distributions()[0])
        self._dist_om = tk.OptionMenu(self, self._dist_var, *Part.retrieve_distributions())
        self._dist_om.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Nominal Value', font=self._font)\
            .grid(row=r, column=0, sticky='e')
        self._nominal_entry = tk.Entry(self)
        self._nominal_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Tolerance', font=self._font)\
            .grid(row=r, column=0, sticky='e')
        self._tolerance_entry = tk.Entry(self)
        self._tolerance_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Button(self, text='Add Part', font=self._font, command=self._on_add_part)\
            .grid(row=r, column=0, columnspan=2, sticky='ew')

    def _on_add_part(self):
        name = self._name_entry.get().strip()
        nominal_str = self._nominal_entry.get().strip()
        tolerance_str = self._tolerance_entry.get().strip()

        if name == '':
            showerror('Name is Empty', 'The part name value must not be empty.')
            return

        if nominal_str == '':
            showerror('Nominal value empty!', 'The nominal value must not be empty.')
            return
        if tolerance_str == '':
            showerror('Tolerance value empty!', 'The tolerance value must not be empty.')
            return

        try:
            nominal = float(nominal_str)
        except ValueError as e:
            showerror('Bad nominal value', f'The nominal value is not valid\nError: {e}')
            return

        try:
            tolerance = float(tolerance_str)
        except ValueError as e:
            showerror('Bad tolerance value', f'The tolerance value is not valid\nError: {e}')
            return

        self._on_add_callback(name=name, distribution=self._dist_var.get(), nominal=nominal, tolerance=tolerance)

        self._name_entry.delete(0, 'end')
        self._dist_var.set(Part.retrieve_distributions()[0])
        self._nominal_entry.delete(0, 'end')
        self._tolerance_entry.delete(0, 'end')


class PartsFrame(_BaseFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._parts = {}

    def _redraw(self):
        # remove parts currently in the frame
        for child in self.winfo_children():
            child.destroy()

        row = 0
        tk.Label(self, text='Parts List', font=self._heading)\
            .grid(row=row, column=0, columnspan=5, sticky='ew')

        row += 1
        tk.Label(self, text='Part', font=self._font, relief='sunken')\
            .grid(row=row, column=0, sticky='ew')
        tk.Label(self, text='Distribution', font=self._font, relief='sunken')\
            .grid(row=row, column=1, sticky='ew')
        tk.Label(self, text='Value', font=self._font, relief='sunken')\
            .grid(row=row, column=2, sticky='ew')
        tk.Label(self, text='Tolerance', font=self._font, relief='sunken')\
            .grid(row=row, column=3, sticky='ew')

        row += 1
        for part_name, part in self._parts.items():
            pn_label = tk.Label(self, text=part.name, font=self._font, relief='sunken')
            pn_label.grid(row=row, column=0, sticky='ew')

            dist_label = tk.Label(self, text=part.distribution, font=self._font, relief='sunken')
            dist_label.grid(row=row, column=1, sticky='ew')

            nom_label = tk.Label(self, text=part.nominal_value, font=self._font, relief='sunken')
            nom_label.grid(row=row, column=2, sticky='ew')

            tol_label = tk.Label(self, text=part.tolerance, font=self._font, relief='sunken')
            tol_label.grid(row=row, column=3, sticky='ew')

            remove_label = tk.Label(self, text='-', font=self._font, relief='raised')
            remove_label.grid(row=row, column=4, sticky='ew')

            remove_label.bind('<Button-1>', lambda _, x=part_name: self.remove_part(x))

            row += 1

    def add_part(self, name: str, distribution: str, nominal: (int, float), tolerance: (int, float)):
        part = Part(
            name=name,
            distribution=distribution,
            nominal_value=nominal,
            tolerance=tolerance
        )

        self._parts[name] = part

        self._redraw()

    def remove_part(self, name: str):
        self._parts.pop(name)
        self._redraw()


if __name__ == '__main__':
    Application()
