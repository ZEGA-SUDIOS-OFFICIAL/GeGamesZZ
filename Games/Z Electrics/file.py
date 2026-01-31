import customtkinter as cctk
from tkinter import filedialog
from logs import telemetry

class ZegaExplorer:
    def __init__(self, parent, mode="save", callback=None):
        if mode == "save":
            path = filedialog.asksaveasfilename(defaultextension=".zsff", filetypes=[("ZEGA Format", "*.zsff")])
        else:
            path = filedialog.askopenfilename(filetypes=[("ZEGA Format", "*.zsff"), ("CSV", "*.csv")])
        if path and callback: callback(path, mode)