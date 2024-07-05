from A1_Variables import *
from A2_Decorators import method_efficency
from B3_Media import Media
from B2_SQLite import RHMH
from C1_DBMS import DBMS,Buttons

class TableFrame:
    def __init__(self, root:Tk) -> None:
        self.BUTT = Buttons()
        self.DBMS = DBMS()
        
        self.BUTT.FilterOptions = {'Datum Operacije':'Operisan' , 'Datum Otpusta':'Otpušten'}

        # PARENT FRAME for RIGHT PANEL
        notebookROW = 9
        Window_Frame = Frame(root)
        Window_Frame.grid(row=1, column=1, padx=shape_padding[0], pady=shape_padding[1], sticky=NSEW)
        self.BUTT.MessageBoxParent = Window_Frame
                # Ovo znaci da ce se NOTEBOOK siriti sa WINDOW
        Window_Frame.grid_rowconfigure(notebookROW, weight=1) 
        Window_Frame.grid_columnconfigure(0, weight=1)

            # Search BAR Frame -- TOP of RIGHT PANES
        searchButtonROW = 8
        self.DBMS.SearchBar = Frame(Window_Frame, bd=bd_inner_frame, relief=RIDGE)
        self.DBMS.SearchBar.grid(row=0, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky=NSEW)
                # Ovo znaci da ce se zadnja 2 BUTONNA uvek biti desno
        self.DBMS.SearchBar.grid_columnconfigure(searchButtonROW,weight=1)
        self.DBMS.SearchBar.grid_rowconfigure(0,weight=1)  
        self.DBMS.SearchBar.bind('<Button-1>',self.BUTT.lose_focus)

                # Create SEARCH BAR
        self.SearchBar_StaticPart(searchButtonROW)
        self.DBMS.SearchAdd_Button,self.DBMS.SearchRemove_Button = self.SearchBar_AddRemove()

        for _ in range(max_searchby):
             self.SearchBar_DynamicPart() # Napravi sve samo jednom
        for _ in range(max_searchby-1):
            self.DBMS.search_bar_remove() # Ostavi samo jedan
        

            # NOTE NOTEBOOK
        self.DBMS.NoteBook = tb.Notebook(Window_Frame)#, bootstyle=bootstyle_table)
        self.DBMS.NoteBook.grid(row=notebookROW, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky=NSEW)
        self.DBMS.NoteBook.bind('<<NotebookTabChanged>>', self.DBMS.tab_change)

                # NOTEBOOK Tab PACIJENTI -- 0
        self.DBMS.Table_Pacijenti = self.PacijentiTab_Create(self.DBMS.fill_PatientForm)
        self.DBMS.selected_columns(self.DBMS.Pacijenti_ColumnVars.items(),self.DBMS.Table_Pacijenti , columnvar=True)

                 # NOTEBOOK Tab SLIKE  -- 1
        self.DBMS.Table_Slike = self.SlikeTab_Create(F_SIZE*50, self.BUTT.Show_Image,
                                [self.BUTT.Add_Image,self.BUTT.Edit_Image,self.BUTT.Delete_Image,self.BUTT.Download_SelectedImages])
        self.DBMS.selected_columns(self.DBMS.TableSlike_Columns , self.DBMS.Table_Slike , columnvar=False)

                # NOTEBOOK Tab KATALOG -- 2
        self.DBMS.Table_MKB, self.DBMS.Table_Zaposleni = self.KatalogTab_Create(
                mkbside = {     'buttons': [self.BUTT.Add_MKB, self.BUTT.Update_MKB, self.BUTT.Delete_MKB],
                            'bindmethods': {    'fill_Form': self.DBMS.fill_MKBForm,
                                                'double_click': self.DBMS.MKB_double_click }  },
                zaposleniside = {   'buttons': [self.BUTT.Add_Zaposleni, self.BUTT.Update_Zaposleni, self.BUTT.Delete_Zaposleni],
                                'bindmethods': { 'fill_Form': self.DBMS.fill_ZaposleniForm,
                                                 'double_click': self.DBMS.Zaposleni_double_click }  }   )
        self.DBMS.selected_columns(self.DBMS.TableMKB_Columns , self.DBMS.Table_MKB , columnvar=False)
        self.DBMS.selected_columns(self.DBMS.TableZaposleni_Columns , self.DBMS.Table_Zaposleni , columnvar=False)

            # NOTEBOOK Tab GRAPH -- 3
        self.DBMS.Graph_Frame = self.GraphTab_Create()

            # NOTEBOOK Tab LOGS -- 4
        self.DBMS.Table_Logs, self.DBMS.FreeQuery_Frame = self.LogsTab_Create(self.DBMS.fill_LogsForm)
        self.DBMS.selected_columns(self.DBMS.TableLogs_Columns , self.DBMS.Table_Logs , columnvar=False)
        self.DBMS.NoteBook.hide(4)

            # NOTEBOOK Tab SESSION -- 5
        self.DBMS.Table_Session = self.SessionTab_Create()
        self.DBMS.selected_columns(self.DBMS.TableSession_Columns , self.DBMS.Table_Session , columnvar=False)
        self.DBMS.NoteBook.hide(5)

            # SETTINGS TAB -- 6
        self.DBMS.Settings_Tab = self.SettingsTab_Create()

            # ABOUT TAB -- 7
        self.DBMS.About_Tab = self.AboutTab_Create()

    def Roundbutton_Create(self,parent_frame:Frame):
        for i,(col,txt) in enumerate(self.BUTT.FilterOptions.items()):
            self.BUTT.FilterOptions[col] = [txt,IntVar()] # Ovde dodajen varijablu int da bi mogao da menjam sa json

            cb = tb.Checkbutton(parent_frame, text=txt, variable=self.BUTT.FilterOptions[col][1], bootstyle='success, round-toggle')
            cb.grid(row=0, column=i, padx=form_padding_button[0], pady=(0,3))

            butt = ctk.CTkButton(parent_frame, text='FILTER', width=form_butt_width, height=form_butt_height//2, corner_radius=10,
                            font=font_label(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'],text_color_disabled=ThemeColors['secondary'],
                                command=lambda column=col: self.DBMS.filter_data(column))
            butt.grid(row=1, column=i, padx=form_padding_button[0], pady=(0,3))
            self.BUTT.buttons['Filter Patient'] += [cb,butt]

    def SearchBar_StaticPart(self,searchButtonROW):
            # JUST LABEL for SEARCH (SEARCH BY, PRETRAZI)
        tb.Label(self.DBMS.SearchBar, anchor=CENTER, bootstyle=labelColor, text='SEARCH BY', font=font_entry).grid(
                            row=0, column=1, rowspan=max_searchby, padx=form_padding_button[0], pady=form_padding_button[1], sticky=NSEW)
            # FILTER OPTIONS
        filterFrame = Frame(self.DBMS.SearchBar)
        filterFrame.grid(row=0,column=searchButtonROW,rowspan=max_searchby,sticky=SE)
        self.Roundbutton_Create(filterFrame)    
        butf = ctk.CTkButton(filterFrame, text='FILTER\nBOTH', width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                            command=lambda column=['Datum Operacije','Datum Otpusta']: self.DBMS.filter_data(column))
        butf.grid(row=0, column=2, rowspan=max_searchby,
                padx=(form_padding_button[0][0],33), pady=form_padding_button[1], sticky=SE)
        self.BUTT.buttons['Filter Patient'].append(butf)

            # BUTTONS for SEARCH and SHOWALL
        buts = ctk.CTkButton(self.DBMS.SearchBar, text='SEARCH', width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'],  text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=self.DBMS.search_data)
        buts.grid(row=0, column=searchButtonROW+3, rowspan=max_searchby,
                padx=form_padding_button[0], pady=form_padding_button[1], sticky=SE)
        self.BUTT.buttons['Search'] = buts

        buta = ctk.CTkButton(self.DBMS.SearchBar, text='SHOW ALL', width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=self.DBMS.showall_data)
        buta.grid(row=0, column=searchButtonROW+4, rowspan=max_searchby,
                padx=form_padding_button[0], pady=form_padding_button[1], sticky=SE)
        self.BUTT.buttons['Show All'] = buta

    def SearchBar_AddRemove(self):
                # BUTTONS for adding and removing SEARCH CRITERIA
        color_add, darker_add, color_remove, darker_remove = Media.label_ImageLoad(IMAGES['Add']+IMAGES['Remove'])

        add = tb.Label(self.DBMS.SearchBar, image=color_add)
        add.grid(row=0, column=0, rowspan=max_searchby, sticky=NW)
        add.bind('<ButtonRelease-1>',self.DBMS.search_bar_add)
        add.bind('<Enter>', lambda event,img=darker_add: Media.hover_label_button(event,img))
        add.bind('<Leave>', lambda event,img=color_add: Media.hover_label_button(event,img))

        remove = tb.Label(self.DBMS.SearchBar, image=color_remove)
        remove.grid(row=0, column=0, rowspan=max_searchby, sticky=SW)
        remove.bind('<ButtonRelease-1>',self.DBMS.search_bar_remove)
        remove.bind('<Enter>', lambda event,img=darker_remove: Media.hover_label_button(event,img))
        remove.bind('<Leave>', lambda event,img=color_remove: Media.hover_label_button(event,img))
        remove.grid_remove()

        return add,remove

    def SearchBar_DynamicPart(self):
        n = self.DBMS.SearchBar_number
        ROW = self.DBMS.SearchBar_number-1

        def grid_set(widget,col,colspan=1,remove=True):
            widget.grid(row=ROW, column=col, columnspan=colspan, padx=search_padding[0], pady=search_padding[1],sticky=EW)
            if remove:
                widget.grid_remove()

        def create_widgets():
            col_val = self.DBMS.TablePacijenti_Columns[1:] 
            Search_option = tb.Combobox(self.DBMS.SearchBar, width=19, values=col_val, height=len(col_val), font=font_entry, state='readonly')
            self.DBMS.SearchBar_widgets[f'search_option_{self.DBMS.SearchBar_number}'] = Search_option
            grid_set(Search_option,4,remove=False)
            Search_option.bind('<<ComboboxSelected>>', lambda event: self.DBMS.Options(n,event))

            Search_type_label = tb.Label(self.DBMS.SearchBar, width=7, anchor=CENTER, bootstyle=labelColor, text='', font=font_entry)
            self.DBMS.SearchBar_widgets[f'search_type_{self.DBMS.SearchBar_number}'] = Search_type_label
            grid_set(Search_type_label,5)
        
            sex_val = ['Muško','Žensko']
            Search_input_equal = tb.Combobox(self.DBMS.SearchBar, values=sex_val, height=len(sex_val), width=search_1_width, font=font_entry, state='readonly')
            self.DBMS.SearchBar_widgets[f'equal_{self.DBMS.SearchBar_number}'] = Search_input_equal
            grid_set(Search_input_equal,6,colspan=2)

            Search_input_like = tb.Entry(self.DBMS.SearchBar, width=search_1_width, font=font_entry)
            self.DBMS.SearchBar_widgets[f'like_{self.DBMS.SearchBar_number}'] = Search_input_like
            grid_set(Search_input_like,6,colspan=2)

            Search_date_from = widgets.DateEntry(self.DBMS.SearchBar, width=search_2_width+2, dateformat='%d-%b-%Y', firstweekday=0)
            Search_date_from.entry.delete(0,END)
            self.DBMS.SearchBar_widgets[f'date_from_{self.DBMS.SearchBar_number}'] = Search_date_from
            grid_set(Search_date_from,6)

            Search_date_to = widgets.DateEntry(self.DBMS.SearchBar, width=search_2_width+2, dateformat='%d-%b-%Y', firstweekday=0)
            Search_date_to.entry.delete(0,END)
            self.DBMS.SearchBar_widgets[f'date_to_{self.DBMS.SearchBar_number}'] = Search_date_to
            grid_set(Search_date_to,7)

            Search_input_from = tb.Entry(self.DBMS.SearchBar, width=search_2_width, font=font_entry)
            self.DBMS.SearchBar_widgets[f'from_{self.DBMS.SearchBar_number}'] = Search_input_from
            grid_set(Search_input_from,6)

            Search_input_to = tb.Entry(self.DBMS.SearchBar, width=search_2_width, font=font_entry)
            self.DBMS.SearchBar_widgets[f'to_{self.DBMS.SearchBar_number}'] = Search_input_to
            grid_set(Search_input_to,7)

        create_widgets()
        self.DBMS.SearchBar_number += 1

    def PacijentiTab_Create(self,method:callable) -> (tb.ttk.Treeview):
        table: tb.ttk.Treeview
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Pacijenti')

        def PacijentiTable_Create():
            nonlocal table
            scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
            scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

            table = tb.ttk.Treeview(notebook_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=1, column=0, sticky=NSEW)
            
            for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
                table.bind(bindevent,method)
            table.bind('<Shift-Up>',self.BUTT.shift_up)
            table.bind('<Shift-Down>',self.BUTT.shift_down)

            scroll_x.grid(row=2, column=0, sticky=EW)
            scroll_y.grid(row=1, column=1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

        # Top Frame with CheckButtons
        extra_frame = Frame(notebook_frame)
        extra_frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        self.Checkbutton_Create(extra_frame)

        # Table Main Part
        PacijentiTable_Create()

        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)
        return table

    def Checkbutton_Create(self,parent_frame:Frame):
        swap = False
        grouping = [None, -1, 0]
        for orig_name,dicty in MainTablePacijenti.items():
            self.DBMS.Pacijenti_ColumnVars[orig_name].set(1) # Svi ukljuceni na pocetku (prva 3 moraju biti jer su checkbutton: NONE)
            if dicty['checkbutton']:
                if grouping[0] != dicty['group']:
                    try: # Ovo se izvrsava na promeni grupe, na kraju
                        frame.grid_columnconfigure([i for i in range(grouping[2])], weight=1)
                        frame.grid_rowconfigure([1,2],weight=1)
                        lbl.grid_configure(columnspan = grouping[2])
                    except:
                        pass
                    grouping[0] = dicty['group'] # grupacije checkbuttona
                    grouping[1] += 1 # kolone za grupe
                    grouping[2] = 0 # kolone za checkbuttone (resetuje kod nove grupe)
                    frame = Frame(parent_frame, bd=2, relief=RAISED)
                    frame.grid(row=0, column=grouping[1], sticky=NSEW)
                    if dicty['group']:
                        lbl = tb.Label(frame,anchor=CENTER, bootstyle=labelColor, text=dicty['group'], font=font_label())
                        lbl.grid(row=0, column=0, pady=4)
                if dicty['group']:
                    tb.Checkbutton(frame, text=dicty['checkbutton'], variable=self.DBMS.Pacijenti_ColumnVars[orig_name],
                            bootstyle=bootstyle_check).grid(row=1, column=grouping[2], padx=6, pady=(0,4))
                    grouping[2] += 1

                else:
                    tb.Checkbutton(frame, text=dicty['checkbutton'], variable=self.DBMS.Pacijenti_ColumnVars[orig_name],
                            bootstyle=bootstyle_check).grid(row=swap, column=grouping[2]-swap, padx=6, pady=(8*(not swap),4)) # ovo pady ce dati 8,4,4 padding
                    grouping[2] += 1
                    swap = not swap # vrti 0/1 za redove checkbuttona kod None grupe
        frame.grid_columnconfigure([i for i in range(grouping[2])], weight=1) # na kraju jos jednom za poslednju grupu
        frame.grid_rowconfigure([1,2],weight=1)
        parent_frame.grid_columnconfigure([i for i in range(grouping[1]+1)],weight=1)
    
    def SlikeTab_Create(self, tablewidth:int, method:callable, button_cmd:list) -> (tb.ttk.Treeview):
        table:tb.ttk.Treeview
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Slike')

        tableparent_frame = Frame(notebook_frame, width=tablewidth)
        tableparent_frame.grid(row=0, column=0, sticky=NSEW)
        tableparent_frame.grid_propagate(False) # Ovo je da table ne uzme prostor koliko joj treba za kolone
        tableparent_frame.grid_rowconfigure(1, weight=1) # Ovo je da se siri table a ne buttons
        tableparent_frame.grid_columnconfigure(0, weight=1) # Ovo je da se siri table a ne scroll

        self.BUTT.Slike_HideTable = tableparent_frame # Ovo je da moze da se radi hide table frejma

        def ButtonsSlike_Create(parent, row, column, columnspan):
            button_frame = Frame(parent, bd=2, relief=RAISED)
            button_frame.grid(row=row, column=column, columnspan=columnspan, sticky=EW)
            button_frame.grid_columnconfigure(0, weight=1)

            for i,butt in enumerate(Image_buttons):
                button = ctk.CTkButton(button_frame, text=butt[0], width=form_butt_width, height=form_butt_height, corner_radius=10,
                                font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                command=button_cmd[i])
                button.grid(row=0, column=i, padx=form_padding_button[0], pady=form_padding_button[1], sticky=E)
                if butt[1]:
                    button.configure(fg_color=ThemeColors[butt[1]])
                self.BUTT.buttons[butt[0].replace('\n',' ')] = button

        def TableSlike_Create(parent, row, column):
            nonlocal table
            scroll_x = tb.Scrollbar(parent, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
            scroll_y = tb.Scrollbar(parent, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

            table = tb.ttk.Treeview(parent, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=row, column=column, sticky=NSEW)
            
            for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
                table.bind(bindevent, method)
            table.bind('<Shift-Up>',self.BUTT.shift_up)
            table.bind('<Shift-Down>',self.BUTT.shift_down)

            scroll_x.grid(row=row+1, column=column, sticky=EW)
            scroll_y.grid(row=row, column=column+1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

        #editorparent_frame = Frame(notebook_frame, width=tablewidth)
        #editorparent_frame.grid(row=0, column=0, sticky=NSEW)

        def SlikeEditor_Create(row,column):
            pass

        # Table+Buttons Left Side
        ButtonsSlike_Create(parent=tableparent_frame, row=0, column=0, columnspan=2)
        TableSlike_Create(parent=tableparent_frame, row=1, column=0)

        # CANVAS Right Side
        canvas_frame = Frame(notebook_frame, bd=3, relief=RAISED)
        canvas_frame.grid(row=0, column=1, sticky=NSEW)
        self.Slike_SideFrame(canvas_frame)

        notebook_frame.grid_rowconfigure(0, weight=1) # Ovo je da se sire nadole svi elementi
        notebook_frame.grid_columnconfigure(1, weight=1) # Ovo je da se siri canvas a ne table i editor

        return table

    def Slike_SideFrame(self,parent_frame:Frame):
        Media.Slike_Viewer = Canvas(parent_frame)
        Media.Slike_Viewer.pack(side=LEFT, fill=BOTH, expand=True)

        self.scroll_y = tb.Scrollbar(Media.Slike_Viewer, orient=VERTICAL, command=Media.Slike_Viewer.yview)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.scroll_x = tb.Scrollbar(Media.Slike_Viewer, orient=HORIZONTAL, command=Media.Slike_Viewer.xview)
        self.scroll_x.pack(side=BOTTOM, fill=X)
        Media.Slike_Viewer.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

    def KatalogTab_Create(self, mkbside:dict, zaposleniside:dict) -> (tb.ttk.Treeview):
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Katalog')
        notebook_frame.grid_columnconfigure(0,weight=1) # MKB se siri (tj left side)
        notebook_frame.grid_rowconfigure(0,weight=1) # MKB se siri (tj left side)

        def Create_One_Side(method:callable, bindmethods:dict, *args):
            PartFrame = tb.Frame(notebook_frame)
            PartFrame.grid(row=0, column=COLUMN, sticky=NSEW) # Ovo sticky mora da bi se rasirio frame
            PartFrame.grid_rowconfigure(1, weight=1) # tabela se siri
            PartFrame.grid_columnconfigure(0, weight=1) # tabela se siri

            scroll_x = tb.Scrollbar(PartFrame, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
            scroll_y = tb.Scrollbar(PartFrame, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

            table = tb.ttk.Treeview(PartFrame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=1, column=0, sticky=NSEW)
            
            for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
                table.bind(bindevent,bindmethods['fill_Form'])
            table.bind('<Double-1>',bindmethods['double_click'])
            table.bind('<Shift-Up>',self.BUTT.shift_up)
            table.bind('<Shift-Down>',self.BUTT.shift_down)

            scroll_x.grid(row=2, column=0, sticky=EW)
            scroll_y.grid(row=1, column=1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

            entry_Frame = Frame(PartFrame, bd=2, relief=RAISED)
            entry_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
            method(entry_Frame,*args) # Katalog_Entry_Create

            return table

        COLUMN = 0 # Left Part -- (0,0) je za row,col za frejm ispod tabele
        tableMKB = Create_One_Side(self.Katalog_Entry_Create,
                                   mkbside['bindmethods'],
                                   *[Katalog_Entry['mkb10'],mkbside['buttons']])
        COLUMN += 1 # Right Part -- (1,-1) je za row,col za frejm ispod tabele
        tableZapo = Create_One_Side(self.Katalog_Entry_Create,
                                    zaposleniside['bindmethods'],
                                    *[Katalog_Entry['zaposleni'],zaposleniside['buttons']])

        return tableMKB,tableZapo

    def Katalog_Entry_Create(self,parent_frame:Frame,entry_dict:dict,buttons:list):  
        parent_frame.grid_rowconfigure(0,weight=1) 
        for column,values in entry_dict.items():
            frame = Frame(parent_frame)
            if column=='Buttons':
                for j,butt in enumerate(values):
                    if j==0:
                        frame.grid(row=butt[0], column=butt[1], rowspan=butt[2], columnspan=butt[3], sticky=NSEW)
                        frame.grid_columnconfigure([i for i in range(len(values)-1)], weight=1)
                        frame.grid_rowconfigure(0, weight=1)
                    else:
                        button = ctk.CTkButton(frame, text=butt[0], width=form_butt_width, height=form_butt_height, corner_radius=10,
                            font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                            command=buttons[j-1])
                        button.grid(row=0, column=j-1, padx=form_padding_button[0], pady=form_padding_button[1])
                        if butt[1]:
                            button.configure(fg_color=ThemeColors[butt[1]])
                        self.BUTT.buttons[butt[0].replace('\n',' ')] = button
                        
            else:
                frame.grid(row=values[2][0], column=values[2][1], rowspan=values[2][2], columnspan=values[2][3], sticky=NSEW)
                if column == 'Combobox':
                    parent_frame.grid_columnconfigure(values[2][1], weight=1)
                    self.BUTT.Katalog_FormVariables[values[0]] = StringVar()
                    VALUES = RHMH.dr_funkcija if values[0]=='Funkcija' else RHMH.dg_kategorija if values[0]=='Kategorija' else None
                    tb.Combobox(frame, values=VALUES, justify=CENTER,
                                textvariable=self.BUTT.Katalog_FormVariables[values[0]],
                                width=values[1], font=font_entry, state='readonly').grid(padx=12, pady=form_padding_entry[1])
                    frame.grid_configure(sticky=E)
                    frame.grid_rowconfigure(0, weight=1)
                    parent_frame.grid_columnconfigure(values[2][1], weight=1)
                else:
                    self.BUTT.Katalog_FormVariables[column] = StringVar()
                    tb.Label(frame, anchor=CENTER, justify=CENTER, bootstyle=labelColor, text=values[0], font=font_entry).grid(
                                row=0, column=0, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky=EW)
                    tb.Entry(frame, width=values[1], font=font_entry,
                                textvariable=self.BUTT.Katalog_FormVariables[column]).grid(
                                    row=0, column=1, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky=EW)
                    frame.grid_columnconfigure(1,weight=1) # Ovo kaze da se siri entry a ne label
                    frame.grid_rowconfigure(0,weight=1) # Ovo mora jer je Opis Dijagnoze u 2 reda da bi se rasirio prvi label          

    def LogsTab_Create(self, method:callable):      
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Logs')

        # Top FreeQuery Panel
        freequery_frame = Frame(notebook_frame)
        freequery_frame.grid(row=0, column=0, columnspan=3, sticky=NSEW)
        freequery_frame.grid_columnconfigure(0, weight=1)

        self.DBMS.FreeQuery = StringVar()
        tb.Entry(freequery_frame, font=font_entry, textvariable=self.DBMS.FreeQuery).grid(
                    row=0, column=0, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky=EW)
        
        button = ctk.CTkButton(freequery_frame, text='Free\nQuery', width=form_butt_width, height=form_butt_height, corner_radius=10,
            font=font_label(), fg_color=ThemeColors['danger'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
            command=self.DBMS.FreeQuery_Execute)
        button.grid(row=0, column=1, padx=form_padding_button[0], pady=form_padding_button[1])
        freequery_frame.grid_remove()
        self.BUTT.buttons['Free Query'] = button

        # Left Table Panel
        scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
        scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

        table = tb.ttk.Treeview(notebook_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        table.grid(row=1, column=0, sticky=NSEW)
        
        for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
            table.bind(bindevent,method)

        scroll_x.grid(row=2, column=0, sticky=EW)
        scroll_y.grid(row=1, column=1, sticky=NS)
        scroll_x.config(command=table.xview)
        scroll_y.config(command=table.yview)

        # Right Text Panel
        text_frame = Frame(notebook_frame)
        text_frame.grid(row=1, column=2, rowspan=2, sticky=NSEW)
        self.Log_SideFrame(text_frame)

        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)

        return table,freequery_frame

    def Log_SideFrame(self,parent_frame:Frame):
        lbl1 = tb.Label(parent_frame,text='Full Query', anchor=CENTER, justify=CENTER, bootstyle=labelColor, font=font_label())
        lbl1.grid(row=0, column=0)
        text1 = tb.Text(parent_frame, font=font_entry)
        text1.grid(row=1, column=0, sticky=NSEW)
        self.BUTT.Logs_FormVariables['Full Query'] = text1
        lbl1 = tb.Label(parent_frame,text='Full Error', anchor=CENTER, justify=CENTER, bootstyle=labelColor, font=font_label())
        lbl1.grid(row=2, column=0)
        text2 = tb.Text(parent_frame, font=font_entry)
        text2.grid(row=3, column=0, sticky=NSEW)
        self.BUTT.Logs_FormVariables['Full Error'] = text2

        parent_frame.grid_rowconfigure([1,3],weight=1)
        parent_frame.grid_columnconfigure(0,weight=1)

    def SessionTab_Create(self):
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Session')

        scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
        scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

        table = tb.ttk.Treeview(notebook_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        table.grid(row=0, column=0, sticky=NSEW)
        
        scroll_x.grid(row=1, column=0, sticky=EW)
        scroll_y.grid(row=0, column=1, sticky=NS)
        scroll_x.config(command=table.xview)
        scroll_y.config(command=table.yview)

        notebook_frame.grid_rowconfigure(0, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)

        return table

    def GraphTab_Create(self):
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Grafikon')
        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)


        optionsframe = Frame(notebook_frame, bd=3, relief=RAISED)
        optionsframe.grid(row=0, column=0, sticky=EW)
        
        def add_graph_grouping_option(event):
            widget:tb.Combobox = self.BUTT.Graph_FormVariables['X2-1'][0]
            lastchoice:StringVar = self.BUTT.Graph_FormVariables['X1-1'][1].get()
            Values = graph_Xoptions[:]
            vreme = ['Godina' , 'Mesec' , 'Dan' , 'Dan u Sedmici']
            dijagnoza = ['Trauma', 'MKB Grupe','MKB Pojedinačno']
            if lastchoice in vreme:
                removelist = vreme[:vreme.index(lastchoice)+1] if not 'Dan' in lastchoice else vreme
                for val in removelist:
                    Values.remove(val)
            elif lastchoice in dijagnoza:
                if lastchoice == 'Trauma':
                    removelist = ['MKB Pojedinačno','Trauma']
                elif lastchoice == 'MKB Grupe':
                    removelist = ['MKB Grupe','Trauma']
                else:
                    removelist = dijagnoza
                for val in removelist:
                    Values.remove(val)
            else:
                Values.remove(lastchoice)

            width = len(max(Values, key=len))
            width = width-4 if width>20 else 3 if width<3 else width-1
            widget.configure(values=Values, width=width)
            widget.grid()
            event.widget.grid_remove()

        values = ['Broj Pacijenata' , 'Broj dana Hospitalizovan' , 'Broj dana od Prijema do Operacije' , 'Broj dana od Operacije do Otpusta']
        width = len(max(values, key=len))-5
        combo = tb.Combobox(optionsframe, values=values, width=width, font=font_entry, state='readonly')
        self.BUTT.Graph_FormVariables['Y'] = (combo,StringVar())
        combo.configure(textvariable=self.BUTT.Graph_FormVariables['Y'][1])
        combo.grid(row=0, column=0, rowspan=2, padx=(form_padding_entry[0][0]+12, form_padding_entry[0][1]), pady=form_padding_entry[1])
        combo.bind("<<ComboboxSelected>>", lambda event, opt='Y': self.DBMS.Graph_Options(event,opt))

        def create_X_combo(row):
            for i in range(1,4):
                name = f'X{row+1}-{i}'
                combo = tb.Combobox(optionsframe, values=[], font=font_entry, state='readonly')
                self.BUTT.Graph_FormVariables[name] = (combo,StringVar())
                combo.configure(textvariable=self.BUTT.Graph_FormVariables[name][1])

                combo.grid(row=row, column=i, padx=form_padding_entry[0], pady=form_padding_entry[1],sticky=EW)
                combo.bind("<<ComboboxSelected>>", lambda event, opt=name: self.DBMS.Graph_Options(event,opt))
                combo.grid_remove()
    
        def add_button(col):
            color_add, darker_add = Media.label_ImageLoad(IMAGES['Add'])
            add = tb.Label(optionsframe, image=color_add)
            add.grid(row=0, column=col, sticky=W)
            add.bind('<ButtonRelease-1>',add_graph_grouping_option)
            add.bind('<Enter>', lambda event,img=darker_add: Media.hover_label_button(event,img))
            add.bind('<Leave>', lambda event,img=color_add: Media.hover_label_button(event,img))
            self.BUTT.Graph_FormVariables['Add'] = add
            add.grid_remove()

        def colorvalues_options(col):
            frame_c = Frame(optionsframe)
            frame_c.grid(row=0, column=col, rowspan=2, padx=main_title_padding[0], pady=form_padding_button[1], sticky=NSEW)
            for i,txt in enumerate(['values','color']):
                cb = tb.Checkbutton(frame_c, text=txt, bootstyle=bootstyle_check)
                self.BUTT.Graph_FormVariables['afterchoice'][txt] = (cb,IntVar())
                cb.configure(variable=self.BUTT.Graph_FormVariables['afterchoice'][txt][1])

                cb.grid(row=i, column=0, padx=form_padding_button[0], pady=form_padding_button[1], sticky=W)
                cb.grid_remove()

        def radio_choice(col):
            frame_r = Frame(optionsframe)
            frame_r.grid(row=0, column=col, rowspan=2, padx=main_title_padding[0], pady=form_padding_button[1], sticky=NSEW)
            self.BUTT.Graph_FormVariables['afterchoice']['radio'] = {'widgets':{},'choice':StringVar(value='bars')}
            for txt in ['bars','pie','stacked']:
                ROW = 0 if txt=='bars' else 1
                radio = tb.Radiobutton(frame_r, text=txt, variable=self.BUTT.Graph_FormVariables['afterchoice']['radio']['choice'], value=txt)
                radio.grid(row=ROW, column=0, padx=form_padding_button[0], pady=form_padding_button[1], sticky=W)
                self.BUTT.Graph_FormVariables['afterchoice']['radio']['widgets'][txt] = radio
                radio.grid_remove()

        def filtertable_option(col):
            cb = tb.Checkbutton(optionsframe, text=' FILTER\n  Table', bootstyle='success, square-toggle')
            self.BUTT.Graph_FormVariables['afterchoice']['Filter Main Table'] = (cb,IntVar())
            cb.configure(variable=self.BUTT.Graph_FormVariables['afterchoice']['Filter Main Table'][1])
            cb.grid(row=0, column=col, rowspan=2, padx=main_title_padding[0], pady=form_padding_button[1], sticky=W)
            cb.grid_remove()

        def showgraph_button(col):
            button = ctk.CTkButton(optionsframe, text='SHOW\nGraph', width=form_butt_width, height=form_butt_height, corner_radius=10,
                font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                command=self.DBMS.Show_Graph)
            button.grid(row=0, column=col, rowspan=2, padx=(6,18), pady=form_padding_button[1], sticky=E)
            self.BUTT.buttons['SHOW\nGraph'.replace('\n',' ')] = button
            button.configure(state=DISABLED)

        self.BUTT.Graph_FormVariables['afterchoice'] = dict()
        create_X_combo(row=0) # col 3 last
        create_X_combo(row=1) # col 3 last
        add_button(col=4)
        radio_choice(col=5)
        colorvalues_options(col=6)
        filtertable_option(col=7)
        showgraph_button(col=8)

        optionsframe.grid_columnconfigure(4, weight=1) # checkbuttoni zauzimaju prazan i ravnaju E
        optionsframe.grid_rowconfigure(0, weight=1)

        plotframe = Frame(notebook_frame, bd=3, relief=RAISED)
        plotframe.grid(row=1,column=0, sticky=NSEW)

        return plotframe

    def SettingsTab_Create(self):
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='Settings')

        return notebook_frame
    
    def AboutTab_Create(self):
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text='About')

        return notebook_frame