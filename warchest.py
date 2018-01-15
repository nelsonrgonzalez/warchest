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

from toolbox import write_to_console, is_even, exec_qry
import numpy as np
import pandas as pd
import os.path
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from preprocessing import EncodeClassLabel, Scale
from insights import ColumnInsight
from ordinalmaps import OrdinalMapping
from toolsdialogs import ClassifiersCRUD, ClassifiersModelDefaults
from toolsdialogs import TrainAndTestSplitDefaults, ScalingDefaults
from datasets import Dataset
from models import Model
from modeltasks import ModelTask
from sessions import Session
from transformations import Transformation
from modeloptions import ModelOption
from automator import Automator
from global_config import g
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import Pmw
from wcpandastable.core import Table

APP_NAME = "Warchest"
CELL_CLR_NORMAL = '#FFFFFF'  # White
CELL_CLR_CLS_LBL = '#FFFF00'  # Yellow
CELL_CLR_MODEL_NUMERICAL = '#00FFFF'  # Cyan
CELL_CLR_MODEL_DATETIME = '#F5DEB3'  # Wheat
CELL_CLR_MODEL_BOOLEAN = '#EE82EE'  # Violet
CELL_CLR_MODEL_NOMINAL = '#ADD8E6'  # LightBlue
CELL_CLR_MODEL_ORDINAL = '#00BFFF'  # DeepSkyBlue


class Warchest():

    def __init__(self, root):
        self.root = root
        self.root.resizable(width=False, height=False)
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.db_filename = 'warchest.db'
        self.root.title(APP_NAME)
        self.tooltip = Pmw.Balloon(self.root)
        self.set_app_size()
        self.setup_app_styles()

        self.session_id = 0
        # top area variables
        self.selected_column = 0
        self.selected_column_name = ''
        self.column_tab_dict = {}
        self.available_to_model = {}
        self.class_label_status = {}
        self.nominal_ordinal = {}
        self.available_to_model_final = {}
        self.model_columns = {}

        self.selected_dataset = ''

        self.transformations_log_list = []

        # absolute path of application py file
        self.absolute_path = os.path.dirname(os.path.abspath(__file__))
        self.datasets_path = os.path.join(self.absolute_path, 'datasets')
        self.trans_path = os.path.join(self.absolute_path, 'transformations')
        self.model_columns_path = os.path.join(self.absolute_path, 'modelcolumns')
        self.create_gui()

    def create_gui(self):
        self.create_top_menu()
        self.create_top_area()
        self.create_dataframe_area()

    def setup_app_styles(self):

        self.app_style = ttk.Style()
        self.app_style.configure('Tabs.TFrame', background='white')
        self.app_style.configure('Tabs.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')

    def set_app_size(self):

        width = 1371
        height = 756
        x_offset = (self.root.winfo_screenwidth()/2)-(width/2)
        y_offset = (self.root.winfo_screenheight()/2)-(height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x_offset, y_offset))
        return

    def create_top_menu(self):

        self.menu_bar = tk.Menu(self.root)

        # model_menu
        self.model_menu = tk.Menu(self.menu_bar, tearoff=0,
                                  activebackground="#A2A2A2",
                                  activeforeground="black")
        self.model_menu.add_command(
            label="Select Dataset",
            command=self.on_select_dataset_menu_clicked)
        self.model_menu.add_command(
            label="Load Dataset", command=self.on_load_dataset_menu_clicked)
        self.model_menu.add_command(
            label="Run Dataset (OLD)", command=self.on_run_dataset_menu_old_clicked)
        self.model_menu.add_separator()
        self.model_menu.add_command(
            label="Load Model Columns", command=self.on_load_model_columns_menu_clicked)
        self.model_menu.add_command(
            label="Save Model Columns", command=self.on_save_model_columns_menu_clicked)
        self.model_menu.add_separator()
        self.model_menu.add_command(
            label="Model Dataset", command=self.on_model_dataset_menu_clicked)
        self.model_menu.add_separator()
        self.model_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="Model", menu=self.model_menu)

        # transformations_menu
        self.transformations_menu = tk.Menu(self.menu_bar, tearoff=0,
                                            activebackground="#A2A2A2",
                                            activeforeground="black")
        self.transformations_menu.add_command(
                label="Toggle Selected",
                command=self.on_toggle_selected_transformations_menu_clicked)
        self.transformations_menu.add_command(
                label="Flag All",
                command=self.on_flag_all_transformations_menu_clicked)
        self.transformations_menu.add_command(
                label="Unflag All",
                command=self.on_unflag_all_transformations_menu_clicked)
        self.transformations_menu.add_separator()
        self.transformations_menu.add_command(
                label="Replicate Selected",
                command=self.
                on_replicate_selected_transformations_menu_clicked)
        self.transformations_menu.add_command(
                label="Replicate All",
                command=self.on_replicate_all_transformations_menu_clicked)
        self.transformations_menu.add_separator()
        self.transformations_menu.add_command(
                label="Load Transformations",
                command=self.on_load_transformations_menu_clicked)
        self.transformations_menu.add_command(
                label="Save Transformations",
                command=self.on_save_transformations_menu_clicked)
        self.transformations_menu.add_separator()
        self.transformations_menu.add_command(
                label="Clear All",
                command=self.on_clear_all_transformations_menu_clicked)
        self.menu_bar.add_cascade(label="Transformations",
                                  menu=self.transformations_menu)

        # tools_menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0,
                                  activebackground="#A2A2A2",
                                  activeforeground="black")
        self.tools_menu.add_command(
                label="Ordinal Mappings",
                command=self.on_ordinal_mappings_menu_clicked)
        self.menu_bar.add_cascade(label="Tools",
                                  menu=self.tools_menu)

        # algorithms_menu (under tools_menu)
        self.algorithms_menu = tk.Menu(self.tools_menu, tearoff=0,
                                       activebackground="#A2A2A2",
                                       activeforeground="black")
        self.algorithms_menu.add_command(
                label="Classifiers",
                command=self.on_classifiers_menu_clicked)
        self.tools_menu.add_cascade(label="Algorithms",
                                      menu=self.algorithms_menu)

        # settings_menu (under tools_menu)
        self.settings_menu = tk.Menu(self.tools_menu, tearoff=0,
                                           activebackground="#A2A2A2",
                                           activeforeground="black")
        self.tools_menu.add_cascade(label="Settings",
                                      menu=self.settings_menu)

        # model_defaults_menu (under settings_menu)
        self.model_defaults_menu = tk.Menu(self.settings_menu, tearoff=0,
                                           activebackground="#A2A2A2",
                                           activeforeground="black")
        self.model_defaults_menu.add_command(
                label="Classifiers",
                command=self.on_default_classifiers_menu_clicked)
        self.model_defaults_menu.add_command(
                label="Train and Test Splits",
                command=self.on_default_train_and_test_split_menu_clicked)
        self.model_defaults_menu.add_command(
                label="Scaling",
                command=self.on_default_scaling_menu_clicked)
        self.settings_menu.add_cascade(label="Model Defaults",
                                       menu=self.model_defaults_menu)

        # about_menu
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0,
                                  activebackground="#A2A2A2",
                                  activeforeground="black")
        self.about_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)

        self.root.config(menu=self.menu_bar)

    def create_top_area(self):

        self.top_area = tk.Frame(self.root, height=25, bg="white")
        self.top_area.pack(fill='both', expand=1)

    def create_dataframe_area(self):

        self.dataframe_area = tk.Frame(self.root, bg="white")
        self.dataframe_area.pack(fill='both', expand=1)

    def create_top_area_items(self):

        self.create_tabs()
        self.create_column_tab_widgets()
        self.create_table_tab_widgets()
        self.create_insights_tab_widgets()
        self.create_transformations_log_tab_widgets()

    def create_tabs(self):

        self.tabs = ttk.Notebook(self.top_area)
        self.tabs.pack(fill='both', expand=1)

        self.column_tab = ttk.Frame(self.tabs)
        self.table_tab = ttk.Frame(self.tabs)
        self.insights_tab = ttk.Frame(self.tabs)
        self.transformations_log_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.column_tab, text='Column')
        self.tabs.add(self.table_tab, text='Table')
        self.tabs.add(self.insights_tab, text='Insights')
        self.tabs.add(self.transformations_log_tab, text='Transformations Log')

        self.column_tab.configure(style='Tabs.TFrame')
        self.table_tab.configure(style='Tabs.TFrame')
        self.insights_tab.configure(style='Tabs.TFrame')
        self.transformations_log_tab.configure(style='Tabs.TFrame')

        def on_tab_change(event):

            if self.tabs.index(self.tabs.select()) == 3:
                if self.session_id > 0:
                    self.update_transformations_log_tab_widgets()

            if self.tabs.index(self.tabs.select()) == 1:
                self.update_table_tab_widgets()

        self.tabs.bind("<<NotebookTabChanged>>", on_tab_change)

    def clean_top_area_items(self):

        if hasattr(self, 'tabs'):
            self.tabs.destroy()

    def create_column_tab_widgets(self):

        # analyze_column_button
        self.analyze_column_button = \
            ttk.Button(self.column_tab,
                       text="Analyze Column",
                       name="analyze_column_button",
                       command=self.on_analyze_column_button_clicked)
        self.analyze_column_button.grid(row=0, column=0, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.analyze_column_button)

        # toggle_model_availability_button
        self.toggle_model_availability_button = \
            ttk.Button(self.column_tab,
                       text="Flg Model Available",
                       name="toggle_model_availability_button",
                       command=self.on_toggle_model_availability_button_clicked)
        self.toggle_model_availability_button.grid(row=0, column=1, sticky="nsew",
                                         padx=1, pady=1)
        #self.add_tooltip_to_widget(self.toggle_model_availability_button)

        # toggle_class_label_status_button
        self.toggle_class_label_status_button = \
            ttk.Button(self.column_tab,
                       text="Flg Class Label",
                       name="toggle_class_label_status_button",
                       command=self.on_toggle_class_label_status_button_clicked)
        self.toggle_class_label_status_button.grid(row=0, column=2, sticky="nsew",
                                         padx=1, pady=1)
        #self.add_tooltip_to_widget(self.toggle_class_label_status_button)

        # toggle_nominal_ordinal_button
        self.toggle_nominal_ordinal_button = \
            ttk.Button(self.column_tab,
                       text="Nominal/Ordinal",
                       name="toggle_nominal_ordinal_button",
                       command=self.on_toggle_nominal_ordinal_button_clicked)
        self.toggle_nominal_ordinal_button.grid(row=0, column=3, sticky="nsew",
                                         padx=1, pady=1)
        #self.add_tooltip_to_widget(self.toggle_nominal_ordinal_button)

        # column_tab_progressbar
        self.column_tab_progressbar_label = \
            ttk.Label(self.column_tab,
                      text="")
        self.column_tab_progressbar_label.grid(row=0, column=14,
                                               sticky="e",
                                               padx=1, pady=1)
        self.column_tab_progressbar_label.configure(style='Tabs.TLabel')
        self.column_tab_progressbar_label.grid_remove()
        self.column_tab_progressbar = ttk.Progressbar(self.column_tab,
                                                      orient=tk.HORIZONTAL,
                                                      length=50)
        self.column_tab_progressbar.grid(row=0, column=15, sticky="nsew",
                                         padx=1, pady=1)
        self.column_tab_progressbar.config(mode='indeterminate')
        self.column_tab_progressbar.grid_remove()

        # general_information_section_label
        self.general_information_section_label = \
            ttk.Label(self.column_tab,
                      text="General Information")
        self.general_information_section_label.grid(row=1, column=0,
                                                    columnspan=4,
                                                    sticky="nsew",
                                                    padx=1, pady=1)
        self.general_information_section_label. \
            configure(style='Sections.TLabel')

        # selected_column_name_entry
        self.selected_column_name_label = \
            ttk.Label(self.column_tab,
                      text="Column name:",
                      name="selected_column_name_label")
        self.selected_column_name_label.grid(row=2, column=0, sticky="nsew",
                                             padx=1, pady=1)
        self.selected_column_name_label.configure(style='Tabs.TLabel')
        self.selected_column_name_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="selected_column_name_entry")
        self.selected_column_name_entry.grid(row=2, column=1, sticky="nsew",
                                             padx=1, pady=1)
        self.add_tooltip_to_widget(self.selected_column_name_entry)
        self.selected_column_name_entry.delete(0, tk.END)
        self.selected_column_name_entry.insert(0, self.selected_column_name)
        self.selected_column_name_entry.configure(state='readonly')

        # selected_column_entry
        self.selected_column_label = \
            ttk.Label(self.column_tab,
                      text="Column index:",
                      name="selected_column_label")
        self.selected_column_label.grid(row=3, column=0, sticky="nsew",
                                        padx=1, pady=1)
        self.selected_column_label.configure(style='Tabs.TLabel')
        self.selected_column_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="selected_column_entry")
        self.selected_column_entry.grid(row=3, column=1, sticky="nsew",
                                        padx=1, pady=1)
        self.add_tooltip_to_widget(self.selected_column_entry)
        self.selected_column_entry.delete(0, tk.END)
        self.selected_column_entry.insert(0, self.selected_column)
        self.selected_column_entry.configure(state='readonly')

        # feature_type_entry
        self.feature_type_label = \
            ttk.Label(self.column_tab,
                      text="Feature type:",
                      name="feature_type_label")
        self.feature_type_label.grid(row=4, column=0, sticky="nsew",
                                     padx=1, pady=1)
        self.feature_type_label.configure(style='Tabs.TLabel')
        self.feature_type_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="feature_type_entry")
        self.feature_type_entry.grid(row=4, column=1, sticky="nsew",
                                     padx=1, pady=1)
        self.add_tooltip_to_widget(self.feature_type_entry)
        self.feature_type_entry.configure(state='readonly')

        # available_to_model_entry
        self.available_to_model_label = \
            ttk.Label(self.column_tab,
                      text="Available to model:",
                      name="available_to_model_label")
        self.available_to_model_label.grid(row=5, column=0, sticky="nsew",
                                           padx=1, pady=1)
        self.available_to_model_label.configure(style='Tabs.TLabel')
        self.available_to_model_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="available_to_model_entry")
        self.available_to_model_entry.grid(row=5, column=1, sticky="nsew",
                                           padx=1, pady=1)
        self.add_tooltip_to_widget(self.available_to_model_entry)
        self.available_to_model_entry.configure(state='readonly')

        # dtype_entry
        self.dtype_label = \
            ttk.Label(self.column_tab,
                      text="Dtype:",
                      name="dtype_label")
        self.dtype_label.grid(row=6, column=0, sticky="nsew",
                              padx=1, pady=1)
        self.dtype_label.configure(style='Tabs.TLabel')
        self.dtype_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="dtype_entry")
        self.dtype_entry.grid(row=6, column=1, sticky="nsew",
                              padx=1, pady=1)
        self.add_tooltip_to_widget(self.dtype_entry)
        self.dtype_entry.configure(state='readonly')

        # dense_sparse_entry
        self.dense_sparse_label = \
            ttk.Label(self.column_tab,
                      text="Dense/sparse:",
                      name="dense_sparse_label")
        self.dense_sparse_label.grid(row=7, column=0, sticky="nsew",
                                     padx=1, pady=1)
        self.dense_sparse_label.configure(style='Tabs.TLabel')
        self.dense_sparse_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="dense_sparse_entry")
        self.dense_sparse_entry.grid(row=7, column=1, sticky="nsew",
                                     padx=1, pady=1)
        self.add_tooltip_to_widget(self.dense_sparse_entry)
        self.dense_sparse_entry.configure(state='readonly')

        # non_null_count_entry
        self.non_null_count_label = \
            ttk.Label(self.column_tab,
                      text="Count (non-null):",
                      name="non_null_count_label")
        self.non_null_count_label.grid(row=8, column=0, sticky="nsew",
                                       padx=1, pady=1)
        self.non_null_count_label.configure(style='Tabs.TLabel')
        self.non_null_count_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="non_null_count_entry")
        self.non_null_count_entry.grid(row=8, column=1, sticky="nsew",
                                       padx=1, pady=1)
        self.add_tooltip_to_widget(self.non_null_count_entry)
        self.non_null_count_entry.configure(state='readonly')

        # duplicates_in_col_entry
        self.duplicates_in_col_label = \
            ttk.Label(self.column_tab,
                      text="Duplicates in column:",
                      name="duplicates_in_col_label")
        self.duplicates_in_col_label.grid(row=2, column=2, sticky="nsew",
                                          padx=1, pady=1)
        self.duplicates_in_col_label.configure(style='Tabs.TLabel')
        self.duplicates_in_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="duplicates_in_col_entry")
        self.duplicates_in_col_entry.grid(row=2, column=3, sticky="nsew",
                                          padx=1, pady=1)
        self.add_tooltip_to_widget(self.duplicates_in_col_entry)
        self.duplicates_in_col_entry.configure(state='readonly')

        # unique_values_in_col_entry
        self.unique_values_in_col_label = \
            ttk.Label(self.column_tab,
                      text="Unique in column:",
                      name="unique_values_in_col_label")
        self.unique_values_in_col_label.grid(row=3, column=2, sticky="nsew",
                                             padx=1, pady=1)
        self.unique_values_in_col_label.configure(style='Tabs.TLabel')
        self.unique_values_in_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="unique_values_in_col_entry")
        self.unique_values_in_col_entry.grid(row=3, column=3, sticky="nsew",
                                             padx=1, pady=1)
        self.add_tooltip_to_widget(self.unique_values_in_col_entry)
        self.unique_values_in_col_entry.configure(state='readonly')

        # missing_values_in_col_entry
        self.missing_values_in_col_label = \
            ttk.Label(self.column_tab,
                      text="Missing in column:",
                      name="missing_values_in_col_label")
        self.missing_values_in_col_label.grid(row=4, column=2, sticky="nsew",
                                              padx=1, pady=1)
        self.missing_values_in_col_label.configure(style='Tabs.TLabel')
        self.missing_values_in_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="missing_values_in_col_entry")
        self.missing_values_in_col_entry.grid(row=4, column=3, sticky="nsew",
                                              padx=1, pady=1)
        self.add_tooltip_to_widget(self.missing_values_in_col_entry)
        self.missing_values_in_col_entry.configure(state='readonly')

        # memory_usage_section_label
        self.memory_usage_section_label = \
            ttk.Label(self.column_tab,
                      text="Memory Usage")
        self.memory_usage_section_label.grid(row=1, column=4,
                                             columnspan=2,
                                             sticky="nsew",
                                             padx=1, pady=1)
        self.memory_usage_section_label. \
            configure(style='Sections.TLabel')

        # update_bytes_in_data_entry
        self.bytes_in_data_label = \
            ttk.Label(self.column_tab,
                      text="Bytes in column:",
                      name="bytes_in_data_label")
        self.bytes_in_data_label.grid(row=2, column=4, sticky="nsew",
                                      padx=1, pady=1)
        self.bytes_in_data_label.configure(style='Tabs.TLabel')
        self.bytes_in_data_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="bytes_in_data_entry")
        self.bytes_in_data_entry.grid(row=2, column=5, sticky="nsew",
                                      padx=1, pady=1)
        self.add_tooltip_to_widget(self.bytes_in_data_entry)
        self.bytes_in_data_entry.configure(state='readonly')

        # update_bytes_in_col_index_entry
        self.bytes_in_col_index_label = \
            ttk.Label(self.column_tab,
                      text="Bytes in column index:",
                      name="bytes_in_col_index_label")
        self.bytes_in_col_index_label.grid(row=3, column=4, sticky="nsew",
                                           padx=1, pady=1)
        self.bytes_in_col_index_label.configure(style='Tabs.TLabel')
        self.bytes_in_col_index_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="bytes_in_col_index_entry")
        self.bytes_in_col_index_entry.grid(row=3, column=5, sticky="nsew",
                                           padx=1, pady=1)
        self.add_tooltip_to_widget(self.bytes_in_col_index_entry)
        self.bytes_in_col_index_entry.configure(state='readonly')

        # update_memusage_of_col_without_index_entry
        self.memusage_of_col_without_index_label = \
            ttk.Label(self.column_tab,
                      text="Memory usage of column w/o index:",
                      name="memusage_of_col_without_index_label")
        self.memusage_of_col_without_index_label.grid(row=4, column=4,
                                                      sticky="nsew",
                                                      padx=1, pady=1)
        self.memusage_of_col_without_index_label.configure(style='Tabs.TLabel')
        self.memusage_of_col_without_index_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="memusage_of_col_without_index_entry")
        self.memusage_of_col_without_index_entry.grid(row=4, column=5,
                                                      sticky="nsew",
                                                      padx=1, pady=1)
        self.add_tooltip_to_widget(self.memusage_of_col_without_index_entry)
        self.memusage_of_col_without_index_entry.configure(state='readonly')

        # update_memusage_of_col_with_index_entry
        self.memusage_of_col_with_index_label = \
            ttk.Label(self.column_tab,
                      text="Memory usage of column w/index:",
                      name="memusage_of_col_with_index_label")
        self.memusage_of_col_with_index_label.grid(row=5, column=4,
                                                   sticky="nsew",
                                                   padx=1, pady=1)
        self.memusage_of_col_with_index_label.configure(style='Tabs.TLabel')
        self.memusage_of_col_with_index_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="memusage_of_col_with_index_entry")
        self.memusage_of_col_with_index_entry.grid(row=5, column=5,
                                                   sticky="nsew",
                                                   padx=1, pady=1)
        self.add_tooltip_to_widget(self.memusage_of_col_with_index_entry)
        self.memusage_of_col_with_index_entry.configure(state='readonly')

        # update_deep_memusage_of_col_with_index_entry
        self.deep_memusage_of_col_with_index_label = \
            ttk.Label(self.column_tab,
                      text="Deep memory usage of column/index:",
                      name="deep_memusage_of_col_with_index_label")
        self.deep_memusage_of_col_with_index_label.grid(row=6, column=4,
                                                        sticky="nsew",
                                                        padx=1, pady=1)
        self.deep_memusage_of_col_with_index_label. \
            configure(style='Tabs.TLabel')
        self.deep_memusage_of_col_with_index_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="deep_memusage_of_col_with_index_entry")
        self.deep_memusage_of_col_with_index_entry.grid(row=6, column=5,
                                                        sticky="nsew",
                                                        padx=1, pady=1)
        self.add_tooltip_to_widget(self.deep_memusage_of_col_with_index_entry)
        self.deep_memusage_of_col_with_index_entry.configure(state='readonly')

        # update_getsizeof_col_entry
        self.getsizeof_col_label = \
            ttk.Label(self.column_tab,
                      text="System size of column:",
                      name="getsizeof_col_label")
        self.getsizeof_col_label.grid(row=7, column=4, sticky="nsew",
                                      padx=1, pady=1)
        self.getsizeof_col_label.configure(style='Tabs.TLabel')
        self.getsizeof_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="getsizeof_col_entry")
        self.getsizeof_col_entry.grid(row=7, column=5, sticky="nsew",
                                      padx=1, pady=1)
        self.add_tooltip_to_widget(self.getsizeof_col_entry)
        self.getsizeof_col_entry.configure(state='readonly')

        # statistics_section_label
        self.statistics_section_label = \
            ttk.Label(self.column_tab,
                      text="Statistics")
        self.statistics_section_label.grid(row=1, column=6,
                                           columnspan=9,
                                           sticky="nsew",
                                           padx=1, pady=1)
        self.statistics_section_label. \
            configure(style='Sections.TLabel')

        # mean_of_col_entry
        self.mean_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Mean:",
                      name="mean_of_col_label")
        self.mean_of_col_label.grid(row=2, column=6, sticky="nsew",
                                    padx=1, pady=1)
        self.mean_of_col_label.configure(style='Tabs.TLabel')
        self.mean_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="mean_of_col_entry")
        self.mean_of_col_entry.grid(row=2, column=7, sticky="nsew",
                                    columnspan=2, padx=1, pady=1)
        self.add_tooltip_to_widget(self.mean_of_col_entry)
        self.mean_of_col_entry.configure(state='readonly')

        # median_of_col_entry
        self.median_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Median:",
                      name="median_of_col_label")
        self.median_of_col_label.grid(row=3, column=6, sticky="nsew",
                                      padx=1, pady=1)
        self.median_of_col_label.configure(style='Tabs.TLabel')
        self.median_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="median_of_col_entry")
        self.median_of_col_entry.grid(row=3, column=7, sticky="nsew",
                                      columnspan=2, padx=1, pady=1)
        self.add_tooltip_to_widget(self.median_of_col_entry)
        self.median_of_col_entry.configure(state='readonly')

        # mode_of_col_text
        self.mode_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Mode:",
                      name="mode_of_col_label")
        self.mode_of_col_label.grid(row=4, column=6, sticky="nsew",
                                    padx=1, pady=1)
        self.mode_of_col_label.configure(style='Tabs.TLabel')
        self.mode_of_col_text = \
            tk.Text(self.column_tab,
                    background='white',
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=10,
                    height=2,
                    wrap='word',
                    name="mode_of_col_text")
        self.mode_of_col_text.grid(row=4, column=7, sticky="nsew",
                                   rowspan=3,
                                   padx=1, pady=1)
        self.add_tooltip_to_widget(self.mode_of_col_text)
        self.mode_of_col_scrollbar = \
            ttk.Scrollbar(self.column_tab,
                          orient=tk.VERTICAL,
                          command=self.mode_of_col_text.yview)
        self.mode_of_col_scrollbar.grid(row=4, column=8, rowspan=3,
                                        sticky='ns')
        self.mode_of_col_text.configure(yscrollcommand=self.
                                        mode_of_col_scrollbar.set)
        self.mode_of_col_text.configure(state='disabled')

        # std_dev_of_col_entry
        self.std_dev_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Std Dev:",
                      name="std_dev_of_col_label")
        self.std_dev_of_col_label.grid(row=7, column=6, sticky="nsew",
                                       padx=1, pady=1)
        self.std_dev_of_col_label.configure(style='Tabs.TLabel')
        self.std_dev_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="std_dev_of_col_entry")
        self.std_dev_of_col_entry.grid(row=7, column=7, sticky="nsew",
                                       columnspan=2, padx=1, pady=1)
        self.add_tooltip_to_widget(self.std_dev_of_col_entry)
        self.std_dev_of_col_entry.configure(state='readonly')

        # mean_abs_dev_of_col_entry
        self.mean_abs_dev_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Mean abs dev:",
                      name="mean_abs_dev_of_col_label")
        self.mean_abs_dev_of_col_label.grid(row=8, column=6, sticky="nsew",
                                            padx=1, pady=1)
        self.mean_abs_dev_of_col_label.configure(style='Tabs.TLabel')
        self.mean_abs_dev_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="mean_abs_dev_of_col_entry")
        self.mean_abs_dev_of_col_entry.grid(row=8, column=7, sticky="nsew",
                                            columnspan=2, padx=1, pady=1)
        self.add_tooltip_to_widget(self.mean_abs_dev_of_col_entry)
        self.mean_abs_dev_of_col_entry.configure(state='readonly')

        # std_err_mean_of_col_entry
        self.std_err_mean_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Std error of mean:",
                      name="std_err_mean_of_col_label")
        self.std_err_mean_of_col_label.grid(row=2, column=9, sticky="nsew",
                                            padx=1, pady=1)
        self.std_err_mean_of_col_label.configure(style='Tabs.TLabel')
        self.std_err_mean_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="std_err_mean_of_col_entry")
        self.std_err_mean_of_col_entry.grid(row=2, column=10, sticky="nsew",
                                            padx=1, pady=1)
        self.add_tooltip_to_widget(self.std_err_mean_of_col_entry)
        self.std_err_mean_of_col_entry.configure(state='readonly')

        # skewness_of_col_entry
        self.skewness_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Skewness:",
                      name="skewness_of_col_label")
        self.skewness_of_col_label.grid(row=3, column=9, sticky="nsew",
                                        padx=1, pady=1)
        self.skewness_of_col_label.configure(style='Tabs.TLabel')
        self.skewness_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="skewness_of_col_entry")
        self.skewness_of_col_entry.grid(row=3, column=10, sticky="nsew",
                                        padx=1, pady=1)
        self.add_tooltip_to_widget(self.skewness_of_col_entry)
        self.skewness_of_col_entry.configure(state='readonly')

        # kurtosis_of_col_entry
        self.kurtosis_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Kurtosis (Fisher's):",
                      name="kurtosis_of_col_label")
        self.kurtosis_of_col_label.grid(row=4, column=9, sticky="nsew",
                                        padx=1, pady=1)
        self.kurtosis_of_col_label.configure(style='Tabs.TLabel')
        self.kurtosis_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="kurtosis_of_col_entry")
        self.kurtosis_of_col_entry.grid(row=4, column=10, sticky="nsew",
                                        padx=1, pady=1)
        self.add_tooltip_to_widget(self.kurtosis_of_col_entry)
        self.kurtosis_of_col_entry.configure(state='readonly')

        # variance_of_col_entry
        self.variance_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Variance:",
                      name="variance_of_col_label")
        self.variance_of_col_label.grid(row=5, column=9, sticky="nsew",
                                        padx=1, pady=1)
        self.variance_of_col_label.configure(style='Tabs.TLabel')
        self.variance_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="variance_of_col_entry")
        self.variance_of_col_entry.grid(row=5, column=10, sticky="nsew",
                                        padx=1, pady=1)
        self.add_tooltip_to_widget(self.variance_of_col_entry)
        self.variance_of_col_entry.configure(state='readonly')

        # sum_of_col_entry
        self.sum_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Sum:",
                      name="sum_of_col_label")
        self.sum_of_col_label.grid(row=6, column=9, sticky="nsew",
                                   padx=1, pady=1)
        self.sum_of_col_label.configure(style='Tabs.TLabel')
        self.sum_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="sum_of_col_entry")
        self.sum_of_col_entry.grid(row=6, column=10, sticky="nsew",
                                   padx=1, pady=1)
        self.add_tooltip_to_widget(self.sum_of_col_entry)
        self.sum_of_col_entry.configure(state='readonly')

        # min_of_col_entry
        self.min_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Min:",
                      name="min_of_col_label")
        self.min_of_col_label.grid(row=2, column=11, sticky="nsew",
                                   padx=1, pady=1)
        self.min_of_col_label.configure(style='Tabs.TLabel')
        self.min_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="min_of_col_entry")
        self.min_of_col_entry.grid(row=2, column=12, sticky="nsew",
                                   padx=1, pady=1)
        self.add_tooltip_to_widget(self.min_of_col_entry)
        self.min_of_col_entry.configure(state='readonly')

        # min_index_of_col_entry
        self.min_index_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Min (index):",
                      name="min_index_of_col_label")
        self.min_index_of_col_label.grid(row=3, column=11, sticky="nsew",
                                         padx=1, pady=1)
        self.min_index_of_col_label.configure(style='Tabs.TLabel')
        self.min_index_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="min_index_of_col_entry")
        self.min_index_of_col_entry.grid(row=3, column=12, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.min_index_of_col_entry)
        self.min_index_of_col_entry.configure(state='readonly')

        # max_of_col_entry
        self.max_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Max:",
                      name="max_of_col_label")
        self.max_of_col_label.grid(row=4, column=11, sticky="nsew",
                                   padx=1, pady=1)
        self.max_of_col_label.configure(style='Tabs.TLabel')
        self.max_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="max_of_col_entry")
        self.max_of_col_entry.grid(row=4, column=12, sticky="nsew",
                                   padx=1, pady=1)
        self.add_tooltip_to_widget(self.max_of_col_entry)
        self.max_of_col_entry.configure(state='readonly')

        # max_index_of_col_entry
        self.max_index_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Max (index):",
                      name="max_index_of_col_label")
        self.max_index_of_col_label.grid(row=5, column=11, sticky="nsew",
                                         padx=1, pady=1)
        self.max_index_of_col_label.configure(style='Tabs.TLabel')
        self.max_index_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="max_index_of_col_entry")
        self.max_index_of_col_entry.grid(row=5, column=12, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.max_index_of_col_entry)
        self.max_index_of_col_entry.configure(state='readonly')

        # ptp_of_col_entry
        self.ptp_of_col_label = \
            ttk.Label(self.column_tab,
                      text="Peak-to-peak:",
                      name="ptp_of_col_label")
        self.ptp_of_col_label.grid(row=6, column=11, sticky="nsew",
                                   padx=1, pady=1)
        self.ptp_of_col_label.configure(style='Tabs.TLabel')
        self.ptp_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="ptp_of_col_entry")
        self.ptp_of_col_entry.grid(row=6, column=12, sticky="nsew",
                                   padx=1, pady=1)
        self.add_tooltip_to_widget(self.ptp_of_col_entry)
        self.ptp_of_col_entry.configure(state='readonly')

        # ------------------------------------------------------------

        # five_pct_of_col_entry
        self.five_pct_of_col_label = \
            ttk.Label(self.column_tab,
                      text="5%:",
                      name="five_pct_of_col_label")
        self.five_pct_of_col_label.grid(row=2, column=13, sticky="nsew",
                                        padx=1, pady=1)
        self.five_pct_of_col_label.configure(style='Tabs.TLabel')
        self.five_pct_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="five_pct_of_col_entry")
        self.five_pct_of_col_entry.grid(row=2, column=14, sticky="nsew",
                                        padx=1, pady=1)
        self.add_tooltip_to_widget(self.five_pct_of_col_entry)
        self.five_pct_of_col_entry.configure(state='readonly')

        # twenty_five_pct_of_col_entry
        self.twenty_five_pct_of_col_label = \
            ttk.Label(self.column_tab,
                      text="25%:",
                      name="twenty_five_pct_of_col_label")
        self.twenty_five_pct_of_col_label.grid(row=3, column=13, sticky="nsew",
                                               padx=1, pady=1)
        self.twenty_five_pct_of_col_label.configure(style='Tabs.TLabel')
        self.twenty_five_pct_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="twenty_five_pct_of_col_entry")
        self.twenty_five_pct_of_col_entry.grid(row=3, column=14, sticky="nsew",
                                               padx=1, pady=1)
        self.add_tooltip_to_widget(self.twenty_five_pct_of_col_entry)
        self.twenty_five_pct_of_col_entry.configure(state='readonly')

        # fifty_pct_of_col_entry
        self.fifty_pct_of_col_label = \
            ttk.Label(self.column_tab,
                      text="50%:",
                      name="fifty_pct_of_col_label")
        self.fifty_pct_of_col_label.grid(row=4, column=13, sticky="nsew",
                                         padx=1, pady=1)
        self.fifty_pct_of_col_label.configure(style='Tabs.TLabel')
        self.fifty_pct_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="fifty_pct_of_col_entry")
        self.fifty_pct_of_col_entry.grid(row=4, column=14, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.fifty_pct_of_col_entry)
        self.fifty_pct_of_col_entry.configure(state='readonly')

        # seventy_five_pct_of_col_entry
        self.seventy_five_pct_of_col_label = \
            ttk.Label(self.column_tab,
                      text="75%:",
                      name="seventy_five_pct_of_col_label")
        self.seventy_five_pct_of_col_label.grid(row=5, column=13,
                                                sticky="nsew", padx=1, pady=1)
        self.seventy_five_pct_of_col_label.configure(style='Tabs.TLabel')
        self.seventy_five_pct_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="seventy_five_pct_of_col_entry")
        self.seventy_five_pct_of_col_entry.grid(row=5, column=14,
                                                sticky="nsew", padx=1, pady=1)
        self.add_tooltip_to_widget(self.seventy_five_pct_of_col_entry)
        self.seventy_five_pct_of_col_entry.configure(state='readonly')

        # ninety_five_pct_of_col_entry
        self.ninety_five_pct_of_col_label = \
            ttk.Label(self.column_tab,
                      text="95%:",
                      name="ninety_five_pct_of_col_label")
        self.ninety_five_pct_of_col_label.grid(row=6, column=13,
                                               sticky="nsew", padx=1, pady=1)
        self.ninety_five_pct_of_col_label.configure(style='Tabs.TLabel')
        self.ninety_five_pct_of_col_entry = \
            tk.Entry(self.column_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=10,
                     name="ninety_five_pct_of_col_entry")
        self.ninety_five_pct_of_col_entry.grid(row=6, column=14,
                                               sticky="nsew", padx=1, pady=1)
        self.add_tooltip_to_widget(self.ninety_five_pct_of_col_entry)
        self.ninety_five_pct_of_col_entry.configure(state='readonly')

    def create_table_tab_widgets(self):

        # ordinal_mappings_button
        self.ordinal_mappings_button = \
            ttk.Button(self.table_tab,
                       text="Ordinal Mappings",
                       name="ordinal_mappings_button",
                       command=self.on_ordinal_mappings_button_clicked)
        self.ordinal_mappings_button.grid(row=0, column=0, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.ordinal_mappings_button)

        # table_tab_progressbar_label
        self.table_tab_progressbar_label = \
            ttk.Label(self.table_tab,
                      text="")
        self.table_tab_progressbar_label.grid(row=0, column=14,
                                              sticky="e",
                                              padx=1, pady=1)
        self.table_tab_progressbar_label.configure(style='Tabs.TLabel')
        self.table_tab_progressbar_label.grid_remove()
        self.table_tab_progressbar = ttk.Progressbar(self.table_tab,
                                                     orient=tk.HORIZONTAL,
                                                     length=50)
        self.table_tab_progressbar.grid(row=0, column=15, sticky="nsew",
                                        padx=1, pady=1)
        self.table_tab_progressbar.config(mode='indeterminate')
        self.table_tab_progressbar.grid_remove()

        # general_information_section_label
        self.general_information_section_label_tbl = \
            ttk.Label(self.table_tab,
                      text="General Information")
        self.general_information_section_label_tbl.grid(row=1, column=0,
                                                        columnspan=2,
                                                        sticky="nsew",
                                                        padx=1, pady=1)
        self.general_information_section_label_tbl. \
            configure(style='Sections.TLabel')

        # number_of_columns_entry
        self.number_of_columns_label = \
            ttk.Label(self.table_tab,
                      text="Number of columns:",
                      name="number_of_columns_label")
        self.number_of_columns_label.grid(row=2, column=0, sticky="nsew",
                                     padx=1, pady=1)
        self.number_of_columns_label.configure(style='Tabs.TLabel')
        self.number_of_columns_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="number_of_columns_entry")
        self.number_of_columns_entry.grid(row=2, column=1, sticky="nsew",
                                     padx=1, pady=1)
        #self.add_tooltip_to_widget(self.number_of_columns_entry)
        self.number_of_columns_entry.configure(state='readonly')

        # number_of_rows_entry
        self.number_of_rows_label = \
            ttk.Label(self.table_tab,
                      text="Number of rows:",
                      name="number_of_rows_label")
        self.number_of_rows_label.grid(row=3, column=0, sticky="nsew",
                                     padx=1, pady=1)
        self.number_of_rows_label.configure(style='Tabs.TLabel')
        self.number_of_rows_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="number_of_rows_entry")
        self.number_of_rows_entry.grid(row=3, column=1, sticky="nsew",
                                     padx=1, pady=1)
        #self.add_tooltip_to_widget(self.number_of_rows_entry)
        self.number_of_rows_entry.configure(state='readonly')

        # missing_values_in_df_entry
        self.missing_values_in_df_label = \
            ttk.Label(self.table_tab,
                      text="Missing in table:",
                      name="missing_values_in_df_label")
        self.missing_values_in_df_label.grid(row=4, column=0, sticky="nsew",
                                     padx=1, pady=1)
        self.missing_values_in_df_label.configure(style='Tabs.TLabel')
        self.missing_values_in_df_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=15,
                     name="missing_values_in_df_entry")
        self.missing_values_in_df_entry.grid(row=4, column=1, sticky="nsew",
                                     padx=1, pady=1)
        #self.add_tooltip_to_widget(self.missing_values_in_df_entry)
        self.missing_values_in_df_entry.configure(state='readonly')

        # memory_usage_section_label
        self.memory_usage_section_label_tbl = \
            ttk.Label(self.table_tab,
                      text="Memory Usage")
        self.memory_usage_section_label_tbl.grid(row=1, column=2,
                                             columnspan=2,
                                             sticky="nsew",
                                             padx=1, pady=1)
        self.memory_usage_section_label_tbl. \
            configure(style='Sections.TLabel')

        # bytes_in_df_entry
        self.bytes_in_df_label = \
            ttk.Label(self.table_tab,
                      text="Bytes in table:",
                      name="bytes_in_df_label")
        self.bytes_in_df_label.grid(row=2, column=2, sticky="nsew",
                                    padx=1, pady=1)
        self.bytes_in_df_label.configure(style='Tabs.TLabel')
        self.bytes_in_df_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="bytes_in_df_entry")
        self.bytes_in_df_entry.grid(row=2, column=3, sticky="nsew",
                                    padx=1, pady=1)
        self.add_tooltip_to_widget(self.bytes_in_df_entry)
        self.bytes_in_df_entry.configure(state='readonly')

        # bytes_in_df_index_entry
        self.bytes_in_df_index_label = \
            ttk.Label(self.table_tab,
                      text="Bytes in table index:",
                      name="bytes_in_df_index_label")
        self.bytes_in_df_index_label.grid(row=3, column=2, sticky="nsew",
                                          padx=1, pady=1)
        self.bytes_in_df_index_label.configure(style='Tabs.TLabel')
        self.bytes_in_df_index_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="bytes_in_df_index_entry")
        self.bytes_in_df_index_entry.grid(row=3, column=3, sticky="nsew",
                                          padx=1, pady=1)
        self.add_tooltip_to_widget(self.bytes_in_df_index_entry)
        self.bytes_in_df_index_entry.configure(state='readonly')

        # memusage_of_df_without_index_entry
        self.memusage_of_df_without_index_label = \
            ttk.Label(self.table_tab,
                      text="Memory usage of table w/o index:",
                      name="memusage_of_df_without_index_label")
        self.memusage_of_df_without_index_label.grid(row=4, column=2,
                                                     sticky="nsew",
                                                     padx=1, pady=1)
        self.memusage_of_df_without_index_label.configure(style='Tabs.TLabel')
        self.memusage_of_df_without_index_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="memusage_of_df_without_index_entry")
        self.memusage_of_df_without_index_entry.grid(row=4, column=3,
                                                     sticky="nsew",
                                                     padx=1, pady=1)
        self.add_tooltip_to_widget(self.memusage_of_df_without_index_entry)
        self.memusage_of_df_without_index_entry.configure(state='readonly')

        # memusage_of_df_with_index_entry
        self.memusage_of_df_with_index_label = \
            ttk.Label(self.table_tab,
                      text="Memory usage of table w/index:",
                      name="memusage_of_df_with_index_label")
        self.memusage_of_df_with_index_label.grid(row=5, column=2,
                                                  sticky="nsew",
                                                  padx=1, pady=1)
        self.memusage_of_df_with_index_label.configure(style='Tabs.TLabel')
        self.memusage_of_df_with_index_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="memusage_of_df_with_index_entry")
        self.memusage_of_df_with_index_entry.grid(row=5, column=3,
                                                  sticky="nsew",
                                                  padx=1, pady=1)
        self.add_tooltip_to_widget(self.memusage_of_df_with_index_entry)
        self.memusage_of_df_with_index_entry.configure(state='readonly')

        # deep_memusage_of_df_with_index_entry
        self.deep_memusage_of_df_with_index_label = \
            ttk.Label(self.table_tab,
                      text="Deep memory usage of table/index:",
                      name="deep_memusage_of_df_with_index_label")
        self.deep_memusage_of_df_with_index_label.grid(row=6, column=2,
                                                       sticky="nsew",
                                                       padx=1, pady=1)
        self.deep_memusage_of_df_with_index_label. \
            configure(style='Tabs.TLabel')
        self.deep_memusage_of_df_with_index_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="deep_memusage_of_df_with_index_entry")
        self.deep_memusage_of_df_with_index_entry.grid(row=6, column=3,
                                                       sticky="nsew",
                                                       padx=1, pady=1)
        self.add_tooltip_to_widget(self.deep_memusage_of_df_with_index_entry)
        self.deep_memusage_of_df_with_index_entry.configure(state='readonly')

        # getsizeof_df_entry
        self.getsizeof_df_label = \
            ttk.Label(self.table_tab,
                      text="System size of table:",
                      name="getsizeof_df_label")
        self.getsizeof_df_label.grid(row=7, column=2, sticky="nsew",
                                     padx=1, pady=1)
        self.getsizeof_df_label.configure(style='Tabs.TLabel')
        self.getsizeof_df_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground='white',
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="getsizeof_df_entry")
        self.getsizeof_df_entry.grid(row=7, column=3, sticky="nsew",
                                     padx=1, pady=1)
        self.add_tooltip_to_widget(self.getsizeof_df_entry)
        self.getsizeof_df_entry.configure(state='readonly')

        # model_information_section_label
        self.model_information_section_label = \
            ttk.Label(self.table_tab,
                      text="Model Information")
        self.model_information_section_label.grid(row=1, column=4,
                                             columnspan=16,
                                             sticky="nsew",
                                             padx=1, pady=1)
        self.model_information_section_label. \
            configure(style='Sections.TLabel')

        # class_col_entry
        self.class_col_label = \
            ttk.Label(self.table_tab,
                      text="Class label:",
                      name="class_col_label")
        self.class_col_label.grid(row=2, column=5, sticky="nsew",
                                  padx=1, pady=1)
        self.class_col_label.configure(style='Tabs.TLabel')
        self.class_col_entry = \
            tk.Entry(self.table_tab,
                     text="",
                     readonlybackground=CELL_CLR_CLS_LBL,
                     relief='flat',
                     highlightbackground='black',
                     highlightthickness=1,
                     highlightcolor='black',
                     width=13,
                     name="class_col_entry")
        self.class_col_entry.grid(row=2, column=6, sticky="nsew",
                                  columnspan=2, padx=1, pady=1)
        #self.add_tooltip_to_widget(self.class_col_entry)
        self.class_col_entry.configure(state='readonly')

        # not_in_model_cols_text
        self.not_in_model_cols_label = \
            ttk.Label(self.table_tab,
                      text="Not in",
                      name="not_in_model_cols_label")
        self.not_in_model_cols_label.grid(row=3, column=5, sticky="nsew",
                                          padx=1, pady=1)
        self.not_in_model_cols_label.configure(style='Tabs.TLabel')
        self.not_in_model_cols_label_addl = \
            ttk.Label(self.table_tab,
                      text="model:",
                      name="not_in_model_cols_label_addl")
        self.not_in_model_cols_label_addl.grid(row=4, column=5, sticky="nsew",
                                           padx=1, pady=1)
        self.not_in_model_cols_label_addl.configure(style='Tabs.TLabel')
        self.not_in_model_cols_text = \
            tk.Text(self.table_tab,
                    background='white',
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=13,
                    height=2,
                    wrap='word',
                    name="not_in_model_cols_text")
        self.not_in_model_cols_text.grid(row=3, column=6, sticky="nsew",
                                         rowspan=6,
                                         padx=1, pady=1)
        #self.add_tooltip_to_widget(self.not_in_model_cols_text)
        self.not_in_model_cols_scrollbar = \
            ttk.Scrollbar(self.table_tab,
                          orient=tk.VERTICAL,
                          command=self.not_in_model_cols_text.yview)
        self.not_in_model_cols_scrollbar.grid(row=3, column=7, rowspan=6,
                                              sticky='ns')
        self.not_in_model_cols_text.configure(yscrollcommand=self.
                                              not_in_model_cols_scrollbar.set)
        self.not_in_model_cols_text.configure(state='disabled')

        # numerical_features_text
        self.numerical_features_label = \
            ttk.Label(self.table_tab,
                      text="Numerical",
                      name="numerical_features_label")
        self.numerical_features_label.grid(row=2, column=8, sticky="nsew",
                                           padx=1, pady=1)
        self.numerical_features_label.configure(style='Tabs.TLabel')
        self.numerical_features_label_addl = \
            ttk.Label(self.table_tab,
                      text="features:",
                      name="numerical_features_label_addl")
        self.numerical_features_label_addl.grid(row=3, column=8, sticky="nsew",
                                           padx=1, pady=1)
        self.numerical_features_label_addl.configure(style='Tabs.TLabel')
        self.numerical_features_text = \
            tk.Text(self.table_tab,
                    background=CELL_CLR_MODEL_NUMERICAL,
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=13,
                    height=2,
                    wrap='word',
                    name="numerical_features_text")
        self.numerical_features_text.grid(row=2, column=9, sticky="nsew",
                                         rowspan=7,
                                         padx=1, pady=1)
        #self.add_tooltip_to_widget(self.numerical_features_text)
        self.numerical_features_scrollbar = \
            ttk.Scrollbar(self.table_tab,
                          orient=tk.VERTICAL,
                          command=self.numerical_features_text.yview)
        self.numerical_features_scrollbar.grid(row=2, column=10, rowspan=7,
                                               sticky='ns')
        self.numerical_features_text.configure(yscrollcommand=self.
                                               numerical_features_scrollbar.set)
        self.numerical_features_text.configure(state='disabled')

        # nominal_features_text
        self.nominal_features_label = \
            ttk.Label(self.table_tab,
                      text="Nominal",
                      name="nominal_features_label")
        self.nominal_features_label.grid(row=2, column=11, sticky="nsew",
                                         padx=1, pady=1)
        self.nominal_features_label.configure(style='Tabs.TLabel')
        self.nominal_features_label_addl = \
            ttk.Label(self.table_tab,
                      text="features:",
                      name="nominal_features_label_addl")
        self.nominal_features_label_addl.grid(row=3, column=11, sticky="nsew",
                                              padx=1, pady=1)
        self.nominal_features_label_addl.configure(style='Tabs.TLabel')
        self.nominal_features_text = \
            tk.Text(self.table_tab,
                    background=CELL_CLR_MODEL_NOMINAL,
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=13,
                    height=2,
                    wrap='word',
                    name="nominal_features_text")
        self.nominal_features_text.grid(row=2, column=12, sticky="nsew",
                                        rowspan=7,
                                        padx=1, pady=1)
        #self.add_tooltip_to_widget(self.nominal_features_text)
        self.nominal_features_text_scrollbar = \
            ttk.Scrollbar(self.table_tab,
                          orient=tk.VERTICAL,
                          command=self.nominal_features_text.yview)
        self.nominal_features_text_scrollbar.grid(row=2, column=13, rowspan=7,
                                                  sticky='ns')
        self.nominal_features_text.configure(yscrollcommand=self.
                                             nominal_features_text_scrollbar.set)
        self.nominal_features_text.configure(state='disabled')

        # ordinal_features_text
        self.ordinal_features_label = \
            ttk.Label(self.table_tab,
                      text="Ordinal",
                      name="ordinal_features_label")
        self.ordinal_features_label.grid(row=2, column=14, sticky="nsew",
                                         padx=1, pady=1)
        self.ordinal_features_label.configure(style='Tabs.TLabel')
        self.ordinal_features_label_addl = \
            ttk.Label(self.table_tab,
                      text="features:",
                      name="ordinal_features_label_addl")
        self.ordinal_features_label_addl.grid(row=3, column=14, sticky="nsew",
                                              padx=1, pady=1)
        self.ordinal_features_label_addl.configure(style='Tabs.TLabel')
        self.ordinal_features_text = \
            tk.Text(self.table_tab,
                    background=CELL_CLR_MODEL_ORDINAL,
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=13,
                    height=2,
                    wrap='word',
                    name="ordinal_features_text")
        self.ordinal_features_text.grid(row=2, column=15, sticky="nsew",
                                        rowspan=7,
                                        padx=1, pady=1)
        #self.add_tooltip_to_widget(self.ordinal_features_text)
        self.ordinal_features_text_scrollbar = \
            ttk.Scrollbar(self.table_tab,
                          orient=tk.VERTICAL,
                          command=self.ordinal_features_text.yview)
        self.ordinal_features_text_scrollbar.grid(row=2, column=16, rowspan=7,
                                                  sticky='ns')
        self.ordinal_features_text.configure(yscrollcommand=self.
                                             ordinal_features_text_scrollbar.set)
        self.ordinal_features_text.configure(state='disabled')

        # datetime_features_text
        self.datetime_features_label = \
            ttk.Label(self.table_tab,
                      text="Datetime",
                      name="datetime_features_label")
        self.datetime_features_label.grid(row=2, column=17, sticky="nsew",
                                         padx=1, pady=1)
        self.datetime_features_label.configure(style='Tabs.TLabel')
        self.datetime_features_label_addl = \
            ttk.Label(self.table_tab,
                      text="features:",
                      name="datetime_features_label_addl")
        self.datetime_features_label_addl.grid(row=3, column=17, sticky="nsew",
                                              padx=1, pady=1)
        self.datetime_features_label_addl.configure(style='Tabs.TLabel')
        self.datetime_features_text = \
            tk.Text(self.table_tab,
                    background=CELL_CLR_MODEL_DATETIME,
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=13,
                    height=2,
                    wrap='word',
                    name="datetime_features_text")
        self.datetime_features_text.grid(row=2, column=18, sticky="nsew",
                                        rowspan=3,
                                        padx=1, pady=1)
        #self.add_tooltip_to_widget(self.datetime_features_text)
        self.datetime_features_text_scrollbar = \
            ttk.Scrollbar(self.table_tab,
                          orient=tk.VERTICAL,
                          command=self.datetime_features_text.yview)
        self.datetime_features_text_scrollbar.grid(row=2, column=19, rowspan=3,
                                                  sticky='ns')
        self.datetime_features_text.configure(yscrollcommand=self.
                                             datetime_features_text_scrollbar.set)
        self.datetime_features_text.configure(state='disabled')

        # boolean_features_text
        self.boolean_features_label = \
            ttk.Label(self.table_tab,
                      text="Boolean",
                      name="boolean_features_label")
        self.boolean_features_label.grid(row=5, column=17, sticky="nsew",
                                         padx=1, pady=1)
        self.boolean_features_label.configure(style='Tabs.TLabel')
        self.boolean_features_label_addl = \
            ttk.Label(self.table_tab,
                      text="features:",
                      name="boolean_features_label_addl")
        self.boolean_features_label_addl.grid(row=6, column=17, sticky="nsew",
                                              padx=1, pady=1)
        self.boolean_features_label_addl.configure(style='Tabs.TLabel')
        self.boolean_features_text = \
            tk.Text(self.table_tab,
                    background=CELL_CLR_MODEL_BOOLEAN,
                    relief='flat',
                    font=('Arial', '9'),
                    highlightbackground='black',
                    highlightthickness=1,
                    highlightcolor='black',
                    width=13,
                    height=2,
                    wrap='word',
                    name="boolean_features_text")
        self.boolean_features_text.grid(row=5, column=18, sticky="nsew",
                                        rowspan=3,
                                        padx=1, pady=1)
        #self.add_tooltip_to_widget(self.boolean_features_text)
        self.boolean_features_text_scrollbar = \
            ttk.Scrollbar(self.table_tab,
                          orient=tk.VERTICAL,
                          command=self.boolean_features_text.yview)
        self.boolean_features_text_scrollbar.grid(row=5, column=19, rowspan=3,
                                                  sticky='ns')
        self.boolean_features_text.configure(yscrollcommand=self.
                                             boolean_features_text_scrollbar.set)
        self.boolean_features_text.configure(state='disabled')

    def create_insights_tab_widgets(self):

        # insights_tree
        self.insights_tree = \
            ttk.Treeview(self.insights_tab,
                         height=10,
                         columns=('Column Name','Column Index','Insight','Priority','Created On'),
                         selectmode = 'browse',
                         name="insights_tree")
        self.insights_tree.grid(row=0, column=0, sticky="nsew",
                                padx=1, pady=1)
        self.insights_tree.column('#0', width=200)
        self.insights_tree.column('#1', width=90)
        self.insights_tree.column('#2', width=830)
        self.insights_tree.column('#3', width=50)
        self.insights_tree.column('#4', width=175)
        self.insights_tree.column('#5', width=0)
        self.insights_tree.heading('#0', text='Column Name', anchor=tk.W)
        self.insights_tree.heading('#1', text='Column Index', anchor=tk.W)
        self.insights_tree.heading('#2', text='Insight', anchor=tk.W)
        self.insights_tree.heading('#3', text='Priority', anchor=tk.W)
        self.insights_tree.heading('#4', text='Created On', anchor=tk.W)

        self.insights_tree_scrollbar = \
            ttk.Scrollbar(self.insights_tab,
                          orient=tk.VERTICAL,
                          command=self.insights_tree.yview)
        self.insights_tree_scrollbar.grid(row=0, column=1, sticky='ns')
        self.insights_tree.configure(yscrollcommand=self.
                                     insights_tree_scrollbar.set)

    def create_transformations_log_tab_widgets(self):

        # transformations_log_tree
        self.transformations_log_tree = \
            ttk.Treeview(self.transformations_log_tab,
                         height=10,
                         columns=('Transformation','Session Name','Created On','Session ID','Trans ID', 'Replicate'),
                         selectmode = 'browse',
                         name="transformations_log_tree")
        self.transformations_log_tree.grid(row=0, column=0, sticky="nsew",
                                padx=1, pady=1)
        self.transformations_log_tree.column('#0', width=745)
        self.transformations_log_tree.column('#1', width=200)
        self.transformations_log_tree.column('#2', width=175)
        self.transformations_log_tree.column('#3', width=75)
        self.transformations_log_tree.column('#4', width=75)
        self.transformations_log_tree.column('#5', width=75)
        self.transformations_log_tree.column('#6', width=0)
        self.transformations_log_tree.heading('#0', text='Transformation', anchor=tk.W)
        self.transformations_log_tree.heading('#1', text='Session Name', anchor=tk.W)
        self.transformations_log_tree.heading('#2', text='Created On', anchor=tk.W)
        self.transformations_log_tree.heading('#3', text='Session ID', anchor=tk.W)
        self.transformations_log_tree.heading('#4', text='Trans ID', anchor=tk.W)
        self.transformations_log_tree.heading('#5', text='Replicate', anchor=tk.W)

        self.transformations_log_tree.tag_configure('odd_row', background='white')
        self.transformations_log_tree.tag_configure('even_row', background='grey90')

        self.transformations_log_tree.bind("<Double-Button-1>",
                               self.handle_transformations_log_double_click)

        self.transformations_log_tree_scrollbar = \
            ttk.Scrollbar(self.transformations_log_tab,
                          orient=tk.VERTICAL,
                          command=self.transformations_log_tree.yview)
        self.transformations_log_tree_scrollbar.grid(row=0, column=1, sticky='ns')
        self.transformations_log_tree.configure(yscrollcommand=self.
                                        transformations_log_tree_scrollbar.set)

    def on_describe_column_button_clicked(self):

        pass

    def on_analyze_column_button_clicked(self):

        self.update_column_tab_widgets()  # update for selected column

        insight = ColumnInsight(self.get_col_values(), self.column_tab_dict)
        insight.reset_insights()

        is_missing = insight.missing_values()
        if is_missing is False:
            insight.memory_usage()

        self.update_insights_tab_widgets(insight)  # update for selected column

    def on_toggle_model_availability_button_clicked(self):

        self.available_to_model = self. \
            get_model_option_x('available_to_model_dict')

        if self.available_to_model[self.selected_column] == 'No':
            self.available_to_model[self.selected_column] = 'Yes'
        else:
            self.available_to_model[self.selected_column] = 'No'

        self.update_model_option_available_to_model(self.available_to_model)
        self.update_column_tab_widgets()

    def on_toggle_class_label_status_button_clicked(self):

        self.class_label_status = self. \
            get_model_option_x('class_label_status_dict')

        if self.class_label_status[self.selected_column] == 'No':

            for i in range(len(self.table.model.df.columns)):
                self.class_label_status[i] = 'No'
            self.class_label_status[self.selected_column] = 'Yes'

        else:
            self.class_label_status[self.selected_column] = 'No'

        self.update_model_option_class_label_status(self.class_label_status)
        self.update_column_tab_widgets()

    def on_toggle_nominal_ordinal_button_clicked(self):

        self.nominal_ordinal = self.get_model_option_x('nominal_ordinal_dict')

        if self.nominal_ordinal[self.selected_column] == 'nominal':
            self.nominal_ordinal[self.selected_column] = 'ordinal'
        else:
            self.nominal_ordinal[self.selected_column] = 'nominal'

        self.update_model_option_nominal_ordinal(self.nominal_ordinal)
        self.update_column_tab_widgets()

    def on_ordinal_mappings_button_clicked(self):

        self.update_column_tab_widgets()  # update for selected column

        OrdinalMapping(self.root,
                       self.get_col_values(),
                       self.get_feature_type(self.get_col_values()))

    def update_column_tab_widgets(self):

        self.turn_progressbar_on(self.column_tab_progressbar,
                                 self.column_tab_progressbar_label)

        self.update_table_tab_widgets()

        self.column_tab_dict = {}

        # General Information --------------------------------
        self.update_selected_column_name_entry()
        self.update_selected_column_entry()
        self.update_feature_type_entry()
        self.update_available_to_model_entry()
        self.update_dtype_entry()
        self.update_dense_sparse_entry()
        self.update_non_null_count_entry()
        self.update_duplicates_in_col_entry()
        self.update_unique_values_in_col_entry()
        self.update_missing_values_in_col_entry()

        # Memory Usage ---------------------------------------
        self.update_bytes_in_data_entry()
        self.update_bytes_in_col_index_entry()
        self.update_memusage_of_col_without_index_entry()
        self.update_memusage_of_col_with_index_entry()
        self.update_deep_memusage_of_col_with_index_entry()
        self.update_getsizeof_col_entry()

        # Statistics -----------------------------------------
        self.update_mean_of_col_entry()
        self.update_median_of_col_entry()
        self.update_mode_of_col_text()
        self.update_std_dev_of_col_entry()
        self.update_mean_abs_dev_of_col_entry()
        self.update_std_err_mean_of_col_entry()
        self.update_skewness_of_col_entry()
        self.update_kurtosis_of_col_entry()
        self.update_variance_of_col_entry()
        self.update_sum_of_col_entry()
        self.update_min_of_col_entry()
        self.update_min_index_of_col_entry()
        self.update_max_of_col_entry()
        self.update_max_index_of_col_entry()
        self.update_ptp_of_col_entry()
        self.update_five_pct_of_col_entry()
        self.update_twenty_five_pct_of_col_entry()
        self.update_fifty_pct_of_col_entry()
        self.update_seventy_five_pct_of_col_entry()
        self.update_ninety_five_pct_of_col_entry()

        self.turn_progressbar_off(self.column_tab_progressbar,
                                  self.column_tab_progressbar_label)

    def update_table_tab_widgets(self):

        self.turn_progressbar_on(self.table_tab_progressbar,
                                 self.table_tab_progressbar_label)

        # General Information --------------------------------
        self.update_number_of_columns_entry()
        self.update_number_of_rows_entry()
        self.update_missing_values_in_df_entry()

        # Memory Usage ---------------------------------------
        self.update_bytes_in_df_entry()
        self.update_bytes_in_df_index_entry()
        self.update_memusage_of_df_without_index_entry()
        self.update_memusage_of_df_with_index_entry()
        self.update_deep_memusage_of_df_with_index_entry()
        self.update_getsizeof_df_entry()

        # Model Information --------------------------------
        self.update_class_col_entry()
        self.update_not_in_model_cols_text()
        self.update_numerical_features_text()
        self.update_nominal_features_text()
        self.update_ordinal_features_text()
        self.update_datetime_features_text()
        self.update_boolean_features_text()

        self.turn_progressbar_off(self.table_tab_progressbar,
                                  self.table_tab_progressbar_label)

    def update_insights_tab_widgets(self, cls):

        # remove current items from tree
        for item in self.insights_tree.get_children():
            self.insights_tree.delete(item)
        # add new items to tree
        for row in cls.get_insights():
            self.insights_tree.insert('', 0, text=row[2], values=(row[1],
                                      row[3], row[4], row[5]))

    def update_transformations_log_tab_widgets(self):

        trans = Transformation()

        for item in self.transformations_log_tree.get_children():
            self.transformations_log_tree.delete(item)

        self.transformations_log_list = [
            {
                'TransformationLogID': row[0],
                'SessionID': row[1],
                'SessionDesc': row[2],
                'ColumnIndex': row[3],
                'ColumnName': row[4],
                'TransformationID': row[5],
                'TransformationDesc': row[6],
                'DateCreated': row[7],
                'TransformationLogDesc': row[8],
                'IsReplicate': row[9],
                'Option1': row[10],
                'Option2': row[11],
                'Option3': row[12]
            }
            for row in trans.get_transformations_by_session(self.session_id)]

        for i, row in enumerate(trans.get_transformations_by_session(self.session_id)):

            if is_even(i):
                self.transformations_log_tree.insert('', 0, text=row[8],
                                                     values=(row[2],
                                                     row[7], row[1], row[0],
                                                     row[9]),
                                                     tags=('even_row',))
            else:
                self.transformations_log_tree.insert('', 0, text=row[8],
                                                     values=(row[2],
                                                     row[7], row[1], row[0],
                                                     row[9]),
                                                     tags=('odd_row',))

    # BEGIN COLUMN TAB WIDGETS #

    # General Information --------------------------------
    def update_selected_column_name_entry(self):

        string = str(self.selected_column_name)
        self.update_disabled_widget(self.selected_column_name_entry, string)
        self.update_column_tab_dict(self.selected_column_name_entry, string)

    def update_selected_column_entry(self):

        string = str(self.selected_column)
        self.update_disabled_widget(self.selected_column_entry, string)
        self.update_column_tab_dict(self.selected_column_entry, string)

    def update_feature_type_entry(self):

        string = self.get_feature_type(self.get_col_values())
        self.update_disabled_widget(self.feature_type_entry, string)
        self.update_column_tab_dict(self.feature_type_entry, string)

    def update_available_to_model_entry(self):

        self.update_model_columns()

        self.model_columns = self. \
            get_model_option_x('model_columns_dict')

        if self.model_columns[self.selected_column] == 'No':
            string = 'No'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_NORMAL)
        elif self.model_columns[self.selected_column] == 'Class (numerical)':
            string = 'Class (numerical)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_CLS_LBL)
        elif self.model_columns[self.selected_column] == 'Yes (numerical)':
            string = 'Yes (numerical)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_MODEL_NUMERICAL)
        elif self.model_columns[self.selected_column] == 'Class (datetime)':
            string = 'Class (datetime)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_CLS_LBL)
        elif self.model_columns[self.selected_column] == 'Yes (datetime)':
            string = 'Yes (datetime)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_MODEL_DATETIME)
        elif self.model_columns[self.selected_column] == 'Class (boolean)':
            string = 'Class (boolean)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_CLS_LBL)
        elif self.model_columns[self.selected_column] == 'Yes (boolean)':
            string = 'Yes (boolean)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_MODEL_BOOLEAN)
        elif self.model_columns[self.selected_column] == 'Class (nominal)':
            string = 'Class (nominal)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_CLS_LBL)
        elif self.model_columns[self.selected_column] == 'Yes (nominal)':
            string = 'Yes (nominal)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_MODEL_NOMINAL)
        elif self.model_columns[self.selected_column] == 'Yes (ordinal)':
            string = 'Yes (ordinal)'
            self.available_to_model_entry. \
                configure(readonlybackground=CELL_CLR_MODEL_ORDINAL)

        self.update_disabled_widget(self.available_to_model_entry, string)
        self.update_column_tab_dict(self.available_to_model_entry, string)

    def update_dtype_entry(self):

        if self.get_col_values().dtype.name == "category":
            string = "category"
        else:
            string = np.dtype(self.get_col_values())
        self.update_disabled_widget(self.dtype_entry, string)
        self.update_column_tab_dict(self.dtype_entry, string)

    def update_dense_sparse_entry(self):

        string = self.get_col_values().ftype.split(":")[-1]
        self.update_disabled_widget(self.dense_sparse_entry, string)
        self.update_column_tab_dict(self.dense_sparse_entry, string)

    def update_non_null_count_entry(self):

        string = "{0:.0f}".format(self.get_col_values().count())
        self.update_disabled_widget(self.non_null_count_entry, string)
        self.update_column_tab_dict(self.non_null_count_entry, string)

    def update_duplicates_in_col_entry(self):

        if len(self.get_col_values().index) == 0:  # if column is empty
            string = "N/A"
        else:
            pct = "{0:.2f}".format(100 * (self.get_col_values()[self.
                                   get_col_values().notnull()].
                                   duplicated(False).sum() /
                                   len(self.get_col_values().index)))
            string = str(self.get_col_values()[self.get_col_values().
                         notnull()].duplicated(False).
                         sum()) + " (" + str(pct) + "%)"
        self.update_disabled_widget(self.duplicates_in_col_entry, string)
        self.update_column_tab_dict(self.duplicates_in_col_entry, string)

    def update_unique_values_in_col_entry(self):

        if len(self.get_col_values().index) == 0:  # if column is empty
            string = "N/A"
        else:
            pct = "{0:.2f}".format(100 * (self.get_col_values().nunique() /
                                   len(self.get_col_values().index)))
            string = str(self.get_col_values().
                         nunique()) + " (" + str(pct) + "%)"
        self.update_disabled_widget(self.unique_values_in_col_entry, string)
        self.update_column_tab_dict(self.unique_values_in_col_entry, string)

    def update_missing_values_in_col_entry(self):

        if len(self.get_col_values().index) == 0:  # if column is empty
            string = "N/A"
        else:
            pct = "{0:.2f}".format(100 * (self.get_col_values().
                                   isnull().sum() /
                                   len(self.get_col_values().index)))
            string = str(self.get_col_values().
                         isnull().sum()) + " (" + str(pct) + "%)"
        self.update_disabled_widget(self.missing_values_in_col_entry, string)
        self.update_column_tab_dict(self.missing_values_in_col_entry, string)

    # Memory Usage ---------------------------------------
    def update_bytes_in_data_entry(self):

        string = str(self.get_col_values().nbytes)
        self.update_disabled_widget(self.bytes_in_data_entry, string)
        self.update_column_tab_dict(self.bytes_in_data_entry, string)

    def update_bytes_in_col_index_entry(self):

        string = str(self.get_col_values().index.nbytes)
        self.update_disabled_widget(self.bytes_in_col_index_entry, string)
        self.update_column_tab_dict(self.bytes_in_col_index_entry, string)

    def update_memusage_of_col_without_index_entry(self):

        string = str(self.get_col_values().
                     memory_usage(index=False, deep=False))
        self.update_disabled_widget(self.memusage_of_col_without_index_entry,
                                    string)
        self.update_column_tab_dict(self.memusage_of_col_without_index_entry,
                                    string)

    def update_memusage_of_col_with_index_entry(self):

        string = str(self.get_col_values().
                     memory_usage(index=True, deep=False))
        self.update_disabled_widget(self.memusage_of_col_with_index_entry,
                                    string)
        self.update_column_tab_dict(self.memusage_of_col_with_index_entry,
                                    string)

    def update_deep_memusage_of_col_with_index_entry(self):

        string = str(self.get_col_values().memory_usage(index=True, deep=True))
        self.update_disabled_widget(self.deep_memusage_of_col_with_index_entry,
                                    string)
        self.update_column_tab_dict(self.deep_memusage_of_col_with_index_entry,
                                    string)

    def update_getsizeof_col_entry(self):

        import sys

        string = str(sys.getsizeof(self.get_col_values()))
        self.update_disabled_widget(self.getsizeof_col_entry, string)
        self.update_column_tab_dict(self.getsizeof_col_entry, string)

    # Statistics -----------------------------------------
    def update_mean_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().mean())
        else:
            string = "N/A"
        self.update_disabled_widget(self.mean_of_col_entry, string)
        self.update_column_tab_dict(self.mean_of_col_entry, string)

    def update_median_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().median())
        else:
            string = "N/A"
        self.update_disabled_widget(self.median_of_col_entry, string)
        self.update_column_tab_dict(self.median_of_col_entry, string)

    def update_mode_of_col_text(self):

        string = ""
        if self.get_col_values().mode().count() > 1:

            for i, row in self.get_col_values().mode().iteritems():
                string = string + str(self.get_col_values().mode()[i]) + '\n'
        else:
            if self.get_col_values().mode().count() == 0:  # if column is empty
                string = "N/A"
            else:
                string = str(self.get_col_values().mode()[0])
        self.update_disabled_widget(self.mode_of_col_text, string)
        self.update_column_tab_dict(self.mode_of_col_text, string)

    def update_std_dev_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().std())
        else:
            string = "N/A"
        self.update_disabled_widget(self.std_dev_of_col_entry, string)
        self.update_column_tab_dict(self.std_dev_of_col_entry, string)

    def update_mean_abs_dev_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().mad())
        else:
            string = "N/A"
        self.update_disabled_widget(self.mean_abs_dev_of_col_entry, string)
        self.update_column_tab_dict(self.mean_abs_dev_of_col_entry, string)

    def update_std_err_mean_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().sem())
        else:
            string = "N/A"
        self.update_disabled_widget(self.std_err_mean_of_col_entry, string)
        self.update_column_tab_dict(self.std_err_mean_of_col_entry, string)

    def update_skewness_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().skew())
        else:
            string = "N/A"
        self.update_disabled_widget(self.skewness_of_col_entry, string)
        self.update_column_tab_dict(self.skewness_of_col_entry, string)

    def update_kurtosis_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().kurt())
        else:
            string = "N/A"
        self.update_disabled_widget(self.kurtosis_of_col_entry, string)
        self.update_column_tab_dict(self.kurtosis_of_col_entry, string)

    def update_variance_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().var())
        else:
            string = "N/A"
        self.update_disabled_widget(self.variance_of_col_entry, string)
        self.update_column_tab_dict(self.variance_of_col_entry, string)

    def update_sum_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.5f}".format(self.get_col_values().sum())
        else:
            string = "N/A"
        self.update_disabled_widget(self.sum_of_col_entry, string)
        self.update_column_tab_dict(self.sum_of_col_entry, string)

    def update_min_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().min())
        else:
            string = "N/A"
        self.update_disabled_widget(self.min_of_col_entry, string)
        self.update_column_tab_dict(self.min_of_col_entry, string)

    def update_min_index_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.0f}".format(self.get_col_values().argmin())
        else:
            string = "N/A"
        self.update_disabled_widget(self.min_index_of_col_entry, string)
        self.update_column_tab_dict(self.min_index_of_col_entry, string)

    def update_max_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().max())
        else:
            string = "N/A"
        self.update_disabled_widget(self.max_of_col_entry, string)
        self.update_column_tab_dict(self.max_of_col_entry, string)

    def update_max_index_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.0f}".format(self.get_col_values().argmax())
        else:
            string = "N/A"
        self.update_disabled_widget(self.max_index_of_col_entry, string)
        self.update_column_tab_dict(self.max_index_of_col_entry, string)

    def update_ptp_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().ptp())
        else:
            string = "N/A"
        self.update_disabled_widget(self.ptp_of_col_entry, string)
        self.update_column_tab_dict(self.ptp_of_col_entry, string)

    def update_five_pct_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().quantile(.05))
        else:
            string = "N/A"
        self.update_disabled_widget(self.five_pct_of_col_entry, string)
        self.update_column_tab_dict(self.five_pct_of_col_entry, string)

    def update_twenty_five_pct_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().quantile(.25))
        else:
            string = "N/A"
        self.update_disabled_widget(self.twenty_five_pct_of_col_entry, string)
        self.update_column_tab_dict(self.twenty_five_pct_of_col_entry, string)

    def update_fifty_pct_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().quantile(.5))
        else:
            string = "N/A"
        self.update_disabled_widget(self.fifty_pct_of_col_entry, string)
        self.update_column_tab_dict(self.fifty_pct_of_col_entry, string)

    def update_seventy_five_pct_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().quantile(.75))
        else:
            string = "N/A"
        self.update_disabled_widget(self.seventy_five_pct_of_col_entry, string)
        self.update_column_tab_dict(self.seventy_five_pct_of_col_entry, string)

    def update_ninety_five_pct_of_col_entry(self):

        if self.get_feature_type(self.get_col_values()) == "numerical":
            string = "{0:.1f}".format(self.get_col_values().quantile(.95))
        else:
            string = "N/A"
        self.update_disabled_widget(self.ninety_five_pct_of_col_entry, string)
        self.update_column_tab_dict(self.ninety_five_pct_of_col_entry, string)

    # END COLUMN TAB WIDGETS #

    # BEGIN TABLE TAB WIDGETS #

    # General Information --------------------------------
    def update_number_of_columns_entry(self):

        string = len(self.table.model.df.columns)
        self.update_disabled_widget(self.number_of_columns_entry, string)

    def update_number_of_rows_entry(self):

        string = len(self.table.model.df.index)
        self.update_disabled_widget(self.number_of_rows_entry, string)

    def update_missing_values_in_df_entry(self):

        if len(self.table.model.df.index) == 0:
            string = "N/A"
        else:
            pct = "{0:.2f}".format(100 * (self.table.model.df.
                                   isnull().sum().sum()) /
                                   (len(self.table.model.df.index) *
                                    len(self.table.model.df.columns)))
            string = str(self.table.model.df.
                         isnull().sum().sum()) + " (" + str(pct) + "%)"
        self.update_disabled_widget(self.missing_values_in_df_entry, string)

    # Memory Usage ---------------------------------------
    def update_bytes_in_df_entry(self):

        total = 0
        for index, column in enumerate(self.table.model.df.columns):
            total += self.get_col_values_by_col(index).nbytes

        string = str(total)
        self.update_disabled_widget(self.bytes_in_df_entry, string)

    def update_bytes_in_df_index_entry(self):

        total = 0
        for index, column in enumerate(self.table.model.df.columns):
            total += self.get_col_values_by_col(index).index.nbytes

        string = str(total)
        self.update_disabled_widget(self.bytes_in_df_index_entry, string)

    def update_memusage_of_df_without_index_entry(self):

        total = 0
        for index, column in enumerate(self.table.model.df.columns):
            total += self.get_col_values_by_col(index). \
                memory_usage(index=False, deep=False)

        string = str(total)
        self.update_disabled_widget(self.memusage_of_df_without_index_entry,
                                    string)

    def update_memusage_of_df_with_index_entry(self):

        total = 0
        for index, column in enumerate(self.table.model.df.columns):
            total += self.get_col_values_by_col(index). \
                memory_usage(index=True, deep=False)

        string = str(total)
        self.update_disabled_widget(self.memusage_of_df_with_index_entry,
                                    string)

    def update_deep_memusage_of_df_with_index_entry(self):

        total = 0
        for index, column in enumerate(self.table.model.df.columns):
            total += self.get_col_values_by_col(index). \
                memory_usage(index=True, deep=True)

        string = str(total)
        self.update_disabled_widget(self.deep_memusage_of_df_with_index_entry,
                                    string)

    def update_getsizeof_df_entry(self):

        import sys

        total = 0
        for index, column in enumerate(self.table.model.df.columns):
            total += sys.getsizeof(self.get_col_values_by_col(index))

        string = str(total)
        self.update_disabled_widget(self.getsizeof_df_entry, string)

    # Model Information --------------------------------

    def update_class_col_entry(self):

        lst = []
        for k, v in self.model_columns.items():

            if (v == "Class (numerical)") or \
               (v == "Class (datetime)") or \
               (v == "Class (boolean)") or \
               (v == "Class (nominal)"):

                lst.append([self.get_col_name_by_index(k)])

        if len(lst) > 0:
            string = lst
        else:
            string = "N/A"

        self.update_disabled_widget(self.class_col_entry, string)

    def update_not_in_model_cols_text(self):

        string = self.get_model_column_names_by_feature("No")
        self.update_disabled_widget(self.not_in_model_cols_text, string)

    def update_numerical_features_text(self):

        string = self.get_model_column_names_by_feature("Yes (numerical)")
        self.update_disabled_widget(self.numerical_features_text, string)

    def update_nominal_features_text(self):

        string = self.get_model_column_names_by_feature("Yes (nominal)")
        self.update_disabled_widget(self.nominal_features_text, string)

    def update_ordinal_features_text(self):

        string = self.get_model_column_names_by_feature("Yes (ordinal)")
        self.update_disabled_widget(self.ordinal_features_text, string)

    def update_datetime_features_text(self):

        string = self.get_model_column_names_by_feature("Yes (datetime)")
        self.update_disabled_widget(self.datetime_features_text, string)

    def update_boolean_features_text(self):

        string = self.get_model_column_names_by_feature("Yes (boolean)")
        self.update_disabled_widget(self.boolean_features_text, string)

    # END TABLE TAB WIDGETS #

    def on_select_dataset_menu_clicked(self):

        Dataset(self.root, self.datasets_path)

    def get_selected_dataset(self):

        qry = 'SELECT SelectedDataset FROM Datasets'
        cursor = exec_qry(qry)

        for row in cursor:
            return row[0]

    def load_dataset(self, obj):

        write_to_console('\nLoading %s Dataset...' % (obj))
        df = pd.read_csv("./datasets/" + str(obj))
        write_to_console('\nLoading complete.')
        return df

    def on_load_dataset_menu_clicked(self):

        self.clean_top_area_items()

        # Load iris Dataset
        self.selected_dataset = self.get_selected_dataset()
        if self.selected_dataset == '':
            messagebox.showwarning("Warning", "No dataset selected.")
            return
        else:
            self.loaded_df = self.load_dataset(self.selected_dataset)

        # Load eda Dataset
        self.table = pt = Table(self.dataframe_area,
                                dataframe=self.loaded_df,
                                callback=self.update_from_pandastable,
                                showtoolbar=True,
                                showstatusbar=True,
                                absolute_path=self.absolute_path)
        pt.show()

        session = Session()
        self.session_id = session.add_session(self.selected_dataset)

        self.selected_column = pt.currentcol
        self.selected_column_name = pt.currentcol_name

        self.init_available_to_model_dict()
        self.init_class_label_status_dict()
        self.init_nominal_ordinal_dict()
        self.init_model_columns_dict()

        self.create_top_area_items()

        self.update_column_tab_widgets()

        self.init_model_overrides()

    def update_from_pandastable(self, selected_column, selected_column_name,
                                option):

        self.selected_column = selected_column
        self.selected_column_name = selected_column_name

        if option == 'describe_column':
            self.describe_column()

    def init_available_to_model_dict(self):

        self.available_to_model.clear()
        for i in range(len(self.table.model.df.columns)):
            self.available_to_model[i] = 'No'
        self.update_model_option_available_to_model(self.available_to_model)

    def init_class_label_status_dict(self):

        self.class_label_status.clear()
        for i in range(len(self.table.model.df.columns)):
            self.class_label_status[i] = 'No'
        self.update_model_option_class_label_status(self.class_label_status)

    def init_nominal_ordinal_dict(self):

        self.nominal_ordinal.clear()
        for i in range(len(self.table.model.df.columns)):
            self.nominal_ordinal[i] = 'nominal'
        self.update_model_option_nominal_ordinal(self.nominal_ordinal)

    def init_model_columns_dict(self):

        self.model_columns.clear()
        for i in range(len(self.table.model.df.columns)):
            self.model_columns[i] = 'No'
        self.update_model_option_model_columns(self.model_columns)

    def get_feature_type(self, col_values):

        if col_values.dtype.name == "category":
            return "categorical/factor"
            #column_type = "category"
        elif np.dtype(col_values) == "object":
            return "nominal or ordinal"
            #column_type = "string"
        elif np.dtype(col_values) == "bool":
            return "boolean"
            #column_type = "boolean"
        elif np.dtype(col_values) == "float16":
            return "numerical"
            #column_type = "float"
        elif np.dtype(col_values) == "float32":
            return "numerical"
            #column_type = "float"
        elif np.dtype(col_values) == "float64":
            return "numerical"
            #column_type = "float"
        elif np.dtype(col_values) == "int8":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "int16":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "int32":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "int64":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "uint8":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "uint16":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "uint32":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "uint64":
            return "numerical"
            #column_type = "int"
        elif np.dtype(col_values) == "complex64":
            return "complex (numerical)"
            #column_type = "complex"
        elif np.dtype(col_values) == "complex128":
            return "complex (numerical)"
            #column_type = "complex"
        elif np.dtype(col_values) == "datetime64[ns]":
            return "datetime"
            #column_type = "datetime"
        else:
            try:
                return "unknown"
                print(col_values.dtype.name)
                print(np.dtype(col_values))
            except:
                pass
                # column_type = "unknown"

    def get_values_from_selected_column(self):

        return self.table.model.df.iloc[:, self.selected_column]

    def get_values_from_any_column(self, index):

        return self.table.model.df.iloc[:, index]

    def get_col_values(self):

        return self.get_values_from_selected_column()

    def get_col_values_by_col(self, index):

        return self.get_values_from_any_column(index)

    def get_col_name_by_index(self, index):

        return self.table.model.df.columns[index]

    def add_tooltip_to_widget(self, widget):

        widget_name = str(widget).split(".")[-1]
        for row in self.read_tooltip_from_db(table_name='Tooltips',
                                             item_name=widget_name,
                                             language=g.localized_lang):
            tooltip_text = row[0]
        self.tooltip.bind(widget, tooltip_text)

    def read_tooltip_from_db(self, table_name=None, item_name=None, language=1):

        where_column1 = 'WidgetName'
        sel_column_1 = 'TooltipText'
        lang_column1 = 'LanguageID'

        qry = "SELECT {col} FROM {tbl} WHERE {cond}=? AND {lang}=?".\
                format(col=sel_column_1,
                       tbl=table_name,
                       cond=where_column1,
                       lang=lang_column1)
        parameters = (item_name, language)

        return exec_qry(qry, parameters)

    def set_x_and_y_old(self):

        self.y = EncodeClassLabel(self.loaded_df['4'].values)
        print(type(self.y))
        print(self.y)

        self.x = self.loaded_df.iloc[:, [2, 3]].values
        print(type(self.x))
        print(self.x)

    def set_model_classlabel(self):

        if self.has_model_classlabel():
            self.y = self.table.model.df[self.get_model_classlabel_index()].values
        else:
            self.y = np.empty(0)

        print(type(self.y))
        print(self.y)

    def set_model_features(self):

        self.x = self.table.model.df.iloc[:, self.get_features_from_model_columns()].values
        print(type(self.x))
        print(self.x)

    def on_model_dataset_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.set_model_classlabel()
        self.set_model_features()

        Model(self.root, self.x, self.y)

    def on_run_dataset_menu_old_clicked(self):

        if not hasattr(self, 'loaded_df'):
            messagebox.showwarning("Warning", "No dataset selected.")
            return

        self.set_x_and_y_old()

        # ******************* Preprocess ****************************

        # Splitting data into training and test data
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
             self.x, self.y, test_size=0.3, random_state=0)

        # Standardize features
        self.x_train_std, self.x_test_std = Scale(self.x_train, self.x_test, t="std")

        # Combine data for plotting
        self.x_combined_std = np.vstack((self.x_train_std, self.x_test_std))
        self.x_combined = np.vstack((self.x_train, self.x_test))
        self.y_combined = np.hstack((self.y_train, self.y_test))

        # Whether or not need to plot decision regions
        g.decision_regions = False

        # ******************* Learning ****************************
        # Fit with Perceptron
        Automator("ClfPerceptron",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  n_iter=40,
                  eta0=0.1,
                  random_state=0)

        # Fit with AdalineGD
        Automator("ClfAdalineGD",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  n_iter=15,
                  eta0=0.01)

        # Fit with AdalineSGD
        Automator("ClfAdalineSGD",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  n_iter=15,
                  eta0=0.01,
                  random_state=1)

        # Fit with Logistic Regression

        # Tunning Bias-variance trade-off:
        # L2 regularization via C parameter

        # Feature selection
        # L1 regularization via penalty paramenter
        # default: ‘l2’

        Automator("ClfLogisticRegression",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  C=1000.0,
                  penalty='l1',
                  random_state=0)

        # Fit with Linear Support Vector Machines
        Automator("ClfLinearSVM",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  kernel='linear',
                  C=1.0,
                  random_state=0)

        # Fit with Kernel Support Vector Machines
        Automator("ClfKernelSVM",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  kernel='rbf',
                  gamma=0.2,
                  C=1.0,
                  random_state=0)

        # Fit with Decision Tree
        Automator("ClfDecisionTree",
                  self.x_train,
                  self.x_test,
                  self.y_train,
                  self.y_test,
                  self.x_combined,
                  self.y_combined,
                  criterion='entropy',
                  max_depth=3,
                  random_state=0)

        # Fit with Random Forest
        Automator("ClfRandomForest",
                  self.x_train,
                  self.x_test,
                  self.y_train,
                  self.y_test,
                  self.x_combined,
                  self.y_combined,
                  criterion='entropy',
                  n_estimators=10,
                  random_state=1)

        # Fit with K-nearest Neighbors
        # TODO: need to add feature selection via SBS
        Automator("ClfKNN",
                  self.x_train_std,
                  self.x_test_std,
                  self.y_train,
                  self.y_test,
                  self.x_combined_std,
                  self.y_combined,
                  n_neighbors=5,
                  p=2,
                  metric='minkowski')

    def on_toggle_selected_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        try:
            self.transformations_log_tree. \
                item(self.transformations_log_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No transformation selected.")
            return

        self.toggle_selected_transformation()

    def on_flag_all_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.tabs.select(3)
        self.update_transformations_log_tab_widgets()

        if len(self.transformations_log_list) == 0:
            messagebox.showwarning("Warning", "No transformations available.")
            return

        self.flag_all_transformations()

    def on_unflag_all_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.tabs.select(3)
        self.update_transformations_log_tab_widgets()

        if len(self.transformations_log_list) == 0:
            messagebox.showwarning("Warning", "No transformations available.")
            return

        self.unflag_all_transformations()

    def on_replicate_selected_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        try:
            self.transformations_log_tree. \
                item(self.transformations_log_tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Warning", "No transformation selected.")
            return

        self.replicate_selected_transformation()

    def on_replicate_all_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.tabs.select(3)
        self.update_transformations_log_tab_widgets()

        if len(self.transformations_log_list) == 0:
            messagebox.showwarning("Warning", "No transformations available.")
            return

        self.replicate_all_transformations()

    def on_load_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.tabs.select(3)
        self.update_transformations_log_tab_widgets()

        if len(self.transformations_log_list) != 0:
            if messagebox.askokcancel("Warning", "Current transformations will be deleted. Do you want to proceed?"):
                self.load_transformations()
        else:
            self.load_transformations()
        return

    def on_save_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.tabs.select(3)
        self.update_transformations_log_tab_widgets()

        if len(self.transformations_log_list) == 0:
            messagebox.showwarning("Warning", "No transformations available.")
            return

        self.save_transformations()

    def on_clear_all_transformations_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.tabs.select(3)
        self.update_transformations_log_tab_widgets()

        if len(self.transformations_log_list) != 0:
            if messagebox.askokcancel("Warning", "Current transformations will be deleted. Do you want to proceed?"):
                self.clear_all_transformations()
        else:
            self.clear_all_transformations()
        return

    def on_load_model_columns_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        if (self.has_model_classlabel() or
                len(self.get_features_from_model_columns()) != 0):
            if messagebox.askokcancel("Warning", "Current model columns selection will be deleted. Do you want to proceed?"):
                self.load_model_columns()
        else:
            self.load_model_columns()
        return

    def on_save_model_columns_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        if (self.has_model_classlabel() == False and
                len(self.get_features_from_model_columns()) == 0):
            messagebox.showwarning("Warning", "No model columns selection available.")
            return

        self.save_model_columns()

    def on_ordinal_mappings_menu_clicked(self):

        if self.dataset_does_not_exist():
            return

        self.update_column_tab_widgets()  # update for selected column

        OrdinalMapping(self.root,
                       self.get_col_values(),
                       self.get_feature_type(self.get_col_values()))

    def on_classifiers_menu_clicked(self):

        ClassifiersCRUD(self.root)

    def on_default_classifiers_menu_clicked(self):

        ClassifiersModelDefaults(self.root)

    def on_default_train_and_test_split_menu_clicked(self):

        TrainAndTestSplitDefaults(self.root)

    def on_default_scaling_menu_clicked(self):

        ScalingDefaults(self.root)

    def dataset_does_not_exist(self):

        if not hasattr(self, 'table'):
            messagebox.showwarning("Warning", "No dataset selected.")
            return True
        return False

    def turn_progressbar_on(self, progressbar, progressbar_label):

        progressbar.grid()
        progressbar.start()

        progressbar_label.grid()
        progressbar_label.config(text="Working...")

    def turn_progressbar_off(self, progressbar, progressbar_label):

        progressbar.stop()
        progressbar.grid_remove()

        progressbar_label.config(text="")
        progressbar_label.grid_remove()

    def update_disabled_widget(self, widget, string):

        if isinstance(widget, tk.Entry):
            widget.configure(state='normal')
            widget.delete(0, tk.END)
            widget.insert(0, string)
            widget.configure(state='readonly')
        elif isinstance(widget, tk.Text):
            widget.configure(state='normal')
            widget.delete('1.0', tk.END)
            widget.insert(tk.END, string)
            widget.configure(state='disabled')

    def color_disabled_widget(self, widget, clr):

        if isinstance(widget, tk.Entry):
            widget.configure(state='normal')
            widget.configure(background=clr)
            widget.configure(state='readonly')
        elif isinstance(widget, tk.Text):
            widget.configure(state='normal')
            widget.configure(background=clr)
            widget.configure(state='disabled')

    def update_column_tab_dict(self, widget, value):

        widget_name = str(widget).split(".")[-1]
        if "entry" in widget_name:
            widget_label = widget_name.replace("entry", "label")
        elif "text" in widget_name:
            widget_label = widget_name.replace("text", "label")

        label_text = getattr(self, widget_label).cget("text")
        self.column_tab_dict[widget_name] = [value, label_text]

    def handle_transformations_log_double_click(self, event):

        if len(self.transformations_log_list) == 0:
            return

        self.toggle_selected_transformation()

    def toggle_selected_transformation(self):

        trans_id = self.transformations_log_tree. \
            item(self.transformations_log_tree.selection())['values'][3]
        trans = Transformation()

        if (self.transformations_log_tree.
            item(self.transformations_log_tree.selection())['values'][4]
                == "Yes"):

            trans.toggle_selected("No", trans_id)

        elif (self.transformations_log_tree.
              item(self.transformations_log_tree.selection())['values'][4]
              == "No"):

            trans.toggle_selected("Yes", trans_id)

        self.update_transformations_log_tab_widgets()
        return

    def flag_all_transformations(self):

        for item in self.transformations_log_tree.get_children():
            iid = item

        self.transformations_log_tree.selection_set(iid)

        session_id = self.transformations_log_tree. \
            item(self.transformations_log_tree.selection())['values'][2]
        trans = Transformation()

        trans.flag_all(session_id)

        self.update_transformations_log_tab_widgets()
        return

    def unflag_all_transformations(self):

        for item in self.transformations_log_tree.get_children():
            iid = item

        self.transformations_log_tree.selection_set(iid)

        session_id = self.transformations_log_tree. \
            item(self.transformations_log_tree.selection())['values'][2]
        trans = Transformation()

        trans.unflag_all(session_id)

        self.update_transformations_log_tab_widgets()
        return

    def replicate_selected_transformation(self):

        trans_id = self.transformations_log_tree. \
            item(self.transformations_log_tree.selection())['values'][3]

        trans = Transformation()

        if (self.transformations_log_tree.
            item(self.transformations_log_tree.selection())['values'][4]
                == "Yes"):

            lst = [element for element in self.transformations_log_list
                   if element['TransformationLogID'] == trans_id]

            trans.replicate(lst, self.table.model.df)
            self.table.redraw()

        elif (self.transformations_log_tree.
              item(self.transformations_log_tree.selection())['values'][4]
              == "No"):

            messagebox.showwarning("Warning", "Flagged for no replication.")

        return

    def replicate_all_transformations(self):

        lst = [element for element in self.transformations_log_list
               if element['IsReplicate'] == 'Yes']

        trans = Transformation()

        trans.replicate(lst, self.table.model.df)
        self.table.redraw()
        return

    def load_transformations(self):

        trans = Transformation()

        for item in self.transformations_log_tree.get_children():
            self.transformations_log_tree.delete(item)
        trans.delete_transformations_by_session(self.session_id)

        file_name = filedialog.askopenfilename(
            filetypes=[('Warchest Transformations File', '*.wct')],
            title='Load file...',
            initialdir=self.trans_path)

        if (file_name is None) or (file_name == ''):
            return
        file_obj = open(file_name, "rb")

        try:
            self.transformations_log_list = pickle.load(file_obj)
        except EOFError:
            messagebox.showerror("Error",
                                 "Warchest Transformations File corrupted")
        file_obj.close()

        for transformation in self.transformations_log_list:

            index = transformation.get('ColumnIndex')
            name = transformation.get('ColumnName')
            transform = transformation.get('TransformationDesc')
            option1 = transformation.get('Option1')
            option2 = transformation.get('Option2')
            option3 = transformation.get('Option3')

            if transform == 'setColumnType':
                trans.add_transformation(session=self.session_id,
                                         index=index,
                                         name=name,
                                         transformation=transform,
                                         option1=option1)

            if transform == 'createCategorical':
                trans.add_transformation(session=self.session_id,
                                         index=index,
                                         name=name,
                                         transformation=transform,
                                         option1=option1,
                                         option2=option2,
                                         option3=option3)

        self.update_transformations_log_tab_widgets()

    def save_transformations(self):

        lst = [element for element in self.transformations_log_list
               if element['IsReplicate'] == 'Yes']
        for trans in lst:
            session_file = trans.get('SessionDesc')
            date_file = trans.get('DateCreated')
            break

        date_ = (date_file[0:13] + date_file[14:16]).replace(" ", "-", 1)

        file_name = filedialog.asksaveasfilename(
            filetypes=[('Warchest Transformations File', '*.wct')],
            title="Save file as...",
            initialdir=self.trans_path,
            initialfile=session_file + '-' + str(date_),
            defaultextension='.wct')

        if (file_name is None) or (file_name == ''):
            return
        pickle.dump(self.transformations_log_list, open(file_name, "wb"))

    def clear_all_transformations(self):

        trans = Transformation()

        for item in self.transformations_log_tree.get_children():
            self.transformations_log_tree.delete(item)
        trans.delete_transformations_by_session(self.session_id)

    def load_model_columns(self):

        file_name = filedialog.askopenfilename(
            filetypes=[('Warchest Model Columns File', '*.wcc')],
            title='Load file...',
            initialdir=self.model_columns_path)

        if (file_name is None) or (file_name == ''):
            return
        file_obj = open(file_name, "rb")

        try:
            temp1, temp2, temp3, temp4 = pickle.load(file_obj)
            if len(temp1) != len(self.table.model.df.columns):
                messagebox.showerror("Error",
                                     "Number of columns in Warchest Model Columns File and current dataset do not match")
                file_obj.close()
                return
            else:
                file_obj.close()
        except EOFError:
            messagebox.showerror("Error",
                                 "Warchest Model Columns File corrupted")
            file_obj.close()
            return

        file_obj = open(file_name, "rb")
        try:
            self.available_to_model, self.class_label_status, self.nominal_ordinal, self.model_columns = pickle.load(file_obj)
            print(self.model_columns)
            print(type(self.model_columns))
            self.update_model_option_available_to_model(self.available_to_model)
            self.update_model_option_class_label_status(self.class_label_status)
            self.update_model_option_nominal_ordinal(self.nominal_ordinal)
            self.update_model_option_model_columns(self.model_columns)
            self.update_column_tab_widgets()
        except EOFError:
            messagebox.showerror("Error",
                                 "Warchest Model Columns File corrupted")
        file_obj.close()

    def save_model_columns(self):

        session_file = self.selected_dataset
        date_file = str(datetime.now())

        date_ = (date_file[0:13] + date_file[14:16]).replace(" ", "-", 1)

        file_name = filedialog.asksaveasfilename(
            filetypes=[('Warchest Model Columns File', '*.wcc')],
            title="Save file as...",
            initialdir=self.model_columns_path,
            initialfile=session_file + '-' + str(date_),
            defaultextension='.wcc')

        if (file_name is None) or (file_name == ''):
            return
        pickle.dump((self.available_to_model,
                     self.class_label_status,
                     self.nominal_ordinal,
                     self.model_columns), open(file_name, "wb"))

    def update_model_option_available_to_model(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('available_to_model_dict', var)

    def update_model_option_class_label_status(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('class_label_status_dict', var)

    def update_model_option_nominal_ordinal(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('nominal_ordinal_dict', var)

    def update_model_option_model_columns(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('model_columns_dict', var)

    def get_model_option_x(self, option):

        modelopt = ModelOption()
        return {int(k): v for k, v in modelopt.get_model_option(option).items()}

    def update_model_columns(self):

        self.available_to_model = self. \
            get_model_option_x('available_to_model_dict')
        self.class_label_status = self. \
            get_model_option_x('class_label_status_dict')
        self.nominal_ordinal = self. \
            get_model_option_x('nominal_ordinal_dict')
        self.model_columns = self. \
            get_model_option_x('model_columns_dict')

        for index, column in enumerate(self.table.model.df.columns):

            f_type = self.get_feature_type(self.get_col_values_by_col(index))

            if self.available_to_model[index] == 'No':
                self.model_columns[index] = 'No'
            else:
                if f_type == 'numerical':
                    if self.class_label_status[index] == 'Yes':
                        self.model_columns[index] = 'Class (numerical)'
                    else:
                        self.model_columns[index] = 'Yes (numerical)'
                elif f_type == 'datetime':
                    if self.class_label_status[index] == 'Yes':
                        self.model_columns[index] = 'Class (datetime)'
                    else:
                        self.model_columns[index] = 'Yes (datetime)'
                elif f_type == 'boolean':
                    if self.class_label_status[index] == 'Yes':
                        self.model_columns[index] = 'Class (boolean)'
                    else:
                        self.model_columns[index] = 'Yes (boolean)'
                elif (f_type == 'nominal or ordinal') or \
                        (f_type == 'categorical/factor'):
                    if self.class_label_status[index] == 'Yes':
                        if self.nominal_ordinal[index] == 'nominal':
                            self.model_columns[index] = 'Class (nominal)'
                    else:
                        if self.nominal_ordinal[index] == 'nominal':
                            self.model_columns[index] = 'Yes (nominal)'
                        else:
                            self.model_columns[index] = 'Yes (ordinal)'

        self.update_model_option_model_columns(self.model_columns)
        print('model_columns')
        print(self.model_columns)

    def get_model_column_names_by_feature(self, feature):

        lst = []
        string = ""
        for k, v in self.model_columns.items():

            if (v == feature):
                lst.append("[" + self.get_col_name_by_index(k) + "]")

        if len(lst) > 0:
            for i, row in enumerate(lst):
                string = string + str(lst[i]) + '\n'
        else:
            string = "N/A"

        return string

    def has_model_classlabel(self):

        for k, v in self.model_columns.items():

            if (v == "Class (numerical)") or \
               (v == "Class (datetime)") or \
               (v == "Class (boolean)") or \
               (v == "Class (nominal)"):

                return True
        return False

    def get_model_classlabel_index(self):

        for k, v in self.model_columns.items():

            if (v == "Class (numerical)") or \
               (v == "Class (datetime)") or \
               (v == "Class (boolean)") or \
               (v == "Class (nominal)"):

                return str(k)

    def get_features_from_model_columns(self):

        lst = []
        for k, v in self.model_columns.items():
            if (v != 'No'):
                if (v == "Class (numerical)") or \
                   (v == "Class (datetime)") or \
                   (v == "Class (boolean)") or \
                   (v == "Class (nominal)"):
                    pass
                else:
                    lst.append(k)
        return lst

    def apply_column_color(self, index, clr):

        self.table.columncolors[self.table.model.df.columns[index]] = clr
        self.table.redraw()

    def describe_column(self):

        self.update_column_tab_widgets()

    def init_model_overrides(self):

        model_task = ModelTask()
        model_task.update_model_override_algorithms()
        model_task.update_model_override_algorithm_params()
        model_task.update_model_overrides()

    def exit_app(self):

        if messagebox.askokcancel("Quit", "Really quit?"):
            self.root.destroy()

    def show_about(self):
        messagebox.showinfo(APP_NAME,
                            "One Program To Rule Them All")


if __name__ == "__main__":
    root = tk.Tk()
    app = Warchest(root)
    root.mainloop()
