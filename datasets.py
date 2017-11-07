"""
    Warchest: Data management and automation GUI for Machine Learning projects
    Created September 2017
    Copyright (C) Nelson R Gonzalez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from toolbox import exec_qry, exec_insert_qry
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import pandas as pd
import os
import json


class Dataset(tk.Toplevel):

    def __init__(self, parent, datasets_path):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Datasets')
        self.parent = parent
        self.datasets_path = datasets_path

        self.config(background="#ffffff")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (800, 500,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.default_dataset = self.get_default_dataset()
        self.select_area_var = tk.IntVar()
        self.select_area_var.set(1)

        self.setup_styles()
        self.create_gui()
        self.grab_set()

    def setup_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Body.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')

    def get_default_dataset(self):

        qry = 'SELECT DefaultDataset FROM Datasets'
        cursor = exec_qry(qry)

        for row in cursor:
            return row[0]

    def create_gui(self):

        self.create_select_area()
        self.create_browse_area()
        self.create_default_area()

    def create_select_area(self):

        self.select_area_frame = tk.Frame(self, background="#ffffff")
        self.select_area_frame.grid(row=0, column=0, rowspan=2, sticky='nsew')

        self.select_existing_datasets_section_label = \
            ttk.Label(self.select_area_frame,
                      text="Select From Existing Datasets")
        self.select_existing_datasets_section_label.grid(row=0, column=0,
                                                         columnspan=2,
                                                         sticky="nsew",
                                                         padx=1, pady=1)
        self.select_existing_datasets_section_label. \
            configure(style='Sections.TLabel')

        self.default_dataset_label = \
            ttk.Label(self.select_area_frame,
                      text="Default Dataset:",
                      name="default_dataset_label")
        self.default_dataset_label.grid(row=1, column=1, sticky="nsew",
                                             padx=1, pady=1)
        self.default_dataset_label.configure(style='Body.TLabel')

        self.default_dataset_radiobutton = \
            ttk.Radiobutton(self.select_area_frame,
                            variable=self.select_area_var,
                            value=1,
                            command=self.on_select_area_toggle_clicked)
        self.default_dataset_radiobutton.grid(row=2, column=0, sticky="nsew",
                                             padx=1, pady=1)

        self.default_dataset_entry = \
            tk.Entry(self.select_area_frame,
                     text="",
                     #readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="default_dataset_entry")
        self.default_dataset_entry.grid(row=2, column=1, sticky="nsew",
                                             padx=1, pady=1)
        self.default_dataset_entry.delete(0, tk.END)
        self.default_dataset_entry.insert(0, self.default_dataset)
        self.default_dataset_entry.configure(state='readonly')

        self.available_datasets_label = \
            ttk.Label(self.select_area_frame,
                      text="Available Datasets:",
                      name="available_datasets_label")
        self.available_datasets_label.grid(row=3, column=1, sticky="nsew",
                                             padx=1, pady=1)
        self.available_datasets_label.configure(style='Body.TLabel')

        self.available_dataset_radiobutton = \
            ttk.Radiobutton(self.select_area_frame,
                            variable=self.select_area_var,
                            value=2,
                            command=self.on_select_area_toggle_clicked)
        self.available_dataset_radiobutton.grid(row=4, column=0, sticky="nsew",
                                             padx=1, pady=1)

        self.available_dataset_listbox = \
            tk.Listbox(self.select_area_frame,
                       selectmode=tk.SINGLE,
                     background='grey95',
                     disabledforeground='grey',
                     relief='flat',
                     activestyle='none',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="available_dataset_listbox")
        self.available_dataset_listbox.grid(row=4, column=1, sticky="nsew",
                                             padx=1, pady=1)
        self.update_available_datasets_listbox()
        self.available_dataset_listbox.configure(state='disabled')
        self.available_dataset_scrollbar = \
            ttk.Scrollbar(self.select_area_frame, orient=tk.VERTICAL,
                          command=self.available_dataset_listbox.yview)
        self.available_dataset_scrollbar.grid(row=4, column=2,
                                         sticky='ns', padx=0, pady=1)
        self.available_dataset_listbox.configure(yscrollcommand=self.
                                    available_dataset_scrollbar.set)


        self.select_area_ok_button = \
            ttk.Button(self.select_area_frame,
                       text="OK",
                       name="select_area_ok_button",
                       command=self.
                       on_select_area_ok_button_clicked)
        self.select_area_ok_button.grid(row=5, column=1, sticky="nsew",
                                         padx=1, pady=1)



    def create_browse_area(self):

        self.browse_area_frame = tk.Frame(self, background="#ffffff")
        self.browse_area_frame.grid(row=0, column=1, sticky='nsew')

        self.browse_local_datasets_section_label = \
            ttk.Label(self.browse_area_frame,
                      text="Browse Local Datasets")
        self.browse_local_datasets_section_label.grid(row=0, column=0,
                                                         columnspan=2,
                                                         sticky="nsew",
                                                         padx=1, pady=1)
        self.browse_local_datasets_section_label. \
            configure(style='Sections.TLabel')

        self.browse_local_dataset_label = \
            ttk.Label(self.browse_area_frame,
                      text="Browse Dataset:",
                      name="browse_local_dataset_label")
        self.browse_local_dataset_label.grid(row=1, column=0, sticky="nsew",
                                             columnspan=2, padx=1, pady=1)
        self.browse_local_dataset_label.configure(style='Body.TLabel')

        self.browse_local_dataset_entry = \
            tk.Entry(self.browse_area_frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="browse_local_dataset_entry")
        self.browse_local_dataset_entry.grid(row=2, column=0, sticky="nsew",
                                             columnspan=2, padx=1, pady=1)
        self.browse_local_dataset_entry.configure(state='readonly')

        self.browse_local_dataset_button = \
            ttk.Button(self.browse_area_frame,
                       text="Browse...",
                       name="browse_local_dataset_button",
                       command=lambda: self.
                       on_aw_add_new_line_button_clicked(self.aw_frame))
        self.browse_local_dataset_button.grid(row=3, column=0, sticky="nsew",
                                         padx=1, pady=1)

        self.browse_area_ok_button = \
            ttk.Button(self.browse_area_frame,
                       text="OK",
                       name="browse_area_ok_button",
                       command=lambda: self.
                       on_aw_add_new_line_button_clicked(self.aw_frame))
        self.browse_area_ok_button.grid(row=3, column=1, sticky="nsew",
                                         padx=1, pady=1)

    def create_default_area(self):

        self.default_area_frame = tk.Frame(self, background="#ffffff")
        self.default_area_frame.grid(row=1, column=1, sticky='nsew')

        self.choose_default_datasets_section_label = \
            ttk.Label(self.default_area_frame,
                      text="Choose Default Datasets")
        self.choose_default_datasets_section_label.grid(row=0, column=0,
                                                         columnspan=2,
                                                         sticky="nsew",
                                                         padx=1, pady=1)
        self.choose_default_datasets_section_label. \
            configure(style='Sections.TLabel')

        self.choose_default_dataset_label = \
            ttk.Label(self.default_area_frame,
                      text="Choose Default Dataset:",
                      name="choose_default_dataset_label")
        self.choose_default_dataset_label.grid(row=1, column=0, sticky="nsew",
                                             columnspan=2, padx=1, pady=1)
        self.choose_default_dataset_label.configure(style='Body.TLabel')

        self.choose_default_dataset_entry = \
            tk.Entry(self.default_area_frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="choose_default_dataset_entry")
        self.choose_default_dataset_entry.grid(row=2, column=0, sticky="nsew",
                                               columnspan=2, padx=1, pady=1)
        self.choose_default_dataset_entry.configure(state='readonly')

        self.choose_default_dataset_button = \
            ttk.Button(self.default_area_frame,
                       text="Browse...",
                       name="choose_default_dataset_button",
                       command=lambda: self.
                       on_aw_add_new_line_button_clicked(self.aw_frame))
        self.choose_default_dataset_button.grid(row=3, column=0, sticky="nsew",
                                         padx=1, pady=1)

        self.default_area_ok_button = \
            ttk.Button(self.default_area_frame,
                       text="OK",
                       name="default_area_ok_button",
                       command=lambda: self.
                       on_aw_add_new_line_button_clicked(self.aw_frame))
        self.default_area_ok_button.grid(row=3, column=1, sticky="nsew",
                                         padx=1, pady=1)

    def on_select_area_toggle_clicked(self):

        if self.select_area_var.get() == 1:
            self.available_dataset_listbox.configure(state='disabled')
            self.available_dataset_listbox.configure(background='grey95')

            self.default_dataset_entry.focus_set()

        elif self.select_area_var.get() == 2:
            self.available_dataset_listbox.configure(state='normal')
            self.available_dataset_listbox.configure(background='white')

            self.default_dataset_entry.configure(state='readonly')

            self.available_dataset_listbox.focus_set()

    def on_select_area_ok_button_clicked(self):

        if self.select_area_var.get() == 1:
            self.set_selected_dataset(self.default_dataset)
        elif self.select_area_var.get() == 2:
            selected_item = self.available_dataset_listbox. \
                get(self.available_dataset_listbox.curselection()[0])
            self.set_selected_dataset(selected_item)
        self.exit_window()

    def set_selected_dataset(self, dataset):

        qry = 'UPDATE Datasets SET SelectedDataset=?'
        parameters = (dataset,)
        exec_qry(qry, parameters)

    def update_available_datasets_listbox(self):

        files_in_dir = []
        for (dir_path, dir_names, file_names) in os.walk(self.datasets_path):
            for file in file_names:
                if file.endswith(".csv"):
                    files_in_dir.append(file)
        for file in files_in_dir:
            self.available_dataset_listbox.insert(tk.END, file)

    def exit_window(self):

        self.destroy()
