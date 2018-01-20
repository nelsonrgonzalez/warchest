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

from toolbox import exec_qry, exec_insert_qry, is_even
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class ClassifiersCRUD(tk.Toplevel):

    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Classifiers')
        self.parent = parent

        self.config(background="#ffffff")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (800, 328,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.needs_scaling = tk.StringVar()
        self.is_optional = tk.StringVar()
        self.is_active = tk.StringVar()

        self.setup_styles()
        self.create_gui()
        self.focus_set()
        self.grab_set()

    def setup_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Body.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')

    def create_gui(self):
        self.create_tree_view()
        self.create_right_buttons()
        self.view_classifiers()

    def create_tree_view(self):
        self.classifier_tree = ttk.Treeview(self, height=15, columns=2)
        self.classifier_tree.grid(row=0, column=0, rowspan=3)
        self.classifier_tree.column('#0', width=600)
        self.classifier_tree.column(2, width=50)
        self.classifier_tree.heading('#0', text='Classifier', anchor=tk.W)
        self.classifier_tree.heading(2, text='Active', anchor=tk.W)

        self.classifier_tree.tag_configure('odd_row', background='white')
        self.classifier_tree.tag_configure('even_row', background='grey90')

        self.classifier_tree.bind("<Double-Button-1>",
                               self.classifier_tree_handle_double_click)

        self.classifier_tree_scrollbar = \
            ttk.Scrollbar(self, orient=tk.VERTICAL,
                          command=self.classifier_tree.yview)
        self.classifier_tree_scrollbar.grid(row=0, column=1, rowspan=3,
                                         sticky='ns')
        self.classifier_tree.configure(yscrollcommand=self.
                                    classifier_tree_scrollbar.set)

    def create_right_buttons(self):
        self.right_buttons_frame = tk.Frame(self, background="#ffffff")
        self.right_buttons_frame.grid(row=0, column=2, sticky='nsew')

        ttk.Button(self.right_buttons_frame, text='Add New Classifier',
                   command=self.on_add_new_classifier_button_clicked).grid(
                   row=0, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Delete Classifier',
                   command=self.on_delete_classifier_button_clicked).grid(
                   row=1, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Modify Classifier',
                   command=self.on_modify_classifier_button_clicked).grid(
                   row=2, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Toggle Selection',
                   command=self.on_toggle_selection_button_clicked).grid(
                   row=3, column=2, sticky="nsew", padx=10, pady=1)

    def on_add_new_classifier_button_clicked(self):

        self.open_add_new_classifier_window()

    def on_delete_classifier_button_clicked(self):

        try:
            self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No classifier was selected.")
            return
        self.delete_classifier()

    def on_modify_classifier_button_clicked(self):

        try:
            self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No classifier was selected.")
            return
        self.open_modify_classifier_window()

    def on_toggle_selection_button_clicked(self):

        try:
            self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
            ndx = self.classifier_tree.index(self.classifier_tree.selection()[0])
        except IndexError as e:
            messagebox.showwarning("Warning", "No classifier was selected.")
            return

        algorithm_id = self. \
            get_algorithm_id(self.classifier_tree.
                             item(self.classifier_tree.selection())['text'])

        if self.is_classifier_active() is True:
            qry = 'UPDATE Algorithms SET IsActive=? WHERE AlgorithmID=?'
            parameters = ("No", algorithm_id)
            exec_qry(qry, parameters)
        else:
            qry = 'UPDATE Algorithms SET IsActive=? WHERE AlgorithmID=?'
            parameters = ("Yes", algorithm_id)
            exec_qry(qry, parameters)

        self.view_classifiers()
        items = self.classifier_tree.get_children()
        for i, item in enumerate(items):
            if i == ndx:
                self.classifier_tree.selection_set(item)

    def on_add_new_param_button_clicked(self):

        self.open_add_new_param_window()

    def on_delete_param_button_clicked(self):

        try:
            self.params_tree.item(self.params_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No parameter was selected.")
            return
        self.delete_param()

    def on_modify_param_button_clicked(self):

        try:
            self.params_tree.item(self.params_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No parameter was selected.")
            return
        self.open_modify_param_window()

    def is_classifier_active(self):

        if (self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
                == "Yes"):
            return True
        else:
            return False

    def view_classifiers(self):
        items = self.classifier_tree.get_children()
        for item in items:
            self.classifier_tree.delete(item)
        qry = 'SELECT * FROM Algorithms WHERE AlgorithmTypeID=1 ORDER BY AlgorithmDesc'
        classifiers = exec_qry(qry)
        for i, row in enumerate(classifiers):
            if is_even(i):
                self.classifier_tree.insert('', 0, text=row[3], values=row[10],
                                            tags=('even_row',))
            else:
                self.classifier_tree.insert('', 0, text=row[3], values=row[10],
                                            tags=('odd_row',))

    def view_params(self):

        for item in self.params_tree.get_children():
            self.params_tree.delete(item)

        qry = 'SELECT * FROM AlgorithmParams WHERE AlgorithmID=? ORDER BY ParamName DESC'
        parameters = (self.algorithm_id,)
        cursor = exec_qry(qry, parameters)

        for i, row in enumerate(cursor):
            if row[6] == 1:
                is_optional = 'Yes'
            else:
                is_optional = 'No'
            if row[7] == 1:
                is_active = 'Yes'
            else:
                is_active = 'No'
            if is_even(i):
                self.params_tree.insert('', 0, text=row[2],
                                                     values=(row[3],
                                                     row[4], is_optional,
                                                     is_active),
                                                     tags=('even_row',))
            else:
                self.params_tree.insert('', 0, text=row[2],
                                                     values=(row[3],
                                                     row[4], is_optional,
                                                     is_active),
                                                     tags=('odd_row',))

    def show_classifier_entries(self, frame):

        self.general_information_section_label = \
            ttk.Label(frame,
                      text="General Information")
        self.general_information_section_label.grid(row=0, column=0,
                                                    columnspan=2,
                                                    sticky="nsew",
                                                    padx=1, pady=1)
        self.general_information_section_label. \
            configure(style='Sections.TLabel')

        # algorithm_name_entry
        self.algorithm_name_label = \
            ttk.Label(frame,
                      text="Name:",
                      name="algorithm_name_label")
        self.algorithm_name_label.grid(row=1, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_name_label.configure(style='Body.TLabel')
        self.algorithm_name_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_name_entry")
        self.algorithm_name_entry.grid(row=1, column=1, sticky="nsew",
                                       padx=1, pady=1)

        # algorithm_internal_name_entry
        self.algorithm_internal_name_label = \
            ttk.Label(frame,
                      text="Internal name:",
                      name="algorithm_internal_name_label")
        self.algorithm_internal_name_label.grid(row=2, column=0, sticky="nsew",
                                                padx=1, pady=1)
        self.algorithm_internal_name_label.configure(style='Body.TLabel')
        self.algorithm_internal_name_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_internal_name_entry")
        self.algorithm_internal_name_entry.grid(row=2, column=1, sticky="nsew",
                                                padx=1, pady=1)

        # algorithm_desc_entry
        self.algorithm_desc_label = \
            ttk.Label(frame,
                      text="Description:",
                      name="algorithm_desc_label")
        self.algorithm_desc_label.grid(row=3, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_desc_label.configure(style='Body.TLabel')
        self.algorithm_desc_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_desc_entry")
        self.algorithm_desc_entry.grid(row=3, column=1, sticky="nsew",
                                       padx=1, pady=1)

        # algorithm_notes_entry
        self.algorithm_notes_label = \
            ttk.Label(frame,
                      text="Notes:",
                      name="algorithm_notes_label")
        self.algorithm_notes_label.grid(row=4, column=0, sticky="nsew",
                                        padx=1, pady=1)
        self.algorithm_notes_label.configure(style='Body.TLabel')
        self.algorithm_notes_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_notes_entry")
        self.algorithm_notes_entry.grid(row=4, column=1, sticky="nsew",
                                        padx=1, pady=1)

        # algorithm_docs_entry
        self.algorithm_docs_label = \
            ttk.Label(frame,
                      text="Documentation:",
                      name="algorithm_docs_label")
        self.algorithm_docs_label.grid(row=5, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_docs_label.configure(style='Body.TLabel')
        self.algorithm_docs_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_docs_entry")
        self.algorithm_docs_entry.grid(row=5, column=1, sticky="nsew",
                                       padx=1, pady=1)

        # algorithm_guides_entry
        self.algorithm_guides_label = \
            ttk.Label(frame,
                      text="Guides:",
                      name="algorithm_guides_label")
        self.algorithm_guides_label.grid(row=6, column=0, sticky="nsew",
                                         padx=1, pady=1)
        self.algorithm_guides_label.configure(style='Body.TLabel')
        self.algorithm_guides_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_guides_entry")
        self.algorithm_guides_entry.grid(row=6, column=1, sticky="nsew",
                                         padx=1, pady=1)

        # algorithm_wiki_entry
        self.algorithm_wiki_label = \
            ttk.Label(frame,
                      text="Wiki:",
                      name="algorithm_wiki_label")
        self.algorithm_wiki_label.grid(row=7, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_wiki_label.configure(style='Body.TLabel')
        self.algorithm_wiki_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=80,
                     name="algorithm_wiki_entry")
        self.algorithm_wiki_entry.grid(row=7, column=1, sticky="nsew",
                                       padx=1, pady=1)

        # needs_scaling_combo
        self.needs_scaling_label = \
            ttk.Label(frame,
                      text="Scaling:",
                      name="needs_scaling_label")
        self.needs_scaling_label.grid(row=8, column=0, sticky="nsew",
                                      padx=1, pady=1)
        self.needs_scaling_label.configure(style='Body.TLabel')
        self.needs_scaling_combo = \
            ttk.Combobox(frame,
                         textvariable=self.needs_scaling,
                         values=('Yes', 'No'),
                         width=25)
        self.needs_scaling_combo.grid(row=8, column=1, sticky="nsew",
                                      padx=1, pady=1)
        self.needs_scaling_combo.configure(state='readonly')

    def show_param_entries(self, frame):

        # param_name_entry
        self.param_name_label = \
            ttk.Label(frame,
                      text="Name:",
                      name="param_name_label")
        self.param_name_label.grid(row=0, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.param_name_label.configure(style='Body.TLabel')
        self.param_name_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=50,
                     name="param_name_entry")
        self.param_name_entry.grid(row=0, column=1, sticky="nsew",
                                       padx=1, pady=1)

        # param_type_entry
        self.param_type_label = \
            ttk.Label(frame,
                      text="Type:",
                      name="param_type_label")
        self.param_type_label.grid(row=1, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.param_type_label.configure(style='Body.TLabel')
        self.param_type_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=25,
                     name="param_type_entry")
        self.param_type_entry.grid(row=1, column=1, sticky="nsew",
                                   padx=1, pady=1)

        # defaults_to_entry
        self.defaults_to_label = \
            ttk.Label(frame,
                      text="Defaults to:",
                      name="defaults_to_label")
        self.defaults_to_label.grid(row=2, column=0, sticky="nsew",
                                    padx=1, pady=1)
        self.defaults_to_label.configure(style='Body.TLabel')
        self.defaults_to_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=25,
                     name="defaults_to_entry")
        self.defaults_to_entry.grid(row=2, column=1, sticky="nsew",
                                    padx=1, pady=1)

        # depends_on_entry
        self.depends_on_label = \
            ttk.Label(frame,
                      text="Depends on:",
                      name="depends_on_label")
        self.depends_on_label.grid(row=3, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.depends_on_label.configure(style='Body.TLabel')
        self.depends_on_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=25,
                     name="depends_on_entry")
        self.depends_on_entry.grid(row=3, column=1, sticky="nsew",
                                   padx=1, pady=1)

        # is_optional_combo
        self.is_optional_label = \
            ttk.Label(frame,
                      text="Optional:",
                      name="is_optional_label")
        self.is_optional_label.grid(row=4, column=0, sticky="nsew",
                                    padx=1, pady=1)
        self.is_optional_label.configure(style='Body.TLabel')
        self.is_optional_combo = \
            ttk.Combobox(frame,
                         textvariable=self.is_optional,
                         values=('Yes', 'No'),
                         width=25)
        self.is_optional_combo.grid(row=4, column=1, sticky="nsew",
                                    padx=1, pady=1)
        self.is_optional_combo.configure(state='readonly')

        # is_active_combo
        self.is_active_label = \
            ttk.Label(frame,
                      text="Active:",
                      name="is_active_label")
        self.is_active_label.grid(row=5, column=0, sticky="nsew",
                                  padx=1, pady=1)
        self.is_active_label.configure(style='Body.TLabel')
        self.is_active_combo = \
            ttk.Combobox(frame,
                         textvariable=self.is_active,
                         values=('Yes', 'No'),
                         width=25)
        self.is_active_combo.grid(row=5, column=1, sticky="nsew",
                                  padx=1, pady=1)
        self.is_active_combo.configure(state='readonly')

    def populate_entries(self, frame):

        for widget in frame.winfo_children():
            if "entry" in (str(widget).split(".")[-1]):
                widget.delete(0, tk.END)

        qry = 'SELECT * FROM Algorithms WHERE AlgorithmID=?'
        parameters = (self.algorithm_id,)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            if row[1] is not None:
                self.algorithm_name_entry.insert(0, row[1])
            if row[2] is not None:
                self.algorithm_internal_name_entry.insert(0, row[2])
            if row[3] is not None:
                self.algorithm_desc_entry.insert(0, row[3])
            if row[4] is not None:
                self.algorithm_notes_entry.insert(0, row[4])
            if row[5] is not None:
                self.algorithm_docs_entry.insert(0, row[5])
            if row[6] is not None:
                self.algorithm_guides_entry.insert(0, row[6])
            if row[7] is not None:
                self.algorithm_wiki_entry.insert(0, row[7])
            if row[9] == 1:
                self.needs_scaling.set('Yes')
            else:
                self.needs_scaling.set('No')

    def populate_param_entries(self, frame):

        for widget in frame.winfo_children():
            if "entry" in (str(widget).split(".")[-1]):
                widget.delete(0, tk.END)

        qry = 'SELECT * FROM AlgorithmParams WHERE AlgorithmParamID=?'
        parameters = (self.algorithm_param_id,)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            if row[2] is not None:
                self.param_name_entry.insert(0, row[2])
            if row[3] is not None:
                self.param_type_entry.insert(0, row[3])
            if row[4] is not None:
                self.defaults_to_entry.insert(0, row[4])
            if row[5] is not None:
                self.depends_on_entry.insert(0, row[5])
            if row[6] is not None:
                if row[6] == 1:
                    self.is_optional.set('Yes')
                else:
                    self.is_optional.set('No')
            if row[7] is not None:
                if row[7] == 1:
                    self.is_active.set('Yes')
                else:
                    self.is_active.set('No')

    def open_add_new_classifier_window(self):

        self.algorithm_id = 0
        self.needs_scaling.set('Yes')

        self.add_window = tk.Toplevel()
        self.add_window.title('Add Classifier')
        self.add_window.resizable(width=False, height=False)
        self.add_window.config(background="#ffffff")
        self.add_window. \
            geometry('%dx%d+%d+%d' % (600, 260,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.aw_classifier_frame = tk.Frame(self.add_window,
                                            background="#ffffff")
        self.aw_classifier_frame.pack(side='top', padx=10, pady=3, fill='both',
                                      expand=1)

        self.aw_button_frame = tk.Frame(self.add_window, background="#ffffff")
        self.aw_button_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.show_classifier_entries(self.aw_classifier_frame)

        self.aw_save_classifier_button = \
            ttk.Button(self.aw_button_frame,
                       text="Save",
                       name="aw_save_classifier_button",
                       command=lambda: self.
                       on_aw_save_classifier_button_clicked(self.aw_classifier_frame))
        self.aw_save_classifier_button.grid(row=0, column=0, sticky="nsew",
                                            padx=5, pady=1)

        self.add_window.focus_set()
        self.add_window.grab_set()

    def open_modify_classifier_window(self):

        self.algorithm_id = self. \
            get_algorithm_id(self.classifier_tree.
                             item(self.classifier_tree.selection())['text'])

        self.modify_window = tk.Toplevel()
        self.modify_window.title('Modify Classifier')
        self.modify_window.resizable(width=False, height=False)
        self.modify_window.config(background="#ffffff")

        self.modify_window. \
            geometry('%dx%d+%d+%d' % (600, 610,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.mw_classifier_frame = tk.Frame(self.modify_window,
                                            background="#ffffff")
        self.mw_classifier_frame.pack(side='top', padx=10, pady=3, fill='both',
                                      expand=1)

        self.mw_params_frame = tk.Frame(self.modify_window,
                                        background="#ffffff")
        self.mw_params_frame.pack(side='top', padx=10, pady=3, fill='both',
                                  expand=1)

        self.mw_button_frame = tk.Frame(self.modify_window,
                                        background="#ffffff")
        self.mw_button_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.show_classifier_entries(self.mw_classifier_frame)
        self.populate_entries(self.mw_classifier_frame)

        self.params_section_label = \
            ttk.Label(self.mw_params_frame,
                      text="Parameters")
        self.params_section_label.grid(row=0, column=0,
                                       columnspan=3,
                                       sticky="nsew",
                                       padx=1, pady=1)
        self.params_section_label. \
            configure(style='Sections.TLabel')

        self.params_tree = ttk.Treeview(self.mw_params_frame,
                                        height=15,
                                        columns=('Name','Type','Defaults To','Optional','Active'),
                                        selectmode = 'browse')
        self.params_tree.grid(row=1, column=0, rowspan=3)
        self.params_tree.column('#0', width=170)
        self.params_tree.column('#1', width=50)
        self.params_tree.column('#2', width=100)
        self.params_tree.column('#3', width=60)
        self.params_tree.column('#4', width=60)
        self.params_tree.column('#5', width=1)
        self.params_tree.heading('#0', text='Name', anchor=tk.W)
        self.params_tree.heading('#1', text='Type', anchor=tk.W)
        self.params_tree.heading('#2', text='Defaults To', anchor=tk.W)
        self.params_tree.heading('#3', text='Optional', anchor=tk.W)
        self.params_tree.heading('#4', text='Active', anchor=tk.W)
        self.params_tree.tag_configure('odd_row', background='white')
        self.params_tree.tag_configure('even_row', background='grey90')
        self.params_tree.bind("<Double-Button-1>",
                              self.params_tree_handle_double_click)
        self.params_tree_scrollbar = \
            ttk.Scrollbar(self.mw_params_frame, orient=tk.VERTICAL,
                          command=self.params_tree.yview)
        self.params_tree_scrollbar.grid(row=1, column=1, rowspan=3,
                                        sticky='ns')
        self.params_tree.configure(yscrollcommand=self.
                                   params_tree_scrollbar.set)

        self.view_params()

        self.right_buttons_frame = tk.Frame(self.mw_params_frame, background="#ffffff")
        self.right_buttons_frame.grid(row=1, column=2, sticky='nsew')

        ttk.Button(self.right_buttons_frame, text='Add Parameter',
                   command=self.on_add_new_param_button_clicked).grid(
                   row=0, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Delete Parameter',
                   command=self.on_delete_param_button_clicked).grid(
                   row=1, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Modify Parameter',
                   command=self.on_modify_param_button_clicked).grid(
                   row=2, column=2, sticky="nsew", padx=10, pady=1)

        self.mw_save_classifier_button = \
            ttk.Button(self.mw_button_frame,
                       text="Save",
                       name="mw_save_classifier_button",
                       command=lambda: self.
                       on_mw_save_classifier_button_clicked(self.mw_classifier_frame))
        self.mw_save_classifier_button.grid(row=1, column=0, sticky="nsew",
                                            padx=5, pady=1)

        self.modify_window.focus_set()
        self.modify_window.grab_set()

    def open_add_new_param_window(self):

        self.algorithm_param_id = 0

        self.is_optional.set('Yes')
        self.is_active.set('Yes')

        self.add_param_window = tk.Toplevel()
        self.add_param_window.title('Add Parameter')
        self.add_param_window.resizable(width=False, height=False)
        self.add_param_window.config(background="#ffffff")
        self.add_param_window. \
            geometry('%dx%d+%d+%d' % (400, 200,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.aw_param_frame = tk.Frame(self.add_param_window,
                                       background="#ffffff")
        self.aw_param_frame.pack(side='top', padx=10, pady=3, fill='both',
                                 expand=1)

        self.aw_param_button_frame = tk.Frame(self.add_param_window, background="#ffffff")
        self.aw_param_button_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.show_param_entries(self.aw_param_frame)
        self.param_name_entry.focus_set()

        self.aw_save_param_button = \
            ttk.Button(self.aw_param_button_frame,
                       text="Save",
                       name="aw_save_param_button",
                       command=lambda: self.
                       on_aw_save_param_button_clicked(self.aw_param_frame))
        self.aw_save_param_button.grid(row=0, column=0, sticky="nsew",
                                       padx=5, pady=1)

        self.add_param_window.focus_set()
        self.add_param_window.grab_set()

    def open_modify_param_window(self):

        self.algorithm_param_id = self. \
            get_algorithm_param_id(self.params_tree.
                                   item(self.params_tree.selection())['text'],
                                   self.algorithm_id)

        self.modify_param_window = tk.Toplevel()
        self.modify_param_window.title('Modify Parameter')
        self.modify_param_window.resizable(width=False, height=False)
        self.modify_param_window.config(background="#ffffff")

        self.modify_param_window. \
            geometry('%dx%d+%d+%d' % (400, 200,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.mw_param_frame = tk.Frame(self.modify_param_window,
                                       background="#ffffff")
        self.mw_param_frame.pack(side='top', padx=10, pady=3, fill='both',
                                 expand=1)

        self.mw_param_button_frame = tk.Frame(self.modify_param_window,
                                              background="#ffffff")
        self.mw_param_button_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.show_param_entries(self.mw_param_frame)
        self.populate_param_entries(self.mw_param_frame)

        self.mw_save_param_button = \
            ttk.Button(self.mw_param_button_frame,
                       text="Save",
                       name="mw_save_param_button",
                       command=lambda: self.
                       on_mw_save_param_button_clicked(self.mw_param_frame))
        self.mw_save_param_button.grid(row=0, column=0, sticky="nsew",
                                       padx=5, pady=1)

        self.modify_param_window.focus_set()
        self.modify_param_window.grab_set()

    def on_aw_save_classifier_button_clicked(self, frame):

        self.save_classifier(frame)

    def on_mw_save_classifier_button_clicked(self, frame):

        self.save_classifier(frame)

    def on_aw_save_param_button_clicked(self, frame):

        self.save_param(frame)

    def on_mw_save_param_button_clicked(self, frame):

        self.save_param(frame)

    def save_classifier(self, frame):

        if self.algorithm_id == 0:
            self.insert_classifier(frame)

        else:
            self.update_classifier(frame)

    def save_param(self, frame):

        if self.algorithm_param_id == 0:
            self.insert_param(frame)

        else:
            self.update_param(frame)

    def update_classifier(self, frame):

        if self.needs_scaling.get() == 'Yes':
            needs_scaling = 1
        else:
            needs_scaling = 0

        qry = "UPDATE Algorithms SET " \
            "AlgorithmName=?, AlgorithmInternalName=?, AlgorithmDesc=?, " \
            "AlgorithmNotes=?, " \
            "AlgorithmDocs=?, AlgorithmGuides=?, AlgorithmWiki=?, " \
            "AlgorithmTypeID=?, NeedsScaling=?, IsActive=? " \
            "WHERE AlgorithmID=?"
        parameters = (self.algorithm_name_entry.get(),
                      self.algorithm_internal_name_entry.get(),
                      self.algorithm_desc_entry.get(),
                      self.algorithm_notes_entry.get(),
                      self.algorithm_docs_entry.get(),
                      self.algorithm_guides_entry.get(),
                      self.algorithm_wiki_entry.get(),
                      1,
                      needs_scaling,
                      "Yes",
                      self.algorithm_id)
        exec_qry(qry, parameters)
        self.view_classifiers()
        self.exit_crud_window()

    def update_param(self, frame):

        if self.is_optional.get() == 'Yes':
            is_optional = 1
        else:
            is_optional = 0
        if self.is_active.get() == 'Yes':
            is_active = 1
        else:
            is_active = 0

        qry = "UPDATE AlgorithmParams SET " \
            "ParamName=?, ParamType=?, " \
            "DefaultsTo=?, DependsOn=?, IsOptional=?, " \
            "IsActive=? " \
            "WHERE AlgorithmParamID=?"
        parameters = (self.param_name_entry.get(),
                      self.param_type_entry.get(),
                      self.defaults_to_entry.get(),
                      self.depends_on_entry.get(),
                      is_optional,
                      is_active,
                      self.algorithm_param_id)
        exec_qry(qry, parameters)
        self.view_params()
        self.exit_param_crud_window()

        self.modify_window.focus_set()
        self.modify_window.grab_set()

    def insert_classifier(self, frame):

        if self.needs_scaling.get() == 'Yes':
            needs_scaling = 1
        else:
            needs_scaling = 0

        qry = "INSERT INTO Algorithms (" \
            "AlgorithmName, AlgorithmInternalName, AlgorithmDesc, " \
            "AlgorithmNotes=?, " \
            "AlgorithmDocs, AlgorithmGuides, AlgorithmWiki, " \
            "AlgorithmTypeID, NeedsScaling, IsActive) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        parameters = (self.algorithm_name_entry.get(),
                      self.algorithm_internal_name_entry.get(),
                      self.algorithm_desc_entry.get(),
                      self.algorithm_notes_entry.get(),
                      self.algorithm_docs_entry.get(),
                      self.algorithm_guides_entry.get(),
                      self.algorithm_wiki_entry.get(),
                      1,
                      needs_scaling,
                      "Yes")
        self.algorithm_id = exec_insert_qry(qry, parameters)
        self.view_classifiers()
        self.exit_crud_window()

    def insert_param(self, frame):

        if self.is_optional.get() == 'Yes':
            is_optional = 1
        else:
            is_optional = 0
        if self.is_active.get() == 'Yes':
            is_active = 1
        else:
            is_active = 0

        qry = "INSERT INTO AlgorithmParams (" \
            "AlgorithmID, ParamName, ParamType, " \
            "DefaultsTo, DependsOn, IsOptional, " \
            "IsActive) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        parameters = (self.algorithm_id,
                      self.param_name_entry.get(),
                      self.param_type_entry.get(),
                      self.defaults_to_entry.get(),
                      self.depends_on_entry.get(),
                      is_optional,
                      is_active)
        self.algorithm_param_id = exec_insert_qry(qry, parameters)
        self.view_params()
        self.exit_param_crud_window()

        self.modify_window.focus_set()
        self.modify_window.grab_set()

    def delete_classifier(self):

        if messagebox.askyesno("Warning", "Do you want to delete the " +
                               "selected classifier?"):

            algorithm_id = self. \
                get_algorithm_id(self.classifier_tree.
                                 item(self.classifier_tree.selection())['text'])
            qry = 'DELETE FROM Algorithms WHERE AlgorithmID=?'
            parameters = (algorithm_id,)
            exec_qry(qry, parameters)

            qry = 'DELETE FROM AlgorithmParams WHERE AlgorithmID=?'
            parameters = (algorithm_id,)
            exec_qry(qry, parameters)

            self.view_classifiers()

    def delete_param(self):

        if messagebox.askyesno("Warning", "Do you want to delete the " +
                               "selected parameter?"):

            algorithm_param_id = self. \
                get_algorithm_param_id(self.params_tree.
                                       item(self.params_tree.selection())['text'],
                                       self.algorithm_id)
            qry = 'DELETE FROM AlgorithmParams WHERE AlgorithmParamID=?'
            parameters = (algorithm_param_id,)
            exec_qry(qry, parameters)
            self.view_params()

        self.modify_window.focus_set()
        self.modify_window.grab_set()

    def classifier_tree_handle_double_click(self, event):

        self.on_modify_classifier_button_clicked()
        return

    def params_tree_handle_double_click(self, event):

        self.on_modify_param_button_clicked()
        return

    def get_algorithm_id(self, algorithm_desc_str):

        where_column1 = 'AlgorithmDesc'

        qry = "SELECT AlgorithmID FROM Algorithms WHERE {cond}=?".\
            format(cond=where_column1)
        parameters = (algorithm_desc_str,)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

    def get_algorithm_param_id(self, param_name, algorithm_id):

        qry = "SELECT AlgorithmParamID FROM AlgorithmParams WHERE ParamName=? AND AlgorithmID=?"
        parameters = (param_name, algorithm_id)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

    def exit_crud_window(self):

        if hasattr(self, 'add_window'):
            self.add_window.destroy()
        if hasattr(self, 'modify_window'):
            self.modify_window.destroy()

    def exit_param_crud_window(self):

        if hasattr(self, 'add_param_window'):
            self.add_param_window.destroy()
        if hasattr(self, 'modify_param_window'):
            self.modify_param_window.destroy()

    def exit_window(self):

        self.destroy()


class ClassifiersModelDefaults(tk.Toplevel):

    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Classifiers Defaults')
        self.parent = parent

        self.config(background="#ffffff")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (800, 328,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.is_optional = tk.StringVar()
        self.is_selected = tk.StringVar()

        self.setup_styles()
        self.create_gui()
        self.focus_set()
        self.grab_set()

    def setup_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Body.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')

    def create_gui(self):
        self.create_tree_view()
        self.create_right_buttons()
        self.init_classifiers()

    def create_tree_view(self):

        self.classifier_tree = ttk.Treeview(self,
                                        height=15,
                                        columns=('Classifier','Scaling','Selected'),
                                        selectmode = 'browse')
        self.classifier_tree.grid(row=0, column=0, rowspan=3)
        self.classifier_tree.column('#0', width=540)
        self.classifier_tree.column('#1', width=50)
        self.classifier_tree.column('#2', width=70)
        self.classifier_tree.column('#3', width=0)
        self.classifier_tree.heading('#0', text='Classifier', anchor=tk.W)
        self.classifier_tree.heading('#1', text='Scaling', anchor=tk.W)
        self.classifier_tree.heading('#2', text='Selected', anchor=tk.W)
        self.classifier_tree.tag_configure('odd_row', background='white')
        self.classifier_tree.tag_configure('even_row', background='grey90')

        self.classifier_tree.bind("<Double-Button-1>",
                                  self.classifier_tree_handle_double_click)

        self.classifier_tree_scrollbar = \
            ttk.Scrollbar(self, orient=tk.VERTICAL,
                          command=self.classifier_tree.yview)
        self.classifier_tree_scrollbar.grid(row=0, column=1, rowspan=3,
                                            sticky='ns')
        self.classifier_tree.configure(yscrollcommand=self.
                                       classifier_tree_scrollbar.set)

    def create_right_buttons(self):
        self.right_buttons_frame = tk.Frame(self, background="#ffffff")
        self.right_buttons_frame.grid(row=0, column=2, sticky='nsew')

        ttk.Button(self.right_buttons_frame, text='Edit Parameters',
                   command=self.on_edit_params_button_clicked).grid(
                   row=2, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Toggle Scaling',
                   command=self.on_toggle_scaling_button_clicked).grid(
                   row=3, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Toggle Selected',
                   command=self.on_toggle_selected_button_clicked).grid(
                   row=4, column=2, sticky="nsew", padx=10, pady=1)

    def on_edit_params_button_clicked(self):

        try:
            self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No classifier was selected.")
            return
        self.open_edit_params_window()

    def on_toggle_scaling_button_clicked(self):

        try:
            self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
            ndx = self.classifier_tree.index(self.classifier_tree.selection()[0])
        except IndexError as e:
            messagebox.showwarning("Warning", "No classifier was selected.")
            return

        algorithm_id = self. \
            get_algorithm_id(self.classifier_tree.
                             item(self.classifier_tree.selection())['text'])

        if self.is_scaling_selected() is True:
            qry = 'UPDATE ModelDefaultAlgorithms SET NeedsScaling=? WHERE AlgorithmID=?'
            parameters = (0, algorithm_id)
            exec_qry(qry, parameters)
        else:
            qry = 'UPDATE ModelDefaultAlgorithms SET NeedsScaling=? WHERE AlgorithmID=?'
            parameters = (1, algorithm_id)
            exec_qry(qry, parameters)

        self.view_classifiers()
        items = self.classifier_tree.get_children()
        for i, item in enumerate(items):
            if i == ndx:
                self.classifier_tree.selection_set(item)

    def on_toggle_selected_button_clicked(self):

        try:
            self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
            ndx = self.classifier_tree.index(self.classifier_tree.selection()[0])
        except IndexError as e:
            messagebox.showwarning("Warning", "No classifier was selected.")
            return

        algorithm_id = self. \
            get_algorithm_id(self.classifier_tree.
                             item(self.classifier_tree.selection())['text'])

        if self.is_classifier_selected() is True:
            qry = 'UPDATE ModelDefaultAlgorithms SET IsSelected=? WHERE AlgorithmID=?'
            parameters = ("No", algorithm_id)
            exec_qry(qry, parameters)
        else:
            qry = 'UPDATE ModelDefaultAlgorithms SET IsSelected=? WHERE AlgorithmID=?'
            parameters = ("Yes", algorithm_id)
            exec_qry(qry, parameters)

        self.view_classifiers()
        items = self.classifier_tree.get_children()
        for i, item in enumerate(items):
            if i == ndx:
                self.classifier_tree.selection_set(item)

    def on_modify_param_button_clicked(self):

        try:
            self.params_tree.item(self.params_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No parameter was selected.")
            return
        self.open_modify_param_window()

    def is_scaling_selected(self):

        if (self.classifier_tree.item(self.classifier_tree.selection())['values'][0]
                == "Yes"):
            return True
        else:
            return False

    def is_classifier_selected(self):

        if (self.classifier_tree.item(self.classifier_tree.selection())['values'][1]
                == "Yes"):
            return True
        else:
            return False

    def init_classifiers(self):

        # get previous selections
        qry_sel = 'SELECT * FROM ModelDefaultAlgorithms WHERE AlgorithmTypeID=1 ORDER BY AlgorithmID'
        model_default_algorithms = exec_qry(qry_sel)
        model_default_algorithms_dict = {}
        for row in model_default_algorithms:
            model_default_algorithms_dict[row[0]] = row[4]

        qry_del = 'DELETE FROM ModelDefaultAlgorithms WHERE AlgorithmTypeID=1'
        exec_qry(qry_del)

        # update with active algorithms
        qry_upd = 'SELECT * FROM Algorithms WHERE AlgorithmTypeID=1 AND IsActive=? ORDER BY AlgorithmDesc'
        parameters = ('Yes',)
        algorithms = exec_qry(qry_upd, parameters)
        lst = []
        for row in algorithms:
            lst.append(list([row[0], row[3], row[9]]))

        for row in lst:
            # check previous selection
            if row[0] in model_default_algorithms_dict:
                is_selected = model_default_algorithms_dict[row[0]]
            else:
                is_selected = 'No'
            qry_ins = "INSERT INTO ModelDefaultAlgorithms (" \
                "AlgorithmID, AlgorithmDesc, " \
                "AlgorithmTypeID, NeedsScaling, IsSelected) " \
                "VALUES (?, ?, ?, ?, ?)"
            parameters = (row[0], row[1], 1, row[2], is_selected)
            exec_insert_qry(qry_ins, parameters)

        self.view_classifiers()

    def init_params(self):

        # get previous selections
        qry_sel = 'SELECT * FROM ModelDefaultAlgorithmParams WHERE AlgorithmID=?'
        param_sel = (self.algorithm_id,)
        model_default_algorithm_params = exec_qry(qry_sel, param_sel)
        model_default_algorithm_params_is_selected_dict = {}
        model_default_algorithm_params_defaults_to_dict = {}
        for row in model_default_algorithm_params:
            model_default_algorithm_params_is_selected_dict[row[0]] = row[7]
            model_default_algorithm_params_defaults_to_dict[row[0]] = row[4]

        qry_del = 'DELETE FROM ModelDefaultAlgorithmParams WHERE AlgorithmID=?'
        param_del = (self.algorithm_id,)
        exec_qry(qry_del, param_del)

        # update with active algorithm parameters
        qry_upd = 'SELECT * FROM AlgorithmParams WHERE AlgorithmID=? AND IsActive=? ORDER BY ParamName'
        parameters = (self.algorithm_id, 1)
        algorithms = exec_qry(qry_upd, parameters)
        lst = []
        for row in algorithms:
            lst.append(list([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]]))

        for row in lst:
            # check previous selection
            if row[0] in model_default_algorithm_params_is_selected_dict:
                is_selected = model_default_algorithm_params_is_selected_dict[row[0]]
            else:
                is_selected = 0
            if row[0] in model_default_algorithm_params_defaults_to_dict:
                defaults_to = model_default_algorithm_params_defaults_to_dict[row[0]]
            else:
                defaults_to = row[4]
            qry_ins = "INSERT INTO ModelDefaultAlgorithmParams (" \
                "AlgorithmParamID, AlgorithmID, ParamName, " \
                "ParamType, DefaultsTo, DependsOn, " \
                "IsOptional, IsSelected) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            parameters = (row[0], row[1], row[2], row[3],
                          defaults_to, row[5], row[6], is_selected)
            exec_insert_qry(qry_ins, parameters)

        self.view_params()

    def view_classifiers(self):
        items = self.classifier_tree.get_children()
        for item in items:
            self.classifier_tree.delete(item)

        qry = 'SELECT * FROM ModelDefaultAlgorithms WHERE AlgorithmTypeID=1 ORDER BY AlgorithmDesc'
        model_default_algorithms = exec_qry(qry)

        for i, row in enumerate(model_default_algorithms):
            if row[3] == 1:
                needs_scaling = "Yes"
            else:
                needs_scaling = "No"
            if is_even(i):
                self.classifier_tree.insert('', 0, text=row[1],
                                                values=(needs_scaling, row[4]),
                                                tags=('even_row',))
            else:
                self.classifier_tree.insert('', 0, text=row[1],
                                                values=(needs_scaling, row[4]),
                                                tags=('odd_row',))

    def view_params(self):

        for item in self.params_tree.get_children():
            self.params_tree.delete(item)

        qry = 'SELECT * FROM ModelDefaultAlgorithmParams WHERE AlgorithmID=? ORDER BY ParamName DESC'
        parameters = (self.algorithm_id,)
        cursor = exec_qry(qry, parameters)

        for i, row in enumerate(cursor):
            if row[6] == 1:
                is_optional = 'Yes'
            else:
                is_optional = 'No'
            if row[7] == 1:
                is_selected = 'Yes'
            else:
                is_selected = 'No'
            if is_even(i):
                self.params_tree.insert('', 0, text=row[2],
                                                     values=(row[3],
                                                     row[4], is_optional,
                                                     is_selected),
                                                     tags=('even_row',))
            else:
                self.params_tree.insert('', 0, text=row[2],
                                                     values=(row[3],
                                                     row[4], is_optional,
                                                     is_selected),
                                                     tags=('odd_row',))

    def show_classifier_entries(self, frame):

        self.general_information_section_label = \
            ttk.Label(frame,
                      text="General Information")
        self.general_information_section_label.grid(row=0, column=0,
                                                    columnspan=2,
                                                    sticky="nsew",
                                                    padx=1, pady=1)
        self.general_information_section_label. \
            configure(style='Sections.TLabel')

        # algorithm_name_entry
        self.algorithm_name_label = \
            ttk.Label(frame,
                      text="Name:",
                      name="algorithm_name_label")
        self.algorithm_name_label.grid(row=1, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_name_label.configure(style='Body.TLabel')
        self.algorithm_name_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_name_entry")
        self.algorithm_name_entry.grid(row=1, column=1, sticky="nsew",
                                       padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_name_entry)
        self.algorithm_name_entry.configure(state='readonly')

        # algorithm_internal_name_entry
        self.algorithm_internal_name_label = \
            ttk.Label(frame,
                      text="Internal name:",
                      name="algorithm_internal_name_label")
        self.algorithm_internal_name_label.grid(row=2, column=0, sticky="nsew",
                                                padx=1, pady=1)
        self.algorithm_internal_name_label.configure(style='Body.TLabel')
        self.algorithm_internal_name_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_internal_name_entry")
        self.algorithm_internal_name_entry.grid(row=2, column=1, sticky="nsew",
                                                padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_internal_name_entry)
        self.algorithm_internal_name_entry.configure(state='readonly')

        # algorithm_desc_entry
        self.algorithm_desc_label = \
            ttk.Label(frame,
                      text="Description:",
                      name="algorithm_desc_label")
        self.algorithm_desc_label.grid(row=3, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_desc_label.configure(style='Body.TLabel')
        self.algorithm_desc_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_desc_entry")
        self.algorithm_desc_entry.grid(row=3, column=1, sticky="nsew",
                                       padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_desc_entry)
        self.algorithm_desc_entry.configure(state='readonly')

        # algorithm_notes_entry
        self.algorithm_notes_label = \
            ttk.Label(frame,
                      text="Notes:",
                      name="algorithm_notes_label")
        self.algorithm_notes_label.grid(row=4, column=0, sticky="nsew",
                                        padx=1, pady=1)
        self.algorithm_notes_label.configure(style='Body.TLabel')
        self.algorithm_notes_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_notes_entry")
        self.algorithm_notes_entry.grid(row=4, column=1, sticky="nsew",
                                        padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_notes_entry)
        self.algorithm_notes_entry.configure(state='readonly')

        # algorithm_docs_entry
        self.algorithm_docs_label = \
            ttk.Label(frame,
                      text="Documentation:",
                      name="algorithm_docs_label")
        self.algorithm_docs_label.grid(row=5, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_docs_label.configure(style='Body.TLabel')
        self.algorithm_docs_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_docs_entry")
        self.algorithm_docs_entry.grid(row=5, column=1, sticky="nsew",
                                       padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_docs_entry)
        self.algorithm_docs_entry.configure(state='readonly')

        # algorithm_guides_entry
        self.algorithm_guides_label = \
            ttk.Label(frame,
                      text="Guides:",
                      name="algorithm_guides_label")
        self.algorithm_guides_label.grid(row=6, column=0, sticky="nsew",
                                         padx=1, pady=1)
        self.algorithm_guides_label.configure(style='Body.TLabel')
        self.algorithm_guides_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=65,
                     name="algorithm_guides_entry")
        self.algorithm_guides_entry.grid(row=6, column=1, sticky="nsew",
                                         padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_guides_entry)
        self.algorithm_guides_entry.configure(state='readonly')

        # algorithm_wiki_entry
        self.algorithm_wiki_label = \
            ttk.Label(frame,
                      text="Wiki:",
                      name="algorithm_wiki_label")
        self.algorithm_wiki_label.grid(row=7, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.algorithm_wiki_label.configure(style='Body.TLabel')
        self.algorithm_wiki_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=80,
                     name="algorithm_wiki_entry")
        self.algorithm_wiki_entry.grid(row=7, column=1, sticky="nsew",
                                       padx=1, pady=1)
        # self.add_tooltip_to_widget(self.algorithm_wiki_entry)
        self.algorithm_wiki_entry.configure(state='readonly')

    def show_param_entries(self, frame):

        # param_name_entry
        self.param_name_label = \
            ttk.Label(frame,
                      text="Name:",
                      name="param_name_label")
        self.param_name_label.grid(row=0, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.param_name_label.configure(style='Body.TLabel')
        self.param_name_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=50,
                     name="param_name_entry")
        self.param_name_entry.grid(row=0, column=1, sticky="nsew",
                                       padx=1, pady=1)
        # self.add_tooltip_to_widget(self.param_name_entry)
        self.param_name_entry.configure(state='readonly')

        # param_type_entry
        self.param_type_label = \
            ttk.Label(frame,
                      text="Type:",
                      name="param_type_label")
        self.param_type_label.grid(row=1, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.param_type_label.configure(style='Body.TLabel')
        self.param_type_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=25,
                     name="param_type_entry")
        self.param_type_entry.grid(row=1, column=1, sticky="nsew",
                                   padx=1, pady=1)
        # self.add_tooltip_to_widget(self.param_type_entry)
        self.param_type_entry.configure(state='readonly')

        # defaults_to_entry
        self.defaults_to_label = \
            ttk.Label(frame,
                      text="Defaults to:",
                      name="defaults_to_label")
        self.defaults_to_label.grid(row=2, column=0, sticky="nsew",
                                    padx=1, pady=1)
        self.defaults_to_label.configure(style='Body.TLabel')
        self.defaults_to_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=25,
                     name="defaults_to_entry")
        self.defaults_to_entry.grid(row=2, column=1, sticky="nsew",
                                    padx=1, pady=1)

        # depends_on_entry
        self.depends_on_label = \
            ttk.Label(frame,
                      text="Depends on:",
                      name="depends_on_label")
        self.depends_on_label.grid(row=3, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.depends_on_label.configure(style='Body.TLabel')
        self.depends_on_entry = \
            tk.Entry(frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=25,
                     name="depends_on_entry")
        self.depends_on_entry.grid(row=3, column=1, sticky="nsew",
                                   padx=1, pady=1)
        # self.add_tooltip_to_widget(self.depends_on_entry)
        self.depends_on_entry.configure(state='readonly')

        # is_optional_combo
        self.is_optional_label = \
            ttk.Label(frame,
                      text="Optional:",
                      name="is_optional_label")
        self.is_optional_label.grid(row=4, column=0, sticky="nsew",
                                    padx=1, pady=1)
        self.is_optional_label.configure(style='Body.TLabel')
        self.is_optional_combo = \
            ttk.Combobox(frame,
                         textvariable=self.is_optional,
                         values=('Yes', 'No'),
                         width=25)
        self.is_optional_combo.grid(row=4, column=1, sticky="nsew",
                                    padx=1, pady=1)
        self.is_optional_combo.configure(state='disabled')

        # is_selected_combo
        self.is_selected_label = \
            ttk.Label(frame,
                      text="Selected:",
                      name="is_selected_label")
        self.is_selected_label.grid(row=5, column=0, sticky="nsew",
                                    padx=1, pady=1)
        self.is_selected_label.configure(style='Body.TLabel')
        self.is_selected_combo = \
            ttk.Combobox(frame,
                         textvariable=self.is_selected,
                         values=('Yes', 'No'),
                         width=25)
        self.is_selected_combo.grid(row=5, column=1, sticky="nsew",
                                    padx=1, pady=1)
        self.is_selected_combo.configure(state='readonly')

    def populate_entries(self, frame):

        qry = 'SELECT * FROM Algorithms WHERE AlgorithmID=?'
        parameters = (self.algorithm_id,)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            if row[1] is not None:
                self.update_disabled_widget(self.algorithm_name_entry, row[1])
            if row[2] is not None:
                self.update_disabled_widget(self.algorithm_internal_name_entry, row[2])
            if row[3] is not None:
                self.update_disabled_widget(self.algorithm_desc_entry, row[3])
            if row[4] is not None:
                self.update_disabled_widget(self.algorithm_notes_entry, row[4])
            if row[5] is not None:
                self.update_disabled_widget(self.algorithm_docs_entry, row[5])
            if row[6] is not None:
                self.update_disabled_widget(self.algorithm_guides_entry, row[6])
            if row[7] is not None:
                self.update_disabled_widget(self.algorithm_wiki_entry, row[7])

    def populate_param_entries(self, frame):

        qry = 'SELECT * FROM ModelDefaultAlgorithmParams WHERE AlgorithmParamID=?'
        parameters = (self.algorithm_param_id,)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            if row[2] is not None:
                self.update_disabled_widget(self.param_name_entry, row[2])
            if row[3] is not None:
                self.update_disabled_widget(self.param_type_entry, row[3])
            if row[4] is not None:
                self.defaults_to_entry.insert(0, row[4])
            if row[5] is not None:
                self.update_disabled_widget(self.depends_on_entry, row[5])
            if row[6] is not None:
                if row[6] == 1:
                    self.is_optional.set('Yes')
                else:
                    self.is_optional.set('No')
            if row[7] is not None:
                if row[7] == 1:
                    self.is_selected.set('Yes')
                else:
                    self.is_selected.set('No')

    def open_edit_params_window(self):

        self.algorithm_id = self. \
            get_algorithm_id(self.classifier_tree.
                             item(self.classifier_tree.selection())['text'])

        self.edit_params_window = tk.Toplevel()
        self.edit_params_window.title('Edit Parameter Defaults')
        self.edit_params_window.resizable(width=False, height=False)
        self.edit_params_window.config(background="#ffffff")

        self.edit_params_window. \
            geometry('%dx%d+%d+%d' % (600, 590,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.classifier_frame = tk.Frame(self.edit_params_window,
                                         background="#ffffff")
        self.classifier_frame.pack(side='top', padx=10, pady=3, fill='both',
                                   expand=1)

        self.params_frame = tk.Frame(self.edit_params_window,
                                     background="#ffffff")
        self.params_frame.pack(side='top', padx=10, pady=3, fill='both',
                               expand=1)

        self.button_frame = tk.Frame(self.edit_params_window,
                                     background="#ffffff")
        self.button_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.show_classifier_entries(self.classifier_frame)
        self.populate_entries(self.classifier_frame)

        self.params_section_label = \
            ttk.Label(self.params_frame,
                      text="Parameters")
        self.params_section_label.grid(row=0, column=0,
                                       columnspan=3,
                                       sticky="nsew",
                                       padx=1, pady=1)
        self.params_section_label. \
            configure(style='Sections.TLabel')

        self.params_tree = ttk.Treeview(self.params_frame,
                                        height=15,
                                        columns=('Name','Type','Defaults To','Optional','Selected'),
                                        selectmode = 'browse')
        self.params_tree.grid(row=1, column=0, rowspan=3)
        self.params_tree.column('#0', width=170)
        self.params_tree.column('#1', width=50)
        self.params_tree.column('#2', width=100)
        self.params_tree.column('#3', width=60)
        self.params_tree.column('#4', width=70)
        self.params_tree.column('#5', width=1)
        self.params_tree.heading('#0', text='Name', anchor=tk.W)
        self.params_tree.heading('#1', text='Type', anchor=tk.W)
        self.params_tree.heading('#2', text='Defaults To', anchor=tk.W)
        self.params_tree.heading('#3', text='Optional', anchor=tk.W)
        self.params_tree.heading('#4', text='Selected', anchor=tk.W)
        self.params_tree.tag_configure('odd_row', background='white')
        self.params_tree.tag_configure('even_row', background='grey90')
        self.params_tree.bind("<Double-Button-1>",
                              self.params_tree_handle_double_click)
        self.params_tree_scrollbar = \
            ttk.Scrollbar(self.params_frame, orient=tk.VERTICAL,
                          command=self.params_tree.yview)
        self.params_tree_scrollbar.grid(row=1, column=1, rowspan=3,
                                        sticky='ns')
        self.params_tree.configure(yscrollcommand=self.
                                   params_tree_scrollbar.set)

        self.init_params()

        self.right_buttons_frame = tk.Frame(self.params_frame, background="#ffffff")
        self.right_buttons_frame.grid(row=1, column=2, sticky='nsew')

        ttk.Button(self.right_buttons_frame, text='Change Defaults',
                   command=self.on_modify_param_button_clicked).grid(
                   row=0, column=2, sticky="nsew", padx=10, pady=1)

        self.close_classifier_button = \
            ttk.Button(self.button_frame,
                       text="Close",
                       name="close_classifier_button",
                       command=self.on_close_classifier_button_clicked)
        self.close_classifier_button.grid(row=1, column=0, sticky="nsew",
                                          padx=5, pady=1)

        self.edit_params_window.focus_set()
        self.edit_params_window.grab_set()

    def open_modify_param_window(self):

        self.algorithm_param_id = self. \
            get_algorithm_param_id(self.params_tree.
                                   item(self.params_tree.selection())['text'],
                                   self.algorithm_id)

        self.modify_param_window = tk.Toplevel()
        self.modify_param_window.title('Edit Parameter Defaults')
        self.modify_param_window.resizable(width=False, height=False)
        self.modify_param_window.config(background="#ffffff")

        self.modify_param_window. \
            geometry('%dx%d+%d+%d' % (400, 200,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.mw_param_frame = tk.Frame(self.modify_param_window,
                                       background="#ffffff")
        self.mw_param_frame.pack(side='top', padx=10, pady=3, fill='both',
                                 expand=1)

        self.mw_param_button_frame = tk.Frame(self.modify_param_window,
                                              background="#ffffff")
        self.mw_param_button_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.show_param_entries(self.mw_param_frame)
        self.populate_param_entries(self.mw_param_frame)

        self.mw_save_param_button = \
            ttk.Button(self.mw_param_button_frame,
                       text="Save",
                       name="mw_save_param_button",
                       command=lambda: self.
                       on_mw_save_param_button_clicked(self.mw_param_frame))
        self.mw_save_param_button.grid(row=0, column=0, sticky="nsew",
                                       padx=5, pady=1)

        self.modify_param_window.focus_set()
        self.modify_param_window.grab_set()

    def on_close_classifier_button_clicked(self):

        self.exit_default_window()

    def on_mw_save_param_button_clicked(self, frame):

        self.save_param(frame)

    def save_param(self, frame):

        if self.algorithm_param_id == 0:
            pass

        else:
            self.update_param(frame)

    def update_param(self, frame):

        if self.is_selected.get() == 'Yes':
            is_selected = 1
        else:
            is_selected = 0

        qry = "UPDATE ModelDefaultAlgorithmParams SET " \
            "DefaultsTo=?, " \
            "IsSelected=? " \
            "WHERE AlgorithmParamID=?"
        parameters = (self.defaults_to_entry.get(),
                      is_selected,
                      self.algorithm_param_id)
        exec_qry(qry, parameters)
        self.view_params()
        self.exit_param_default_window()

    def classifier_tree_handle_double_click(self, event):

        self.on_edit_params_button_clicked()
        return

    def params_tree_handle_double_click(self, event):

        self.on_modify_param_button_clicked()
        return

    def update_disabled_widget(self, widget, string):

        if isinstance(widget, tk.Entry):
            widget.configure(state='normal')
            widget.delete(0, tk.END)
            widget.insert(0, string)
            widget.configure(state='readonly')

    def get_algorithm_id(self, algorithm_desc_str):

        where_column1 = 'AlgorithmDesc'

        qry = "SELECT AlgorithmID FROM ModelDefaultAlgorithms WHERE {cond}=?".\
            format(cond=where_column1)
        parameters = (algorithm_desc_str,)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

    def get_algorithm_param_id(self, param_name, algorithm_id):

        qry = "SELECT AlgorithmParamID FROM ModelDefaultAlgorithmParams WHERE ParamName=? AND AlgorithmID=?"
        parameters = (param_name, algorithm_id)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

    def exit_default_window(self):

        if hasattr(self, 'edit_params_window'):
            self.edit_params_window.destroy()

    def exit_param_default_window(self):

        if hasattr(self, 'modify_param_window'):
            self.modify_param_window.destroy()

    def exit_window(self):

        self.destroy()


class TrainAndTestSplitDefaults(tk.Toplevel):

    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Train and Test Split Defaults')
        self.parent = parent

        self.config(background="#ffffff")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (280, 180,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.random_state_var = tk.IntVar()

        self.setup_styles()
        self.create_gui()
        self.focus_set()
        self.grab_set()

    def setup_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Body.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')
        self.app_style.configure('Body.TRadiobutton', background='white')

    def create_gui(self):
        self.create_options_area()
        self.create_buttons_area()
        self.populate_entries()
        self.enable_disable_entries()

    def create_options_area(self):

        self.options_frame = tk.Frame(self, background="#ffffff")
        self.options_frame.pack(side='top', padx=10, pady=3, fill='both',
                                expand=1)

        self.train_and_test_size_section_label = \
            ttk.Label(self.options_frame,
                      text="Train and Test Size")
        self.train_and_test_size_section_label.grid(row=0, column=0,
                                                    columnspan=2,
                                                    sticky="nsew",
                                                    padx=1, pady=1)
        self.train_and_test_size_section_label. \
            configure(style='Sections.TLabel')

        # train_size_entry
        self.train_size_label = \
            ttk.Label(self.options_frame,
                      text="Train size:",
                      width=20,
                      name="train_size_label")
        self.train_size_label.grid(row=1, column=0, sticky="nsew",
                                   padx=1, pady=1)
        self.train_size_label.configure(style='Body.TLabel')
        self.train_size_entry = \
            tk.Entry(self.options_frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="train_size_entry")
        self.train_size_entry.grid(row=1, column=1, sticky="nsew",
                                   padx=1, pady=1)

        # test_size_entry
        self.test_size_label = \
            ttk.Label(self.options_frame,
                      text="Test size:",
                      width=20,
                      name="test_size_label")
        self.test_size_label.grid(row=2, column=0, sticky="nsew",
                                  padx=1, pady=1)
        self.test_size_label.configure(style='Body.TLabel')
        self.test_size_entry = \
            tk.Entry(self.options_frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="test_size_entry")
        self.test_size_entry.grid(row=2, column=1, sticky="nsew",
                                  padx=1, pady=1)

        self.random_state_section_label = \
            ttk.Label(self.options_frame,
                      text="Use Random State")
        self.random_state_section_label.grid(row=3, column=0,
                                             columnspan=2,
                                             sticky="nsew",
                                             padx=1, pady=1)
        self.random_state_section_label. \
            configure(style='Sections.TLabel')

        self.random_state_true_radiobutton = \
            ttk.Radiobutton(self.options_frame,
                            variable=self.random_state_var,
                            value=1,
                            text="Yes",
                            command=self.on_random_state_toggle_clicked)
        self.random_state_true_radiobutton.grid(row=4, column=0, sticky="nsew",
                                                padx=1, pady=1)
        self.random_state_true_radiobutton.configure(style='Body.TRadiobutton')

        self.random_state_false_radiobutton = \
            ttk.Radiobutton(self.options_frame,
                            variable=self.random_state_var,
                            value=0,
                            text="No",
                            command=self.on_random_state_toggle_clicked)
        self.random_state_false_radiobutton.grid(row=4, column=1, sticky="nsew",
                                                 padx=1, pady=1)
        self.random_state_false_radiobutton.configure(style='Body.TRadiobutton')

        # random_state_entry
        self.random_state_label = \
            ttk.Label(self.options_frame,
                      text="Random state:",
                      width=20,
                      name="random_state_label")
        self.random_state_label.grid(row=5, column=0, sticky="nsew",
                                     padx=1, pady=1)
        self.random_state_label.configure(style='Body.TLabel')
        self.random_state_entry = \
            tk.Entry(self.options_frame,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="random_state_entry")
        self.random_state_entry.grid(row=5, column=1, sticky="nsew",
                                     padx=1, pady=1)
        # self.add_tooltip_to_widget(self.random_state_entry)
        # self.random_state_entry.configure(state='readonly')

    def create_buttons_area(self):

        self.buttons_frame = tk.Frame(self, background="#ffffff")
        self.buttons_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.save_button = \
            ttk.Button(self.buttons_frame,
                       text="Save",
                       name="save_button",
                       command=self.on_save_button_clicked)
        self.save_button.grid(row=1, column=0, sticky="nsew",
                              padx=5, pady=1)

    def populate_entries(self):

        qry = 'SELECT * FROM ModelDefaults WHERE ModelDefaultName=?'
        parameters = ('train_and_test_split',)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            self.random_state_var.set(row[4])
            self.random_state_entry.insert(0, row[5])
            self.train_size_entry.insert(0, row[6])
            self.test_size_entry.insert(0, row[7])

    def enable_disable_entries(self):

        self.on_random_state_toggle_clicked()

    def on_random_state_toggle_clicked(self):

        if self.random_state_var.get() == 1:
            self.random_state_entry.configure(state='normal')
            self.random_state_entry.configure(readonlybackground='white')

        elif self.random_state_var.get() == 0:
            self.random_state_entry.configure(readonlybackground='grey95')
            self.random_state_entry.configure(state='readonly')

    def on_save_button_clicked(self):

        if self.validate_all() is True:
            self.save_default()

    def save_default(self):

        qry = "UPDATE ModelDefaults SET " \
            "ModelDefaultInt1=?, ModelDefaultInt2=?, ModelDefaultFloat1=?, " \
            "ModelDefaultFloat2=? " \
            "WHERE ModelDefaultName=?"
        parameters = (self.random_state_var.get(),
                      self.random_state_entry.get(),
                      self.train_size_entry.get(),
                      self.test_size_entry.get(),
                      'train_and_test_split')
        exec_qry(qry, parameters)
        self.exit_window()

    def validate_all(self):

        if (self.validate_train_and_test_sizes() is True and
                self.validate_data_in_random_state() is True):
            return True
        return False

    def validate_train_and_test_sizes(self):

        for c in self.train_size_entry.get():
            if c.isdigit() is False:
                if c != '.':
                    messagebox.showwarning("Warning", "Train sizes "
                                           "must be numeric or decimal.")
                    return False
        for c in self.test_size_entry.get():
            if c.isdigit() is False:
                if c != '.':
                    messagebox.showwarning("Warning", "Test sizes "
                                           "must be numeric or decimal.")
                    return False

        if self.train_size_entry.get() == '.':
            messagebox.showwarning("Warning", "Train sizes "
                                   "must be numeric or decimal.")
            return False
        if self.test_size_entry.get() == '.':
            messagebox.showwarning("Warning", "Test sizes "
                                   "must be numeric or decimal.")
            return False

        if (float(self.train_size_entry.get()) +
                float(self.test_size_entry.get())) != 1:
            messagebox.showwarning("Warning", "Train and Test sizes must "
                                   "add up to one (1). Please adjust your "
                                   "values and try again.")
            return False

        return True

    def validate_data_in_random_state(self):

        for c in self.random_state_entry.get():
            if c.isdigit() is False:
                messagebox.showwarning("Warning", "Random state "
                                       "must be integer.")
                return False
        return True

    def exit_window(self):

        self.destroy()


class ScalingDefaults(tk.Toplevel):

    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Scaling Defaults')
        self.parent = parent

        self.config(background="#ffffff")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (280, 180,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.scaling_var = tk.IntVar()

        self.setup_styles()
        self.create_gui()
        self.focus_set()
        self.grab_set()

    def setup_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Body.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')
        self.app_style.configure('Body.TRadiobutton', background='white')

    def create_gui(self):
        self.create_options_area()
        self.create_buttons_area()
        self.populate()

    def create_options_area(self):

        self.options_frame = tk.Frame(self, background="#ffffff")
        self.options_frame.pack(side='top', padx=10, pady=3, fill='both',
                                expand=1)

        self.scaling_section_label = \
            ttk.Label(self.options_frame,
                      text="Scaling Options")
        self.scaling_section_label.grid(row=0, column=0,
                                        columnspan=2,
                                        sticky="nsew",
                                        padx=1, pady=1)
        self.scaling_section_label. \
            configure(style='Sections.TLabel')

        self.standardization_radiobutton = \
            ttk.Radiobutton(self.options_frame,
                            variable=self.scaling_var,
                            value=0,
                            text="Standardization")

        self.standardization_radiobutton.grid(row=1, column=0, sticky="nsew",
                                              padx=1, pady=1)
        self.standardization_radiobutton.configure(style='Body.TRadiobutton')

        self.normalization_radiobutton = \
            ttk.Radiobutton(self.options_frame,
                            variable=self.scaling_var,
                            value=1,
                            text="Normalization")

        self.normalization_radiobutton.grid(row=2, column=0, sticky="nsew",
                                            padx=1, pady=1)
        self.normalization_radiobutton.configure(style='Body.TRadiobutton')

    def create_buttons_area(self):

        self.buttons_frame = tk.Frame(self, background="#ffffff")
        self.buttons_frame.pack(side='top', padx=10, pady=3, expand=1)

        self.save_button = \
            ttk.Button(self.buttons_frame,
                       text="Save",
                       name="save_button",
                       command=self.on_save_button_clicked)
        self.save_button.grid(row=1, column=0, sticky="nsew",
                              padx=5, pady=1)

    def populate(self):

        qry = 'SELECT * FROM ModelDefaults WHERE ModelDefaultName=?'
        parameters = ('scaling',)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            self.scaling_var.set(row[4])

    def on_save_button_clicked(self):

        self.save_default()

    def save_default(self):

        qry = "UPDATE ModelDefaults SET " \
            "ModelDefaultInt1=? " \
            "WHERE ModelDefaultName=?"
        parameters = (self.scaling_var.get(), 'scaling')
        exec_qry(qry, parameters)
        self.exit_window()

    def exit_window(self):

        self.destroy()
