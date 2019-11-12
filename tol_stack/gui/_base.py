import logging
import tkinter as tk


class BaseFrame(tk.Frame):
    font_heading = ('Arial', 14, 'bold')
    font = ('Arial', 12)

    def __init__(self, parent, loglevel=logging.INFO, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(loglevel)

        self._parent = parent
        super().__init__(self._parent, padx=3, **kwargs)
