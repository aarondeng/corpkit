#!usr/bin/python

# corpkit GUI
# Daniel McDonald
# Template created by: Patrick T. Cossette <cold_soul79078@yahoo.com>

import Tkinter
from Tkinter import *
import sys,string
import threading
import ScrolledText
import time
from time import strftime, localtime
from ttk import Progressbar, Style

########################################################################

# stdout to app
class RedirectText(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, text_ctrl, log_text):
        """Constructor"""
        def dumfun():
            pass

        self.output = text_ctrl
        self.log = log_text
        self.flush = dumfun
 
    #----------------------------------------------------------------------
    def write(self, string):
        """""" 
        import re
        if 'Parsing file' not in string and 'Initialising parser' not in string:
            self.log.append(string)
        # remove blank lines
        show_reg = re.compile(r'^\s*$')
        if not re.match(show_reg, string):
            self.output.set(string)
            #self.output.insert(Tkinter.END, '\n' + string.replace('\r', ''))

class Notebook(Frame):

    """Notebook Widget"""
    def __init__(self, parent, activerelief = RAISED, inactiverelief = RIDGE, xpad = 4, ypad = 6, activefg = 'black', inactivefg = 'black', **kw):
        """Construct a Notebook Widget

        Notebook(self, parent, activerelief = RAISED, inactiverelief = RIDGE, xpad = 4, ypad = 6, activefg = 'black', inactivefg = 'black', **kw)        
    
        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width, activerelief,
        inactiverelief, xpad, ypad.

        xpad and ypad are values to be used as ipady and ipadx
        with the Label widgets that make up the tabs. activefg and inactivefg define what
        color the text on the tabs when they are selected, and when they are not

        """
                                                                                           #Make various argument available to the rest of the class
        self.activefg = activefg                                                           
        self.inactivefg = inactivefg
        self.deletedTabs = []        
        self.xpad = xpad
        self.ypad = ypad
        self.activerelief = activerelief
        self.inactiverelief = inactiverelief                                               
        self.kwargs = kw                                                                   
        self.tabVars = {}                                                                  #This dictionary holds the label and frame instances of each tab
        self.tabs = 0                                                                      #Keep track of the number of tabs                                                                             
        self.progvar = DoubleVar()
        self.progvar.set(0)
        self.style = Style()
        self.style.theme_use("default")
        self.style.configure("TProgressbar", thickness=15)
        self.kwargs = kw                                                                   
        self.tabVars = {}                                                                  #This dictionary holds the label and frame instances of each tab
        self.tabs = 0                                                                      #Keep track of the number of tabs                                                                             
        # the notebook, with its tabs, middle, status bars
        self.noteBookFrame = Frame(parent)                                                 #Create a frame to hold everything together
        self.BFrame = Frame(self.noteBookFrame)
        self.statusbar = Frame(self.noteBookFrame, bd = 2, height = 25)                                            #Create a frame to put the "tabs" in
        self.progbarspace = Frame(self.noteBookFrame, relief = RAISED, bd = 2, height = 25)
        self.noteBook = Frame(self.noteBookFrame, relief = RAISED, bd = 2, **kw)           #Create the frame that will parent the frames for each tab
        self.noteBook.grid_propagate(0)
        # status bar text and log
        self.status_text = StringVar()
        self.log_stream = []
        self.text = Label(self.statusbar, textvariable = self.status_text, height = 1, font = ("Courier New", 13), width = 135, anchor = W)
        self.text.grid(sticky = W)
        self.progbar = Progressbar(self.progbarspace, orient = 'horizontal', length = 500, mode = 'determinate', variable = self.progvar, style="TProgressbar")
        self.progbar.grid(sticky = E)

        self.redir = RedirectText(self.status_text, self.log_stream)
        sys.stdout = self.redir
        sys.stderr = self.redir

        #self.statusbar.grid_propagate(0)                                                    #self.noteBook has a bad habit of resizing itself, this line prevents that
        Frame.__init__(self)
        self.noteBookFrame.grid()
        self.BFrame.grid(row = 0, column = 0, columnspan = 27, sticky = N) # ", column = 13)" puts the tabs in the middle!
        self.noteBook.grid(row = 1, column = 0, columnspan = 27)
        self.statusbar.grid(row = 2, column = 0, padx = (0, 265))
        self.progbarspace.grid(row = 2, column = 0, padx = (265, 0), sticky = E)

    def change_tab(self, IDNum):
        """Internal Function"""
        
        for i in (a for a in range(0, len(self.tabVars.keys()))):
            if not i in self.deletedTabs:                                                  #Make sure tab hasen't been deleted
                if i <> IDNum:                                                             #Check to see if the tab is the one that is currently selected
                    self.tabVars[i][1].grid_remove()                                       #Remove the Frame corresponding to each tab that is not selected
                    self.tabVars[i][0]['relief'] = self.inactiverelief                     #Change the relief of all tabs that are not selected to "Groove"
                    self.tabVars[i][0]['fg'] = self.inactivefg                             #Set the fg of the tab, showing it is selected, default is black
                else:                                                                      #When on the tab that is currently selected...
                    self.tabVars[i][1].grid()                                              #Re-grid the frame that corresponds to the tab                      
                    self.tabVars[IDNum][0]['relief'] = self.activerelief                   #Change the relief to "Raised" to show the tab is selected
                    self.tabVars[i][0]['fg'] = self.activefg                               #Set the fg of the tab, showing it is not selected, default is black
        # prog to zero on change tab?
        # self.progvar.set(0)

    def add_tab(self, width = 2, **kw):
        import Tkinter
        """Creates a new tab, and returns its corresponding frame

        """
        
        temp = self.tabs
        self.tabVars[self.tabs] = [Label(self.BFrame, relief = RIDGE, **kw)]               #Create the tab
        self.tabVars[self.tabs][0].bind("<Button-1>", lambda Event:self.change_tab(temp))  #Makes the tab "clickable"
        self.tabVars[self.tabs][0].pack(side = LEFT, ipady = self.ypad, ipadx = self.xpad) #Packs the tab as far to the left as possible
        self.tabVars[self.tabs].append(Frame(self.noteBook, **self.kwargs))                #Create Frame, and append it to the dictionary of tabs
        self.tabVars[self.tabs][1].grid(row = 0, column = 0)                               #Grid the frame ontop of any other already existing frames
        self.change_tab(0)                                                                 #Set focus to the first tab
        self.tabs += 1                                                                     #Update the tab count
        return self.tabVars[temp][1]                                                       #Return a frame to be used as a parent to other widgets

    def destroy_tab(self, tab):
        """Delete a tab from the notebook, as well as it's corresponding frame

        """
        
        self.iteratedTabs = 0                                                              #Keep track of the number of loops made
        for b in self.tabVars.values():                                                    #Iterate through the dictionary of tabs
            if b[1] == tab:                                                                #Find the NumID of the given tab
                b[0].destroy()                                                             #Destroy the tab's frame, along with all child widgets
                self.tabs -= 1                                                             #Subtract one from the tab count
                self.deletedTabs.append(self.iteratedTabs)                                 #Apend the NumID of the given tab to the list of deleted tabs
                break                                                                      #Job is done, exit the loop
            self.iteratedTabs += 1                                                         #Add one to the loop count
    
    def focus_on(self, tab):
        """Locate the IDNum of the given tab and use
        change_tab to give it focus

        """
        
        self.iteratedTabs = 0                                                              #Keep track of the number of loops made
        for b in self.tabVars.values():                                                    #Iterate through the dictionary of tabs
            if b[1] == tab:                                                                #Find the NumID of the given tab
                self.change_tab(self.iteratedTabs)                                         #send the tab's NumID to change_tab to set focus, mimicking that of each tab's event bindings
                break                                                                      #Job is done, exit the loop
            self.iteratedTabs += 1                                                         #Add one to the loop count

def corpkit_gui():
    import Tkinter, Tkconstants, tkFileDialog, tkMessageBox, tkSimpleDialog
    from Tkinter import StringVar, Listbox, Text
    import sys
    from tkintertable import TableCanvas, TableModel
    import os
    import corpkit
    from nltk.draw.table import MultiListbox, Table

    def resource_path(relative):
        import os
        return os.path.join(os.environ.get("_MEIPASS2",os.path.abspath(".")),relative)

    # add tregex to path
    corpath = os.path.dirname(corpkit.__file__)
    baspat = os.path.dirname(os.path.dirname(corpkit.__file__))
    dicpath = os.path.join(baspat, 'dictionaries')
    os.environ["PATH"] += os.pathsep + corpath + os.pathsep + dicpath
    sys.path.append(corpath)
    sys.path.append(dicpath)
    sys.path.append(baspat)

    def adjustCanvas(someVariable = None):
        fontLabel["font"] = ("arial", var.get())

    # key binding
    if sys.platform == 'darwin':
        key = 'Mod1'
    else:
        key = 'Control'
    
    root = Tk()
    root.title("corpkit")
    root.resizable(FALSE,FALSE)

    #HWHW h 550
    note = Notebook(root, width= 1365, height = 660, activefg = 'red', inactivefg = 'blue')  #Create a Note book Instance
    note.grid()
    tab0 = note.add_tab(text = "Build")
    tab1 = note.add_tab(text = "Interrogate")                                                  #Create a tab with the text "Tab One"
    tab2 = note.add_tab(text = "Edit")                                                  #Create a tab with the text "Tab Two"
    tab3 = note.add_tab(text = "Visualise")                                                    #Create a tab with the text "Tab Three"
    tab4 = note.add_tab(text = "Concordance")                                                 #Create a tab with the text "Tab Four"
    tab5 = note.add_tab(text = "Manage")                                                 #Create a tab with the text "Tab Five"
    note.text.update_idletasks()

    ###################     ###################     ###################     ###################
    # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #
    ###################     ###################     ###################     ###################


    tab1.grid_columnconfigure(2, weight=5)
    # a dict of the editor frame names and models
    editor_tables = {}
    currently_in_each_frame = {}
    sort_direction = True
    names = []

    def convert_pandas_dict_to_ints(dict_obj):
        """try to turn pandas as_dict into ints, for tkintertable

           the huge try statement is to stop errors when there
           is a single corpus --- need to find source of problem
           earlier, though"""
        vals = []
        try:
            for a, b in dict_obj.items():
                # c = year, d = count
                for c, d in b.items():
                    vals.append(d)
            if all([float(x).is_integer() for x in vals if is_number(x)]):
                for a, b in dict_obj.items():
                    for c, d in b.items():
                        if is_number(d):
                            b[c] = int(d)
        except TypeError:
            pass

        return dict_obj

    def update_spreadsheet(frame_to_update, df_to_show = None, model = False, height = 140, width = False, indexwidth = 70, just_default_sort = False):
        """refresh a spreadsheet in the editor window"""
        from collections import OrderedDict
        import pandas
        kwarg = {}
        if width:
            kwarg['width'] = width
        if model and not df_to_show:
            df_to_show = make_df_from_model(model)
            if need_make_totals:
                df_to_show = make_df_totals(df_to_show)
        if df_to_show is not None:

            if just_default_sort is False:    
                # for abs freq, make total
                model = TableModel()
                df_to_show = pandas.DataFrame(df_to_show, dtype = object)
                if need_make_totals(df_to_show):
                    df_to_show = make_df_totals(df_to_show)
                
                # turn pandas into dict
                raw_data = df_to_show.to_dict()
                
                # convert to int if possible
                raw_data = convert_pandas_dict_to_ints(raw_data)
                        
                table = TableCanvas(frame_to_update, model=model, 
                                    showkeynamesinheader=True, 
                                    height = height,
                                    rowheaderwidth=indexwidth, cellwidth=50)
                table.createTableFrame()
                model = table.model
                model.importDict(raw_data)
                # move columns into correct positions
                for index, name in enumerate(list(df_to_show.index)):
                    model.moveColumn(model.getColumnIndex(name), index)
                table.createTableFrame()
                # sort the rows
                if 'tkintertable-order' in list(df_to_show.index):
                    table.sortTable(columnName = 'tkintertable-order')
                    ind = model.columnNames.index('tkintertable-order')
                    try:
                        model.deleteColumn(ind)
                    except:
                        pass
                else:
                    #nm = os.path.basename(corpus_fullpath.get().rstrip('/'))
                    #table.sortTable(columnIndex = 0, reverse = 1)
                    pass
            else:
                table = TableCanvas(frame_to_update, model=model, 
                                    showkeynamesinheader=True, 
                                    height = height,
                                    rowheaderwidth=indexwidth, cellwidth=60,
                                    **kwarg)
                table.createTableFrame()
                table.sortTable(columnName = 'Total', reverse = direct())

            table.redrawTable()
            editor_tables[frame_to_update] = model
            currently_in_each_frame[frame_to_update] = df_to_show
            return
        if model:
            table = TableCanvas(frame_to_update, model=model, 
                                showkeynamesinheader=True, 
                                height = height,
                                rowheaderwidth=indexwidth, cellwidth=60,
                                **kwarg)
            table.createTableFrame()
            try:
                table.sortTable(columnName = 'Total', reverse = direct())
            except:
                direct()           
                table.sortTable(reverse = direct())
            table.createTableFrame()            # sorts by total freq, ok for now
            table.redrawTable()
        else:
            table = TableCanvas(frame_to_update, height = height, width = width, cellwidth=60)
            table.createTableFrame()            # sorts by total freq, ok for now
            table.redrawTable()

    def remake_special_query(query):
        lst_of_specials = ['PROCESSES:', 'ROLES:', 'WORDLISTS:']
        if any([special in query for special in lst_of_specials]):
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Special query detected. Loading wordlists ... ' % thetime
            from dictionaries.process_types import processes
            from dictionaries.roles import roles
            from dictionaries.wordlists import wordlists
            dict_of_specials = {'PROCESSES:': processes, 'ROLES:': roles, 'WORDLISTS:': wordlists}
            for special in lst_of_specials:
                # temporary, to show off process type searching.
                if special == 'PROCESSES:':
                    lemmatag = 'v'
                from corpkit import as_regex
                if special in query:
                    types = [k for k in dict_of_specials[special]._asdict().keys()]
                    reg = re.compile('(^.*)(%s)(:)([A-Z]+)(.*$)' % special[:-1])
                    divided = re.search(reg, query)
                    if special == 'PROCESSES:':
                        the_bound = 'w'
                    if special == 'ROLES:':
                        the_bound = False
                    if special == 'WORDLISTS:':
                        the_bound = 'w'
                    try:
                        lst_of_matches = dict_of_specials[special]._asdict()[divided.group(4).lower()]
                        asr = as_regex(lst_of_matches, 
                                       boundaries = the_bound, 
                                       case_sensitive = case_sensitive.get(), 
                                       inverse = False)
                        query = divided.group(1) + asr + divided.group(5)
                    except:
                        thetime = strftime("%H:%M:%S", localtime())
                        print '%s: "%s" must be: %s' % (thetime, divided.group(4), ', '.join(dict_of_specials[special]._asdict().keys()))
                        return False
        return query

    def ignore():
        return "break"

    def need_make_totals(df):
        # because there is tkinter-order, the min is 2
        if len(list(df.index)) < 3:
            return False
        try:
            x = df.iloc[0,0]
        except:
            return False
        # if was_series, basically
        try:
            vals = [i for i in list(df.iloc[0,].values) if is_number(i)]
        except TypeError:
            return False
        if len(vals) == 0:
            return False
        if all([float(x).is_integer() for x in vals]):
            return True
        else:
            return False

    def make_df_totals(df):   
        df = df.drop('Total', errors = 'ignore')
        # add new totals
        df.ix['Total'] = df.drop('tkintertable-order', errors = 'ignore').sum().astype(object)
        return df

    def make_df_from_model(model):
        import pandas
        from StringIO import StringIO
        recs = model.getAllCells()
        colnames = model.columnNames
        collabels = model.columnlabels
        row=[]
        csv_data = []
        for c in colnames:
            row.append(collabels[c])
        try:
            csv_data.append(','.join([unicode(s, errors = 'ignore') for s in row]))
        except TypeError:
            csv_data.append(','.join([str(s) for s in row]))
        #csv_data.append('\n')
        for row in recs.keys():
            rowname = model.getRecName(row)
            try:
                csv_data.append(','.join([unicode(rowname, errors = 'ignore')] + [unicode(s, errors = 'ignore') for s in recs[row]]))
            except TypeError:
                csv_data.append(','.join([str(rowname)] + [str(s) for s in recs[row]]))

            #csv_data.append('\n')
            #writer.writerow(recs[row])
        csv = '\n'.join(csv_data)
        newdata = pandas.read_csv(StringIO(csv), index_col=0, header=0)
        newdata = pandas.DataFrame(newdata, dtype = object)
        newdata = newdata.T
        newdata = newdata.drop('Total', errors = 'ignore')
        newdata = add_tkt_index(newdata)
        if need_make_totals(newdata):
            newdata = make_df_totals(newdata)
        return newdata

    def refresh():
        """refreshes the list of dataframes in the editor and plotter panes"""
        # Reset name_of_o_ed_spread and delete all old options
        # get the latest only after first interrogation
        if len(all_interrogations.keys()) == 1:
            selected_to_edit.set(all_interrogations.keys()[-1])
        dataframe1s['menu'].delete(0, 'end')
        dataframe2s['menu'].delete(0, 'end')
        if len(all_interrogations.keys()) > 0:
            data_to_plot.set(all_interrogations.keys()[-1])
        every_interrogation['menu'].delete(0, 'end')
        every_interro_listbox.delete(0, 'end')
        new_choices = []
        for interro in all_interrogations.keys():
            new_choices.append(interro)
        new_choices = tuple(new_choices)
        dataframe2s['menu'].add_command(label='Self', command=Tkinter._setit(data2_pick, 'Self'))
        for choice in new_choices:
            dataframe1s['menu'].add_command(label=choice, command=Tkinter._setit(selected_to_edit, choice))
            dataframe2s['menu'].add_command(label=choice, command=Tkinter._setit(data2_pick, choice))
            every_interrogation['menu'].add_command(label=choice, command=Tkinter._setit(data_to_plot, choice))
            #every_interro_listbox.delete(0, END)
            if choice != 'None':
                every_interro_listbox.insert(END, choice)
        new_clines = []
        prev_conc_listbox.delete(0, 'end')
        for cline in all_conc.keys():
            new_clines.append(cline)
        new_clines = tuple(new_clines)
        for choice in new_clines:
            #every_interro_listbox.delete(0, END)
            if choice != 'None':
                ev_conc_listbox.insert(END, choice)
                prev_conc_listbox.insert(END, choice)

    def add_tkt_index(df):
        import pandas
        """add order to df for tkintertable"""
        df = df.T
        df = df.drop('tkintertable-order', errors = 'ignore', axis = 1)
        df['tkintertable-order'] = pandas.Series([index for index, data in enumerate(list(df.index))], index = list(df.index))
        df = df.T
        return df

    def namer(name_box_text, type_of_data = 'interrogation'):
        """returns a name to store interrogation/editor result as"""
        
        if name_box_text.lower() == 'untitled' or name_box_text == '':
            c = 0
            the_name = '%s-%s' % (type_of_data, str(c).zfill(2))
            while the_name in all_interrogations.keys():
                c += 1
                the_name = '%s-%s' % (type_of_data, str(c).zfill(2))
        else:
            the_name = name_box_text
        return the_name

    transdict = {
            'Get distance from root for regex match': 'a',
            'Get tag and word of match': 'b',
            'Count matches': 'c',
            'Get role of match': 'f',
            'Get "role:dependent", matching governor': 'd',
            'Get "role:governor", matching dependent': 'g',
            'Get lemmata': 'l',
            'Get tokens by role': 'm',
            'Get dependency index of regular expression match': 'n',
            'Get part-of-speech tag': 'p',
            'Regular expression search': 'r',
            'Simple search string search': 's',
            'Get tokens': 't',
            'Get words': 'w',
            'Get tokens matching regular expression': 'h',
            'Get tokens matching list': 'e'}

    option_dict = {'Trees': ['Get words', 
                             'Get tag and word of match', 
                             'Count matches', 
                             'Get part-of-speech tag'],
                   'Tokens': ['Get tokens matching regular expression', 
                             'Get tokens matching list'], 
                   'Dependencies':
                            ['Get role of match',
                             'Get lemmata',
                             'Get tokens',
                             'Get tokens by role',
                             'Get "role:dependent", matching governor',
                             'Get "role:governor", matching dependent',
                             'Get distance from root for regex match'],
                   'Plaintext': 
                            ['Regular expression search', 
                             'Simple search string search']}

    sort_trans = {'None': False,
                  'Total': 'total',
                  'Inverse total': 'infreq',
                  'Name': 'name',
                  'Increase': 'increase',
                  'Decrease': 'decrease',
                  'Static': 'static',
                  'Turbulent': 'turbulent'}

    spec_quer_translate = {'Participants': 'participants',
                           'Any': 'any',
                           'Processes': 'processes',
                           'Subjects': 'subjects',
                           'Entities': 'entities'}

    from dictionaries.process_types import processes
    from corpkit.other import as_regex
    tregex_qs = {'Imperatives': r'ROOT < (/(S|SBAR)/ < (VP !< VBD !< VBG !$ NP !$ SBAR < NP !$-- S !$-- VP !$ VP)) !<< (/\?/ !< __) !<<- /-R.B-/ !<<, /(?i)^(-l.b-|hi|hey|hello|oh|wow|thank|thankyou|thanks|welcome)$/',
                     'Unmodalised declaratives': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP !< MD)))',
                     'Modalised declaratives': r'ROOT < (S < (/(NP|SBAR|VP)/ $+ (VP < MD)))',
                     'Interrogative': r'ROOT << (/\?/ !< __)',
                     'Mental processes': r'/^(S|ROOT)/ < (VP <+(VP) (VP <<# /%s/))' % as_regex(processes.mental, boundaries = 'w'),
                     'Verbal processes': r'/^(S|ROOT)/ < (VP <+(VP) (VP <<# /%s/))' % as_regex(processes.verbal, boundaries = 'w'),
                     'Relational processes': r'/^(S|ROOT)/ < (VP <+(VP) (VP <<# /%s/))' % as_regex(processes.relational, boundaries = 'w')}

    # dep type
    depdict = {'Basic': 'basic-dependencies', 
                   'Collapsed': 'collapsed-dependencies', 
                   'CC-processed': 'collapsed-ccprocessed-dependencies'}


    # not currently using this sort feature---should use in conc though
    import itertools
    direct = itertools.cycle([0,1]).next

    def data_sort(pane = 'interrogate', sort_direction = False):
        """sort spreadsheets ... not currently used"""
        import pandas
        if pane == 'interrogate':
            df = make_df_from_model(editor_tables[interro_results])
            if need_make_totals(df):
                df = make_df_totals(df)
            df_tot = pandas.DataFrame(df.sum(), dtype = object)
            update_spreadsheet(interro_results, df_to_show = df, height = 340, just_default_sort = True, width = 650)
            update_spreadsheet(interro_totals, df_to_show = df_tot, height = 10, just_default_sort = True, width = 650)
        elif pane == 'edit':
            df = make_df_from_model(editor_tables[o_editor_results])
            if need_make_totals(df):
                df = make_df_totals(df)
            df_tot = pandas.DataFrame(df.sum(), dtype = object)
            update_spreadsheet(o_editor_results, df_to_show = df, height = 340, model = editor_tables[o_editor_results], just_default_sort = True, width = 720)
            update_spreadsheet(o_editor_totals, df_to_show = df_tot, height = 10, model = editor_tables[o_editor_totals], just_default_sort = True, width = 720)
            df = make_df_from_model(editor_tables[n_editor_results])
            if need_make_totals(df):
                df = make_df_totals(df)
            df_tot = pandas.DataFrame(df.sum(), dtype = object)
            update_spreadsheet(n_editor_results, df_to_show = None, height = 340, model = editor_tables[n_editor_results], just_default_sort = True, width = 720)
            update_spreadsheet(n_editor_totals, df_to_show = None, height = 10, model = editor_tables[n_editor_totals], just_default_sort = True, width = 720)
        elif pane == 'plot':
            pass

    def do_interrogation():
        Button(tab1, text = 'Interrogate', command = ignore).grid(row = 17, column = 1, sticky = E)
        note.progvar.set(0)
        """performs an interrogation"""
        import pandas
        from corpkit import interrogator
        
        # spelling conversion?
        conv = (spl.var).get()
        if conv == 'Convert spelling' or conv == 'Off':
            conv = False
        
        # lemmatag: do i need to add as button if trees?
        lemmatag = False
        query = False

        # special query: add to this list!
        if special_queries.get() != 'Off' and special_queries.get() != 'Stats':
            query = spec_quer_translate[special_queries.get()]

        else:
            if special_queries.get() != 'Stats':
                query = qa.get(1.0, END)
                query = query.replace('\n', '')
                # allow list queries
                if query.startswith('[') and query.endswith(']'):
                    query = query.lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
                else:
                    # convert special stuff
                    query = remake_special_query(query)

        if funfil.get() is not False and funfil.get() != '':
            ff = remake_special_query(funfil.get())
        else:
            ff = False

        # make name
        the_name = namer(nametext.get(), type_of_data = 'interrogation')
        
        selected_option = transdict[datatype_chosen_option.get()]
        interrogator_args = {'query': query,
                             'lemmatise': lem.get(),
                             'phrases': phras.get(),
                             'titlefilter': tit_fil.get(),
                             'case_sensitive': case_sensitive.get(),
                             'convert_spelling': conv,
                             'root': root,
                             'note': note,
                             'df1_always_df': True,
                             'function_filter': ff,
                             'dep_type': depdict[kind_of_dep.get()]}

        if only_sel_speakers.get():
            ids = [int(i) for i in speaker_listbox.curselection()]
            jspeak = [speaker_listbox.get(i) for i in ids]
            # in the gui, we can't do 'each' queries (right now)
            if 'ALL' in jspeak:
                jspeak = 'each'
                #get_speaker_names_from_xml_corpus(corpus_fullpath.get())
            interrogator_args['just_speakers'] = jspeak

        lemmatag = False
        if lemtag.get() != 'None':
            if lemtag.get() == 'Noun':
                lemmatag = 'N'
            if lemtag.get() == 'Adjective':
                lemmatag = 'A'
            if lemtag.get() == 'Verb':
                lemmatag = 'V'
            if lemtag.get() == 'Adverb':
                lemmatag = 'R'
        if lemmatag is not False:
            interrogator_args['lemmatag'] = lemmatag

        pf = posfil.get()
        if pf is not False and pf != '':
            interrogator_args['pos_filter'] = pf

        if corpus_fullpath.get() == '':
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: You need to select a corpus.' % thetime
            Button(tab1, text = 'Interrogate', command = do_interrogation).grid(row = 17, column = 1, sticky = E)
            return

        if special_queries.get() == 'Stats':
            selected_option = 'v'
            interrogator_args['query'] = 'any'

        interrodata = interrogator(corpus_fullpath.get(), selected_option, **interrogator_args)

        if not interrodata or interrodata == 'Bad query':
            Button(tab1, text = 'Interrogate', command = do_interrogation).grid(row = 17, column = 1, sticky = E)
            update_spreadsheet(interro_results, df_to_show = None, height = 340, width = 650)
            update_spreadsheet(interro_totals, df_to_show = None, height = 10, width = 650)            
            return

        # make non-dict results into dict, so we can iterate
        interrogation_returned_dict = False
        if type(interrodata) != dict:
            dict_of_results = {the_name: interrodata}
        else:
            dict_of_results = interrodata
            interrogation_returned_dict = True

        # remove dummy entry from master
        try:
            del all_interrogations['None']
        except KeyError:
            pass

        # post-process each result and add to master list
        for nm, r in sorted(dict_of_results.items()):
            # drop over 1000?
            # type check probably redundant now
            if 'results' in r._asdict().keys():
                large = [n for i, n in enumerate(list(r.results.columns)) if i > 9999]
                r.results.drop(large, axis = 1, inplace = True)
                r.results.drop('Total', errors = 'ignore', inplace = True)
                r.results.drop('Total', errors = 'ignore', inplace = True, axis = 1)

            # add interrogation to master
            if interrogation_returned_dict:
                all_interrogations[the_name + '-' + nm] = r
            else:
                all_interrogations[nm] = r

        # show most recent (alphabetically last) interrogation spreadsheet
        recent_interrogation_name = all_interrogations.keys()[-1]
        recent_interrogation_data = all_interrogations[recent_interrogation_name]

        name_of_interro_spreadsheet.set(recent_interrogation_name)
        i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))

        # total in a way that tkintertable likes
        totals_as_df = pandas.DataFrame(recent_interrogation_data.totals, dtype = object)

        # update spreadsheets
        if 'results' in recent_interrogation_data._asdict().keys():
            update_spreadsheet(interro_results, recent_interrogation_data.results, height = 340, indexwidth = 70, width = 650)
        update_spreadsheet(interro_totals, totals_as_df, height = 10, indexwidth = 70, width = 650)
        
        refresh()
        
        # add current subcorpora to editor menu
        #subc_listbox.configure(state = NORMAL)
        subc_listbox.delete(0, 'end')
        for e in list(r.results.index):
            if e != 'tkintertable-order':
                subc_listbox.insert(END, e)
        #subc_listbox.configure(state = DISABLED)



        #reset name
        nametext.set('untitled')

        Button(tab1, text = 'Update interrogation', command = lambda: update_all_interrogations(pane = 'interrogate')).grid(row = 17, column = 2, sticky = E)
        Button(tab1, text = 'Interrogate', command = do_interrogation).grid(row = 17, column = 1, sticky = E)

    class MyOptionMenu(OptionMenu):
        """Simple OptionMenu for things that don't change"""
        def __init__(self, tab1, status, *options):
            self.var = StringVar(tab1)
            self.var.set(status)
            OptionMenu.__init__(self, tab1, self.var, *options)
            self.config(font=('calibri',(12)),width=20)
            self['menu'].config(font=('calibri',(10)))
    
    # corpus path setter
    corpus_fullpath = StringVar()
    corpus_fullpath.set('')
    basepath = StringVar()
    basepath.set('Select corpus')
    subcorpora = {corpus_fullpath.get(): ['None']}

    def getdir(ask = True):
        import os
        if os.path.isdir(os.path.join(project_fullpath.get(), 'data')):
            initdir = os.path.join(project_fullpath.get(), 'data')
        else:
            initdir = False
        if ask:
            fp = tkFileDialog.askdirectory(title = 'Select corpus', initialdir = initdir)
        else:
            fp = corpus_fullpath.get()
        if not fp:
            return
        corpus_fullpath.set(fp)
        subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
        if len(subdrs) == 0:
            charttype.set('bar')
        basepath.set(os.path.basename(fp))
        subs = sorted([d for d in os.listdir(fp) if os.path.isdir(os.path.join(fp, d))])
        for k in subcorpora.keys():
            del subcorpora[k]
        subcorpora[fp] = subs
        pick_subcorpora['menu'].delete(0, 'end')
        if len(subs) > 0:
            pick_subcorpora.config(state = NORMAL)
            for choice in subs:
                pick_subcorpora['menu'].add_command(label=choice, command=Tkinter._setit(subc_pick, choice))
        else:
            pick_subcorpora.config(state = NORMAL)
            pick_subcorpora['menu'].add_command(label='None', command=Tkinter._setit(subc_pick, 'None'))
            pick_subcorpora.config(state = DISABLED)
        path_to_new_unparsed_corpus.set(fp)
        add_corpus_button.set('Added: "%s"' % os.path.basename(fp))
        sel_corpus.set(fp)        
        parse_button_text.set('Parse corpus: %s' % os.path.basename(fp))
        add_subcorpora_to_build_box(fp)
        sel_corpus_button.set('Corpus selected: "%s"' % os.path.basename(fp))
        note.progvar.set(0)
        lab.set('Concordancing: %s' % os.path.basename(corpus_fullpath.get()))
        time = strftime("%H:%M:%S", localtime())
        for i in names:
            names.pop()
        togglespeaker()
        print '%s: Set corpus directory: "%s"' % (time, os.path.basename(fp))
    
    Label(tab1, text = 'Corpus:').grid(row = 0, column = 0, sticky = W)
    Button(tab1, textvariable = basepath, command = getdir, width = 30).grid(row = 0, column = 0, columnspan = 2, sticky = E)

    # function filter
    funfil = StringVar()
    Label(tab1, text = 'Function filter:').grid(row = 10, column = 0, sticky = W)
    #funfil.set(r'(nsubj|nsubjpass)')
    funfil.set('')
    q = Entry(tab1, textvariable = funfil, width = 31, state = DISABLED)
    q.grid(row = 10, column = 0, columnspan = 2, sticky = E)

    # pos filter
    posfil = StringVar()
    Label(tab1, text = 'POS filter:').grid(row = 11, column = 0, sticky = W)
    #posfil.set(r'^n')
    posfil.set(r'')
    qr = Entry(tab1, textvariable = posfil, width = 31, state = DISABLED)
    qr.grid(row = 11, column = 0, columnspan = 2, sticky = E)

    # lemma tags
    lemtags = tuple(('Off', 'Noun', 'Verb', 'Adjective', 'Adverb'))
    lemtag = StringVar(root)
    lemtag.set('')
    Label(tab1, text = 'Result word class (for lemmatisation):').grid(row = 12, column = 0, columnspan = 2, sticky = W)
    lmt = OptionMenu(tab1, lemtag, *lemtags)
    lmt.config(state = NORMAL)
    lmt.grid(row = 12, column = 1, sticky=E)
    #lemtag.trace("w", d_callback)

    def togglespeaker(*args):
        """this adds names to the speaker listbox"""
        if len(names) == 0:
            from corpkit.build import get_speaker_names_from_xml_corpus
            # try to get the unparsed corpus
            corp = corpus_fullpath.get() # .replace('-parsed', '').replace('-stripped', '')
            try:
                ns = get_speaker_names_from_xml_corpus(corp)
            except:
                return
            for n in ns:
                names.append(n)
        lbs = []
        delfrom = []
        if int(only_sel_speakers.get()) == 1:
            lbs.append(speaker_listbox)
        else:
            delfrom.append(speaker_listbox)
        if int(only_sel_speakers_conc.get()) == 1:
            lbs.append(speaker_listbox_conc)
        else:
            delfrom.append(speaker_listbox_conc)
        for lb in lbs:
            lb.configure(state = NORMAL)
            lb.delete(0, END)
            lb.insert(END, 'ALL')
            for id in names:
                lb.insert(END, id)
        for lb in delfrom:
            lb.configure(state = NORMAL)
            lb.delete(0, END)
            lb.configure(state = DISABLED)

    # speaker names
    # save these with project!
    only_sel_speakers = IntVar()
    speakcheck = Checkbutton(tab1, text="Speakers", variable=only_sel_speakers, command = togglespeaker)
    speakcheck.grid(column = 0, row = 13, sticky=W)
    only_sel_speakers.trace("w", togglespeaker)

    spk_scrl = Frame(tab1)
    spk_scrl.grid(row = 13, column = 0, rowspan = 2, columnspan = 2, sticky = E)
    spk_sbar = Scrollbar(spk_scrl)
    spk_sbar.pack(side=RIGHT, fill=Y)
    speaker_listbox = Listbox(spk_scrl, selectmode = SINGLE, width = 32, height = 4, 
                              yscrollcommand=spk_sbar.set, exportselection = False)
    speaker_listbox.pack()
    speaker_listbox.configure(state = DISABLED)
    spk_sbar.config(command=speaker_listbox.yview)

    # dep type
    dep_types = tuple(('Basic', 'Collapsed', 'CC-processed'))
    kind_of_dep = StringVar(root)
    kind_of_dep.set('CC-processed')
    Label(tab1, text = 'Dependency type:').grid(row = 15, column = 0, sticky = W)
    pick_dep_type = OptionMenu(tab1, kind_of_dep, *dep_types)
    pick_dep_type.config(state = DISABLED)
    pick_dep_type.grid(row = 15, column = 1, sticky=E)
    #kind_of_dep.trace("w", d_callback)

    # query
    entrytext = StringVar()

    Label(tab1, text = 'Query:').grid(row = 4, column = 0, sticky = 'NW')
    entrytext.set(r'JJ > (NP <<# /NN.?/)')
    qa = Text(tab1, width = 44, height = 4, borderwidth = 0.5, 
              font = ("Courier New", 14), undo = True, relief = SUNKEN)
    qa.grid(row = 5, column = 0, columnspan = 2, sticky = E)

    def entry_callback(*args):
        qa.config(state = NORMAL)
        qa.delete(1.0, END)
        qa.insert(END, entrytext.get())

    entrytext.trace("w", entry_callback)

    def onselect(evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        callback()
        datatype_chosen_option.set(value)
        datatype_listbox.select_set(index)

    # boolean interrogation arguments
    lem = IntVar()
    lbut = Checkbutton(tab1, text="Lemmatise", variable=lem, onvalue = True, offvalue = False)
    lbut.grid(column = 0, row = 7, sticky=W)
    phras = IntVar()
    mwbut = Checkbutton(tab1, text="Multiword results", variable=phras, onvalue = True, offvalue = False)
    mwbut.grid(column = 1, row = 7, sticky=E)
    tit_fil = IntVar()
    tfbut = Checkbutton(tab1, text="Filter titles", variable=tit_fil, onvalue = True, offvalue = False)
    tfbut.grid(row = 8, column = 0, sticky=W)
    case_sensitive = IntVar()
    Checkbutton(tab1, text="Case sensitive", variable=case_sensitive, onvalue = True, offvalue = False).grid(row = 8, column = 1, sticky=E)

    Label(tab1, text = 'Normalise spelling:').grid(row = 9, column = 0, sticky = W)
    spl = MyOptionMenu(tab1, 'Off','UK','US')
    spl.grid(row = 9, column = 1, sticky = E)

    def callback(*args):
        """if the drop down list for data type changes, fill options"""
        #try:
        #    curselect = int(datatype_listbox.curselection()[0])
        #except IndexError:
        #    curselect = False
        datatype_listbox.delete(0, 'end')
        chosen = datatype_picked.get()
        lst = option_dict[chosen]
        for e in lst:
            datatype_listbox.insert(END, e)

        #datatype_listbox.select_set(0)

        if chosen == 'Dependencies':
            pick_dep_type.configure(state = NORMAL)
            q.configure(state = NORMAL)
            qr.configure(state = NORMAL)
            lmt.configure(state = DISABLED)
            mwbut.configure(state = DISABLED)
            tfbut.configure(state = DISABLED)
            entrytext.set(r'\b(m.n|wom.n|child(ren)?)\b')
            if datatype_chosen_option.get() == 'Get tokens by role':
                entrytext.set(r'\b(amod|nn|advm|vmod|tmod)\b')
        else:
            pick_dep_type.configure(state = DISABLED)
            q.configure(state = DISABLED)
            qr.configure(state = DISABLED)
            lmt.configure(state = NORMAL)
            mwbut.configure(state = NORMAL)
            tfbut.configure(state = NORMAL)
        if chosen == 'Trees':
            entrytext.set(r'JJ > (NP <<# /NN.?/)')
        if chosen == 'Plaintext':
            entrytext.set(r'\b(m.n|wom.n|child(ren)?)\b')
            if datatype_chosen_option.get() == 'Simple search string search':
                entrytext.set(r'[cat,cats,mouse,mice,cheese]')
            elif datatype_chosen_option.get() == 'Regular expression search':
                entrytext.set(r'(m.n|wom.n|child(ren)?)')
        if chosen == 'Tokens':
            entrytext.set(r'\b(m.n|wom.n|child(ren)?)\b')
            if datatype_chosen_option.get() == 'Get tokens matching regular expression':
                entrytext.set(r'(m.n|wom.n|child(ren)?)')
            elif datatype_chosen_option.get() == 'Get tokens matching list':
                entrytext.set(r'[cat,cats,mouse,mice,cheese]')
        #if curselect is not False:
        #    datatype_listbox.select_set(curselect)
        #else:
        #    datatype_listbox.select_set(0)


    datatype_picked = StringVar(root)
    datatype_picked.set('Trees')
    Label(tab1, text = 'Kind of data:').grid(row = 1, column = 0, sticky = W)
    pick_a_datatype = OptionMenu(tab1, datatype_picked, *tuple(('Trees', 'Dependencies', 'Tokens', 'Plaintext')))
    pick_a_datatype.configure(width = 26, justify = CENTER)
    pick_a_datatype.grid(row = 1, column = 1, columnspan = 1, sticky = E)
    datatype_picked.trace("w", callback)

    Label(tab1, text = 'Search type:').grid(row = 3, column = 0, sticky = 'NW')
    frm = Frame(tab1)
    frm.grid(row = 3, column = 0, columnspan = 2, sticky = E)
    dtscrollbar = Scrollbar(frm)
    dtscrollbar.pack(side=RIGHT, fill=Y)
    datatype_listbox = Listbox(frm, selectmode = BROWSE, width = 32, height = 5, 
                        yscrollcommand=dtscrollbar.set, exportselection = False)
    datatype_listbox.pack()
    dtscrollbar.config(command=datatype_listbox.yview)
    datatype_chosen_option = StringVar()
    datatype_chosen_option.set('Get words')
    #datatype_chosen_option.set('w')
    x = datatype_listbox.bind('<<ListboxSelect>>', onselect)
    # hack: change it now to populate below 
    datatype_picked.set('Trees')
    datatype_listbox.select_set(0)

    def q_callback(*args):
        if special_queries.get() == 'Off':
            q.configure(state=NORMAL)
            qa.configure(state=NORMAL)
            qr.configure(state=NORMAL)
        else:
            entrytext.set('')
            entry_callback()
            q.configure(state=DISABLED)
            qa.configure(state=DISABLED)
            qr.configure(state=DISABLED)
            #almost everything should be disabled ..

    queries = tuple(('Off', 'Any', 'Participants', 'Processes', 'Subjects', 'Stats'))
    special_queries = StringVar(root)
    special_queries.set('Off')
    Label(tab1, text = 'Preset query:').grid(row = 6, column = 0, sticky = W)
    pick_a_query = OptionMenu(tab1, special_queries, *queries)
    pick_a_query.grid(row = 6, column = 1, sticky=E)
    special_queries.trace("w", q_callback)

    # Interrogation name
    nametext = StringVar()
    nametext.set('untitled')
    Label(tab1, text = 'Interrogation name:').grid(row = 16, column = 0, sticky = W)
    Entry(tab1, textvariable = nametext).grid(row = 16, column = 1, sticky = E)

    def query_help():
        import webbrowser
        webbrowser.open('file://' + resource_path('user_guide.html').replace('corpkit/corpkit/corpkit', 'corpkit/corpkit'), new = 0)
        #webbrowser.open_new('http://htmlpreview.github.io/?https://raw.githubusercontent.com/interrogator/corpkit/master/user_guide.html')

    # query help, interrogate button
    #Button(tab1, text = 'Query help', command = query_help).grid(row = 14, column = 0, sticky = W)
    Button(tab1, text = 'Interrogate', command = do_interrogation).grid(row = 17, column = 1, sticky = E)

    # name to show above spreadsheet 0
    i_resultname = StringVar()
    name_of_interro_spreadsheet = StringVar()
    name_of_interro_spreadsheet.set('')
    i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))
    Label(tab1, textvariable = i_resultname, 
          font = ("Helvetica", 12, "bold")).grid(row = 0, 
           column = 2, sticky = W, padx=20, pady=0)    
    
    # make spreadsheet frames for interrogate pane
    interro_results = Frame(tab1, height = 45, width = 25, borderwidth = 2)
    interro_results.grid(column = 2, row = 1, rowspan=14, padx=20, pady=5)

    interro_totals = Frame(tab1, height = 1, width = 20, borderwidth = 2)
    interro_totals.grid(column = 2, row = 15, rowspan=2, padx=20, pady=5)

    # show nothing in them yet
    update_spreadsheet(interro_results, df_to_show = None, height = 450, width = 800)
    update_spreadsheet(interro_totals, df_to_show = None, height = 10, width = 800)

    ##############    ##############     ##############     ##############     ############## 
    # EDITOR TAB #    # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB # 
    ##############    ##############     ##############     ##############     ############## 

    def exchange_interro_branch(namedtupname, newdata, branch = 'results'):
        """replaces a namedtuple results/totals with newdata
           --- such a hack, should upgrade to recordtype"""
        namedtup = all_interrogations[namedtupname]
        if branch == 'results' and 'results' in namedtup._asdict().keys():
            the_branch = namedtup.results
            the_branch.drop(the_branch.index, inplace = True)
            the_branch.drop(the_branch.columns, axis = 1, inplace = True)
            for i in list(newdata.columns):
                the_branch[i] = i
            for index, i in enumerate(list(newdata.index)):
                the_branch.loc[i] = newdata.ix[index]
        elif branch == 'totals' and 'totals' in namedtup._asdict().keys():
            the_branch = namedtup.totals
            the_branch.drop(the_branch.index, inplace = True)
            for index, datum in zip(newdata.index, newdata.iloc[:,0].values):
                the_branch.set_value(index, datum)
        all_interrogations[namedtupname] = namedtup

    def update_interrogation(table_id, id, is_total = False):
        """takes any changes made to spreadsheet and saves to the interrogation
        id: 0 = interrogator
            1 = old editor window
            2 = new editor window"""

        model=editor_tables[table_id]
        newdata = make_df_from_model(model)
        if need_make_totals(newdata):
            newdata = make_df_totals(newdata)

        if id == 0:
            name_of_interrogation = name_of_interro_spreadsheet.get()
        if id == 1:
            name_of_interrogation = name_of_o_ed_spread.get()
        if id == 2:
            name_of_interrogation = name_of_n_ed_spread.get()
        if not is_total:
            exchange_interro_branch(name_of_interrogation, newdata, branch = 'results')
        else:
            exchange_interro_branch(name_of_interrogation, newdata, branch = 'totals')

    def update_all_interrogations(pane = 'interrogate'):
        import pandas
        """update all_interrogations within spreadsheet data
        need a very serious cleanup!"""
        # to do: only if they are there!
        if pane == 'interrogate':
            update_interrogation(interro_results, id = 0)
            update_interrogation(interro_totals, id = 0, is_total = True)
        if pane == 'edit':
            update_interrogation(o_editor_results, id = 1)
            update_interrogation(o_editor_totals, id = 1, is_total = True)
            # update new editor sheet if it's there
            if name_of_n_ed_spread.get() != '':
                update_interrogation(n_editor_results, id = 2)
                update_interrogation(n_editor_totals, id = 2, is_total = True)
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Updated interrogations with manual data.' % thetime
        if pane == 'interrogate':
            the_data = all_interrogations[name_of_interro_spreadsheet.get()]
            tot = pandas.DataFrame(the_data.totals, dtype = object)
            if 'results' in the_data._asdict().keys():
                update_spreadsheet(interro_results, the_data.results, height = 340, indexwidth = 70, width = 650)
            update_spreadsheet(interro_totals, tot, height = 10, indexwidth = 70, width = 650)
        if pane == 'edit':
            the_data = all_interrogations[name_of_o_ed_spread.get()]
            there_is_new_data = False
            try:
                newdata = all_interrogations[name_of_n_ed_spread.get()]
                there_is_new_data = True
            except:
                pass
            if 'results' in the_data._asdict().keys():
                update_spreadsheet(o_editor_results, the_data.results, height = 140, indexwidth = 70, width = 720)
            update_spreadsheet(o_editor_totals, pandas.DataFrame(the_data.totals, dtype = object), height = 10, indexwidth = 70, width = 720)
            if there_is_new_data:
                if newdata != 'None' and newdata != '':
                    if 'results' in the_data._asdict().keys():
                        update_spreadsheet(n_editor_results, newdata.results, indexwidth = 70, height = 140, width = 720)
                    update_spreadsheet(n_editor_totals, pandas.DataFrame(newdata.totals, dtype = object), height = 10, indexwidth = 70, width = 720)
            if name_of_o_ed_spread.get() == name_of_interro_spreadsheet.get():
                the_data = all_interrogations[name_of_interro_spreadsheet.get()]
                tot = pandas.DataFrame(the_data.totals, dtype = object)
                if 'results' in the_data._asdict().keys():
                    update_spreadsheet(interro_results, the_data.results, height = 340, indexwidth = 70, width = 650)
                update_spreadsheet(interro_totals, tot, height = 10, indexwidth = 70, width = 650)
        
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Updated spreadsheet display in edit window.' % thetime

    def is_number(s):
        """check if str can be added for the below"""
        try:
            float(s) # for int, long and float
        except ValueError:
            try:
                complex(s) # for complex
            except ValueError:
                return False
        return True

    def do_editing():
        Button(tab2, text = 'Edit', command = ignore).grid(row = 20, column = 1, sticky = E)
        """what happens when you press edit"""
        import pandas
        from corpkit import editor

        # translate operation into interrogator input
        operation_text = opp.get()
        if operation_text == 'None' or operation_text == 'Select an operation':
            operation_text = None
        else:
            operation_text = opp.get()[0]

        # translate dataframe2 into interrogator input
        data2 = data2_pick.get()
        if data2 == 'None' or data2 == '' or data2 == 'Self':
            data2 = False

        if data2:
            if df2branch.get() == 'results':
                try:
                    data2 = all_interrogations[data2].results
                except AttributeError:
                    print 'Interrogation has no results branch.'
            elif df2branch.get() == 'totals':
                data2 = all_interrogations[data2].totals
            if transpose.get():
                data2 = data2.T

        the_data = all_interrogations[name_of_o_ed_spread.get()]
        if df1branch.get() == 'results':
            try:
                data1 = the_data.results
            except AttributeError:
                print 'Interrogation has no results branch.'
        elif df1branch.get() == 'totals':
            data1 = the_data.totals

        if (spl_editor.var).get() == 'Off' or (spl_editor.var).get() == 'Convert spelling':
            spel = False
        else:
            spel = (spl_editor.var).get()

        # editor kwargs
        editor_args = {'operation': operation_text,
                       'dataframe2': data2,
                       'spelling': spel,
                       'sort_by': sort_trans[sort_val.get()],
                       'df1_always_df': True}

        if do_sub.get() == 'Merge':
            editor_args['merge_subcorpora'] = subc_sel_vals
        elif do_sub.get() == 'Keep':
            editor_args['just_subcorpora'] = subc_sel_vals
        elif do_sub.get() == 'Span':
            editor_args['span_subcorpora'] = subc_sel_vals
        elif do_sub.get() == 'Skip':
            editor_args['skip_subcorpora'] = subc_sel_vals

        if toreplace_string.get() != '':
            if replacewith_string.get() == '':
                replacetup = toreplace_string.get()
            else:
                replacetup = (toreplace_string.get(), replacewith_string.get())
            editor_args['replace_names'] = replacetup

        # special query: add to this list!
        #if special_queries.get() != 'Off':
            #query = spec_quer_translate[special_queries.get()]
        
        entry_do_with = entry_regex.get()
        # allow list queries
        if entry_do_with.startswith('[') and entry_do_with.endswith(']'):
            entry_do_with = entry_do_with.lower().lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
        else:
            # convert special stuff
            entry_do_with = remake_special_query(entry_do_with)

        if do_with_entries.get() == 'Merge':
            editor_args['merge_entries'] = entry_do_with
            nn = newname_var.get()
            if nn == '':
                editor_args['newname'] = False
            elif is_number(nn):
                editor_args['newname'] = int(nn)
            else:
                editor_args['newname'] = nn
        elif do_with_entries.get() == 'Keep':
            editor_args['just_entries'] = entry_do_with
        elif do_with_entries.get() == 'Skip':
            editor_args['skip_entries'] = entry_do_with
        
        if new_subc_name.get() != '':
            editor_args['new_subcorpus_name'] = new_subc_name.get()
        if newname_var.get() != '':
            editor_args['new_subcorpus_name'] = newname_var.get()
            
        if keep_stats_setting.get() == 1:
            editor_args['keep_stats'] = True

        if rem_abv_p_set.get() == 1:
            editor_args['remove_above_p'] = True

        if just_tot_setting.get() == 1:
            editor_args['just_totals'] = True

        if transpose.get():
            data1 = data1.T

        if keeptopnum.get() != 'all':
            try:
                numtokeep = int(keeptopnum.get())
            except ValueError:
                print 'Keep top n results value must be number.'
                Button(tab2, text = 'Edit', command = lambda: do_editing()).grid(row = 20, column = 1, sticky = E)
                return
            editor_args['keep_top'] = numtokeep
        
        # do editing
        r = editor(data1, **editor_args)
        
        if not r:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Editing caused an error.' % thetime
            Button(tab2, text = 'Edit', command = lambda: do_editing()).grid(row = 20, column = 1, sticky = E)
            return

        if len(list(r.results.columns)) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Editing removed all results.' % thetime
            Button(tab2, text = 'Edit', command = lambda: do_editing()).grid(row = 20, column = 1, sticky = E)
            return

        # drop over 1000?
        # results should now always be dataframes, so this if is redundant
        if type(r.results) == pandas.core.frame.DataFrame:
            large = [n for i, n in enumerate(list(r.results.columns)) if i > 9999]
            r.results.drop(large, axis = 1, inplace = True)

        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Result editing completed successfully.' % thetime
        
        # name the edit
        the_name = namer(edit_nametext.get(), type_of_data = 'edited')

        # add edit to master dict
        all_interrogations[the_name] = r

        # update edited results speadsheet name
        name_of_n_ed_spread.set(all_interrogations.keys()[-1])
        editoname.set('Edited results: %s' % str(name_of_n_ed_spread.get()))
        
        # add current subcorpora to editor menu
        for subcl in [subc_listbox]:
            #subcl.configure(state = NORMAL)
            subcl.delete(0, 'end')
            for e in list(r.results.index):
                if e != 'tkintertable-order':
                    subcl.insert(END, e)
            #subcl.configure(state = DISABLED)

        # update edited spreadsheets
        most_recent = all_interrogations[all_interrogations.keys()[-1]]
        if 'results' in most_recent._asdict().keys():
            update_spreadsheet(n_editor_results, most_recent.results, height = 140, width = 720)
        update_spreadsheet(n_editor_totals, pandas.DataFrame(most_recent.totals, dtype = object), height = 10, width = 720)
        
        # add button to update
        Button(tab2, text = 'Update interrogation(s)', command = lambda: update_all_interrogations(pane = 'edit')).grid(row = 21, column = 1, sticky = E)
        
        # finish up
        refresh()
        # restore button
        Button(tab2, text = 'Edit', command = lambda: do_editing()).grid(row = 20, column = 1, sticky = E)

    def df_callback(*args):
        """show names and spreadsheets for what is selected as result to edit
           also, hide the edited results section"""
        if selected_to_edit.get() != 'None':
            name_of_o_ed_spread.set(selected_to_edit.get())
            if 'results' in all_interrogations[name_of_o_ed_spread.get()]._asdict().keys():
                update_spreadsheet(o_editor_results, all_interrogations[name_of_o_ed_spread.get()].results, height = 140, width = 720)
            update_spreadsheet(o_editor_totals, all_interrogations[name_of_o_ed_spread.get()].totals, height = 10, width = 720)
            resultname.set('Results to edit: %s' % str(name_of_o_ed_spread.get()))
        name_of_n_ed_spread.set('')
        editoname.set('Edited results: %s' % str(name_of_n_ed_spread.get()))
        update_spreadsheet(n_editor_results, df_to_show = None, height = 140, width = 720)
        update_spreadsheet(n_editor_totals, df_to_show = None, height = 10, width = 720)
        for subcl in [subc_listbox]:
            subcl.configure(state = NORMAL)
            subcl.delete(0, 'end')
            if name_of_o_ed_spread.get() != '':
                if 'results' in all_interrogations[name_of_o_ed_spread.get()]._asdict().keys():
                    cols = list(all_interrogations[name_of_o_ed_spread.get()].results.index)
                else:
                    cols = list(all_interrogations[name_of_o_ed_spread.get()].totals.index)
                for e in cols:
                    if e != 'tkintertable-order':
                        subcl.insert(END, e) 
        do_sub.set('Off')
        do_with_entries.set('Off')
            #subcl.configure(state = DISABLED)    


    # all interrogations here
    from collections import OrderedDict
    all_interrogations = OrderedDict()
    all_conc = OrderedDict()
    all_interrogations['None'] = 'None'

    # result to edit
    tup = tuple([i for i in all_interrogations.keys()])    
    selected_to_edit = StringVar(root)
    selected_to_edit.set('None')
    x = Label(tab2, text = 'To edit:', font = ("Helvetica", 12, "bold"))
    x.grid(row = 0, column = 0, sticky = W)
    dataframe1s = OptionMenu(tab2, selected_to_edit, *tup)
    dataframe1s.grid(row = 1, column = 0, sticky=W)
    selected_to_edit.trace("w", df_callback)

    # DF1 branch selection
    df1branch = StringVar()
    df1branch.set('results')
    df1box = OptionMenu(tab2, df1branch, 'results', 'totals')
    df1box.config(width = 19)
    df1box.grid(row = 1, column = 1, sticky = E)

    def op_callback(*args):
        if opp.get() != 'None':
            dataframe2s.config(state = NORMAL)
            df2box.config(state = NORMAL)
        elif opp.get() == 'None':
            dataframe2s.config(state = DISABLED)
            df2box.config(state = DISABLED)

    # operation for editor
    opp = StringVar(root)
    opp.set('None')
    operations = ('None', '%', '*', '/', '-', '+', 'combine', 'keywords', 'a', 'd')
    Label(tab2, text='Operation and demonominator:', font = ("Helvetica", 12, "bold")).grid(row = 2, column = 0, sticky = W)
    ops = OptionMenu(tab2, opp, *operations)
    ops.grid(row = 3, column = 0, sticky = W)
    opp.trace("w", op_callback)

    # DF2 option for editor
    tups = tuple(['Self'] + [i for i in all_interrogations.keys()])
    data2_pick = StringVar(root)
    data2_pick.set('Self')
    #Label(tab2, text = 'Denominator:').grid(row = 3, column = 0, sticky = W)
    dataframe2s = OptionMenu(tab2, data2_pick, *tups)
    dataframe2s.config(state = DISABLED, width = 9)
    dataframe2s.grid(row = 3, column = 0, columnspan = 2, sticky = N)

    # DF2 branch selection
    df2branch = StringVar(root)
    df2branch.set('totals')
    df2box = OptionMenu(tab2, df2branch, 'results', 'totals')
    df2box.config(state = DISABLED)
    df2box.grid(row = 3, column = 1, sticky = E)

    # sort by
    Label(tab2, text = 'Sort results by:', font = ("Helvetica", 12, "bold")).grid(row = 4, column = 0, sticky = W)
    sort_val = StringVar(root)
    sort_val.set('None')
    sorts = OptionMenu(tab2, sort_val, 'None', 'Total', 'Inverse total', 'Name','Increase', 'Decrease', 'Static', 'Turbulent')
    sorts.config(width = 9)
    sorts.grid(row = 4, column = 1, sticky = E)

    # spelling again
    Label(tab2, text = 'Spelling:').grid(row = 5, column = 0, sticky = W)
    spl_editor = MyOptionMenu(tab2, 'Off','UK','US')
    spl_editor.grid(row = 5, column = 1, sticky = E)

    # currently broken: just totals button
    just_tot_setting = IntVar()
    just_tot_but = Checkbutton(tab2, text="Just totals", variable=just_tot_setting)
    #just_tot_but.select()
    just_tot_but.grid(column = 0, row = 6, sticky = W)

    keep_stats_setting = IntVar()
    keep_stat_but = Checkbutton(tab2, text="Keep stats", variable=keep_stats_setting)
    #keep_stat_but.select()
    keep_stat_but.grid(column = 1, row = 6, sticky = E)

    rem_abv_p_set = IntVar()
    rem_abv_p_but = Checkbutton(tab2, text="Remove above p", variable=rem_abv_p_set)
    #rem_abv_p_but.select()
    rem_abv_p_but.grid(column = 0, row = 7, sticky = W)

    # transpose
    transpose = IntVar()
    trans_but = Checkbutton(tab2, text="Transpose", variable=transpose, onvalue = True, offvalue = False)
    trans_but.grid(column = 1, row = 7, sticky = E)

    # keep_top
    Label(tab2, text = 'Keep top results:').grid(row = 8, column = 0, sticky = W)
    keeptopnum = StringVar()
    keeptopnum.set('all')
    keeptopbox = Entry(tab2, textvariable = keeptopnum, width = 5)
    keeptopbox.grid(column = 1, row = 8, sticky = E)

    subc_sel_vals = []
    # entries + entry field for regex, off, skip, keep, merge
    Label(tab2, text = 'Edit entries:', font = ("Helvetica", 12, "bold")).grid(row = 9, column = 0, sticky = W, pady = (10, 0))
    
    # edit entries regex box
    entry_regex = StringVar()
    entry_regex.set(r'.*ing$')
    edit_box = Entry(tab2, textvariable = entry_regex, state = DISABLED)
    edit_box.grid(row = 10, column = 1, sticky = E)

    # merge entries newname
    Label(tab2, text = 'Merge name:').grid(row = 11, column = 0, sticky = W)
    newname_var = StringVar()
    newname_var.set('')
    mergen = Entry(tab2, textvariable = newname_var, state = DISABLED)
    mergen.grid(row = 11, column = 1, sticky = E)

    Label(tab2, text = 'Replace in entry names:').grid(row = 12, column = 0, sticky = W)
    Label(tab2, text = 'Replace with:').grid(row = 12, column = 1, sticky = W)
    toreplace_string = StringVar()
    toreplace_string.set('')
    replacewith_string = StringVar()
    replacewith_string.set('')
    toreplace = Entry(tab2, textvariable = toreplace_string)
    toreplace.grid(row = 13, column = 0, sticky = W)
    replacewith = Entry(tab2, textvariable = replacewith_string)
    replacewith.grid(row = 13, column = 1, sticky = E)    
    
    def do_w_callback(*args):
        """if not merging entries, diable input fields"""
        if do_with_entries.get() != 'Off':
            edit_box.configure(state = NORMAL)
        else:
            edit_box.configure(state = DISABLED)
        if do_with_entries.get() == 'Merge':
            mergen.configure(state = NORMAL)
        else:
            mergen.configure(state = DISABLED)

    # options for editing entries
    do_with_entries = StringVar(root)
    do_with_entries.set('Off')
    edit_ent_op = ('Off', 'Skip', 'Keep', 'Merge')
    ed_op = OptionMenu(tab2, do_with_entries, *edit_ent_op)
    ed_op.grid(row = 10, column = 0, sticky = W)
    do_with_entries.trace("w", do_w_callback)

    def onselect_subc(evt):
        """get selected subcorpora: this probably doesn't need to be
           a callback, as they are only needed during do_edit"""
        for i in subc_sel_vals:
            subc_sel_vals.pop()
        wx = evt.widget
        indices = wx.curselection()
        for index in indices:
            value = wx.get(index)
            if value not in subc_sel_vals:
                subc_sel_vals.append(value)

    def do_s_callback(*args):
        """hide subcorpora edit options if off"""
        if do_sub.get() != 'Off':
            pass
            #subc_listbox.configure(state = NORMAL)
        else:
            pass
            #subc_listbox.configure(state = DISABLED)
        if do_sub.get() == 'Merge':
            merge.configure(state = NORMAL)
        else:
            merge.configure(state = DISABLED)

    # subcorpora + optionmenu off, skip, keep
    Label(tab2, text = 'Edit subcorpora:', font = ("Helvetica", 12, "bold")).grid(row = 14, column = 0, sticky = W)
    
    edit_sub_f = Frame(tab2)
    edit_sub_f.grid(row = 14, column = 1, rowspan = 5, sticky = E, pady = (20,0))
    edsub_scbr = Scrollbar(edit_sub_f)
    edsub_scbr.pack(side=RIGHT, fill=Y)
    subc_listbox = Listbox(edit_sub_f, selectmode = EXTENDED, height = 5, 
                           yscrollcommand=edsub_scbr.set, exportselection = False)
    subc_listbox.pack(fill=BOTH)
    edsub_scbr.config(command=subc_listbox.yview)

    xx = subc_listbox.bind('<<ListboxSelect>>', onselect_subc)
    subc_listbox.select_set(0)

    # subcorpora edit options
    do_sub = StringVar(root)
    do_sub.set('Off')
    do_with_subc = OptionMenu(tab2, do_sub, *('Off', 'Skip', 'Keep', 'Merge', 'Span'))
    do_with_subc.grid(row = 16, column = 0, sticky = W)
    do_sub.trace("w", do_s_callback)

    # subcorpora merge name    
    Label(tab2, text = 'Merge name:').grid(row = 17, column = 0, sticky = 'NW')
    new_subc_name = StringVar()
    new_subc_name.set('')
    merge = Entry(tab2, textvariable = new_subc_name, state = DISABLED)
    merge.grid(row = 17, column = 0, sticky = 'SW')
    
    # name the edit
    edit_nametext = StringVar()
    edit_nametext.set('untitled')
    Label(tab2, text = 'Edit name:', font = ("Helvetica", 12, "bold")).grid(row = 19, column = 0, sticky = W)
    msn = Entry(tab2, textvariable = edit_nametext)
    msn.grid(row = 20, column = 0)

    # edit button
    Button(tab2, text = 'Edit', command = lambda: do_editing()).grid(row = 20, column = 1, sticky = E)

    # show spreadsheets
    resultname = StringVar()
    name_of_o_ed_spread = StringVar()
    name_of_o_ed_spread.set('')
    resultname.set('Results to edit: %s' % str(name_of_o_ed_spread.get()))
    Label(tab2, textvariable = resultname, 
          font = ("Helvetica", 12, "bold")).grid(row = 0, 
           column = 2, sticky = W, padx = 20)    
    o_editor_results = Frame(tab2, height = 20, width = 20)
    o_editor_results.grid(column = 2, row = 1, rowspan=9, padx = 20)
    #Label(tab2, text = 'Totals to edit:', 
          #font = ("Helvetica", 12, "bold")).grid(row = 4, 
           #column = 2, sticky = W, pady=0)
    o_editor_totals = Frame(tab2, height = 1, width = 20)
    o_editor_totals.grid(column = 2, row = 10, rowspan=1, padx = 20)
    update_spreadsheet(o_editor_results, df_to_show = None, height = 200, width = 800)
    update_spreadsheet(o_editor_totals, df_to_show = None, height = 10, width = 800)
    editoname = StringVar()
    name_of_n_ed_spread = StringVar()
    name_of_n_ed_spread.set('')
    editoname.set('Edited results: %s' % str(name_of_n_ed_spread.get()))
    Label(tab2, textvariable = editoname, 
          font = ("Helvetica", 12, "bold")).grid(row = 11, 
           column = 2, sticky = W, padx = 20)        
    n_editor_results = Frame(tab2, height = 30, width = 20)
    n_editor_results.grid(column = 2, row = 12, rowspan=9, padx = 20)
    #Label(tab2, text = 'Edited totals:', 
          #font = ("Helvetica", 12, "bold")).grid(row = 15, 
           #column = 2, sticky = W, padx=20, pady=0)
    n_editor_totals = Frame(tab2, height = 1, width = 20)
    n_editor_totals.grid(column = 2, row = 21, rowspan=1, padx = 20)
    update_spreadsheet(n_editor_results, df_to_show = None, height = 200, width = 800)
    update_spreadsheet(n_editor_totals, df_to_show = None, height = 10, width = 800)

    # ????
    #interrogation_name = StringVar()
    #interrogation_name.set('waiting')
    #Label(tab1, textvariable = interrogation_name.get()).grid()
    #root.TEXT_INFO = Label(tab1, height=20, width=80, text="", justify = LEFT, font=("Courier New", 12))

    #################       #################      #################      #################  
    # VISUALISE TAB #       # VISUALISE TAB #      # VISUALISE TAB #      # VISUALISE TAB #  
    #################       #################      #################      #################  

    # where to put the current figure
    thefig = []

    def do_plotting():
        """when you press plot"""
        Button(tab3, text = 'Plot', command = ignore).grid(row = 15, column = 1, sticky = E)
        # junk for showing the plot in tkinter
        import matplotlib
        matplotlib.use('TkAgg')
        from numpy import arange, sin, pi
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
        # implement the default mpl key bindings
        from matplotlib.backend_bases import key_press_handler
        from matplotlib.figure import Figure
        from corpkit import plotter

        if data_to_plot.get() == 'None':
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No data selected to plot.' % (thetime)
            Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid(row = 15, column = 1, sticky = E)
            return

        if plotbranch.get() == 'results':
            if not 'results' in all_interrogations[data_to_plot.get()]._asdict().keys():
                print 'No results branch to plot.'
                Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid(row = 15, column = 1, sticky = E)
                return
            what_to_plot = all_interrogations[data_to_plot.get()].results
        elif plotbranch.get() == 'totals':
            if not 'totals' in all_interrogations[data_to_plot.get()]._asdict().keys():
                print 'No totals branch to plot.'
                Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid(row = 15, column = 1, sticky = E)
                return
            what_to_plot = all_interrogations[data_to_plot.get()].totals
        
        if transpose_vis.get():
            if plotbranch.get() != 'totals':
                what_to_plot = what_to_plot.T

        # determine num to plot
        def determine_num_to_plot(num):
            """translate num to num_to_plot"""
            try:
                num = int(num)
            except:
                if num.lower() == 'all':
                    num = 'all'
                else:
                    num = 7
            return num

        num = determine_num_to_plot(number_to_plot.get())

        the_kind = charttype.get()
        if the_kind == 'Type of chart':
            the_kind = 'line'
        # plotter options
        d = {'num_to_plot': num,
             'kind': the_kind}

        d['style'] = plot_style.get()
        d['tex'] = texuse.get()
        d['black_and_white'] = bw.get()

        if log_x.get() == 1 and log_y.get() == 1:
            d['log'] = 'x,y'
        if log_x.get() == 1 and not log_y.get() == 1:
            d['log'] = 'x'
        if log_y.get() == 1 and not log_x.get() == 1:
            d['log'] = 'y'

        if x_axis_l.get() != '':
            d['x_label'] = x_axis_l.get()
        if x_axis_l.get() == 'None':
            d['x_label'] = False
        if y_axis_l.get() != '':
            d['y_label'] = y_axis_l.get()
        if y_axis_l.get() == 'None':
            d['y_label'] = False

        if cumul.get():
            d['cumulative'] = True

        if chart_cols.get() != 'Default':
            d['colours'] = chart_cols.get()

        legend_loc = legloc.get()
        if legend_loc == 'None':
            d['legend'] = False
        else:
            d['legend_pos'] = legend_loc

        show_totals_in_plot = showtot.get()
        if show_totals_in_plot == 'plot':
            d['show_totals'] = 'plot'
        if show_totals_in_plot == 'legend':
            d['show_totals'] = 'legend'
        if show_totals_in_plot == 'legend + plot':
            d['show_totals'] = 'both'

        d['figsize'] = (12.6, 6.3)

        f = plotter(plotnametext.get(), what_to_plot, **d)
        time = strftime("%H:%M:%S", localtime())
        print '%s: %s plotted.' % (time, plotnametext.get())
        # a Tkinter.DrawingArea
        toolbar_frame = Tkinter.Frame(tab3)
        toolbar_frame.grid(row=18, column=2, columnspan = 3, sticky = N)
        canvas = FigureCanvasTkAgg(f.gcf(), tab3)
        canvas.show()
        canvas.get_tk_widget().grid(column = 2, row = 1, rowspan = 16, padx = 20, columnspan = 3)
        toolbar = NavigationToolbar2TkAgg(canvas,toolbar_frame)
        toolbar.update()
        for i in thefig:
            thefig.pop()
        thefig.append(f.gcf())
        Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid(row = 15, column = 1, sticky = E)

    def save_current_image():
        import os
        # figre out filename
        filename = namer(plotnametext.get(), type_of_data = 'image') + '.png'
        import sys
        defaultextension = '.png' if sys.platform == 'darwin' else ''
        kwarg = {'defaultextension': defaultextension,
                 #'filetypes': [('all files', '.*'), 
                               #('png file', '.png')],
                 'initialfile': filename}
        imagedir = image_fullpath.get()
        if imagedir:
            kwarg['initialdir'] = imagedir

        fo = tkFileDialog.asksaveasfilename(**kwarg)

        #fo = tkFileDialog.asksaveasfile(mode='w', defaultextension=".png")
        if fo is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        #fo.write(f.gcf())
        #fo.close() # `()` was missing.
        thefig[0].savefig(os.path.join(image_fullpath.get(), fo))
        time = strftime("%H:%M:%S", localtime())
        print '%s: %s saved to %s.' % (time, fo, image_fullpath.get())

    # not working
    def image_clear():
        thefig[0].get_tk_widget().grid_forget()

    def reset_plotter_pane():
        return

    # title tab
    Label(tab3, text = 'Image title:').grid(row = 0, column = 0, sticky = 'W', pady = (35, 0))
    plotnametext = StringVar()
    plotnametext.set('Untitled')
    Entry(tab3, textvariable = plotnametext).grid(row = 0, column = 1, pady = (35, 0))

    Label(tab3, text = 'Data to plot:').grid(row = 1, column = 0, sticky = W)
    # select result to plot
    data_to_plot = StringVar(root)
    most_recent = all_interrogations[all_interrogations.keys()[-1]]
    data_to_plot.set(most_recent)
    every_interrogation = OptionMenu(tab3, data_to_plot, *tuple([i for i in all_interrogations.keys()]))
    every_interrogation.grid(column = 0, row = 2, sticky = W, columnspan = 2)

    # branch selection
    plotbranch = StringVar(root)
    plotbranch.set('results')
    plotbox = OptionMenu(tab3, plotbranch, 'results', 'totals')
    #plotbox.config(state = DISABLED)
    plotbox.grid(row = 2, column = 0, sticky = E, columnspan = 2)


    # num_to_plot
    Label(tab3, text = 'Results to show:').grid(row = 4, column = 0, sticky = W)
    number_to_plot = StringVar()
    number_to_plot.set('7')
    Entry(tab3, textvariable = number_to_plot, width = 3).grid(row = 4, column = 1, sticky = E)

    # chart type
    Label(tab3, text='Kind of chart').grid(row = 5, column = 0, sticky = W)
    charttype = StringVar(root)
    charttype.set('line')
    kinds_of_chart = ('line', 'bar', 'barh', 'pie', 'area')
    chart_kind = OptionMenu(tab3, charttype, *kinds_of_chart)
    chart_kind.grid(row = 5, column = 1, sticky = E)

    # axes
    Label(tab3, text = 'x axis label:').grid(row = 6, column = 0, sticky = W)
    x_axis_l = StringVar()
    x_axis_l.set('')
    Entry(tab3, textvariable = x_axis_l).grid(row = 6, column = 1, sticky = W)

    Label(tab3, text = 'y axis label:').grid(row = 7, column = 0, sticky = W)
    y_axis_l = StringVar()
    y_axis_l.set('')
    Entry(tab3, textvariable = y_axis_l).grid(row = 7, column = 1)

    # log options
    log_x = IntVar()
    Checkbutton(tab3, text="Log x axis", variable=log_x).grid(column = 0, row = 8, sticky = W)
    log_y = IntVar()
    Checkbutton(tab3, text="Log y axis", variable=log_y).grid(column = 1, row = 8, sticky = E)

    # transpose
    transpose_vis = IntVar()
    trans_but_vis = Checkbutton(tab3, text="Transpose", variable=transpose_vis, onvalue = True, offvalue = False)
    trans_but_vis.grid(column = 1, row = 9, sticky = E)

    cumul = IntVar()
    cumulbutton = Checkbutton(tab3, text="Cumulative", variable=cumul, onvalue = True, offvalue = False)
    cumulbutton.grid(column = 0, row = 9, sticky = W)

    bw = IntVar()
    Checkbutton(tab3, text="Black and white", variable=bw, onvalue = True, offvalue = False).grid(column = 0, row = 10, sticky = W)
    texuse = IntVar()
    Checkbutton(tab3, text="Use TeX", variable=texuse, onvalue = True, offvalue = False).grid(column = 1, row = 10, sticky = E)


    # chart type
    Label(tab3, text='Colour scheme:').grid(row = 11, column = 0, sticky = W)
    chart_cols = StringVar(root)
    chart_cols.set('Default')
    schemes = tuple(('Default', 'Spectral', 'summer', 'coolwarm', 'pink_r', 'Set1', 'Set2', 
        'Set3', 'brg_r', 'Dark2', 'prism', 'PuOr_r', 'afmhot_r', 'terrain_r', 'PuBuGn_r', 
        'RdPu', 'gist_ncar_r', 'gist_yarg_r', 'Dark2_r', 'YlGnBu', 'RdYlBu', 'hot_r', 'Wistia_r',
        'gist_rainbow_r', 'gist_stern', 'PuBu_r', 'cool_r', 'cool', 'gray', 'copper_r', 
        'Greens_r', 'GnBu', 'gist_ncar', 'spring_r', 'gist_rainbow', 'gist_heat_r', 'Wistia', 
        'OrRd_r', 'CMRmap', 'bone', 'gist_stern_r', 'RdYlGn', 'Pastel2_r', 'spring', 'terrain', 
        'YlOrRd_r', 'Set2_r', 'winter_r', 'PuBu', 'RdGy_r', 'spectral', 'rainbow', 'flag_r', 
        'jet_r', 'RdPu_r', 'gist_yarg', 'BuGn', 'Paired_r', 'hsv_r', 'bwr', 'cubehelix', 
        'Greens', 'PRGn', 'gist_heat', 'spectral_r', 'Paired', 'hsv', 'Oranges_r', 'prism_r', 
        'Pastel2', 'Pastel1_r', 'Pastel1', 'gray_r', 'jet', 'Spectral_r', 'gnuplot2_r', 
        'gist_earth', 'YlGnBu_r', 'copper', 'gist_earth_r', 'Set3_r', 'OrRd', 'gnuplot_r', 
        'ocean_r', 'brg', 'gnuplot2', 'PuRd_r', 'bone_r', 'BuPu', 'Oranges', 'RdYlGn_r', 'PiYG', 
        'CMRmap_r', 'YlGn', 'binary_r', 'gist_gray_r', 'Accent', 'BuPu_r', 'gist_gray', 'flag', 
        'bwr_r', 'RdBu_r', 'BrBG', 'Reds', 'Set1_r', 'summer_r', 'GnBu_r', 'BrBG_r', 'Reds_r', 
        'RdGy', 'PuRd', 'Accent_r', 'Blues', 'autumn_r', 'autumn', 'cubehelix_r', 
        'nipy_spectral_r', 'ocean', 'PRGn_r', 'Greys_r', 'pink', 'binary', 'winter', 'gnuplot', 
        'RdYlBu_r', 'hot', 'YlOrBr', 'coolwarm_r', 'rainbow_r', 'Purples_r', 'PiYG_r', 'YlGn_r', 
        'Blues_r', 'YlOrBr_r', 'seismic', 'Purples', 'seismic_r', 'RdBu', 'Greys', 'BuGn_r', 
        'YlOrRd', 'PuOr', 'PuBuGn', 'nipy_spectral', 'afmhot'))
    ch_col = OptionMenu(tab3, chart_cols, *schemes)
    ch_col.grid(row = 11, column = 1, sticky = E)

    # style
    stys = tuple(('ggplot', 'fivethirtyeight', 'bmh'))
    plot_style = StringVar(root)
    plot_style.set('ggplot')
    Label(tab3, text = 'Plot style:').grid(row = 12, column = 0, sticky = W)
    pick_a_datatype = OptionMenu(tab3, plot_style, *stys)
    pick_a_datatype.grid(row = 12, column = 1, sticky=E)

    # legend pos
    Label(tab3, text='Legend position:').grid(row = 13, column = 0, sticky = W)
    legloc = StringVar(root)
    legloc.set('best')
    locs = tuple(('best', 'outside right', 'upper right', 'right', 'lower right', 'lower left', 'upper left', 'middle', 'none'))
    loc_options = OptionMenu(tab3, legloc, *locs)
    loc_options.grid(row = 13, column = 1, sticky = E)

    # show_totals option
    Label(tab3, text='Show totals: ').grid(row = 14, column = 0, sticky = W)
    showtot = StringVar(root)
    showtot.set('Off')
    showtot_options = tuple(('Off', 'legend', 'plot', 'legend + plot'))
    show_tot_menu = OptionMenu(tab3, showtot, *showtot_options)
    show_tot_menu.grid(row = 14, column = 1, sticky = E)

    # plot button
    Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid(row = 15, column = 1, sticky = E)

    # save image button
    #Button(tab3, text = 'Save image', command = lambda: save_current_image()).grid(column = 2, row = 13)

    # clear image
    #Button(tab3, text = 'Clear image', command = lambda: do_plotting()).grid(column = 3, row = 13)

    # reset pane
    #Button(tab3, text = 'Reset plotter pane', command = lambda: reset_plotter_pane()).grid(column = 4, row = 13)


    ###################     ###################     ###################     ###################
    # CONCORDANCE TAB #     # CONCORDANCE TAB #     # CONCORDANCE TAB #     # CONCORDANCE TAB #
    ###################     ###################     ###################     ###################

    current_conc = ['None']

    def add_conc_lines_to_window(data, loading = False):
        import pandas as pd
        #pd.set_option('display.height', 1000)
        #pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 200)
        import re
        current_conc[0] = data
        if win.get() == 'Window size':
            window = 70
        else:
            window = int(win.get())
        formatl = lambda x: "{0}".format(x[-window:])
        #formatf = lambda x: "{0}".format(x[-20:])
        formatr = lambda x: "{{:<{}s}}".format(data['r'].str.len().max()).format(x[:window])
        lines = data.to_string(header = False, formatters={'l': formatl,
                                                           'r': formatr}).splitlines()
        lines = [re.sub('\s*\.\.\.\s*$', '', s) for s in lines]
        conclistbox.delete(0, END)
        for line in lines:
            conclistbox.insert(END, line)
        thetime = strftime("%H:%M:%S", localtime())
        if loading:
            print '%s: Concordances loaded.' % (thetime)
        else:
            print '%s: Concordancing done: %d results.' % (thetime, len(lines))

    def do_concordancing():
        Button(tab4, text = 'Run', command = ignore).grid(row = 3, column = 4, sticky = E)
        import os
        """when you press 'run'"""
        time = strftime("%H:%M:%S", localtime())
        print '%s: Concordancing in progress ... ' % (time)       
        from corpkit.conc import conc
        if subc_pick.get() == "Subcorpus":
            corpus = corpus_fullpath.get()
        else:
            corpus = os.path.join(corpus_fullpath.get(), subc_pick.get())

        option = corpus_search_type.get()
        if option == 'Trees':
            option = 't'
        elif option == 'Dependencies':
            option = 'd'
        elif option == 'Plaintext':
            option = 'p'
        elif option == 'Tokens':
            option == 'l'

        query = query_text.get()
        tree = show_trees.get()

        d = {'random': random_conc_option.get(),
             'trees': tree,
             'n': 9999,
             'print_output': False,
             'root': root,
             'note': note,
             'option': option,
             'dep_type': depdict[conc_kind_of_dep.get()]}

        if justdep.get() != '':
            d['dep_function'] = justdep.get()

        if only_sel_speakers_conc.get():
            ids = [int(i) for i in speaker_listbox_conc.curselection()]
            jspeak_conc = [speaker_listbox_conc.get(i) for i in ids]
            if 'ALL' in jspeak_conc:     
                if not names:
                    jspeak_conc = get_speaker_names_from_xml_corpus(corpus_fullpath.get())
                else:
                    jspeak_conc = names
            if 'NONE' in jspeak_conc:
                jspeak_conc = False    
            d['just_speakers'] = jspeak_conc
        
        # special kinds of query
        if query.startswith('[') and query.endswith(']'):
                query = query.lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
        else:
            query = remake_special_query(query)

        if conc_special_queries.get() != 'Preset query':
            from dictionaries.process_types import processes
            from corpkit.other import as_regex
            query = tregex_qs[conc_special_queries.get()]
            d['option'] = 't'

        r = conc(corpus, query, **d)  
        if r is not None and r is not False:
            add_conc_lines_to_window(r)
        Button(tab4, text = 'Run', command = lambda: do_concordancing()).grid(row = 3, column = 4, sticky = E)
        
    def delete_conc_lines(*args):
        if type(current_conc[0]) == str:
            return
        items = conclistbox.curselection()
        #current_conc[0].results.drop(current_conc[0].results.iloc[1,].name)
        r = current_conc[0].drop([current_conc[0].iloc[int(n),].name for n in items])
        add_conc_lines_to_window(r)
        thetime = strftime("%H:%M:%S", localtime())
        if len(items) == 1:
            print '%s: %d line removed.' % (thetime, len(items))
        if len(items) > 1:
            print '%s: %d lines removed.' % (thetime, len(items))

    def delete_reverse_conc_lines(*args):
        if type(current_conc[0]) == str:
            return
        items = [int(i) for i in conclistbox.curselection()]
        r = current_conc[0].iloc[items,]
        add_conc_lines_to_window(r)
        conclistbox.select_set(0, END)
        thetime = strftime("%H:%M:%S", localtime())
        if len(conclistbox.get(0, END)) - len(items) == 1:
            print '%s: %d line removed.' % (thetime, (len(conclistbox.get(0, END)) - len(items)))
        if len(conclistbox.get(0, END)) - len(items) > 1:
            print '%s: %d lines removed.' % (thetime, (len(conclistbox.get(0, END)) - len(items)))

    def conc_export(data = 'default'):
        """export conc lines to csv"""
        import os
        import pandas
        if type(current_conc[0]) == str:
            from time import localtime, strftime
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Nothing to export.' % (thetime)
            return
        if project_fullpath.get() ==  '':
            home = os.path.expanduser("~")
            docpath = os.path.join(home, 'Documents')
        else:
            docpath = project_fullpath.get()
        if data == 'default':
            csv = current_conc[0].to_csv(header = False, sep = '\t')
        else:
            csv = all_conc[data].to_csv(header = False, sep = '\t')
        savepath = tkFileDialog.asksaveasfilename(title = 'Save file',
                                       initialdir = docpath,
                                       message = 'Choose a name and place for your exported data.',
                                       defaultextension = '.csv',
                                       initialfile = 'data.csv')
        if savepath == '':
            return
        with open(savepath, "w") as fo:
            fo.write(csv)
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Concordance lines exported.' % (thetime)

    import itertools
    toggle = itertools.cycle([True, False]).next

    def conc_sort(*args):
        """various sorting for conc. basically, get columns by regex,
        tokenise the l or r if needed, sort by tokens, turn back to df,
        back to string, show.

        current fail when match is first word in sent.

        the new idea is to simply edit and reshow the dataframe!"""

        import re
        import pandas
        import itertools
        sort_way = True
        if type(current_conc[0]) == str:
            return
        if prev_sortval[0] == sortval.get():
            # if subcorpus is the same, etc, as well
            sort_way = toggle()
        df = current_conc[0]
        prev_sortval[0] = sortval.get()
        # sorting by first column is easy, so we don't need pandas
        if sortval.get() == 'M1':
            low = [l.lower() for l in df['m']]
            df['tosorton'] = low

        elif sortval.get() == 'Filename':
            low = [l.lower() for l in df['f']]
            df['tosorton'] = low

        elif sortval.get() == 'Speaker':
            try:
                low = [l.lower() for l in df['s']]
            except:
                from time import localtime, strftime
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: No speaker information to sort by.' % (thetime)
                return
            df['tosorton'] = low
        # if sorting by other columns, however, it gets tough.
        else:
            from nltk import word_tokenize as tokenise
            from time import localtime, strftime
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Tokenising concordance lines ... ' % (thetime)
            # tokenise the right part of each line
            # get l or r column
            col = sortval.get()[0].lower()
            tokenised = [tokenise(s) for s in list(df[col].values)]
            if col == 'm':
                repeats = 2
            else:
                repeats  = 6
            for line in tokenised:
                for i in range(6 - len(line)):
                    if col == 'l':
                        line.insert(0, '')
                    if col == 'r':
                        line.append('')

            # get 1-5 and convert it
            num = int(sortval.get().lstrip('LMR'))
            if col == 'l':
                num = -num
            if col == 'r':
                num = num - 1

            just_sortword = []
            for l in tokenised:    
                if col != 'm':
                    just_sortword.append(l[num].lower())
                else:
                    # horrible
                    if len(l) == 1:
                        just_sortword.append(l[0].lower())
                    elif len(l) > 1:
                        if num == 2:
                            just_sortword.append(l[1].lower())
                        elif num == -2:
                            just_sortword.append(l[-2].lower())
                        elif num == -1:
                            just_sortword.append(l[-1].lower())


            # append list to df
            df['tosorton'] = just_sortword

        df = df.sort(['tosorton'], ascending = sort_way).drop(['tosorton'], axis = 1)
        if show_filenames.get() == 0:
            add_conc_lines_to_window(df.drop('f', axis = 1))
        else:
            add_conc_lines_to_window(df)
        from time import localtime, strftime
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: %d concordance lines sorted.' % (thetime, len(conclistbox.get(0, END)))
        
    # conc box
    fsize = IntVar()
    fsize.set(12)
    cfrm = Frame(tab4, height = 450, width = 1360)
    cfrm.grid(column = 0, columnspan = 60, row = 0)
    cscrollbar = Scrollbar(cfrm)
    cscrollbarx = Scrollbar(cfrm, orient = HORIZONTAL)
    cscrollbar.pack(side=RIGHT, fill=Y)
    cscrollbarx.pack(side=BOTTOM, fill=X)
    conclistbox = Listbox(cfrm, yscrollcommand=cscrollbar.set, 
                          xscrollcommand=cscrollbarx.set, height = 450, 
                          width = 1050, font = ('Courier New', fsize.get()), 
                          selectmode = EXTENDED)
    conclistbox.pack(fill=BOTH)
    cscrollbar.config(command=conclistbox.yview)
    cscrollbarx.config(command=conclistbox.xview)
    cfrm.pack_propagate(False)


    def dec_concfont(*args):
        size = fsize.get()
        fsize.set(size - 1)
        conclistbox.configure(font = ('Courier New', fsize.get()))

    def inc_concfont(*args):
        size = fsize.get()
        fsize.set(size + 1)
        conclistbox.configure(font = ('Courier New', fsize.get()))

    def select_all_conclines(*args):
        conclistbox.select_set(0, END)

    conclistbox.bind("<BackSpace>", delete_conc_lines)
    conclistbox.bind("<Shift-KeyPress-BackSpace>", delete_reverse_conc_lines)
    conclistbox.bind("<Shift-KeyPress-Tab>", conc_sort)
    conclistbox.bind("<%s-minus>" % key, dec_concfont)
    conclistbox.bind("<%s-equal>" % key, inc_concfont)
    conclistbox.bind("<%s-a>" % key, select_all_conclines)
    conclistbox.bind("<%s-s>" % key, lambda x: concsave())
    conclistbox.bind("<%s-e>" % key, lambda x: conc_export())
    conclistbox.bind("<%s-t>" % key, lambda x: toggle_filenames())

    # these were 'generate' and 'edit', but they look ugly right now. the spaces are nice though.
    lab = StringVar()
    lab.set('Concordancing: %s' % os.path.basename(corpus_fullpath.get()))
    Label(tab4, textvariable = lab, font = ("Helvetica", 12, "bold")).grid(row = 1, column = 0, padx = 20, pady = 10, columnspan = 5, sticky = W)
    Label(tab4, text = ' ', font = ("Helvetica", 12, "bold")).grid(row = 1, column = 9, columnspan = 2)

    # select subcorpus
    # add whole corpus option
    subc_pick = StringVar()
    subc_pick.set('Subcorpus')
    pick_subcorpora = OptionMenu(tab4, subc_pick, *tuple(['All'] + [s for s in subcorpora[corpus_fullpath.get()]]))
    pick_subcorpora.configure(width = 22)
    pick_subcorpora.grid(row = 2, column = 0, sticky = W)

    def conc_search_t(*args):
        """turn things on and off based on conc search type"""
        if corpus_search_type.get() == 'Dependencies':
            conc_pick_dep_type.config(state = NORMAL)
            speakcheck_conc.config(state = NORMAL)
            speaker_listbox_conc.config(state = NORMAL)
            query_text.set(r'(garbage|rubbish|trash)')
            ebox.config(state = NORMAL)
        else:
            ebox.config(state = DISABLED)

        if corpus_search_type.get() == 'Trees':
            speakcheck_conc.config(state = NORMAL)
            speaker_listbox_conc.config(state = NORMAL)
            query_text.set('/NN.?/ >># NP')
        else:
            trs.config(state = DISABLED)

        if corpus_search_type.get() == 'Tokens':
            speakcheck_conc.config(state = DISABLED)
            speaker_listbox_conc.config(state = DISABLED)
            query_text.set(r'(garbage|rubbish|trash)')

        if corpus_search_type.get() == 'Plaintext':
            conc_pick_dep_type.config(state = NORMAL)
            query_text.set(r'(garbage|rubbish|trash)')
        

    # kind of data
    corpus_search_type = StringVar()
    corpus_search_type.set('Trees')
    pick_a_conc_datatype = OptionMenu(tab4, corpus_search_type, *tuple(('Trees', 'Dependencies', 'Tokens', 'Plaintext')))
    #pick_a_conc_datatype.configure(state = DISABLED)
    pick_a_conc_datatype.configure(width = 22)
    pick_a_conc_datatype.grid(row = 4, column = 0, sticky=W)
    corpus_search_type.trace("w", conc_search_t)


    conc_dep_types = tuple(('Basic', 'Collapsed', 'CC-processed'))
    conc_kind_of_dep = StringVar(root)
    conc_kind_of_dep.set('CC-processed')
    Label(tab1, text = 'Dependency type:').grid(row = 15, column = 0, sticky = W)
    conc_pick_dep_type = OptionMenu(tab4, conc_kind_of_dep, *dep_types)
    conc_pick_dep_type.config(state = DISABLED, width = 22)
    conc_pick_dep_type.grid(row = 5, column = 0, sticky=W)


    # query:
    query_text = StringVar()
    query_text.set('/NN.?/ >># NP')
    cqb = Entry(tab4, textvariable = query_text, width = 50)
    cqb.grid(row = 2, column = 1, columnspan = 4)

    Label(tab4, text = 'Limit results to function:', font = ("Helvetica", 12, "bold")).grid(row = 4, column = 3)
    justdep = StringVar()
    justdep.set('nsubj(pass)?')
    ebox = Entry(tab4, textvariable = justdep, width = 22)
    ebox.config(state = DISABLED)
    ebox.grid(row = 5, column = 3, columnspan = 2)
    
    # window size: change to dynamic!
    win = StringVar()
    win.set('Window size')
    wind_size = OptionMenu(tab4, win, *tuple(('Window size', '20', '30', '40', '50', '60', '70', '80', '90', '100')))
    wind_size.grid(row = 3, column = 12, columnspan = 2, sticky = E)
    win.trace("w", conc_sort)

    def conc_preset_callback(*args):
        if conc_special_queries.get() != 'Preset query':
            cqb.config(state = NORMAL)
            query_text.set(tregex_qs[conc_special_queries.get()])
            cqb.config(state = DISABLED)
            
            pick_a_conc_datatype.config(state = NORMAL)
            corpus_search_type.set('Trees')
            pick_a_conc_datatype.config(state = DISABLED)

            conc_pick_dep_type.config(state = DISABLED)
            ebox.config(state = DISABLED)
            conc_pick_dep_type.config(state = DISABLED)
            conc_pick_dep_type.config(state = DISABLED)
        else:
            cqb.config(state = NORMAL)
            conc_pick_dep_type.config(state = NORMAL)
            ebox.config(state = NORMAL)
            conc_pick_dep_type.config(state = NORMAL)
            conc_pick_dep_type.config(state = NORMAL)

    conc_queries = tuple(('Preset query', 'Imperatives', 'Modalised declaratives', 'Unmodalised declaratives', 'Interrogatives', 'Mental processes', 'Verbal processes', 'Relational processes'))
    conc_special_queries = StringVar(root)
    conc_special_queries.set('Preset query')
    #Label(tab1, text = 'Preset query:').grid(row = 3, column = 0, sticky = W, columnspan = 2)
    conc_pick_a_query = OptionMenu(tab4, conc_special_queries, *conc_queries)
    conc_pick_a_query.grid(row = 3, column = 0, sticky=W)
    conc_pick_a_query.configure(width = 22)
    conc_special_queries.trace("w", conc_preset_callback)

    only_sel_speakers_conc = IntVar()
    speakcheck_conc = Checkbutton(tab4, text="Speakers", variable=only_sel_speakers_conc, command = togglespeaker)
    speakcheck_conc.grid(column = 1, row = 3, sticky=W)
    only_sel_speakers_conc.trace("w", togglespeaker)

    scfrm = Frame(tab4)
    scfrm.grid(row = 4, column = 1, rowspan = 2, columnspan = 2, sticky = W)
    scscrollbar = Scrollbar(scfrm)
    scscrollbar.pack(side=RIGHT, fill=Y)
    speaker_listbox_conc = Listbox(scfrm, selectmode = EXTENDED, width = 25, height = 4, 
                                   yscrollcommand=scscrollbar.set, exportselection = False)
    speaker_listbox_conc.pack()
    cscrollbar.config(command=speaker_listbox_conc.yview)
    speaker_listbox_conc.configure(state = DISABLED)

    # random
    random_conc_option = IntVar()
    Checkbutton(tab4, text="Randomise", variable=random_conc_option, onvalue = True, offvalue = False).grid(row = 3, column = 3, sticky = E)

    # trees
    show_trees = IntVar()
    trs = Checkbutton(tab4, text="Show trees", variable=show_trees, onvalue = True, offvalue = False)
    trs.grid(row = 3, column = 1, columnspan = 3)

    # run button
    Button(tab4, text = 'Run', command = lambda: do_concordancing()).grid(row = 3, column = 4, sticky = E)

    # edit conc lines
    Button(tab4, text = 'Delete selected', command = lambda: delete_conc_lines(), ).grid(row = 2, column = 9, padx = (220, 0))
    Button(tab4, text = 'Just selected', command = lambda: delete_reverse_conc_lines(), ).grid(row = 2, column = 10)
    Button(tab4, text = 'Sort', command = lambda: conc_sort()).grid(row = 2, column = 11)


    def toggle_filenames(*args):
        import re
        if type(current_conc[0]) == str:
            return
        if win.get() == 'Window size':
            window = 70
        else:
            window = int(win.get())
        data = current_conc[0]
        formatl = lambda x: "{0}".format(x[-window:])
        formatf = lambda x: "{0}".format(x[-20:])
        #formatr = lambda x: 
        formatr = lambda x: "{{:<{}s}}".format(data['r'].str.len().max()).format(x[:window])
        if show_filenames.get() == 0:
            lines = data.drop('f', axis = 1).to_string(header = False, formatters={'l': formatl,
                                                              'r': formatr}).splitlines()
        else:
            lines = data.to_string(header = False, formatters={'l': formatl,
                                                              'r': formatr}).splitlines()
    
        lines = [re.sub('\s*\.\.\.\s*$', '', s) for s in lines]
        import pandas
        
        conclistbox.delete(0, END)
        for line in lines:
            conclistbox.insert(END, line)
        #time = strftime("%H:%M:%S", localtime())
        #print '%s: Concordancing done: %d results.' % (time, len(lines))
        return

    def make_df_matching_screen():
        import re
        if type(current_conc[0]) == str:
            return
        df = current_conc[0]

        if show_filenames.get() == 0:
            df = df.drop('f')
        ix_to_keep = []
        lines = conclistbox.get(0, END)
        reg = re.compile(r'^\s*([0-9]+)')
        for l in lines:
            s = re.search(reg, l)
            ix_to_keep.append(int(s.group(1)))
        df = df.ix[ix_to_keep]
        df = df.reindex(ix_to_keep)
        return df

    def concsave():
        name = tkSimpleDialog.askstring('Concordance name', 'Choose a name for your concordance lines:')
        if not name or name == '':
            return
        
        df = make_df_matching_screen()
        all_conc[name] = df
        refresh()

    Button(tab4, text = 'Save as ... ', command = concsave).grid(row = 5, column = 9, sticky = E, padx = (260,0))

    show_filenames = IntVar()
    fnbut = Checkbutton(tab4, text="Toggle filenames", variable=show_filenames, command=toggle_filenames)
    fnbut.grid(row = 3, column = 10, columnspan = 2, sticky = E)
    fnbut.select()
    show_filenames.trace("w", toggle_filenames)

    # possible sort
    sort_vals = ('Filename', 'Speaker', 'L5', 'L4', 'L3', 'L2', 'L1', 'M1', 'M2', 'M-2', 'M-1', 'R1', 'R2', 'R3', 'R4', 'R5')
    sortval = StringVar()
    sortval.set('M1')
    prev_sortval = ['None']
    srtkind = OptionMenu(tab4, sortval, *sort_vals)
    srtkind.grid(row = 2, column = 12)

    # export to csv
    Button(tab4, text = 'Export', command = lambda: conc_export()).grid(row = 2, column = 13)

    Label(tab4, text = 'Saved concordances:', font = ("Helvetica", 12, "bold")).grid(row = 4, column = 9, columnspan = 2, padx = (260,0))

    def load_saved_conc():
        toget = prev_conc_listbox.curselection()
        if toget != ():
            nm = prev_conc_listbox.get(toget[0])
            df = all_conc[nm]
            add_conc_lines_to_window(df, loading = True)

    Button(tab4, text = 'Load', command = load_saved_conc).grid(row = 5, column = 10, columnspan = 2, padx = (0, 40))
    prev_conc = Frame(tab4)
    prev_conc.grid(row = 4, column = 10, rowspan = 2, columnspan = 4, sticky = E)
    prevcbar = Scrollbar(prev_conc)
    prevcbar.pack(side=RIGHT, fill=Y)
    prev_conc_listbox = Listbox(prev_conc, selectmode = SINGLE, width = 25, height = 4, 
                                yscrollcommand=prevcbar.set, exportselection = False)
    prev_conc_listbox.pack()
    cscrollbar.config(command=speaker_listbox.yview)

    ##############     ##############     ##############     ##############     ############## 
    # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB # 
    ##############     ##############     ##############     ##############     ############## 

    def make_new_project():
        import os
        from corpkit import new_project
        from time import strftime, localtime
        name = tkSimpleDialog.askstring('New project', 'Choose a name for your project:')
        if not name:
            return
        home = os.path.expanduser("~")
        docpath = os.path.join(home, 'Documents')
        fp = tkFileDialog.askdirectory(title = 'New project location',
                                       initialdir = docpath,
                                       message = 'Choose a directory in which to create your new project')
        if not fp:
            return
        new_proj_basepath.set('New project: "%s"' % name)
        new_project(name = name, loc = fp, root = root)
        load_project(path = os.path.join(fp, name))
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Project "%s" created.' % (thetime, name)

    def get_saved_results(kind = 'interrogation'):
        from corpkit import load_all_results
        from time import strftime, localtime
        if kind == 'interrogation':
            datad = data_fullpath.get()
        else:
            datad = conc_fullpath.get()
        if datad == '':
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No project loaded.' % (thetime)
        if kind == 'interrogation':
            r = load_all_results(data_dir = datad, root = root)
        else:
            r = load_all_results(data_dir = datad, root = root, only_concs = True)
        if r is not None:
            for name, loaded in r.items():
                if kind == 'interrogation':
                    all_interrogations[name] = loaded
                else:
                    all_conc[name] = loaded
        refresh()
    
    # corpus path setter
    data_fullpath = StringVar()
    data_fullpath.set('')
    data_basepath = StringVar()
    data_basepath.set('Select data directory')
    project_fullpath = StringVar()
    project_fullpath.set('')
    conc_fullpath = StringVar()
    conc_fullpath.set('')

    def data_getdir():
        import os
        fp = tkFileDialog.askdirectory(title = 'Open data directory')
        if not fp:
            return
        data_fullpath.set(fp)
        data_basepath.set('Saved data: "%s"' % os.path.basename(fp))
        sel_corpus_button.set('Selected corpus: "%s"' % os.path.basename(newc))
        #fs = sorted([d for d in os.listdir(fp) if os.path.isfile(os.path.join(fp, d))])
        time = strftime("%H:%M:%S", localtime())
        print '%s: Set data directory: %s' % (time, os.path.basename(fp))
    
    # corpus path setter
    image_fullpath = StringVar()
    image_fullpath.set('')
    image_basepath = StringVar()
    image_basepath.set('Select image directory')

    def image_getdir(nodialog = False):
        import os
        fp = tkFileDialog.askdirectory()
        if not fp:
            return
        image_fullpath.set(fp)
        image_basepath.set('Images: "%s"' % os.path.basename(fp))
        time = strftime("%H:%M:%S", localtime())
        print '%s: Set image directory: %s' % (time, os.path.basename(fp))

    def save_one_or_more(kind = 'interrogation'):
        if kind == 'interrogation':
            sel_vals = sel_vals_interro
        else:
            sel_vals = sel_vals_conc
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Nothing selected to save' % thetime
            return
        from corpkit import save_result
        import os
        saved = 0
        existing = 0
        for i in sel_vals:
            if urlify(i) + '.p' not in os.listdir(data_fullpath.get()):
                if kind == 'interrogation':
                    save_result(all_interrogations[i], urlify(i) + '.p', savedir = data_fullpath.get())
                else:
                    save_result(all_conc[i], urlify(i) + '.p', savedir = conc_fullpath.get())
                saved += 1
            else:
                existing += 1
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: %s already exists in %s.' % (thetime, urlify(i), os.path.basename(data_fullpath.get()))   
        thetime = strftime("%H:%M:%S", localtime())
        if saved == 1 and existing == 0:
            print '%s: %s saved.' % (thetime, sel_vals[0])
        else:
            if existing == 0:
                print '%s: %d %ss saved.' % (thetime, kind, len(sel_vals))
            else:
                print '%s: %d %ss saved, %d already existed' % (thetime, saved, kind, existing)
        refresh()

    def remove_one_or_more(kind = 'interrogation'):
        if kind == 'interrogation':
            sel_vals = sel_vals_interro
        else:
            sel_vals = sel_vals_conc
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations selected.' % thetime
            return
        for i in sel_vals:
            try:
                if kind == 'interrogation':
                    del all_interrogations[i]
                else:
                    del all_conc[i]
            except:
                pass
        thetime = strftime("%H:%M:%S", localtime())
        if len(sel_vals) == 1:
            print '%s: %s removed.' % (thetime, sel_vals[0])
        else:
            print '%s: %d interrogations removed.' % (thetime, len(sel_vals))
        refresh()

    def del_one_or_more(kind = 'interrogation'):
        if kind == 'interrogation':
            sel_vals = sel_vals_interro
        else:
            sel_vals = sel_vals_conc
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations selected.' % thetime
            return
        import os
        result = tkMessageBox.askquestion("Are You Sure?", "Permanently delete the following files:\n\n    %s" % '\n    '.join(sel_vals), icon='warning')
        if result == 'yes':
            for i in sel_vals:
                try:
                    if kind == 'interrogation':
                        del all_interrogations[i]
                        os.remove(os.path.join(data_fullpath.get(), i + '.p'))
                    else:
                        del all_conc[i]
                        os.remove(os.path.join(data_fullpath.get(), i + '.p'))
                except:
                    pass
        thetime = strftime("%H:%M:%S", localtime())
        if len(sel_vals) == 1:
            print '%s: %s deleted.' % (thetime, sel_vals[0])
        else:
            print '%s: %d %ss deleted.' % (thetime, kind, len(sel_vals))
        refresh()

    def urlify(s):
        "Turn title into filename"
        import re
        s = s.lower()
        s = re.sub(r"[^\w\s-]", '', s)
        s = re.sub(r"\s+", '-', s)
        s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
        return s

    def rename_one_or_more(kind = 'interrogation'):
        if kind == 'interrogation':
            sel_vals = sel_vals_interro
        else:
            sel_vals = sel_vals_conc
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations selected.' % thetime
            return
        import os
        if perm.get():
            perm_text = 'permanently '
        else:
            perm_text = ''
        for i in sel_vals:
            answer = tkSimpleDialog.askstring('Rename', 'Choose a new name for "%s":' % i)
            if answer is None or answer == '':
                continue
            else:
                all_interrogations[answer] = all_interrogations.pop(i)
            if perm.get():
                p = data_fullpath.get()
                oldf = os.path.join(p, i + '.p')
                if os.path.isfile(oldf):
                    newf = os.path.join(p, urlify(answer) + '.p')
                    os.rename(oldf, newf)
            if name_of_interro_spreadsheet.get() == i:
                name_of_interro_spreadsheet.set(answer)
                i_resultname.set('Interrogation results: %s' % str(answer))
                #update_spreadsheet(interro_results, all_interrogations[answer].results)
            if name_of_o_ed_spread.get() == i:
                name_of_o_ed_spread.set(answer)
                #update_spreadsheet(o_editor_results, all_interrogations[answer].results)
            if name_of_n_ed_spread.get() == i:
                name_of_n_ed_spread.set(answer)
                #update_spreadsheet(n_editor_results, all_interrogations[answer].results)

        thetime = strftime("%H:%M:%S", localtime())
        if len(sel_vals) == 1:
            print '%s: %s %srenamed as %s.' % (thetime, sel_vals[0], perm_text, answer)
        print '%s: %d interrogations %srenamed.' % (thetime, len(sel_vals), perm_text)
        refresh()

    sel_vals_interro = []
    sel_vals_conc = []

    def export_interrogation(kind = 'interrogation'):
        if kind == 'interrogation':
            sel_vals = sel_vals_interro
        else:
            sel_vals = sel_conv_vals
        """save dataframes and options to file"""
        import os
        import pandas

        for i in sel_vals:
            answer = tkSimpleDialog.askstring('Rename', 'Choose a save name for "%s":' % i)
            if answer is None or answer == '':
                continue
            if kind != 'interrogation':
                conc_export(data = i)
            else:  
                data = all_interrogations[i]
                keys = data._asdict().keys()
                if project_fullpath.get() == '' or project_fullpath.get() is None:
                    fp = tkFileDialog.askdirectory(title = 'Choose save directory',
                        message = 'Choose save directory for exported interrogation')
                    if fp == '':
                        return
                else:
                    fp = project_fullpath.get()
                os.makedirs(os.path.join(fp, answer))
                for k in keys:
                    if k == 'results':
                        if 'results' in data._asdict().keys():
                            data.results.to_csv(os.path.join(fp, answer, 'results.csv'), sep ='\t')
                    if k == 'totals':
                        if 'totals' in data._asdict().keys():
                            pandas.DataFrame(data.totals).to_csv(os.path.join(fp, answer, 'totals.csv'), sep ='\t')
                    if k == 'query':
                        if 'query' in data._asdict().keys():
                            pandas.DataFrame(data.query.values(), index = data.query.keys()).to_csv(os.path.join(fp, answer, 'query.csv'), sep ='\t')
                    if k == 'table':
                        if 'table' in data._asdict().keys():
                            pandas.DataFrame(data.query.values(), index = data.query.keys()).to_csv(os.path.join(fp, answer, 'table.csv'), sep ='\t')
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Results exported to %s' % (thetime, "answer")        

    def reset_everything():
        # result names
        i_resultname.set('Interrogation results:')
        resultname.set('Results to edit:')
        editoname.set('Edited results:')
        # spreadsheets
        update_spreadsheet(interro_results, df_to_show = None, height = 340, width = 650)
        update_spreadsheet(interro_totals, df_to_show = None, height = 10, width = 650)
        update_spreadsheet(o_editor_results, df_to_show = None, height = 140, width = 720)
        update_spreadsheet(o_editor_totals, df_to_show = None, height = 10, width = 720)
        update_spreadsheet(o_editor_results, df_to_show = None, height = 140, width = 720)
        update_spreadsheet(o_editor_totals, df_to_show = None, height = 10, width = 720)
        # interrogations
        for e in all_interrogations.keys():
            del all_interrogations[e]
        # subcorpora listbox
        subc_listbox.delete(0, END)
        subc_listbox_build.delete(0, END)
        conclistbox.delete(0, END)
        every_interro_listbox.delete(0, END)
        every_interrogation['menu'].delete(0, 'end')
        pick_subcorpora['menu'].delete(0, 'end')
        for k in subcorpora.keys():
            del subcorpora[k]
        refresh()

        # settings
    def load_config():
        import os
        import ConfigParser
        Config = ConfigParser.ConfigParser()
        f = os.path.join(project_fullpath.get(), 'settings.ini')
        Config.read(f)

        def conmap(section):
            dict1 = {}
            options = Config.options(section)
            for option in options:
                try:
                    dict1[option] = Config.get(section, option)
                    if dict1[option] == -1:
                        DebugPrint("skip: %s" % option)
                except:
                    print("exception on %s!" % option)
                    dict1[option] = None
            return dict1

        plot_style.set(conmap("Visualise")['plot style'])
        texuse.set(conmap("Visualise")['use tex'])
        x_axis_l.set(conmap("Visualise")['x axis title'])
        chart_cols.set(conmap("Visualise")['colour scheme'])
        corpus_fullpath.set(conmap("Interrogate")['corpus path'])
        fsize.set(conmap('Concordance')['font size'])
        # window setting causes conc_sort to run, causing problems.
        #win.set(conmap('Concordance')['window'])
        kind_of_dep.set(conmap('Interrogate')['dependency type'])
        conc_kind_of_dep.set(conmap('Concordance')['dependency type'])

        subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
        if len(subdrs) == 0:
            charttype.set('bar')
        refresh()

    def load_project(path = False):
        import os
        if path is False:
            fp = tkFileDialog.askdirectory(title = 'Open project',
                                       message = 'Choose project directory')
        else:
            fp = path
        if not fp or fp == '':
            return
        project_fullpath.set(fp)
        image_fullpath.set(os.path.join(fp, 'images'))
        data_fullpath.set(os.path.join(fp, 'saved_interrogations'))
        conc_fullpath.set(os.path.join(fp, 'saved_concordances'))
        if not os.path.isdir(data_fullpath.get()):
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Selected folder does not contain corpkit project.' % (thetime)    
            return    
        get_saved_results()
        get_saved_results(kind = 'concordance')
        #corpus_fullpath.set(os.path.join(fp, 'corpus'))
        open_proj_basepath.set('Loaded project: "%s"' % os.path.basename(fp))

        os.chdir(fp)
        # reset tool:
        root.title("corpkit: %s" % os.path.basename(fp))
        reset_everything()
        all_corpora = [d for d in os.listdir(os.path.join(fp, 'data')) if os.path.isdir(os.path.join(fp, 'data', d))]
        parsed_corp = [d for d in all_corpora if d.endswith('-parsed')]
        first = False
        if len(parsed_corp) > 0:
            first = parsed_corp[0]
        else:
            if len(all_corpora) > 0:
                first = all_corpora[0]
        if first:
            corpus_fullpath.set(os.path.join(fp, 'data', first))
            subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
            if len(subdrs) == 0:
                charttype.set('bar')

            basepath.set(first)
            subcorpora = {corpus_fullpath.get(): sorted([d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(), d))])}
            lab.set('Concordancing: %s' % os.path.basename(corpus_fullpath.get()))
            subs = sorted([d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(), d))])
            for k in subcorpora.keys():
                del subcorpora[k]
            subcorpora[corpus_fullpath.get()] = subs
            pick_subcorpora['menu'].delete(0, 'end')
            if len(subs) > 0:
                pick_subcorpora.config(state = NORMAL)
                for choice in subs:
                    pick_subcorpora['menu'].add_command(label=choice, command=Tkinter._setit(subc_pick, choice))
            else:
                pick_subcorpora.config(state = NORMAL)
                pick_subcorpora['menu'].add_command(label='None', command=Tkinter._setit(subc_pick, 'None'))
                pick_subcorpora.config(state = DISABLED)
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Project "%s" opened.' % (thetime, os.path.basename(fp))
        f = os.path.join(project_fullpath.get(), 'settings.ini')
        if os.path.isfile(f):
            load_config()
        getdir(ask = False)

    def view_query():
        #Label(tab5, text = 'Query information', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 4, padx = 40)
        mlb = Table(tab5, ['Option', 'Value'],
                  column_weights=[1, 1], height = 50)
        mlb.grid(sticky = N, column = 0, row = 5, rowspan = 40)
                  #reprfunc=(lambda i,j,s: '  %s' % s))

        mlb.columnconfig('Option', background='#afa')
        mlb.columnconfig('Value', background='#efe')

        #MultiListbox(tab5, (('Option', 30), ('Value', 40)))
        #show_query_keys = Listbox(tab5, selectmode = EXTENDED, height = 20)
        
        
        #Label(tab5, text = 'Query value', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 5, padx = 5)
        #show_query_vals = Listbox(tab5, selectmode = EXTENDED, height = 20)
        #show_query_vals.grid(sticky = E, column = 5, row = 2, rowspan = 20, padx = 5)

        #Label(tab5, text = 'Queries', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 2, padx = 40)

        if len(sel_vals) > 1:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Can only view one interrogation at a time.' % (thetime)
            return
        q_dict = dict(all_interrogations[sel_vals[0]].query)
        mlb.clear()
        #show_query_vals.delete(0, 'end')
        flipped_trans = {v: k for k, v in transdict.items()}
        
        # flip options dict, make 'kind of search'
        if 'option' in q_dict.keys():
            flipped_opt = {}
            for nm, lst in option_dict.items():
                for i in lst:
                    flipped_opt[i] = nm
            the_opt = flipped_opt[flipped_trans[q_dict['option']]]
            q_dict['kind_of_search'] = the_opt

        for d in ['dataframe1', 'dataframe2']:
            try:
                del q_dict[d]
            except KeyError:
                pass

        for i, k in enumerate(sorted(q_dict.keys())):
            v = q_dict[k]
            if k == 'option':
                v = flipped_trans[v]
            if v is False:
                v = 'False'

            #mlb.insert(END, (str(k), str(v)))
            mlb.append([k, v])
            #show_query_vals.insert(END, '%d. %s' % (i, str(v)))

    # a list of every interrogation
    def onselect_interro(evt):
        # remove old vals
        for i in sel_vals_interro:
            sel_vals_interro.pop()
        wx = evt.widget
        indices = wx.curselection()
        for index in indices:
            value = wx.get(index)
            if value not in sel_vals_interro:
                sel_vals_interro.append(value)


    ev_int_box = Frame(tab5)
    ev_int_box.grid(sticky = E, column = 1, row = 2, rowspan = 20)
    ev_int_sb = Scrollbar(ev_int_box)
    ev_int_sb.pack(side=RIGHT, fill=Y)
    every_interro_listbox = Listbox(ev_int_box, selectmode = EXTENDED, height = 20, width = 23, 
                                    yscrollcommand=ev_int_sb.set, exportselection=False)
    every_interro_listbox.pack(fill=BOTH)
    every_interro_listbox.select_set(0)
    ev_int_sb.config(command=every_interro_listbox.yview)   
    xx = every_interro_listbox.bind('<<ListboxSelect>>', onselect_interro)
    # default: w option
    every_interro_listbox.select_set(0)

    # Set interrogation option

    new_proj_basepath = StringVar()
    new_proj_basepath.set('New project')
    open_proj_basepath = StringVar()
    open_proj_basepath.set('Open project')

    Label(tab5, text = 'Project', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 0)
    Button(tab5, textvariable = new_proj_basepath, command = make_new_project).grid(row = 1, column = 0, sticky=W)
    Button(tab5, textvariable = open_proj_basepath, command = load_project).grid(row = 2, column = 0, sticky=W)
    Button(tab5, textvariable = basepath, command = getdir).grid(row = 3, column = 0, sticky=W)
    #Button(tab5, textvariable = data_basepath, command = data_getdir).grid(row = 4, column = 0, sticky=W)
    #Label(tab5, text = 'Image directory: ').grid(sticky = W, row = 1, column = 0)
    #Button(tab5, textvariable = image_basepath, command = image_getdir).grid(row = 5, column = 0, sticky=W)

    Label(tab5, text = 'Saved interrogations', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 1)
    Button(tab5, text = 'Get saved interrogations', command = lambda: get_saved_results(), width = 20).grid(row = 1, column = 1)

    #Label(tab5, text = 'Save selected: ').grid(sticky = E, row = 6, column = 1)
    Button(tab5, text = 'Save', command = lambda: save_one_or_more()).grid(sticky = W, column = 1, row = 22)
    Button(tab5, text = 'View', command = lambda: view_query()).grid(sticky = W, column = 1, row = 23)
    Button(tab5, text = 'Rename', command = lambda: rename_one_or_more()).grid(sticky = W, column = 1, row = 24)
    perm = IntVar()
    #Checkbutton(tab5, text="Permanently", variable=perm, onvalue = True, offvalue = False).grid(column = 1, row = 16, sticky=W)
    Button(tab5, text = 'Export', command = lambda: export_interrogation()).grid(sticky = E, column = 1, row = 22)
    #Label(tab5, text = 'Remove selected: '()).grid(sticky = W, row = 4, column = 0)
    Button(tab5, text = 'Remove', command= lambda: remove_one_or_more()).grid(sticky = E, column = 1, row = 23)
    #Label(tab5, text = 'Delete selected: '()).grid(sticky = E, row = 5, column = 1)
    Button(tab5, text = 'Delete', command = lambda: del_one_or_more()).grid(sticky = E, column = 1, row = 24)

    Label(tab5, text = 'Saved concordances', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 2, padx = 50)

    # a list of every interrogation
    def onselect_conc(evt):
        # remove old vals
        for i in sel_vals_conc:
            sel_vals_conc.pop()
        wx = evt.widget
        indices = wx.curselection()
        for index in indices:
            value = wx.get(index)
            if value not in sel_vals_conc:
                sel_vals_conc.append(value)

    ev_conc_box = Frame(tab5)
    ev_conc_box.grid(sticky = E, column = 2, row = 2, rowspan = 20, padx = 50)
    ev_conc_sb = Scrollbar(ev_conc_box)
    ev_conc_sb.pack(side=RIGHT, fill=Y)
    ev_conc_listbox = Listbox(ev_conc_box, selectmode = EXTENDED, height = 20, width = 23,
                              yscrollcommand=ev_conc_sb.set, exportselection = False)
    ev_conc_listbox.pack(fill=BOTH)
    ev_conc_listbox.select_set(0)
    ev_conc_sb.config(command=ev_conc_listbox.yview)   
    xxa = ev_conc_listbox.bind('<<ListboxSelect>>', onselect_conc)

    Button(tab5, text = 'Get saved concordances', command = lambda: get_saved_results(kind = 'concordance'), width = 20).grid(row = 1, column = 2, padx = (50, 50))

    #Label(tab5, text = 'Save selected: ').grid(sticky = E, row = 6, column = 1)
    Button(tab5, text = 'Save', command = lambda: save_one_or_more(kind = 'concordance')).grid(sticky = W, column = 2, row = 22, padx = (50, 50) )
    #Button(tab5, text = 'View', command = lambda: view_query(kind = 'concordance')).grid(sticky = W, column = 2, row = 23, padx = (50, 50) )
    Button(tab5, text = 'Rename', command = lambda: rename_one_or_more(kind = 'concordance')).grid(sticky = W, column = 2, row = 24, padx = (50, 50) )
    perm = IntVar()
    #Checkbutton(tab5, text="Permanently", variable=perm, onvalue = True, offvalue = False).grid(column = 2, row = 16, sticky=W)
    Button(tab5, text = 'Export', command = lambda: export_interrogation(kind = 'concordance')).grid(sticky = E, column = 2, row = 22, padx = (50, 50) )
    #Label(tab5, text = 'Remove selected: '(kind = 'concordance')).grid(sticky = W, row = 4, column = 0)
    Button(tab5, text = 'Remove', command= lambda: remove_one_or_more(kind = 'concordance')).grid(sticky = E, column = 2, row = 23, padx = (50, 50) )
    #Label(tab5, text = 'Delete selected: '(kind = 'concordance')).grid(sticky = E, row = 5, column = 2)
    Button(tab5, text = 'Delete', command = lambda: del_one_or_more(kind = 'concordance')).grid(sticky = E, column = 2, row = 24, padx = (50, 50) )

    ##############     ##############     ##############     ##############     ############## 
    # BUILD TAB  #     # BUILD TAB  #     # BUILD TAB  #     # BUILD TAB  #     # BUILD TAB  # 
    ##############     ##############     ##############     ##############     ############## 
    

    from corpkit import download_cnlp, extract_cnlp, get_corpus_filepaths, check_jdk, parse_corpus, move_parsed_files, corenlp_exists

    def create_tokenised_text():
        note.progvar.set(0)
        Button(tab0, textvariable = tokenise_button_text, command=ignore).grid(row = 6, column = 0, sticky=W)
        unparsed_corpus_path = sel_corpus.get()
        if speakseg.get():
            unparsed_corpus_path = unparsed_corpus_path + '-stripped'
        filelist = get_corpus_filepaths(project_fullpath.get(), unparsed_corpus_path)
        outdir = parse_corpus(project_fullpath.get(), unparsed_corpus_path, filelist, 
                              root = root, stdout = sys.stdout, note = note, only_tokenise = True)
        corpus_fullpath.set(outdir)
        subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
        if len(subdrs) == 0:
            charttype.set('bar')
        basepath.set(os.path.basename(outdir))
        if len([f for f in os.listdir(outdir) if f.endswith('xml')]) > 0:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Corpus parsed and ready to interrogate: "%s"' % (time, os.path.basename(outdir))
        else:
            time = strftime("%H:%M:%S", localtime())
            print '%s: Error: no files created in "%s"' % (time, os.path.basename(outdir))
        Button(tab0, textvariable = tokenise_button_text, command=create_tokenised_text).grid(row = 6, column = 0, sticky=W)

    def create_parsed_corpus():
        """make sure things are installed, do speaker id work, then parse, then structure"""
        note.progvar.set(0)
        import os
        import re
        from time import strftime, localtime

        Button(tab0, textvariable = parse_button_text, command=ignore).grid(row = 6, column = 0, sticky=W)
        unparsed_corpus_path = sel_corpus.get()

        if speakseg.get():
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Processing speaker names ... ' % (thetime)
            from corpkit.build import make_no_id_corpus, get_speaker_names_from_xml_corpus, add_ids_to_xml

            make_no_id_corpus(unparsed_corpus_path, unparsed_corpus_path + '-stripped')
            unparsed_corpus_path = unparsed_corpus_path + '-stripped'
            
        if not corenlp_exists():
            downstall_nlp = tkMessageBox.askyesno("CoreNLP not found.", 
                          "CoreNLP parser not found. Download/install it?")
            if downstall_nlp:
                stanpath, cnlp_zipfile = download_cnlp(project_fullpath.get(), root = root)
                extract_cnlp(cnlp_zipfile, root = root)
            else:
                time = strftime("%H:%M:%S", localtime())
                print '%s: Cannot parse data without Stanford CoreNLP.' % (time)
                return
        jdk = check_jdk()
        if jdk is False:
            downstall_jdk = tkMessageBox.askyesno("You need Java JDK 1.8 to use CoreNLP.", "Hit 'yes' to open web browser at download link. Once installed, corpkit should resume automatically")
            if downstall_jdk:
                import webbrowser
                webbrowser.open_new('http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html')
                import time
                time = strftime("%H:%M:%S", localtime())
                print '%s: Waiting for Java JDK 1.8 installation to complete.' % (time)
                while jdk is False:
                    jdk = check_jdk()
                    time = strftime("%H:%M:%S", localtime())
                    print '%s: Waiting for Java JDK 1.8 installation to complete.' % (time)
                    time.sleep(5)
            else:
                time = strftime("%H:%M:%S", localtime())
                print '%s: Cannot parse data without Java JDK 1.8.' % (time)
                return

        # there are two functions doing the same thing: this and get_filepaths!
        filelist = get_corpus_filepaths(project_fullpath.get(), unparsed_corpus_path)
        
        if filelist is False:
            # zero files...
            from time import localtime, strftime
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Error: no text files found in "%s"' % (thetime, unparsed_corpus_path)
            return

        parsed_dir = parse_corpus(project_fullpath.get(), unparsed_corpus_path, filelist, root = root, stdout = sys.stdout, note = note)
        sys.stdout = note.redir
        new_corpus_path = move_parsed_files(project_fullpath.get(), unparsed_corpus_path, parsed_dir)
        corpus_fullpath.set(new_corpus_path)

        if speakseg.get():
            add_ids_to_xml(new_corpus_path, root = root, note = note)
            corpus_names = get_speaker_names_from_xml_corpus(new_corpus_path)
            for name in names:
                names.pop()
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Names found: %s' % (thetime, ', '.join(corpus_names))           
            for name in corpus_names:
                names.append(name)

        subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
        if len(subdrs) == 0:
            charttype.set('bar')
        basepath.set(os.path.basename(new_corpus_path))
        Button(tab0, textvariable = parse_button_text, command=create_parsed_corpus).grid(row = 6, column = 0, sticky=W)
        time = strftime("%H:%M:%S", localtime())
        print '%s: Corpus parsed and ready to interrogate: "%s"' % (time, os.path.basename(new_corpus_path))

    parse_button_text = StringVar()
    parse_button_text.set('Parse corpus')

    tokenise_button_text = StringVar()
    tokenise_button_text.set('Just tokenise corpus')

    sel_corpus = StringVar()
    sel_corpus.set('')
    sel_corpus_button = StringVar()
    sel_corpus_button.set('Select corpus in project')

    path_to_new_unparsed_corpus = StringVar()
    path_to_new_unparsed_corpus.set('')

    add_corpus = StringVar()
    add_corpus.set('')
    add_corpus_button = StringVar()
    add_corpus_button.set('Add corpus%s' % add_corpus.get())

    selected_corpus_has_no_subcorpora = IntVar()
    selected_corpus_has_no_subcorpora.set(0)

    def add_subcorpora_to_build_box(path_to_corpus):
        import os
        subc_listbox_build.configure(state = NORMAL)
        subc_listbox_build.delete(0, 'end')
        sub_corpora = [d for d in os.listdir(path_to_corpus) if os.path.isdir(os.path.join(path_to_corpus, d))]
        if len(sub_corpora) == 0:
            selected_corpus_has_no_subcorpora.set(1)
            subc_listbox_build.bind('<<Modified>>', onselect_subc_build)
            subc_listbox_build.insert(END, 'No subcorpora found.')
            subc_listbox_build.configure(state = DISABLED)
        else:
            selected_corpus_has_no_subcorpora.set(0)
            for e in sub_corpora:
                subc_listbox_build.insert(END, e)
        onselect_subc_build()

    def select_corpus():
        """selects corpus for viewing/parsing

        clean this up!"""
        from os.path import join as pjoin
        from os.path import basename as bn
        if project_fullpath.get() == '':
            home = os.path.expanduser("~")
            init = pjoin(home, 'Documents')
        else:
            init = pjoin(project_fullpath.get(), 'data')
        unparsed_corpus_path = tkFileDialog.askdirectory(title = 'Path to corpus',
                initialdir = init,
                message = 'Select corpus for viewing/editing/parsing.')
        if unparsed_corpus_path is False or unparsed_corpus_path == '':    
            return
        parse_button_text.set('Parse corpus: "%s"' % bn(unparsed_corpus_path))
        path_to_new_unparsed_corpus.set(unparsed_corpus_path)
        #add_corpus_button.set('Added: %s' % bn(unparsed_corpus_path))
        where_to_put_corpus = pjoin(project_fullpath.get(), 'data')       
        sel_corpus.set(unparsed_corpus_path)
        sel_corpus_button.set('Corpus selected: "%s"' % bn(unparsed_corpus_path))
        parse_button_text.set('Parse corpus: "%s"' % bn(unparsed_corpus_path))
        add_subcorpora_to_build_box(unparsed_corpus_path)
        time = strftime("%H:%M:%S", localtime())
        print '%s: Selected corpus: "%s"' % (time, bn(unparsed_corpus_path))

    def getcorpus():
        """copy unparsed texts to project folder"""
        Button(tab0, textvariable = add_corpus_button, command=ignore).grid(row = 3, column = 0, sticky=W)
        import shutil
        import os
        home = os.path.expanduser("~")
        docpath = os.path.join(home, 'Documents')
        fp = tkFileDialog.askdirectory(title = 'Path to unparsed corpus',
                                       initialdir = docpath,
                                       message = 'Select your corpus of unparsed text files.')
        where_to_put_corpus = os.path.join(project_fullpath.get(), 'data')
        newc = os.path.join(where_to_put_corpus, os.path.basename(fp))
        try:
            shutil.copytree(fp, newc)
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Corpus copied to project folder.' % (thetime)
        except OSError:
            if os.path.basename(fp) == '':
                return
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: "%s" already exists in project.' % (thetime, os.path.basename(fp)) 
            return
        # encode and rename files
        for (rootdir, d, fs) in os.walk(newc):
            for f in fs:
                fpath = os.path.join(rootdir, f)
                with open(fpath) as f:
                    data = f.read()
                with open(fpath, "w") as f:
                    try:
                        f.write(data)
                    except UnicodeEncodeError:
                        import chardet
                        enc = chardet.detect(data)
                        f.write(data.decode(enc['encoding'], 'ignore'))
                # rename file
                dname = '-' + os.path.basename(rootdir)
                newname = fpath.replace('.txt', dname + '.txt')
                shutil.move(fpath, newname)
        path_to_new_unparsed_corpus.set(newc)
        add_corpus_button.set('Added: "%s"' % os.path.basename(fp))
        sel_corpus.set(newc)
        sel_corpus_button.set('Selected corpus: "%s"' % os.path.basename(newc))
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Corpus copied to project folder.' % (thetime)
        parse_button_text.set('Parse corpus: %s' % os.path.basename(newc))
        add_subcorpora_to_build_box(newc)
        time = strftime("%H:%M:%S", localtime())
        print '%s: Selected corpus for viewing/parsing: "%s"' % (time, os.path.basename(newc))
        Button(tab0, textvariable = add_corpus_button, command=getcorpus).grid(row = 3, column = 0, sticky=W)

    # duplicate of one in 'manage
    Label(tab0, text = 'Create project', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 0)
    #Label(tab0, text = 'New project', font = ("Helvetica", 12, "bold")).grid(sticky = W, row = 0, column = 0)
    Button(tab0, textvariable = new_proj_basepath, command = make_new_project).grid(row = 1, column = 0, sticky=W)
    #Label(tab0, text = 'Open project: ').grid(row = 2, column = 0, sticky=W)
    Button(tab0, textvariable = open_proj_basepath, command = load_project).grid(row = 2, column = 0, sticky=W)
    #Label(tab0, text = 'Add corpus to project: ').grid(row = 4, column = 0, sticky=W)
    Button(tab0, textvariable = add_corpus_button, command=getcorpus).grid(row = 3, column = 0, sticky=W)
    #Label(tab0, text = 'Corpus to parse: ').grid(row = 6, column = 0, sticky=W)
    Button(tab0, textvariable = sel_corpus_button, command=select_corpus).grid(row = 4, column = 0, sticky=W)
    #Label(tab0, text = 'Parse corpus: ').grid(row = 8, column = 0, sticky=W)
    speakseg = IntVar()
    speakcheck = Checkbutton(tab0, text="Speaker segmentation", variable=speakseg)
    speakcheck.grid(column = 0, row = 5, sticky=W)
    Button(tab0, textvariable = parse_button_text, command=create_parsed_corpus).grid(row = 6, column = 0, sticky=W)
    #Label(tab0, text = 'Parse corpus: ').grid(row = 8, column = 0, sticky=W)
    Button(tab0, textvariable = tokenise_button_text, command=create_tokenised_text).grid(row = 7, column = 0, sticky=W)

    subc_sel_vals_build = []

    # a list of every interrogation
    def onselect_subc_build(evt = False):
        import os
        if evt:
            """get selected subcorpora"""
            # should only be one
            for i in subc_sel_vals_build:
                subc_sel_vals_build.pop()
            wx = evt.widget
            indices = wx.curselection()
            for index in indices:
                value = wx.get(index)
                if value not in subc_sel_vals_build:
                    subc_sel_vals_build.append(value)

        # return for false click
        if len(subc_sel_vals_build) == 0 and selected_corpus_has_no_subcorpora.get() == 0:
            return
        
        f_view.configure(state = NORMAL)
        f_view.delete(0, 'end')
        newp = path_to_new_unparsed_corpus.get()
        if selected_corpus_has_no_subcorpora.get() == 0:
            newsub = os.path.join(newp, subc_sel_vals_build[0])
        else:
            newsub = newp
        fs = [f for f in os.listdir(newsub) if f.endswith('.txt') or f.endswith('.xml')]
        for e in fs:
            f_view.insert(END, e)
        if selected_corpus_has_no_subcorpora.get() == 0:      
            f_in_s.set('Files in subcorpus: %s' % subc_sel_vals_build[0])
        else:
            f_in_s.set('Files in corpus: %s' % os.path.basename(path_to_new_unparsed_corpus.get()))

    # a listbox of subcorpora
    Label(tab0, text = 'Subcorpora', font = ("Helvetica", 12, "bold")).grid(row = 8, column = 0, sticky=W)


    build_sub_f = Frame(tab0)
    build_sub_f.grid(row = 9, column = 0, sticky = W)
    build_sub_sb = Scrollbar(build_sub_f)
    build_sub_sb.pack(side=RIGHT, fill=Y)
    subc_listbox_build = Listbox(build_sub_f, selectmode = SINGLE, height = 20, state = DISABLED,
                                 yscrollcommand=build_sub_sb.set, exportselection=False)
    subc_listbox_build.pack(fill=BOTH)
    xxy = subc_listbox_build.bind('<<ListboxSelect>>', onselect_subc_build)
    subc_listbox_build.select_set(0)
    build_sub_sb.config(command=subc_listbox_build.yview)

    chosen_f = []
    sentdict = {}
    the_sent_box = {}
    boxes = []
    the_editor = {}

    def show_a_tree(evt):
        """get selected file and show in file view"""
        import os
        from nltk import Tree
        from nltk.tree import ParentedTree
        from nltk.draw.util import CanvasFrame
        from nltk.draw import TreeWidget

        sbox = the_sent_box['box']
        sent = sentdict[int(sbox.curselection()[0])]
        t = ParentedTree.fromstring(sent)

        # make a frame attached to tab0
        #cf = CanvasFrame(tab0, width=200, height=200)
        
        cf = Canvas(tab0, width=650, height=370, bd = 5)
        cf.grid(row = 6, column = 2, rowspan = 2)
        if cf not in boxes:
            boxes.append(cf)
        # draw the tree and send to the frame's canvas
        tc = TreeWidget(cf, t, draggable=1,
                        node_font=('helvetica', -10, 'bold'),
                        leaf_font=('helvetica', -10, 'italic'),
                        roof_fill='white', roof_color='black',
                        leaf_color='green4', node_color='blue2')

        tc.bind_click_trees(tc.toggle_collapsed)
        #tc.bind_click_nodes(color, 3)

    def onselect_f(evt):
        for box in boxes:
            try:
                box.destroy()
            except:
                pass
        import os
        """get selected file and show in file view"""
        # should only be one
        for i in chosen_f:
            chosen_f.pop()
        wx = evt.widget
        indices = wx.curselection()
        for index in indices:
            value = wx.get(index)
            if value not in chosen_f:
                chosen_f.append(value)

        if len(chosen_f) == 0:
            return

        if chosen_f[0].endswith('.txt'):
            newp = path_to_new_unparsed_corpus.get()
            if selected_corpus_has_no_subcorpora.get() == 0:
                fp = os.path.join(newp, subc_sel_vals_build[0], chosen_f[0])
            else:
                fp = os.path.join(newp, chosen_f[0])
            try:
                text = open(fp).read()
            except IOError:
                fp = os.path.join(newp, os.path.basename(corpus_fullpath.get()), chosen_f[0])
                text = open(fp).read()

            editor = Text(tab0, height = 27)
            the_editor['editor'] = editor
            editor.grid(row = 1, column = 2, rowspan = 10)
            if editor not in boxes:
                boxes.append(editor)
            editor.bind("<%s-s>" % key, savebuttonaction)
            editor.config(borderwidth=0,
                  font="{Lucida Sans Typewriter} 12",
                  #foreground="green",
                  #background="black",
                  #insertbackground="white", # cursor
                  #selectforeground="green", # selection
                  #selectbackground="#008000",
                  wrap=WORD, # use word wrapping
                  width=64,
                  undo=True, # Tk 8.4
                  )    
            editor.delete(1.0, END)
            editor.insert(END, text)
            editor.mark_set(INSERT, 1.0)
            editf.set('Edit file: %s' % chosen_f[0])
            viewedit = Label(tab0, textvariable = editf, font = ("Helvetica", 12, "bold"))
            viewedit.grid(row = 2, column = 2, sticky=W)
            if viewedit not in boxes:
                boxes.append(viewedit)
            filename.set(chosen_f[0])
            fullpath_to_file.set(fp)
            but = Button(tab0, text = 'Save changes', command = savebuttonaction)
            but.grid(row = 12, column = 2, sticky = E)
            if but not in boxes:
                boxes.append(but)
        elif chosen_f[0].endswith('.xml'):
            import re
            parsematch = re.compile(r'^\s*<parse>(.*)<.parse>')
            newp = path_to_new_unparsed_corpus.get()
            if selected_corpus_has_no_subcorpora.get() == 0:
                fp = os.path.join(newp, subc_sel_vals_build[0], chosen_f[0])
            else:
                fp = os.path.join(newp, chosen_f[0])
            try:
                text = open(fp).read()
            except IOError:
                fp = os.path.join(newp, os.path.basename(corpus_fullpath.get()), chosen_f[0])
                text = open(fp).read()
            lines = text.splitlines()
            editf.set('View trees: %s' % chosen_f[0])
            vieweditxml = Label(tab0, textvariable = editf, font = ("Helvetica", 12, "bold"))
            vieweditxml.grid(row = 0, column = 2, sticky=W)
            if vieweditxml not in boxes:
                boxes.append(vieweditxml)
            trees = []
            def flatten_treestring(tree):
                import re
                tree = re.sub(r'\(.*? ', '', tree).replace(')', '')
                tree = tree.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
                return tree

            for l in lines:
                searched = re.search(parsematch, l)
                if searched:
                    bracktree = searched.group(1)
                    flat = flatten_treestring(bracktree)
                    trees.append([bracktree, flat])
            sentsbox = Listbox(tab0, selectmode = SINGLE, width = 100, font = ("Courier New", 10))
            if sentsbox not in boxes:
                boxes.append(sentsbox)
            sentsbox.grid(row = 1, column = 2, rowspan = 4)
            sentsbox.delete(0, END)
            the_sent_box['box'] = sentsbox
            for i in sentdict.keys():
                del sentdict[i]
            for i, (t, f) in enumerate(trees):
                cutshort = f[:80] + '...'
                sentsbox.insert(END, '%d: %s' % (i + 1, f))
                sentdict[i] = t
            xxyyz = sentsbox.bind('<<ListboxSelect>>', show_a_tree)
        
        # f_in_s.set('Files in corpus: %s' subc_selected)

    f_in_s = StringVar()
    f_in_s.set('Files in subcorpus: ')

    # a listbox of files
    Label(tab0, textvariable = f_in_s, font = ("Helvetica", 12, "bold")).grid(row = 0, column = 1, sticky=N, padx = 30)
    build_f_box = Frame(tab0)
    build_f_box.grid(row = 1, column = 1, rowspan = 12, padx = 30)
    build_f_sb = Scrollbar(build_f_box)
    build_f_sb.pack(side=RIGHT, fill=Y)
    f_view = Listbox(build_f_box, selectmode = EXTENDED, height = 32, state = DISABLED, 
                     exportselection = False, yscrollcommand=build_f_sb.set)
    f_view.pack(fill=BOTH)
    xxyy = f_view.bind('<<ListboxSelect>>', onselect_f)
    f_view.select_set(0)
    build_f_sb.config(command=f_view.yview)    

    editf = StringVar()
    editf.set('Edit file: ')

    def savebuttonaction(*args):
        f = open(fullpath_to_file.get(), "w")
        editor = the_editor['editor']
        text = editor.get(1.0, END)
        try:
            # normalize trailing whitespace
            f.write(text.rstrip())
            f.write("\n")
        finally:
            f.close()
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: %s saved.' % (thetime, filename.get())

    filename = StringVar()
    filename.set('')
    fullpath_to_file = StringVar()
    fullpath_to_file.set('')

    ############ ############ ############ ############ ############ 
    # MENU BAR # # MENU BAR # # MENU BAR # # MENU BAR # # MENU BAR # 
    ############ ############ ############ ############ ############ 

    realquit = IntVar()
    realquit.set(0)

    def clear_all():
        import os
        import sys
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def save_config():
        import ConfigParser
        import os
        Config = ConfigParser.ConfigParser()
        cfgfile = open(os.path.join(project_fullpath.get(), 'settings.ini') ,'w')
        Config.add_section('Build')
        Config.add_section('Interrogate')
        Config.set('Interrogate','Corpus path', corpus_fullpath.get())
        Config.set('Interrogate','dependency type', kind_of_dep.get())  
        Config.add_section('Edit')
        Config.add_section('Visualise')
        Config.set('Visualise','Plot style', plot_style.get())
        Config.set('Visualise','Use TeX', texuse.get())
        Config.set('Visualise','x axis title', x_axis_l.get())
        Config.set('Visualise','Colour scheme', chart_cols.get())
        Config.add_section('Concordance')
        Config.set('Concordance','font size', fsize.get())
        Config.set('Concordance','dependency type', conc_kind_of_dep.get())
        if win.get() == 'Window size':
            window = 70
        else:
            window = int(win.get())
        Config.set('Concordance','window', window)
        Config.add_section('Manage')
        Config.set('Manage','Project path',project_fullpath.get())
        Config.write(cfgfile)
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Project settings saved to settings.ini ... ' % thetime

    def quitfunc():
        if project_fullpath.get() != '':
            save_ask = tkMessageBox.askyesno("Save project settings.", 
                          "Save settings before quitting?")
            if save_ask:
                save_config()
        realquit.set(1)
        root.quit()

    def check_updates(showfalse = True, lateprint = False):
        """check for updates, showing a window if there is one, and if showfalse, 
           even if not. This works by simply downloading the html of the GitHub main
           page, and searching for the .tar.gz file. This avoids extra dependencies
           on (e.g.) PythonGit. Not sure if this should unzip and overwrite the
           existing file or not."""
        import corpkit
        ver = corpkit.__version__
        ver = float(ver)
        import re
        import urllib2
        from time import strftime, localtime
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Checking for updates ... ' % thetime
        try:
            response = urllib2.urlopen('https://www.github.com/interrogator/corpkit')
            html = response.read()
        except:
            if showfalse:
                tkMessageBox.showinfo(
                "No connection to remote server",
                "Could not connect to remote server.")
            return
        reg = re.compile('title=.corpkit-([0-9\.]+)\.tar\.gz')
        vnum = float(re.search(reg, str(html)).group(1))
        if vnum > ver:
            download_update = tkMessageBox.askyesno("Update available: corpkit %s." % str(vnum), 
                          "Download corpkit %s now?" % str(vnum))
            if download_update:
                import webbrowser
                webbrowser.open_new('https://raw.githubusercontent.com/interrogator/corpkit/master/corpkit-%s.tar.gz' % str(vnum))
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: Update found: corpkit %s' % (thetime, str(vnum))
            else:
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: Update found: corpkit %s. Not downloaded.' % (thetime, str(vnum))
                return
        else:
            if showfalse:
                tkMessageBox.showinfo(
                "Up to date!",
                "corpkit (version %s) up to date!" % ver)
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: corpkit (version %s) up to date.' % (thetime, str(vnum))
                return
            else:
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: No updates available.' % thetime

    def start_update_check():
        check_updates(showfalse = False, lateprint = True)

    #root.after(0, start_update_check) # 500

    menubar = Menu(root)
    if sys.platform == 'darwin':
        filemenu = Menu(menubar, tearoff=0, name='apple')
    else:
        filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New project", command=make_new_project)
    filemenu.add_command(label="Open project", command=load_project)
    filemenu.add_command(label="Select corpus", command=getdir)
    filemenu.add_separator()
    filemenu.add_command(label="Save project settings", command=save_config)
    filemenu.add_command(label="Load project settings", command=load_config)
    filemenu.add_separator()
    filemenu.add_command(label="Check for updates", command=check_updates)
    # broken on deployed version ... path to self stuff
    #filemenu.add_separator()
    #filemenu.add_command(label="Restart tool", command=clear_all)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=quitfunc)
    menubar.add_cascade(label="File", menu=filemenu)
    if sys.platform == 'darwin':
        windowmenu = Menu(menubar, name='window')
        menubar.add_cascade(menu=windowmenu, label='Window')
    else:
        sysmenu = Menu(menubar, name='system')
        menubar.add_cascade(menu=sysmenu)

    # prefrences section
    if sys.platform == 'darwin':
        def showMyPreferencesDialog():
            tkMessageBox.showinfo("Preferences",
                    "Preferences here.")
        root.createcommand('tk::mac::ShowPreferences', showMyPreferencesDialog)

    def about_box():
        import corpkit
        ver = corpkit.__version__
        tkMessageBox.showinfo('About', 'corpkit %s\n\ngithub.com/interrogator/corpkit\npypi.python.org/pypi/corpkit\n\n' \
                              'Creator: Daniel McDonald\nmcdonaldd@unimelb.edu.au' % ver)

    def show_log():
        import os
        from time import strftime, localtime
        if project_fullpath.get() == '':
            home = os.path.expanduser("~")
            docpath = os.path.join(home, 'Documents')
        else:
            docpath = project_fullpath.get()
        input = '\n'.join([unicode(x, errors = 'ignore') for x in note.log_stream])
        #input = note.text.get("1.0",END)
        c = 0
        logpath = os.path.join(docpath, 'log-%s.txt' % str(c).zfill(2))
        while os.path.isfile(logpath):
            logpath = os.path.join(docpath, 'log-%s.txt' % str(c).zfill(2))
            c += 1
        with open(logpath, "w") as fo:
            fo.write(input)
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Log saved to "%s".' % (thetime, logpath)
        import sys
        if sys.platform == 'darwin':
            import subprocess
            subprocess.call(['open', logpath])
        else:
            os.startfile(logpath)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help", command=query_help)
    helpmenu.add_command(label="Save log", command=show_log)
    helpmenu.add_command(label="About", command=about_box)
    menubar.add_cascade(label="Help", menu=helpmenu)

    if sys.platform == 'darwin':
        import corpkit
        import subprocess
        ver = corpkit.__version__
        corpath = os.path.dirname(corpkit.__file__)
        if not corpath.startswith('/Library/Python') and not 'corpkit/corpkit/corpkit' in corpath:
            subprocess.call('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "corpkit-%s" to true' ''' % ver, shell = True)
    root.config(menu=menubar)
    note.focus_on(tab1)
    #root.after(50, start_update_check) # 500
    root.mainloop()

if __name__ == "__main__":
    corpkit_gui()

