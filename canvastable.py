from utils_and_tools import check_platform
import tkinter as tk
from tkinter import ttk


class CanvasTable(tk.Canvas):

    def __init__(self, parent=None, dataframe=None, width=None, height=None,
                 **kwargs):
        tk.Canvas.__init__(self, parent, bg='white', width=width,
                           height=height, relief= GROOVE,
                           scrollregion=(0, 0, 300, 200))
        self.parentframe = parent
        self.platform = check_platform()
        self.width = width
        self.height = height
        self.cellwidth = 60
        self.maxcellwidth = 300
        self.mincellwidth = 30
        self.rowheight = 20
        self.horizlines = 1
        self.vertlines = 1
        self.autoresizecols = 1
        self.inset = 2
        self.x_start = 0
        self.y_start = 1
        self.linewidth = 1.0
        self.rowheaderwidth = 50
        self.showkeynamesinheader = False
        self.thefont = ('Arial',12)
        #barras horizontal y vertical 230, 230, 230 #E6E6E6
        #menues 241 241 241 #F1F1F1
        #cells selection 198 198 198 #C6C6C6
        #header background color when column or row selected  211 240 224 #D3F0E0
        #header foreground color when column or row selected  27 93 57 #1B5D39
        self.cellbackgr = '#F4F4F3'
        #self.cellbackgr = '#FFFFFF' (255,255,255)
        self.entrybackgr = 'white'
        self.grid_color = '#ABB1AD'
        #self.grid_color = '#D4D4D4' (212,212,212)
        self.rowselectedcolor = '#E4DED4'
        #self.rowselectedcolor = '#D2D2D2' (210,210,210)
        self.multipleselectioncolor = '#E0F2F7'
        self.boxoutlinecolor = '#084B8A'
        #self.boxoutlinecolor = '#217346' (33,115,70)
        self.colselectedcolor = '#e4e3e4'
        #self.colselectedcolor = '#D2D2D2' (210,210,210)
        self.floatprecision = 0
        self.columncolors = {}
        self.bg = ttk.Style().lookup('TLabel.label', 'background')
        self.currentpage = None
        self.navFrame = None
        self.currentrow = 0
        self.currentcol = 0
        self.reverseorder = 0
        self.startrow = self.endrow = None
        self.startcol = self.endcol = None
        self.allrows = False
        self.multiplerowlist = []
        self.multiplecollist = []
        self.col_positions = []
        self.mode = 'normal'
        self.editable = True
        self.filtered = False
        self.child = None
        self.queryrow = 4
        self.childrow = 5
        #set any options passed in kwargs to overwrite defaults and prefs
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        self.meta = {}
        self.columnwidths = {} #used to store col widths
        self.df = dataframe
        self.rows = len(self.df.index)
        self.cols = len(self.df.columns)
        self.tablewidth = (self.cellwidth)*self.cols
        return

    def show(self, callback=None):
        """Adds column header and scrollbars and combines them with
           the current table adding all to the master frame provided in constructor.
           Table is then redrawn."""

        #Add the table and header to the frame
        self.rowheader = RowHeader(self.parentframe, self, width=self.rowheaderwidth)
        self.tablecolheader = ColumnHeader(self.parentframe, self)
        self.rowindexheader = IndexHeader(self.parentframe, self)
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient=VERTICAL,command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.tablecolheader['xscrollcommand'] = self.Xscrollbar.set
        self.rowheader['yscrollcommand'] = self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.rowindexheader.grid(row=0,column=0,rowspan=1,sticky='news')
        self.tablecolheader.grid(row=0,column=1,rowspan=1,sticky='news')
        self.rowheader.grid(row=1,column=0,rowspan=1,sticky='news')
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)

        #self.adjustColumnWidths()
        #self.parentframe.bind("<Configure>", self.redrawVisible)
        self.tablecolheader.xview("moveto", 0)
        self.xview("moveto", 0)
        self.statusbar = statusBar(self.parentframe, self)
        self.statusbar.grid(row=3,column=0,columnspan=2,sticky='ew')
        #self.redraw(callback=callback)

        ttk.Label(rowheader, text='rowheader').pack()
        self.canvas.create_text(
            center_x, center_y, font=("", font_size), text=entered_text, fill=self.fill)

        return

    def redraw(self, event=None, callback=None):
        """Redraw table"""

        self.redrawVisible(event, callback)
        #if hasattr(self, 'statusbar'):
        #    self.statusbar.update()
        return

    def redrawVisible(self, event=None, callback=None):
        """Redraw the visible portion of the canvas"""

        model = self.model
        self.rows = len(self.model.df.index)
        self.cols = len(self.model.df.columns)
        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect','colrect')
            self.delete('currentrect','fillrect')
            self.delete('gridline','text')
            self.delete('multicellrect','multiplesel')
            self.delete('colorrect')
            self.setColPositions()
            if self.cols == 0:
                self.tablecolheader.redraw()
            if self.rows == 0:
                self.visiblerows = []
                self.rowheader.redraw()
            return
        self.tablewidth = (self.cellwidth) * self.cols
        self.configure(bg=self.cellbackgr)
        self.setColPositions()

        #are we drawing a filtered subset of the recs?
        if self.filtered == True:
            self.delete('colrect')

        self.rowrange = list(range(0,self.rows))
        self.configure(scrollregion=(0,0, self.tablewidth+self.x_start,
                        self.rowheight*self.rows+10))

        x1, y1, x2, y2 = self.getVisibleRegion()
        startvisiblerow, endvisiblerow = self.getVisibleRows(y1, y2)
        self.visiblerows = list(range(startvisiblerow, endvisiblerow))
        startvisiblecol, endvisiblecol = self.getVisibleCols(x1, x2)
        self.visiblecols = list(range(startvisiblecol, endvisiblecol))

        self.drawGrid(startvisiblerow, endvisiblerow)
        align = self.align
        self.delete('fillrect')
        bgcolor = self.cellbackgr
        df = self.model.df

        #st=time.time()
        def set_precision(x, p):
            if not pd.isnull(x):
                if x<1:
                    x = '{:.{}g}'.format(x, p)
                else:
                    x = '{:.{}f}'.format(x, p)
            return x

        prec = self.floatprecision
        rows = self.visiblerows
        for col in self.visiblecols:
            coldata = df.iloc[rows,col]
            #print (col, coldata.dtype)
            if prec != 0:
                if coldata.dtype == 'float64':
                    coldata = coldata.apply(lambda x: set_precision(x, prec), 1)
                    #print (coldata)
            coldata = coldata.astype(object).fillna('')
            offset = rows[0]
            for row in self.visiblerows:
                text = coldata.iloc[row-offset]
                self.drawText(row, col, text, align)
            colname = df.columns[col]

        self.colorColumns()
        self.tablecolheader.redraw()
        self.rowheader.redraw(align=self.align)
        self.rowindexheader.redraw()
        self.drawSelectedRow()
        self.drawSelectedRect(self.currentrow, self.currentcol)
        if len(self.multiplerowlist)>1:
            self.rowheader.drawSelectedRows(self.multiplerowlist)
            self.drawMultipleRows(self.multiplerowlist)
            self.drawMultipleCells()
        return

class SimpleTable(tk.Frame):
    def __init__(self, parent, df):
        # use black background so it "peeks through" to
        # form grid lines
        self.cell_bg = '#FFFFFF' #(255,255,255)
        self.col_width = 10
        self.max_col_width = 30
        self.min_col_width = 10
        self.entry_style = ttk.Style()
        self.entry_style.configure('TEntry', borderwidth=0)

        import sys
        rows = len(df.index)
        columns = len(df.columns)
        #tk.Frame.__init__(self, parent, background="black")
        tk.Frame.__init__(self, parent)
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
#                label = ttk.Label(self, text="%s/%s" % (row, column),
#                                 borderwidth=0, width=10)
                entry = ttk.Entry(self,
                                 background=self.cell_bg,
                                 width=self.col_width)
                #sdd = df.iloc[row, column]
                #print(sdd, type(sdd))
                #text="%s" % df.iloc[row, column]
                entry.grid(row=row, column=column, sticky="nsew", padx=0, pady=0)
                entry.insert(0, "%s" % df.iloc[row, column])
                current_row.append(entry)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

        print('\nSize of df: {}'.format(sys.getsizeof(df)))
        print('\nSize of widgets: {}'.format(sys.getsizeof(self._widgets)))



#    def set(self, row, column, value):
#        widget = self._widgets[row][column]
#        widget.configure(text=value)