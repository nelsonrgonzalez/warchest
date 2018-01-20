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

from toolbox import exec_qry, exec_insert_qry, scale, is_even
import tkinter as tk
from tkinter import ttk
from sklearn.model_selection import train_test_split
from tkinter import messagebox, filedialog
from modeltasks import ModelTask
from sessions import Session
from modeloverridesdialogs import ClassifiersModelOverrides
from modeloverridesdialogs import TrainAndTestSplitOverrides
from modeloverridesdialogs import ScalingOverrides
import classifiers


class Model(tk.Toplevel):

    def __init__(self, parent, x, y):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Models')
        self.parent = parent
        self.x = x
        self.y = y
        self.x_rows, self.x_cols = self.x.shape
        self.y_rows, = self.y.shape
        if self.x.size == 0:
            self.is_x_empty = True
        else:
            self.is_x_empty = False
        if self.y.size == 0:
            self.is_y_empty = True
        else:
            self.is_y_empty = False

        session = Session()
        self.session_id = session.get_current_session()

        model_task = ModelTask()
        self.simple_set_id = model_task.get_max_simple_set_number()

        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.geometry('%dx%d+%d+%d' % (1100, 600,
                                       parent.winfo_rootx()+50,
                                       parent.winfo_rooty()+50))

        self.init_model_vars()
        self.setup_styles()
        self.create_gui()
        self.focus_set()
        self.grab_set()

    def setup_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Tabs.TFrame', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')

        self.app_style.configure('Tabs.TLabel', background='white')

    def create_gui(self):

        self.create_top_menu()
        self.create_work_area()
        self.create_tabs()
        self.create_dataset_tab_widgets()
        self.create_simple_set_tab_widgets()

    def create_top_menu(self):

        top_menu = self.winfo_toplevel()
        self.menu_bar = tk.Menu(top_menu)
        top_menu['menu'] = self.menu_bar

        # model_menu
        self.model_menu = tk.Menu(self.menu_bar, tearoff=0,
                                  activebackground="#A2A2A2",
                                  activeforeground="black")
        self.model_menu.add_command(
            label="Run Model", command=self.on_run_model_menu_clicked)
        self.model_menu.add_separator()
        self.model_menu.add_command(label="Close", command=self.exit_window)
        self.menu_bar.add_cascade(label="Model", menu=self.model_menu)

        # settings_menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0,
                                      activebackground="#A2A2A2",
                                      activeforeground="black")
        self.menu_bar.add_cascade(label="Settings",
                                  menu=self.settings_menu)

        # model_overrides_menu (under settings_menu)
        self.model_overrides_menu = tk.Menu(self.settings_menu,
                                           tearoff=0,
                                           activebackground="#A2A2A2",
                                           activeforeground="black")
        self.model_overrides_menu.add_command(
                label="Classifiers",
                command=self.on_classifiers_overrides_menu_clicked)
        self.model_overrides_menu.add_command(
                label="Train and Test Splits",
                command=self.on_train_and_test_split_overrides_menu_clicked)
        self.model_overrides_menu.add_command(
                label="Scaling",
                command=self.on_scaling_overrides_menu_clicked)
        self.settings_menu.add_cascade(label="Model Overrides",
                                      menu=self.model_overrides_menu)

    def create_work_area(self):

        self.work_area = tk.Frame(self, height=5, bg="white")
        self.work_area.pack(fill='both', expand=1)

    def create_tabs(self):

        self.tabs = ttk.Notebook(self.work_area)
        self.tabs.pack(fill='both', expand=1)

        self.dataset_tab = ttk.Frame(self.tabs)
        self.simple_set_tab = ttk.Frame(self.tabs)
        self.compound_set_tab = ttk.Frame(self.tabs)
        self.transformations_log_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.dataset_tab, text='Dataset')
        self.tabs.add(self.simple_set_tab, text='Simple Set')
        self.tabs.add(self.compound_set_tab, text='Compound Set')

        self.dataset_tab.configure(style='Tabs.TFrame')
        self.simple_set_tab.configure(style='Tabs.TFrame')
        self.compound_set_tab.configure(style='Tabs.TFrame')

        def on_tab_change(event):

            if self.tabs.index(self.tabs.select()) == 1:
                self.update_simple_set_tree()

        self.tabs.bind("<<NotebookTabChanged>>", on_tab_change)

    def create_dataset_tab_widgets(self):

        self.model_features_section_label = \
            ttk.Label(self.dataset_tab,
                      text="Model Features")
        self.model_features_section_label.grid(row=0, column=0,
                                               columnspan=2,
                                               sticky="nsew",
                                               padx=1, pady=1)
        self.model_features_section_label. \
            configure(style='Sections.TLabel')

        self.x_rows_label = \
            ttk.Label(self.dataset_tab,
                      text="Rows:",
                      name="x_rows_label")
        self.x_rows_label.grid(row=1, column=0, sticky="nsew",
                               padx=1, pady=1)
        self.x_rows_label.configure(style='Tabs.TLabel')
        self.x_rows_entry = \
            tk.Entry(self.dataset_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="x_rows_entry")
        self.x_rows_entry.grid(row=1, column=1, sticky="nsew",
                               padx=1, pady=1)
        #self.add_tooltip_to_widget(self.x_rows_entry)
        self.x_rows_entry.delete(0, tk.END)
        if self.is_x_empty:
            self.x_rows_entry.insert(0, 'No Features')
        else:
            self.x_rows_entry.insert(0, self.x_rows)
        self.x_rows_entry.configure(state='readonly')

        self.x_cols_label = \
            ttk.Label(self.dataset_tab,
                      text="Columns:",
                      name="x_cols_label")
        self.x_cols_label.grid(row=2, column=0, sticky="nsew",
                               padx=1, pady=1)
        self.x_cols_label.configure(style='Tabs.TLabel')
        self.x_cols_entry = \
            tk.Entry(self.dataset_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="x_cols_entry")
        self.x_cols_entry.grid(row=2, column=1, sticky="nsew",
                               padx=1, pady=1)
        #self.add_tooltip_to_widget(self.x_cols_entry)
        self.x_cols_entry.delete(0, tk.END)
        if self.is_x_empty:
            self.x_cols_entry.insert(0, 'No Features')
        else:
            self.x_cols_entry.insert(0, self.x_cols)
        self.x_cols_entry.configure(state='readonly')

        self.x_type_label = \
            ttk.Label(self.dataset_tab,
                      text="Type:",
                      name="x_type_label")
        self.x_type_label.grid(row=3, column=0, sticky="nsew",
                               padx=1, pady=1)
        self.x_type_label.configure(style='Tabs.TLabel')
        self.x_type_entry = \
            tk.Entry(self.dataset_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="x_type_entry")
        self.x_type_entry.grid(row=3, column=1, sticky="nsew",
                               padx=1, pady=1)
        #self.add_tooltip_to_widget(self.x_type_entry)
        self.x_type_entry.delete(0, tk.END)
        if self.is_x_empty:
            self.x_type_entry.insert(0, 'No Features')
        else:
            self.x_type_entry.insert(0, type(self.x))
        self.x_type_entry.configure(state='readonly')

        self.model_classlabel_section_label = \
            ttk.Label(self.dataset_tab,
                      text="Model Class Label")
        self.model_classlabel_section_label.grid(row=4, column=0,
                                                 columnspan=2,
                                                 sticky="nsew",
                                                 padx=1, pady=1)
        self.model_classlabel_section_label. \
            configure(style='Sections.TLabel')

        self.y_rows_label = \
            ttk.Label(self.dataset_tab,
                      text="Rows:",
                      name="y_rows_label")
        self.y_rows_label.grid(row=5, column=0, sticky="nsew",
                               padx=1, pady=1)
        self.y_rows_label.configure(style='Tabs.TLabel')
        self.y_rows_entry = \
            tk.Entry(self.dataset_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="y_rows_entry")
        self.y_rows_entry.grid(row=5, column=1, sticky="nsew",
                               padx=1, pady=1)
        #self.add_tooltip_to_widget(self.y_rows_entry)
        self.y_rows_entry.delete(0, tk.END)
        if self.is_y_empty:
            self.y_rows_entry.insert(0, 'No Class Label')
        else:
            self.y_rows_entry.insert(0, self.y_rows)
        self.y_rows_entry.configure(state='readonly')

        self.y_type_label = \
            ttk.Label(self.dataset_tab,
                      text="Type:",
                      name="y_type_label")
        self.y_type_label.grid(row=6, column=0, sticky="nsew",
                               padx=1, pady=1)
        self.y_type_label.configure(style='Tabs.TLabel')
        self.y_type_entry = \
            tk.Entry(self.dataset_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=20,
                     name="y_type_entry")
        self.y_type_entry.grid(row=6, column=1, sticky="nsew",
                               padx=1, pady=1)
        #self.add_tooltip_to_widget(self.y_type_entry)
        self.y_type_entry.delete(0, tk.END)
        if self.is_y_empty:
            self.y_type_entry.insert(0, 'No Class Label')
        else:
            self.y_type_entry.insert(0, type(self.y))
        self.y_type_entry.configure(state='readonly')

    def create_simple_set_tab_widgets(self):

        self.simple_set_tab_button_area = tk.Frame(self.simple_set_tab, height=1, bg="white")
        self.simple_set_tab_button_area.grid(row=0, column=0, sticky="nsew",
                                             padx=1, pady=0)
        self.simple_set_tab_work_area = tk.Frame(self.simple_set_tab, height=1, bg="white")
        self.simple_set_tab_work_area.grid(row=1, column=0, sticky="nsew",
                                           padx=1, pady=0)
        # run_simple_set_model_button
        self.run_simple_set_model_button = \
            ttk.Button(self.simple_set_tab_button_area,
                       text="Run Model",
                       name="run_simple_set_model_button",
                       command=self.on_run_simple_set_model_button_clicked)
        self.run_simple_set_model_button.grid(row=0, column=0, sticky="nsew",
                                              padx=1, pady=1)
        # self.add_tooltip_to_widget(self.run_simple_set_model_button)

        # simple_set_tree
        self.simple_set_tree = \
            ttk.Treeview(self.simple_set_tab_work_area,
                         height=25,
                         columns=('ID', 'Session ID', 'Simple Set ID',
                                  'Created On', 'Algorithm Name',
                                  'Parameters', 'Misc Samples', 'Misc Error',
                                  'SKL Acc Score', 'Train Acc', 'Test Acc',
                                  'Overfitting'),
                         selectmode='browse',
                         name="simple_set_tree")
        self.simple_set_tree.grid(row=1, column=0, sticky="nsew",
                                  padx=1, pady=1)
        self.simple_set_tree.column('#0', width=40)
        self.simple_set_tree.column('#1', width=65)
        self.simple_set_tree.column('#2', width=40)
        self.simple_set_tree.column('#3', width=100)
        self.simple_set_tree.column('#4', width=250)
        self.simple_set_tree.column('#5', width=160)
        self.simple_set_tree.column('#6', width=70)
        self.simple_set_tree.column('#7', width=70)
        self.simple_set_tree.column('#8', width=70)
        self.simple_set_tree.column('#9', width=65)
        self.simple_set_tree.column('#10', width=65)
        self.simple_set_tree.column('#11', width=80)
        self.simple_set_tree.column('#12', width=0)
        self.simple_set_tree.heading('#0', text='ID', anchor=tk.W)
        self.simple_set_tree.heading('#1', text='Session ID', anchor=tk.W)
        self.simple_set_tree.heading('#2', text='Set ID', anchor=tk.W)
        self.simple_set_tree.heading('#3', text='Created On', anchor=tk.W)
        self.simple_set_tree.heading('#4', text='Algorithm Name', anchor=tk.W)
        self.simple_set_tree.heading('#5', text='Parameters', anchor=tk.W)
        self.simple_set_tree.heading('#6', text='Misc Samples', anchor=tk.W)
        self.simple_set_tree.heading('#7', text='Misc Error', anchor=tk.W)
        self.simple_set_tree.heading('#8', text='SKL Acc Score', anchor=tk.W)
        self.simple_set_tree.heading('#9', text='Train Acc', anchor=tk.W)
        self.simple_set_tree.heading('#10', text='Test Acc', anchor=tk.W)
        self.simple_set_tree.heading('#11', text='Overfitting', anchor=tk.W)

        self.simple_set_tree.tag_configure('odd_row', background='white')
        self.simple_set_tree.tag_configure('even_row', background='grey90')

        self.simple_set_tree.bind("<Double-Button-1>",
                               self.handle_simple_set_tree_double_click)

        self.simple_set_tree_scrollbar = \
            ttk.Scrollbar(self.simple_set_tab_work_area,
                          orient=tk.VERTICAL,
                          command=self.simple_set_tree.yview)
        self.simple_set_tree_scrollbar.grid(row=1, column=1, sticky='ns')
        self.simple_set_tree.configure(yscrollcommand=self.
                                       simple_set_tree_scrollbar.set)

    def init_model_vars(self):

        self.update_model_vars()

    def update_model_vars(self):

        model_task = ModelTask()

        self.selected_classifiers = model_task.get_selected_classifiers()
        print(self.selected_classifiers)

        self.selected_params = model_task.get_selected_params()
        print(self.selected_params)

        self.selected_has_random_state, \
            self.selected_random_state, \
            self.selected_train_size, \
            self.selected_test_size = model_task.get_selected_train_test_splits()
        print(self.selected_has_random_state)
        print(self.selected_random_state)
        print(self.selected_train_size)
        print(self.selected_test_size)

        self.selected_scaling = model_task.get_selected_scaling()
        print(self.selected_scaling)

    def update_from_model_overrides_dialogs(self, option):

        if option == 'update':
            self.update_model_vars()

    def on_run_model_menu_clicked(self):

        if self.is_x_empty:
            messagebox.showwarning("Warning", "No features selected.")
            return

        model_task = ModelTask()
        self.simple_set_id = model_task.get_next_available_simple_set_number()

        self.get_train_and_test_split()
        self.get_scaled_features(self.selected_scaling)

        for row in self.selected_params:
            print(row[0], row[1], row[2], row[3], row[4])

        for row in self.selected_classifiers:

            print(row)
            print(self.get_algorithm_internal_name(row))

            params= {}
            for param in self.selected_params:
                if param[0] == row:
                    print(param[1], param[2], param[3])
                    if param[2] == 'float':
                        params[param[1]] = float(param[3])
                    elif param[2] == 'int':
                        params[param[1]] = int(param[3])
                    elif param[2] == 'str':
                        params[param[1]] = param[3]

            print(params)

            called_clf = getattr(classifiers, self.get_algorithm_internal_name(row))

            if self.does_algorithm_need_scaling(row) == True:
                called_clf(x_train=self.x_train_std,
                           x_test=self.x_test_std,
                           y_train=self.y_train,
                           y_test=self.y_test,
                           session_id=self.session_id,
                           simple_set_id=self.simple_set_id,
                           algorithm_id=row,
                           **params)
            else:
                called_clf(x_train=self.x_train,
                           x_test=self.x_test,
                           y_train=self.y_train,
                           y_test=self.y_test,
                           session_id=self.session_id,
                           simple_set_id=self.simple_set_id,
                           algorithm_id=row,
                           **params)

        self.tabs.select(1)
        self.update_simple_set_tree()

    def on_classifiers_overrides_menu_clicked(self):

        ClassifiersModelOverrides(self, callback=self.update_from_model_overrides_dialogs)

    def on_train_and_test_split_overrides_menu_clicked(self):

        TrainAndTestSplitOverrides(self, callback=self.update_from_model_overrides_dialogs)

    def on_scaling_overrides_menu_clicked(self):

        ScalingOverrides(self, callback=self.update_from_model_overrides_dialogs)

    def on_run_simple_set_model_button_clicked(self):

        self.on_run_model_menu_clicked()

    def get_train_and_test_split(self):

        if self.selected_has_random_state is True:
            self.x_train, self.x_test, self.y_train, self.y_test = \
                train_test_split(self.x, self.y,
                                 train_size=self.selected_train_size,
                                 test_size=self.selected_test_size,
                                 random_state=self.selected_random_state)
        else:
            self.x_train, self.x_test, self.y_train, self.y_test = \
                train_test_split(self.x, self.y,
                                 train_size=self.selected_train_size,
                                 test_size=self.selected_test_size)

    def get_scaled_features(self, selected_scaling):

        if selected_scaling == 0:
            scaling = "std"
        elif selected_scaling == 1:
            scaling = "norm"

        self.x_train_std, self.x_test_std = \
            scale(self.x_train, self.x_test, scaling=scaling)

    def does_algorithm_need_scaling(self, algorithm_id):

        qry = "SELECT NeedsScaling FROM ModelOverrideAlgorithms WHERE AlgorithmID=?"
        parameters = (algorithm_id,)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            if row[0] == 1:
                return True
            else:
                return False

    def get_algorithm_internal_name(self, algorithm_id):

        qry = "SELECT AlgorithmInternalName FROM Algorithms WHERE AlgorithmID=?"
        parameters = (algorithm_id,)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

    def handle_simple_set_tree_double_click(self, event):

        pass

    def update_simple_set_tree(self):

        model_task = ModelTask()

        for item in self.simple_set_tree.get_children():
            self.simple_set_tree.delete(item)

        for i, row in enumerate(model_task.get_simple_set_by_simple_set_id(self.simple_set_id)):

            if is_even(i):
                self.simple_set_tree.insert('', 0, text=row[0],
                                                     values=(row[1],
                                                     row[2], row[3], row[4],
                                                     row[5], row[6], row[7],
                                                     row[8], row[9], row[10],
                                                     row[11]),
                                                     tags=('even_row',))
            else:
                self.simple_set_tree.insert('', 0, text=row[0],
                                                     values=(row[1],
                                                     row[2], row[3], row[4],
                                                     row[5], row[6], row[7],
                                                     row[8], row[9], row[10],
                                                     row[11]),
                                                     tags=('odd_row',))

    def exit_window(self):

        self.destroy()
