from load_datasets import load_dataset
import numpy as np
import pandas as pd
import os.path
import sqlite3
from sklearn.model_selection import train_test_split
from preprocessing import EncodeClassLabel, Scale, handle_missing_data
from insights import ColumnInsight
from ordinalmaps import OrdinalMapping
from automator import Automator
from global_config import g
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Pmw
from pandastablerev import Table, TableModel

APP_NAME = "Machine Learning Mixer"
#df = pd.DataFrame({'A' : []})

class MLMixer():

    # def __init__(self, root, model, player):
    def __init__(self, root):
        self.root = root
        self.root.resizable(width=False, height=False)
        # self.model = model
        # self.player = player
        #self.df = pd.DataFrame({'A' : []})
        self.create_gui()
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.db_filename = 'ml_mixer.db'

        #top area variables
        self.selected_column = 0
        self.selected_column_name = ''
        self.column_tab_dict = {}

        # absolute path of application py file
        self.absolute_path = os.path.dirname(os.path.abspath(__file__))
        #print(self.absolute_path)
        #print(os.path.join(self.absolute_path, self.db_filename))
#        print(os.path.abspath(__file__))
#        print(os.path.dirname(os.path.abspath(__file__)))
#        print(os.path.join(os.path.dirname(__file__)))

    def create_gui(self):
        self.set_app_size()
        self.root.title(APP_NAME)
        self.tooltip = Pmw.Balloon(self.root)
        self.setup_app_styles()
        self.create_top_menu()
        self.create_top_area()
        self.create_dataframe_area()
        # self.create_context_menu()

    def setup_app_styles(self):

#        print(self.column_tab.winfo_class())
#        self.tabs_style.configure('TNotebook', background='white')
        self.app_style = ttk.Style()
        self.app_style.configure('Tabs.TFrame', background='white')
        self.app_style.configure('Tabs.TLabel', background='white')
        self.app_style.configure('Sections.TLabel',
                                 font=('Arial', '8', 'bold'),
                                 foreground='grey25')

        #print(self.app_style.element_options('Treeview.Heading'))
        #self.app_style.configure('Tabs.TEntry', background='white')
        #self.app_style.map('Tabs.TEntry', background = [('readonly', 'white')])

        # print(self.app_style.layout('Tabs.TEntry'))
        # print(self.app_style.lookup('Tabs.TEntry', 'background'))

    def set_app_size(self):
        # width = self.root.winfo_screenwidth()/1.4
        # height = self.root.winfo_screenheight()*0.7
        width = 1371
        height = 756
        x_offset = (self.root.winfo_screenwidth()/2)-(width/2)
        y_offset = (self.root.winfo_screenheight()/2)-(height/2)
        # print('%dx%d+%d+%d' % (width, height, x_offset, y_offset))
        self.root.geometry('%dx%d+%d+%d' % (width, height, x_offset, y_offset))
        return

    def create_top_menu(self):

        self.menu_bar = tk.Menu(self.root)

        self.dataset_menu = tk.Menu(self.menu_bar, tearoff=0,
                                    activebackground="#A2A2A2",
                                    activeforeground="black")
        self.dataset_menu.add_command(
            label="Load Dataset", command=self.on_load_dataset_menu_clicked)
        self.dataset_menu.add_command(
            label="Run Dataset", command=self.on_run_dataset_menu_clicked)
#        self.file_menu.add_command(
#            label="Save Project", command=self.save_project)
        self.dataset_menu.add_separator()
        self.dataset_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="Datasets", menu=self.dataset_menu)

        self.about_menu = tk.Menu(self.menu_bar, tearoff=0,
                                  activebackground="#A2A2A2",
                                  activeforeground="black")
        self.about_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)

        self.root.config(menu=self.menu_bar)

    def create_top_area(self):

        self.top_area = tk.Frame(self.root, height=25, bg="white")
        self.top_area.pack(fill='both', expand=1)

    def create_tabs(self):

        self.tabs = ttk.Notebook(self.top_area)
        self.tabs.pack(fill='both', expand=1)

        self.column_tab = ttk.Frame(self.tabs)
        self.table_tab = ttk.Frame(self.tabs)
        self.insights_tab = ttk.Frame(self.tabs)
        self.transformations_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.column_tab, text='Column')
        self.tabs.add(self.table_tab, text='Table')
        self.tabs.add(self.insights_tab, text='Insights')
        self.tabs.add(self.transformations_tab, text='Transformations')

        self.column_tab.configure(style='Tabs.TFrame')
        self.table_tab.configure(style='Tabs.TFrame')
        self.insights_tab.configure(style='Tabs.TFrame')
        self.transformations_tab.configure(style='Tabs.TFrame')

    def clean_top_area_items(self):

        # print(self.tabs.winfo_exists())

        self.reset_db_fields()

        if hasattr(self, 'tabs'):
            self.tabs.destroy()

    def create_top_area_items(self):

        self.create_tabs()
        self.create_column_tab_widgets()
        self.create_table_tab_widgets()
        self.create_insights_tab_widgets()
        self.create_transformations_tab_widgets()

    def create_column_tab_widgets(self):

        # describe_column_button
        self.describe_column_button = \
            ttk.Button(self.column_tab,
                       text="Describe Column",
                       name="describe_column_button",
                       command=self.on_describe_column_button_clicked)
        self.describe_column_button.grid(row=0, column=0, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.describe_column_button)

        # analyze_column_button
        self.analyze_column_button = \
            ttk.Button(self.column_tab,
                       text="Analyze Column",
                       name="analyze_column_button",
                       command=self.on_analyze_column_button_clicked)
        self.analyze_column_button.grid(row=0, column=1, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.analyze_column_button)

        # ordinal_mapping_button
        self.ordinal_mapping_button = \
            ttk.Button(self.column_tab,
                       text="Ordinal Mapping",
                       name="ordinal_mapping_button",
                       command=self.on_ordinal_mapping_button_clicked)
        self.ordinal_mapping_button.grid(row=0, column=2, sticky="nsew",
                                         padx=1, pady=1)
        self.add_tooltip_to_widget(self.ordinal_mapping_button)

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
                      text="Column Name:",
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
                      text="Column Index:",
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

        # dtype_entry
        self.dtype_label = \
            ttk.Label(self.column_tab,
                      text="Dtype:",
                      name="dtype_label")
        self.dtype_label.grid(row=5, column=0, sticky="nsew",
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
        self.dtype_entry.grid(row=5, column=1, sticky="nsew",
                              padx=1, pady=1)
        self.add_tooltip_to_widget(self.dtype_entry)
        self.dtype_entry.configure(state='readonly')

        # dense_sparse_entry
        self.dense_sparse_label = \
            ttk.Label(self.column_tab,
                      text="Dense/sparse:",
                      name="dense_sparse_label")
        self.dense_sparse_label.grid(row=6, column=0, sticky="nsew",
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
        self.dense_sparse_entry.grid(row=6, column=1, sticky="nsew",
                                     padx=1, pady=1)
        self.add_tooltip_to_widget(self.dense_sparse_entry)
        self.dense_sparse_entry.configure(state='readonly')

        # non_null_count_entry
        self.non_null_count_label = \
            ttk.Label(self.column_tab,
                      text="Count (non-null):",
                      name="non_null_count_label")
        self.non_null_count_label.grid(row=7, column=0, sticky="nsew",
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
        self.non_null_count_entry.grid(row=7, column=1, sticky="nsew",
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
        pass

    def create_insights_tab_widgets(self):

        # insights_tree
        self.insights_tree = \
            ttk.Treeview(self.insights_tab,
                         height=10,
                         #columns=5,
                         columns=('Column Name','Column Index','Insight','Priority','Created On'),
                         #text="Describe Column",
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

    def create_transformations_tab_widgets(self):
        pass

    def on_describe_column_button_clicked(self):

        self.update_column_tab_widgets()

    def on_analyze_column_button_clicked(self):

        self.update_column_tab_widgets()  # update for selected column

        insight = ColumnInsight(self.get_col_values(), self.column_tab_dict)
        insight.reset_insights()

        is_missing = insight.missing_values()
        #print('\nMissing values: {}'.format(is_missing))
        if is_missing is False:
            insight.memory_usage()

        self.update_insights_tab_widgets(insight)  # update for selected column

    def on_ordinal_mapping_button_clicked(self):

        self.update_column_tab_widgets()  # update for selected column

        OrdinalMapping(self.root,
                       self.get_col_values(),
                       self.get_feature_type(self.get_col_values()))

    def update_column_tab_widgets(self):

        self.turn_progressbar_on(self.column_tab_progressbar,
                                 self.column_tab_progressbar_label)

        self.column_tab_dict = {}

        # General Information --------------------------------
        self.update_selected_column_name_entry()
        self.update_selected_column_entry()
        self.update_feature_type_entry()
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

    def update_insights_tab_widgets(self, cls):

        # remove current items from tree
        for item in self.insights_tree.get_children():
            self.insights_tree.delete(item)
        # add new items to tree
        for row in cls.get_insights():
            self.insights_tree.insert('', 0, text=row[2], values=(row[1],
                                      row[3], row[4], row[5]))

    # General Information --------------------------------
    def update_selected_column_name_entry(self):

        for row in self.read_text_from_db(table_name='TopAreaItems',
                                          item_name='selected_column_name'):
            if row[0] != '':  # if there's somwething in the DB
                self.selected_column_name = row[0]
        string = str(self.selected_column_name)
        self.update_disabled_widget(self.selected_column_name_entry, string)
        self.update_column_tab_dict(self.selected_column_name_entry, string)

    def update_selected_column_entry(self):

        for row in self.read_integer_from_db(table_name='TopAreaItems',
                                             item_name='selected_column'):
            self.selected_column = row[0]
        string = str(self.selected_column)
        self.update_disabled_widget(self.selected_column_entry, string)
        self.update_column_tab_dict(self.selected_column_entry, string)

        # print(self.selected_column_entry.get())
        # print(self.selected_column_entry['state'])
        # print(self.selected_column_entry['style'])

    def update_feature_type_entry(self):

        string = self.get_feature_type(self.get_col_values())
        self.update_disabled_widget(self.feature_type_entry, string)
        self.update_column_tab_dict(self.feature_type_entry, string)

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
        # print(col_values.columns.nbytes)
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
            if len(self.get_col_values().index) == 0:  # if column is empty
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

    def create_dataframe_area(self):

        self.dataframe_area = tk.Frame(self.root, bg="white")
        self.dataframe_area.pack(fill='both', expand=1)
#        self.dataframe_area = tk.Canvas(self.root, bg='white', relief='groove',
#                                        width = 640, height = 480,
#                                        scrollregion=(0,0,640,480))
#        self.dataframe_area.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
#        self.dataframe_area.bind('<1>', self.on_dataframe_area_click)
        #self.dataframe_area.config(width = 640, height = 480)
        #ttk.Button(self.dataframe_area, text='Click Me').grid()
#        vb = self.root.geometry()
#        print(vb)

    def on_load_dataset_menu_clicked(self):

        self.clean_top_area_items()

        # Load iris Dataset
        #self.df = load_dataset('iris')

        # Load eda Dataset
        self.df = load_dataset('eda')

        self.table = pt = Table(self.dataframe_area,
                                dataframe=self.df,
                                showtoolbar=True,
                                showstatusbar=True,
                                absolute_path=self.absolute_path)
        #pt.importCSV('iris.csv') # ./datasets/iris.csv'
        pt.show()
        self.get_updated_pandastable_df()
        self.selected_column = pt.currentcol
        self.selected_column_name = pt.currentcol_name
        self.create_top_area_items()
        self.update_column_tab_widgets()
        #pt.redraw()

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

#        if column_type == "category":
#            return "categorical/factor"
#        if column_type == "boolean":
#            return "boolean"
#        if column_type == "string":
#            return "nominal or ordinal"
#        if column_type == "float" or column_type == "int":
#            return "numerical"
#        if column_type == "complex":
#            return "complex (numerical)"
#        if column_type == "datetime":
#            return "datetime"
#        if column_type == "unknown":
#            return "unknown"

        #dtype.kind
        #b 	boolean
        #i 	signed integer
        #u 	unsigned integer
        #f 	floating-point
        #c 	complex floating-point
        #m 	timedelta
        #M 	datetime
        #O 	object
        #S 	(byte-)string
        #U 	Unicode
        #V 	void
        #
        #is_string_dtype
        #dtype.kind in ('O', 'S', 'U') and not is_period_dtype(dtype)


    def get_updated_pandastable_df(self):

        # get df from the pandastable model
        self.pandastable_df = self.table.model.df

    def get_values_from_selected_column(self):

        return self.pandastable_df.iloc[:, self.selected_column]

    def get_col_values(self):

        self.get_updated_pandastable_df()
        return self.get_values_from_selected_column()

    def add_tooltip_to_widget(self, widget):

        widget_name = str(widget).split(".")[-1]
        for row in self.read_tooltip_from_db(table_name='Tooltips',
                                             item_name=widget_name,
                                             language=g.localized_lang):
            tooltip_text = row[0]
        self.tooltip.bind(widget, tooltip_text)

    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

    def read_integer_from_db(self, table_name=None, item_name=None):

        if table_name == 'TopAreaItems':
            where_column1 = 'ItemName'
            sel_column_1 = 'IntegerContent'

#        query = "SELECT ({coi}) FROM {tn} WHERE {cn}={my_id}".\
#                format(coi=column_3, tn=table_name, cn=column_2, my_id=item_name)
        query = "SELECT {col} FROM {tbl} WHERE {cond}=?".\
                format(col=sel_column_1,
                       tbl=table_name,
                       cond=where_column1)
        parameters = (item_name,)

        #name = self.tree.item(self.tree.selection())['text']
        #self.execute_db_query(query, (name,))
        #print(query)

        return self.execute_db_query(query, parameters)
#
#        c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="Hi World"'.\
#                format(coi=column_2, tn=table_name, cn=column_2))
#        all_rows = c.fetchall()
#
#        c.execute("SELECT * FROM {tn} WHERE {idf}=?".\
#                format(tn=table_name, cn=column_2, idf=id_column), (123456,))
#
#        cur.execute("SELECT * FROM tasks WHERE priority=?", (priority,))
#
#        c.execute("SELECT * FROM {tn} WHERE {idf}={my_id}".\
#        format(tn=table_name, cn=column_2, idf=id_column, my_id=some_id))

    def read_text_from_db(self, table_name=None, item_name=None):

        if table_name == 'TopAreaItems':
            where_column1 = 'ItemName'
            sel_column_1 = 'TextContent'

#        query = "SELECT {coi} FROM {tn} WHERE {cn}=?".\
#                format(coi=sel_column_1,
#                       tn=table_name,
#                       cn=where_column1)
#        parameters = (item_name,)

        query = "SELECT {col} FROM {tbl} WHERE {cond}=?".\
                format(col=sel_column_1,
                       tbl=table_name,
                       cond=where_column1)
        parameters = (item_name,)

        return self.execute_db_query(query, parameters)

    def write_integer_to_db(self, table_name=None,
                            item_name=None,
                            item_value=None):

        if table_name == 'TopAreaItems':
            where_column1 = 'ItemName'
            update_column_1 = 'IntegerContent'

        query = "UPDATE {tbl} SET {col}=? WHERE {cond}=?".\
                format(col=update_column_1,
                       tbl=table_name,
                       cond=where_column1)
        parameters = (item_value, item_name)

        return self.execute_db_query(query, parameters)

    def write_text_to_db(self, table_name=None,
                         item_name=None,
                         item_value=None):

        if table_name == 'TopAreaItems':
            where_column1 = 'ItemName'
            update_column_1 = 'TextContent'

        query = "UPDATE {tbl} SET {col}=? WHERE {cond}=?".\
                format(col=update_column_1,
                       tbl=table_name,
                       cond=where_column1)
        parameters = (item_value, item_name)

        return self.execute_db_query(query, parameters)

    def read_tooltip_from_db(self, table_name=None, item_name=None, language=1):

        where_column1 = 'WidgetName'
        sel_column_1 = 'TooltipText'
        lang_column1 = 'LanguageID'

        query = "SELECT {col} FROM {tbl} WHERE {cond}=? AND {lang}=?".\
                format(col=sel_column_1,
                       tbl=table_name,
                       cond=where_column1,
                       lang=lang_column1)
        parameters = (item_name, language)

        return self.execute_db_query(query, parameters)

    def set_x_and_y(self):
        # Encode class labels
        self.y = EncodeClassLabel(self.df['4'].values)
        # Select features
        self.X = self.df.iloc[:, [2, 3]].values

    def on_run_dataset_menu_clicked(self):
        self.set_x_and_y()

        # ******************* Preprocess ****************************

        # Splitting data into training and test data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
             self.X, self.y, test_size=0.3, random_state=0)

        # Standardize features
        self.X_train_std, self.X_test_std = Scale(self.X_train, self.X_test, t="std")

        # Combine data for plotting
        self.X_combined_std = np.vstack((self.X_train_std, self.X_test_std))
        self.X_combined = np.vstack((self.X_train, self.X_test))
        self.y_combined = np.hstack((self.y_train, self.y_test))

        # Whether or not need to plot decision regions
        g.decision_regions = False

        # ******************* Learning ****************************
        # Fit with Perceptron
        Automator("ClfPerceptron",
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
                  self.y_combined,
                  n_iter=40,
                  eta0=0.1,
                  random_state=0)

        # Fit with AdalineGD
        Automator("ClfAdalineGD",
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
                  self.y_combined,
                  n_iter=15,
                  eta0=0.01)

        # Fit with AdalineSGD
        Automator("ClfAdalineSGD",
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
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
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
                  self.y_combined,
                  C=1000.0,
                  penalty='l1',
                  random_state=0)

        # Fit with Linear Support Vector Machines
        Automator("ClfLinearSVM",
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
                  self.y_combined,
                  kernel='linear',
                  C=1.0,
                  random_state=0)

        # Fit with Kernel Support Vector Machines
        Automator("ClfKernelSVM",
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
                  self.y_combined,
                  kernel='rbf',
                  gamma=0.2,
                  C=1.0,
                  random_state=0)

        # Fit with Decision Tree
        Automator("ClfDecisionTree",
                  self.X_train,
                  self.X_test,
                  self.y_train,
                  self.y_test,
                  self.X_combined,
                  self.y_combined,
                  criterion='entropy',
                  max_depth=3,
                  random_state=0)

        # Fit with Random Forest
        Automator("ClfRandomForest",
                  self.X_train,
                  self.X_test,
                  self.y_train,
                  self.y_test,
                  self.X_combined,
                  self.y_combined,
                  criterion='entropy',
                  n_estimators=10,
                  random_state=1)

        # Fit with K-nearest Neighbors
        # TODO: need to add feature selection via SBS
        Automator("ClfKNN",
                  self.X_train_std,
                  self.X_test_std,
                  self.y_train,
                  self.y_test,
                  self.X_combined_std,
                  self.y_combined,
                  n_neighbors=5,
                  p=2,
                  metric='minkowski')

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

    def update_column_tab_dict(self, widget, value):

        widget_name = str(widget).split(".")[-1]
        if "entry" in widget_name:
            widget_label = widget_name.replace("entry", "label")
        elif "text" in widget_name:
            widget_label = widget_name.replace("text", "label")

        label_text = getattr(self, widget_label).cget("text")
        self.column_tab_dict[widget_name] = [value, label_text]
        #self.column_tab_tuples_list.append(tuple([widget_name, value]))

    def reset_db_fields(self):

        # reset selected_column
        self.write_integer_to_db(table_name='TopAreaItems',
                                 item_name='selected_column',
                                 item_value=0)
        self.write_text_to_db(table_name='TopAreaItems',
                              item_name='selected_column_name',
                              item_value='')

    def exit_app(self):
        # self.keep_playing = False
        if messagebox.askokcancel("Quit", "Really quit?"):
            self.reset_db_fields()
            self.root.destroy()

    def show_about(self):
        messagebox.showinfo(APP_NAME,
                            "One Program To Rule Them All")


if __name__ == "__main__":
    root = tk.Tk()
    # root.resizable(width=False, height=False)
    # model = model.Model()
    # player = player.Player()
    # app = View(root, model, player)
    app = MLMixer(root)
    root.mainloop()


