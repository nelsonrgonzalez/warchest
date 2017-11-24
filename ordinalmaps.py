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

from toolbox import exec_qry, exec_insert_qry, sorted_by_second_item, is_even
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json


class OrdinalMapping(tk.Toplevel):

    def __init__(self, parent, col_values, feature_type):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Ordinal Mappings')
        self.parent = parent
        self.col_values = col_values
        self.feature_type = feature_type

        self.config(background="#ffffff")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (800, 228,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.ordinal_mapping_str = ""
        self.ordinal_mapping_dict = {}
        self.ordinal_mapping_list = []
        self.ordinal_map_id = 0

        self.create_gui()
        self.focus_set()
        self.grab_set()

    def create_gui(self):
        self.create_tree_view()
        self.create_right_buttons()
        self.view_mappings()

    def create_tree_view(self):
        self.mapping_tree = ttk.Treeview(self, height=10, columns=2)
        self.mapping_tree.grid(row=0, column=0, rowspan=3)
        self.mapping_tree.column('#0', width=600)
        self.mapping_tree.column(2, width=50)
        self.mapping_tree.heading('#0', text='Mapping', anchor=tk.W)
        self.mapping_tree.heading(2, text='Active', anchor=tk.W)

        self.mapping_tree.tag_configure('odd_row', background='white')
        self.mapping_tree.tag_configure('even_row', background='grey90')

        self.mapping_tree.bind("<Double-Button-1>",
                               self.handle_double_click)

        self.mapping_tree_scrollbar = \
            ttk.Scrollbar(self, orient=tk.VERTICAL,
                          command=self.mapping_tree.yview)
        self.mapping_tree_scrollbar.grid(row=0, column=1, rowspan=3,
                                         sticky='ns')
        self.mapping_tree.configure(yscrollcommand=self.
                                    mapping_tree_scrollbar.set)

    def create_right_buttons(self):
        self.right_buttons_frame = tk.Frame(self, background="#ffffff")
        self.right_buttons_frame.grid(row=0, column=2, sticky='nsew')
        ttk.Button(self.right_buttons_frame, text='Add New Mapping',
                   command=self.on_add_new_mapping_button_clicked).grid(
                   row=0, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Delete Mapping',
                   command=self.on_delete_mapping_button_clicked).grid(
                   row=1, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Modify Mapping',
                   command=self.on_modify_mapping_button_clicked).grid(
                   row=2, column=2, sticky="nsew", padx=10, pady=1)
        ttk.Button(self.right_buttons_frame, text='Set as Active',
                   command=self.on_set_as_active_button_clicked).grid(
                   row=3, column=2, sticky="nsew", padx=10, pady=1)

    def on_add_new_mapping_button_clicked(self):

        if self.feature_type == "nominal or ordinal":
            if messagebox.askyesno("Selection", "Do you want to use the " +
                                   "current column's categorical values?"):
                self.open_add_new_mapping_window(use_current_column=True)
            else:
                self.open_add_new_mapping_window(use_current_column=False)
        else:
            self.open_add_new_mapping_window(use_current_column=False)

    def on_delete_mapping_button_clicked(self):

        try:
            self.mapping_tree.item(self.mapping_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No mapping was selected.")
            return

        if (self.mapping_tree.
                item(self.mapping_tree.selection())['values'][0] == "Yes"):

            messagebox.showwarning("Warning", "Cannot delete Active mappings.")
        else:
            self.delete_mapping()

    def on_modify_mapping_button_clicked(self):

        try:
            self.mapping_tree.item(self.mapping_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No mapping was selected.")
            return
        self.open_modify_mapping_window()

    def on_set_as_active_button_clicked(self):

        try:
            self.mapping_tree.item(self.mapping_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No mapping was selected.")
            return
        if self.is_mapping_active() is True:
            messagebox.showwarning("Warning", "Mapping already set as Active.")
        else:

            qry = 'UPDATE OrdinalMaps SET IsActive=?'
            parameters = ("No",)
            exec_qry(qry, parameters)

            ordinal_map_id = self. \
                get_ordinal_map_id(self.mapping_tree.
                                   item(self.mapping_tree.selection())['text'])

            qry = 'UPDATE OrdinalMaps SET IsActive=? WHERE OrdinalMapID=?'
            parameters = ("Yes", ordinal_map_id)
            exec_qry(qry, parameters)

            self.view_mappings()

    def is_mapping_active(self):

        if (self.mapping_tree.item(self.mapping_tree.selection())['values'][0]
                == "Yes"):
            return True
        else:
            return False

    def view_mappings(self):
        items = self.mapping_tree.get_children()
        for item in items:
            self.mapping_tree.delete(item)
        qry = 'SELECT * FROM OrdinalMaps ORDER BY IsActive'
        mappings = exec_qry(qry)
        for i, row in enumerate(mappings):
            if is_even(i):
                self.mapping_tree.insert('', 0, text=row[1], values=row[2],
                                         tags=('even_row',))
            else:
                self.mapping_tree.insert('', 0, text=row[1], values=row[2],
                                         tags=('odd_row',))

    def get_ordinal_map_id(self, ordinal_mapping_str):

        where_column1 = 'OrdinalMapping'

        qry = "SELECT OrdinalMapID FROM OrdinalMaps WHERE {cond}=?".\
            format(cond=where_column1)
        parameters = (ordinal_mapping_str,)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

    def delete_mapping(self):

        if messagebox.askyesno("Warning", "Do you want to delete the " +
                               "selected mapping?"):

            ordinal_map_id = self. \
                get_ordinal_map_id(self.mapping_tree.
                                   item(self.mapping_tree.selection())['text'])
            qry = 'DELETE FROM OrdinalMaps WHERE OrdinalMapID=?'
            parameters = (ordinal_map_id,)
            exec_qry(qry, parameters)
            self.view_mappings()

    def show_mapping_entries(self, frame):

        self.key_entry = [None] * len(self.ordinal_mapping_list)
        self.value_entry = [None] * len(self.ordinal_mapping_list)

        for widget in frame.winfo_children():
            widget.destroy()

        for i, (key, value) in enumerate(self.ordinal_mapping_list):
            self.key_entry[i] = tk.Entry(frame,
                                         relief='flat',
                                         highlightbackground='black',
                                         highlightthickness=1,
                                         highlightcolor='black',
                                         name='key'+str(i),
                                         width=50)
            self.key_entry[i].grid(row=i, column=1, padx=0, pady=0)
            self.key_entry[i].delete(0, tk.END)
            self.key_entry[i].insert(0, key)
            self.key_entry[i].name = 'key'+str(i)

            self.value_entry[i] = tk.Entry(frame,
                                           relief='flat',
                                           highlightbackground='black',
                                           highlightthickness=1,
                                           highlightcolor='black',
                                           name='value'+str(i),
                                           width=10)
            self.value_entry[i].grid(row=i, column=2, padx=0, pady=0)
            self.value_entry[i].delete(0, tk.END)
            self.value_entry[i].insert(0, value)
            self.value_entry[i].name = 'value'+str(i)

    def open_add_new_mapping_window(self, use_current_column=False):

        if use_current_column is True:

            del self.ordinal_mapping_list[:]

            lst_a = list(self.col_values.unique())
            lst_b = [''] * len(list(self.col_values.unique()))
            self.ordinal_mapping_list.extend(list(zip(lst_a, lst_b)))

        else:
            del self.ordinal_mapping_list[:]
            self.ordinal_mapping_list.append(('', ''))

        self.ordinal_map_id = 0

        self.add_window = tk.Toplevel()
        self.add_window.title('Add Ordinal Mapping')
        self.add_window.resizable(width=False, height=False)
        self.add_window.config(background="#ffffff")
        self.add_window. \
            geometry('%dx%d+%d+%d' % (520, 200,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.aw_ordinal_mapping_frame = tk.Frame(self.add_window,
                                                 background="#ffffff")
        self.aw_ordinal_mapping_frame.pack(side='left')

        self.aw_button_frame = tk.Frame(self.add_window, background="#ffffff")
        self.aw_button_frame.pack(side='left', padx=10, pady=3, fill='both',
                                  expand=1)

        self.aw_canvas = tk.Canvas(self.aw_ordinal_mapping_frame,
                                   borderwidth=0, background="#ffffff")
        self.aw_frame = tk.Frame(self.aw_canvas, background="#ffffff")
        self.aw_canvas_scrollbar = tk.Scrollbar(self.aw_ordinal_mapping_frame,
                                                orient="vertical",
                                                command=self.aw_canvas.yview)
        self.aw_canvas.configure(yscrollcommand=self.aw_canvas_scrollbar.set)
        self.aw_canvas_scrollbar.pack(side="right", fill="y")
        self.aw_canvas.pack(side="left", fill="both", expand=True)
        self.aw_canvas.create_window((1, 1), window=self.aw_frame, anchor="nw",
                                     tags="self.aw_frame")

        def handle_aw_frame_configure(event):
            self.aw_canvas.configure(scrollregion=self.aw_canvas.bbox("all"))
        self.aw_frame.bind("<Configure>", handle_aw_frame_configure)

        self.show_mapping_entries(self.aw_frame)

        self.aw_add_new_line_button = \
            ttk.Button(self.aw_button_frame,
                       text="Add New Line",
                       name="aw_add_new_line_button",
                       command=lambda: self.
                       on_aw_add_new_line_button_clicked(self.aw_frame))
        self.aw_add_new_line_button.grid(row=0, column=0, sticky="nsew",
                                         padx=5, pady=1)
        self.aw_save_mapping_button = \
            ttk.Button(self.aw_button_frame,
                       text="Save Mapping",
                       name="aw_save_mapping_button",
                       command=lambda: self.
                       on_aw_save_mapping_button_clicked(self.aw_frame))
        self.aw_save_mapping_button.grid(row=1, column=0, sticky="nsew",
                                         padx=5, pady=1)
        self.aw_delete_last_line_button = \
            ttk.Button(self.aw_button_frame,
                       text="Delete Last Line",
                       name="aw_delete_last_line_button",
                       command=lambda: self.
                       on_aw_delete_last_line_button_clicked(self.aw_frame))
        self.aw_delete_last_line_button.grid(row=2, column=0, sticky="nsew",
                                             padx=5, pady=1)

        self.add_window.focus_set()
        self.add_window.grab_set()
        self.add_window.mainloop()

    def open_modify_mapping_window(self):

        self.ordinal_mapping_str = self. \
            mapping_tree.item(self.mapping_tree.selection())['text']
        self.ordinal_map_id = self.get_ordinal_map_id(self.ordinal_mapping_str)
        self.ordinal_mapping_dict = json.loads(self.ordinal_mapping_str)
        self.ordinal_mapping_list_unsorted = \
            list(self.ordinal_mapping_dict.items())
        self.ordinal_mapping_list = \
            sorted_by_second_item(self.ordinal_mapping_list_unsorted)

        self.modify_window = tk.Toplevel()
        self.modify_window.title('Modify Ordinal Mapping')
        self.modify_window.resizable(width=False, height=False)
        self.modify_window.config(background="#ffffff")

        self.modify_window. \
            geometry('%dx%d+%d+%d' % (520, 200,
                                      self.parent.winfo_rootx()+150,
                                      self.parent.winfo_rooty()+150))

        self.mw_ordinal_mapping_frame = tk.Frame(self.modify_window,
                                                 background="#ffffff")
        self.mw_ordinal_mapping_frame.pack(side='left')

        self.mw_button_frame = tk.Frame(self.modify_window,
                                        background="#ffffff")
        self.mw_button_frame.pack(side='left', padx=10, pady=3, fill='both',
                                  expand=1)

        self.mw_canvas = tk.Canvas(self.mw_ordinal_mapping_frame,
                                   borderwidth=0, background="#ffffff")
        self.mw_frame = tk.Frame(self.mw_canvas, background="#ffffff")
        self.mw_canvas_scrollbar = tk.Scrollbar(self.mw_ordinal_mapping_frame,
                                                orient="vertical",
                                                command=self.mw_canvas.yview)
        self.mw_canvas.configure(yscrollcommand=self.mw_canvas_scrollbar.set)
        self.mw_canvas_scrollbar.pack(side="right", fill="y")
        self.mw_canvas.pack(side="left", fill="both", expand=True)
        self.mw_canvas.create_window((1, 1), window=self.mw_frame, anchor="nw",
                                     tags="self.mw_frame")

        def handle_mw_frame_configure(event):
            self.mw_canvas.configure(scrollregion=self.mw_canvas.bbox("all"))
        self.mw_frame.bind("<Configure>", handle_mw_frame_configure)

        self.show_mapping_entries(self.mw_frame)

        self.mw_add_new_line_button = \
            ttk.Button(self.mw_button_frame,
                       text="Add New Line",
                       name="mw_add_new_line_button",
                       command=lambda: self.
                       on_mw_add_new_line_button_clicked(self.mw_frame))
        self.mw_add_new_line_button.grid(row=0, column=0, sticky="nsew",
                                         padx=5, pady=1)
        self.mw_save_mapping_button = \
            ttk.Button(self.mw_button_frame,
                       text="Save Mapping",
                       name="mw_save_mapping_button",
                       command=lambda: self.
                       on_mw_save_mapping_button_clicked(self.mw_frame))
        self.mw_save_mapping_button.grid(row=1, column=0, sticky="nsew",
                                         padx=5, pady=1)
        self.mw_delete_last_line_button = \
            ttk.Button(self.mw_button_frame,
                       text="Delete Last Line",
                       name="mw_delete_last_line_button",
                       command=lambda: self.
                       on_mw_delete_last_line_button_clicked(self.mw_frame))
        self.mw_delete_last_line_button.grid(row=2, column=0, sticky="nsew",
                                             padx=5, pady=1)

        self.modify_window.focus_set()
        self.modify_window.grab_set()
        self.modify_window.mainloop()

    def on_aw_add_new_line_button_clicked(self, frame):

        if self.validate_all(frame) is True:

            if self.is_mapping_changed(frame) is True:

                self.save_mapping(frame)

            if len(self.ordinal_mapping_list) == 0:
                self.ordinal_mapping_list.append(('', ''))
            else:
                if self.ordinal_mapping_list[-1] == ('', ''):
                    messagebox.showwarning("Warning",
                                           "New item already added.")
                else:
                    self.ordinal_mapping_list.append(('', ''))

            self.show_mapping_entries(frame)

    def on_mw_add_new_line_button_clicked(self, frame):

        if self.validate_all(frame) is True:

            if self.is_mapping_changed(frame) is True:

                self.save_mapping(frame)

            if len(self.ordinal_mapping_list) == 0:
                self.ordinal_mapping_list.append(('', ''))
            else:
                if self.ordinal_mapping_list[-1] == ('', ''):
                    messagebox.showwarning("Warning",
                                           "New item already added.")
                else:
                    self.ordinal_mapping_list.append(('', ''))

            self.show_mapping_entries(frame)

    def on_aw_save_mapping_button_clicked(self, frame):

        if self.validate_all(frame) is True:
            self.save_mapping(frame)

    def on_mw_save_mapping_button_clicked(self, frame):

        if self.validate_all(frame) is True:
            self.save_mapping(frame)

    def on_aw_delete_last_line_button_clicked(self, frame):

        if self.validate_all(frame) is True:

            for widget in frame.winfo_children()[-2:]:
                widget.destroy()

            self.ordinal_mapping_list.pop()

            self.save_mapping(frame)

    def on_mw_delete_last_line_button_clicked(self, frame):

        if self.validate_all(frame) is True:

            for widget in frame.winfo_children()[-2:]:
                widget.destroy()

            self.ordinal_mapping_list.pop()

            self.save_mapping(frame)

    def validate_all(self, frame):

        if (self.validate_data_in_mapping_entries(frame) is True and
                self.validate_dups_in_mapping_entries(frame) is True):
            return True
        return False

    def validate_dups_in_mapping_entries(self, frame):

        lst = []

        for widget in frame.winfo_children():
            if "key" in str(widget):
                lst.append(widget.get())

        lst.sort()
        for i in range(0, len(lst)-1):
            if lst[i] == lst[i+1]:
                messagebox.showwarning("Warning", "Categories must be unique.")
                return False

        return True

    def validate_data_in_mapping_entries(self, frame):

        # check if key are alphanumeric and if value are digits
        for widget in frame.winfo_children():
            # If Category is not alphanumeric
            if "key" in str(widget):
                if widget.get().isalnum() is False:
                    messagebox.showwarning("Warning",
                                           "Category can only be" +
                                           "alphanumeric.")
                    return False
            # If Value is not digits
            if "value" in str(widget):
                if widget.get().isdigit() is False:
                    messagebox.showwarning("Warning",
                                           "Value can only be digits.")
                    return False
        return True

    def is_mapping_changed(self, frame):

        # get current key and values
        lst_a = []
        lst_b = []

        for widget in frame.winfo_children():
            if "key" in str(widget):
                lst_a.append(widget.get())
            if "value" in str(widget):
                lst_b.append(int(widget.get()))

        # compare with key and values before last save or since the last
        # refresh
        if (self.ordinal_mapping_list == list(zip(lst_a, lst_b))):
            return False
        else:
            return True

    def save_mapping(self, frame):

        if self.ordinal_map_id == 0:
            self.insert_mapping(frame)

        else:
            self.update_mapping(frame)

    def update_mapping(self, frame):

        lst_a = []
        lst_b = []

        for widget in frame.winfo_children():
            if "key" in str(widget):
                lst_a.append(widget.get())
            if "value" in str(widget):
                lst_b.append(int(widget.get()))

        self.ordinal_mapping_list = list(zip(lst_a, lst_b))

        lst_to_dict = dict(sorted_by_second_item(self.ordinal_mapping_list))
        dict_to_str = json.dumps(lst_to_dict)

        qry = 'UPDATE OrdinalMaps SET OrdinalMapping=? WHERE OrdinalMapID=?'
        parameters = (dict_to_str, self.ordinal_map_id)
        exec_qry(qry, parameters)
        self.view_mappings()

    def insert_mapping(self, frame):

        lst_a = []
        lst_b = []

        for widget in frame.winfo_children():
            if "key" in str(widget):
                lst_a.append(widget.get())
            if "value" in str(widget):
                lst_b.append(int(widget.get()))

        self.ordinal_mapping_list = list(zip(lst_a, lst_b))

        lst_to_dict = dict(sorted_by_second_item(self.ordinal_mapping_list))
        dict_to_str = json.dumps(lst_to_dict)

        col_ord_mapping = 'OrdinalMapping'
        col_isactive = 'IsActive'

        qry = 'INSERT INTO OrdinalMaps ({col1}, {col2}) VALUES (?, ?)'.\
            format(col1=col_ord_mapping, col2=col_isactive)
        parameters = (dict_to_str, "No")
        self.ordinal_map_id = exec_insert_qry(qry, parameters)
        self.view_mappings()

    def is_mapping_exists(self, dict_to_str):

        qry = 'SELECT OrdinalMapping FROM OrdinalMaps WHERE OrdinalMapping=?'
        parameters = (dict_to_str,)
        cursor = exec_qry(qry, parameters)
        lst = []
        for row in cursor:
            lst.append(row[0])
        return len(lst)

    def handle_double_click(self, event):

        self.on_modify_mapping_button_clicked()
        return

    def exit_window(self):

        self.destroy()
