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
            .grid(row=r, column=0, columnspan=2, sticky='ew')

        r += 1
        self._limits_frame = LimitsFrame(self)
        self._limits_frame.grid(row=r, column=0, sticky='new')

        self._stack_canvas = StackCanvas(self)
        self._stack_canvas.grid(row=r, column=1, rowspan=2, sticky='news')

        r += 1
        self._parts_frame = PartsFrame(self)
        self._parts_frame.grid(row=r, column=0, sticky='new')


class LimitsFrame(_BaseFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        r = 0
        tk.Label(self, text='Maximum Target Height', font=self._font)\
            .grid(row=r, column=0, sticky='e')
        self._max_height_entry = tk.Entry(self)
        self._max_height_entry.grid(row=r, column=1, sticky='ew')

        r += 1
        tk.Label(self, text='Minimum Target Height', font=self._font)\
            .grid(row=r, column=0, sticky='e')
        self._min_height_entry = tk.Entry(self)
        self._min_height_entry.grid(row=r, column=1, sticky='ew')


class PartsFrame(_BaseFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._parts = {}
        self._redraw()

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

        if len(self._parts) == 0:
            pn_entry = tk.Entry(self, font=self._font, relief='sunken')
            pn_entry.grid(row=row, column=0, sticky='ew')

            dist_entry = tk.Entry(self, font=self._font, relief='sunken')
            dist_entry.grid(row=row, column=1, sticky='ew')

            nom_entry = tk.Entry(self, font=self._font, relief='sunken')
            nom_entry.grid(row=row, column=2, sticky='ew')

            tol_entry = tk.Entry(self, font=self._font, relief='sunken')
            tol_entry.grid(row=row, column=3, sticky='ew')
        else:
            for part_name, part in self._parts.items():
                pn_entry = tk.Entry(self, text=part.name, font=self._font, relief='sunken')
                pn_entry.grid(row=row, column=0, sticky='ew')

                dist_entry = tk.Entry(self, text=part.distribution, font=self._font, relief='sunken')
                dist_entry.grid(row=row, column=1, sticky='ew')

                nom_entry = tk.Entry(self, text=part.nominal_length, font=self._font, relief='sunken')
                nom_entry.grid(row=row, column=2, sticky='ew')

                tol_entry = tk.Entry(self, text=part.tolerance, font=self._font, relief='sunken')
                tol_entry.grid(row=row, column=3, sticky='ew')

                remove_label = tk.Label(self, text='-', font=self._font, relief='raised')
                remove_label.grid(row=row, column=4, sticky='ew')

                remove_label.bind('<Button-1>', lambda _, x=part_name: self.remove_part(x))

                row += 1

    def add_part(self, name: str, distribution: str, nominal: (int, float), tolerance: (int, float)):
        if name in self._parts.keys():
            showerror('Part already exists', 'Part name already exists')
            return

        part = Part(
            name=name,
            distribution=distribution,
            nominal_length=nominal,
            tolerance=tolerance
        )

        self._parts[name] = part

        self._redraw()

    def remove_part(self, name: str):
        self._parts.pop(name)
        self._redraw()


class StackCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        self._parent = parent

        self._height, self._width = 400, 400
        self._max_height, self._min_height = None, None

        super().__init__(self._parent, height=self._height, width=self._width, **kwargs)

        self._draw_datum()
        self.add_max_height()

    def _draw_datum(self):
        # find x0, y0
        x0 = int(self._width * 0.1)
        y0 = int(self._height / 2)

        # find x1, y1
        x1 = int(self._width * 0.9)
        y1 = y0

        self.create_line(x0, y0, x1, y1)
        self.create_text(x1, y1, text='datum', anchor='ne')

    def add_max_height(self, height=None):
        # find x0, y0
        x0 = int(self._width * 0.1)
        y0 = int(self._height / 4)

        # find x1, y1
        x1 = int(self._width * 0.9)
        y1 = y0

        self.create_line(x0, y0, x1, y1, fill='red')
        self.create_text(x1, y1, text='max height', anchor='se', fill='red')

if __name__ == '__main__':
    Application()
