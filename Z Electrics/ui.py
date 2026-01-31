"""
ZEGA ULTIMATE SPREADSHEET - USER INTERFACE ARCHITECTURE
Version: 2026.2.1 (The "Retina-X" Update)
Owner: ZEGA MegaHQ
Architect: ZEGA Lead Developer
Dependencies: CustomTkinter, NumPy, PIL
"""

import customtkinter as cctk
import tkinter as tk
from typing import List, Tuple, Optional, Any
import numpy as np
from logs import telemetry  # [FIX 1] Added Telemetry Link

# --- ZEGA CORPORATE DESIGN LANGUAGE ---
class ZegaTheme:
    PRIMARY = "#58f01b"      # The Soul of ZEGA
    PRIMARY_DIM = "#45c216"  # Hover State
    BACKGROUND = "#050505"   # Void Black
    SURFACE = "#0a0a0a"      # Elevated Surface
    SURFACE_2 = "#111111"    # Secondary Surface
    BORDER = "#1a1a1a"       # Structural divide
    TEXT_MAIN = "#FFFFFF"
    TEXT_DIM = "#888888"
    FONT_HEAD = ("Impact", 14)
    FONT_BODY = ("Consolas", 12)
    FONT_TINY = ("Consolas", 10)

# -----------------------------------------------------------------------------
# COMPONENT: THE REACTIVE CELL
# -----------------------------------------------------------------------------
class ZegaCell(cctk.CTkEntry):
    def __init__(self, master_grid, row: int, col: int, **kwargs):
        super().__init__(
            master_grid,
            width=110,
            height=30,
            corner_radius=0,
            fg_color=ZegaTheme.SURFACE,
            border_color=ZegaTheme.BORDER,
            border_width=1,
            text_color=ZegaTheme.PRIMARY,
            font=ZegaTheme.FONT_BODY,
            placeholder_text="",
            **kwargs
        )
        self.row = row
        self.col = col
        self.master_grid = master_grid
        
        # High-Speed Event Bindings
        self.bind("<FocusIn>", self._on_focus_acquire)
        self.bind("<FocusOut>", self._on_focus_loss)
        self.bind("<Return>", self._on_commit)
        self.bind("<Button-3>", self._on_context_menu)

    def _on_focus_acquire(self, event):
        self.configure(border_color=ZegaTheme.PRIMARY, border_width=2, fg_color=ZegaTheme.SURFACE_2)
        # [FIX 2] Use Direct Controller Link
        self.master_grid.controller.on_cell_select(self.row, self.col, self.get())

    def _on_focus_loss(self, event):
        self.configure(border_color=ZegaTheme.BORDER, border_width=1, fg_color=ZegaTheme.SURFACE)
        # [FIX 2] Use Direct Controller Link
        self.master_grid.controller.on_cell_edit(self.row, self.col, self.get())

    def _on_commit(self, event):
        self.master_grid.navigate(self.row + 1, self.col)

    def _on_context_menu(self, event):
        telemetry.log("info", f"Context menu requested at {self.row}:{self.col}")

    def inject_value(self, val: str):
        self.delete(0, 'end')
        self.insert(0, str(val))

# -----------------------------------------------------------------------------
# COMPONENT: THE FORMULA BAR
# -----------------------------------------------------------------------------
class ZegaFormulaBar(cctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=40, fg_color=ZegaTheme.SURFACE, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        # Coordinate Label
        self.coord_lbl = cctk.CTkLabel(
            self, 
            text="A1", 
            width=50, 
            font=("Impact", 16), 
            text_color=ZegaTheme.TEXT_DIM,
            fg_color=ZegaTheme.SURFACE_2
        )
        self.coord_lbl.pack(side="left", padx=5, pady=5, fill="y")

        # Function Icon
        self.fx_lbl = cctk.CTkLabel(self, text="ƒx", width=30, font=("Times", 14, "italic"))
        self.fx_lbl.pack(side="left", padx=2)

        # The Input Field
        self.entry = cctk.CTkEntry(
            self, 
            fg_color=ZegaTheme.BACKGROUND, 
            border_color=ZegaTheme.BORDER,
            text_color="#FFFFFF",
            font=ZegaTheme.FONT_BODY
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.entry.bind("<Return>", self._sync_to_cell)

    def update_target(self, row_idx, col_idx, content):
        col_char = chr(65 + (col_idx % 26))
        self.coord_lbl.configure(text=f"{col_char}{row_idx+1}")
        self.entry.delete(0, 'end')
        self.entry.insert(0, content)
        self.current_target = (row_idx, col_idx)

    def _sync_to_cell(self, event):
        if hasattr(self, 'current_target'):
            r, c = self.current_target
            val = self.entry.get()
            self.master.update_grid_cell(r, c, val)

# -----------------------------------------------------------------------------
# COMPONENT: THE HOLOGRAPHIC RIBBON
# -----------------------------------------------------------------------------
class ZegaRibbon(cctk.CTkFrame):
    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, height=100, fg_color=ZegaTheme.SURFACE_2, corner_radius=0, **kwargs)
        self.callbacks = callbacks
        self.pack_propagate(False)

        # Tab Selectors
        self.tab_bar = cctk.CTkFrame(self, height=30, fg_color=ZegaTheme.SURFACE, corner_radius=0)
        self.tab_bar.pack(side="top", fill="x")
        
        self.tabs = ["HOME", "DATA", "C++ ENGINE", "VIEW"]
        self.current_tab = "HOME"
        
        self.btn_tabs = {}
        for t in self.tabs:
            btn = cctk.CTkButton(
                self.tab_bar, 
                text=t, 
                width=80, 
                height=30,
                corner_radius=0,
                fg_color="transparent", 
                text_color=ZegaTheme.TEXT_DIM,
                font=("Impact", 12),
                hover_color=ZegaTheme.BORDER,
                command=lambda x=t: self._switch_tab(x)
            )
            btn.pack(side="left", padx=0)
            self.btn_tabs[t] = btn

        # Tool Area
        self.tool_area = cctk.CTkFrame(self, fg_color="transparent")
        self.tool_area.pack(side="top", fill="both", expand=True, padx=10)
        
        self._switch_tab("HOME")

    def _switch_tab(self, tab_name):
        for name, btn in self.btn_tabs.items():
            if name == tab_name:
                btn.configure(text_color=ZegaTheme.PRIMARY, border_width=0, fg_color=ZegaTheme.SURFACE_2)
            else:
                btn.configure(text_color=ZegaTheme.TEXT_DIM, fg_color="transparent")
        
        for w in self.tool_area.winfo_children():
            w.destroy()
            
        if tab_name == "HOME": self._render_home_tools()
        elif tab_name == "DATA": self._render_data_tools()
        elif tab_name == "C++ ENGINE": self._render_cpp_tools()

    def _render_home_tools(self):
        cctk.CTkLabel(self.tool_area, text="CLIPBOARD", font=ZegaTheme.FONT_TINY).pack(side="left", padx=5, anchor="s")
        self._quick_btn("PASTE", "paste")
        self._quick_btn("COPY", "copy")
        cctk.CTkFrame(self.tool_area, width=2, fg_color=ZegaTheme.BORDER).pack(side="left", fill="y", padx=10)
        cctk.CTkLabel(self.tool_area, text="FONT", font=ZegaTheme.FONT_TINY).pack(side="left", padx=5, anchor="s")
        self._quick_btn("BOLD", "bold")

    def _render_data_tools(self):
        self._quick_btn("SAVE .ZSFF", "save")
        self._quick_btn("LOAD", "load")
        cctk.CTkFrame(self.tool_area, width=2, fg_color=ZegaTheme.BORDER).pack(side="left", fill="y", padx=10)
        self._quick_btn("SANITIZE", "sanitize")

    def _render_cpp_tools(self):
        self._quick_btn("SUM ALL", "sum")
        self._quick_btn("SCALE 1.5x", "scale")
        self._quick_btn("GENERATE REPORT", "report")

    def _quick_btn(self, text, action_key):
        cmd = self.callbacks.get(action_key, lambda: print("No implementation"))
        cctk.CTkButton(
            self.tool_area, 
            text=text, 
            width=80, 
            command=cmd,
            fg_color="transparent",
            border_color=ZegaTheme.PRIMARY,
            border_width=1,
            text_color=ZegaTheme.PRIMARY
        ).pack(side="left", padx=5, pady=10)

# -----------------------------------------------------------------------------
# COMPONENT: THE INFINITE SCROLL GRID
# -----------------------------------------------------------------------------
class ZegaGrid(cctk.CTkScrollableFrame):
    def __init__(self, master, rows, cols, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.rows = rows
        self.cols = cols
        self.controller = controller  # [FIX 2] Direct Controller Reference
        self.cells = [] 
        
        self._build_headers()
        self._build_matrix()

    def _build_headers(self):
        cctk.CTkLabel(self, text="", width=40).grid(row=0, column=0)
        for c in range(self.cols):
            char = chr(65 + (c % 26))
            lbl = cctk.CTkButton(
                self, 
                text=char, 
                width=110, 
                height=25,
                fg_color=ZegaTheme.SURFACE, 
                hover_color=ZegaTheme.BORDER,
                text_color=ZegaTheme.TEXT_DIM,
                corner_radius=0
            )
            lbl.grid(row=0, column=c+1, padx=1)

    def _build_matrix(self):
        for r in range(self.rows):
            cctk.CTkButton(
                self, 
                text=str(r+1), 
                width=40, 
                fg_color=ZegaTheme.SURFACE, 
                text_color=ZegaTheme.TEXT_DIM,
                hover_color=ZegaTheme.BORDER,
                corner_radius=0
            ).grid(row=r+1, column=0, pady=1)

            row_cells = []
            for c in range(self.cols):
                cell = ZegaCell(self, r, c)
                cell.grid(row=r+1, column=c+1, padx=1, pady=1)
                row_cells.append(cell)
            self.cells.append(row_cells)

    def navigate(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.cells[r][c].focus_set()

    def set_cell_value(self, r, c, val):
        self.cells[r][c].inject_value(val)

    def get_all_data_array(self):
        data = np.zeros((self.rows, self.cols))
        for r in range(self.rows):
            for c in range(self.cols):
                try:
                    val = self.cells[r][c].get()
                    if val == "": val = 0.0
                    data[r, c] = float(val)
                except ValueError:
                    data[r, c] = 0.0 
        return data

# -----------------------------------------------------------------------------
# COMPONENT: STATUS TELEMETRY FOOTER
# -----------------------------------------------------------------------------
class ZegaStatusBar(cctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=25, fg_color=ZegaTheme.SURFACE, corner_radius=0, **kwargs)
        self.pack_propagate(False)
        
        self.status_lbl = cctk.CTkLabel(self, text="READY", text_color=ZegaTheme.PRIMARY, font=ZegaTheme.FONT_TINY)
        self.status_lbl.pack(side="left", padx=10)
        
        self.stats_lbl = cctk.CTkLabel(self, text="AVG: 0.0 | SUM: 0.0 | COUNT: 0", text_color="#666", font=ZegaTheme.FONT_TINY)
        self.stats_lbl.pack(side="right", padx=10)

    def set_msg(self, msg):
        self.status_lbl.configure(text=msg.upper())

    def update_stats(self, avg, total, count):
        self.stats_lbl.configure(text=f"AVG: {avg:.2f} | SUM: {total:.2f} | COUNT: {count}")

# -----------------------------------------------------------------------------
# MASTER LAYOUT CONTROLLER
# -----------------------------------------------------------------------------
class ZegaInterface(cctk.CTkFrame):
    def __init__(self, master_app, rows, cols, theme_color):
        super().__init__(master_app, fg_color=ZegaTheme.BACKGROUND)
        self.app = master_app
        self.rows = rows
        self.cols = cols
        
        self.callbacks = {
            "save": lambda: self.app.trigger_file_io("save"),
            "load": lambda: self.app.trigger_file_io("load"),
            "sum": lambda: telemetry.log("info", "Sum engine triggered"),
            "scale": lambda: telemetry.log("info", "Scale engine triggered"),
            "sanitize": lambda: self.update_status("Sanitizing Data..."),
            "report": lambda: self.update_status("Generating PDF..."),
        }

        # 1. Ribbon
        self.ribbon = ZegaRibbon(self, self.callbacks)
        self.ribbon.pack(side="top", fill="x")

        # 2. Formula Bar
        self.formula_bar = ZegaFormulaBar(self)
        self.formula_bar.pack(side="top", fill="x", pady=(1, 0))

        # 3. Status Bar
        self.status_bar = ZegaStatusBar(self)
        self.status_bar.pack(side="bottom", fill="x")

        # 4. The Grid (Passed 'self' as controller)
        self.grid_engine = ZegaGrid(self, rows, cols, controller=self)
        self.grid_engine.pack(side="top", expand=True, fill="both", padx=0, pady=0)

    def on_cell_select(self, r, c, val):
        self.formula_bar.update_target(r, c, val)
        try:
            v = float(val) if val else 0.0
            self.status_bar.update_stats(v, v, 1)
        except:
            self.status_bar.update_stats(0, 0, 1)
        telemetry.log("info", f"Cell Select: [{r}, {c}]")

    def on_cell_edit(self, r, c, val):
        self.app.process_cell_update(r, c, val)

    def update_grid_cell(self, r, c, val):
        self.grid_engine.set_cell_value(r, c, val)
        self.app.process_cell_update(r, c, val)

    def populate_grid(self, data_matrix):
        rows, cols = data_matrix.shape
        for r in range(rows):
            for c in range(cols):
                if r < self.rows and c < self.cols:
                    self.grid_engine.set_cell_value(r, c, data_matrix[r, c])

    def get_all_cell_data(self):
        return self.grid_engine.get_all_data_array()

    def update_status(self, msg):
        self.status_bar.set_msg(msg)