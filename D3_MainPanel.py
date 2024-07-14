from A1_Variables import *
from B2_SQLite import RHMH,LOGS
from B3_Media import Media
from B4_Graph import Graph
from C1_Controller import Controller
from C2_ManageDB import ManageDB
from C3_SelectDB import SelectDB

class MainPanel:

    @staticmethod
    def initialize(root:Tk) -> None:
      
        Controller.FilterOptions = {'Datum Operacije':'Operisan' , 'Datum Otpusta':'Otpušten'}

        # PARENT FRAME for RIGHT PANEL
        notebookROW = 9
        Window_Frame = Frame(root)
        Window_Frame.grid(row=1, column=1, padx=padding_6, pady=padding_0_6, sticky=NSEW)
        Controller.MessageBoxParent = Window_Frame
                # Ovo znaci da ce se NOTEBOOK siriti sa WINDOW
        Window_Frame.grid_rowconfigure(notebookROW, weight=1) 
        Window_Frame.grid_columnconfigure(0, weight=1)

            # Search BAR Frame -- TOP of RIGHT PANES
        searchButtonROW = 8
        Controller.SearchBar = Frame(Window_Frame, bd=3, relief=RIDGE)
        Controller.SearchBar.grid(row=0, column=0, padx=padding_6, pady=padding_0_6, sticky=NSEW)
                # Ovo znaci da ce se zadnja 2 BUTONNA uvek biti desno
        Controller.SearchBar.grid_columnconfigure(searchButtonROW,weight=1)
        Controller.SearchBar.grid_rowconfigure(0,weight=1)  
        Controller.SearchBar.bind('<Button-1>',Controller.lose_focus)

                # Create SEARCH BAR
        MainPanel.SearchBar_StaticPart(searchButtonROW)
        Controller.SearchAdd_Button,Controller.SearchRemove_Button = MainPanel.SearchBar_AddRemove()

        for _ in range(Controller.max_SearchBars):
             MainPanel.SearchBar_DynamicPart() # Napravi sve samo jednom
        for _ in range(Controller.max_SearchBars-1):
            SelectDB.search_bar_remove() # Ostavi samo jedan
        

            # NOTE NOTEBOOK
        Controller.NoteBook = tb.Notebook(Window_Frame)
        Controller.NoteBook.grid(row=notebookROW, column=0, padx=padding_6, pady=padding_0_6, sticky=NSEW)
        Controller.NoteBook.bind('<<NotebookTabChanged>>', SelectDB.tab_change)

                # NOTEBOOK Tab PACIJENTI -- 0
        Controller.Pacijenti_ColumnVars =     {column: IntVar() for column in Controller.TablePacijenti_Columns}
        Controller.Table_Pacijenti = MainPanel.PacijentiTab_Create('Pacijenti', SelectDB.fill_PatientForm)
        SelectDB.selected_columns(Controller.Pacijenti_ColumnVars.items(),Controller.Table_Pacijenti , columnvar=True)

                 # NOTEBOOK Tab SLIKE  -- 1
        Controller.Table_Slike = MainPanel.SlikeTab_Create('Slike',F_SIZE*50, SelectDB.Show_Image,
                                [ManageDB.Add_Image,ManageDB.Edit_Image,ManageDB.Delete_Image,ManageDB.Download_SelectedImages])
        Controller.TableSlike_Columns = tuple(['ID']+RHMH.slike)
        SelectDB.selected_columns(Controller.TableSlike_Columns , Controller.Table_Slike , columnvar=False)

                # NOTEBOOK Tab KATALOG -- 2
        Controller.Table_MKB, Controller.Table_Zaposleni = MainPanel.KatalogTab_Create(tabname='Katalog',
                mkbside = {     'buttons': [ManageDB.Add_MKB, ManageDB.Update_MKB, ManageDB.Delete_MKB],
                            'bindmethods': {    'fill_Form': SelectDB.fill_MKBForm,
                                                'double_click': SelectDB.MKB_double_click }  },
                zaposleniside = {   'buttons': [ManageDB.Add_Zaposleni, ManageDB.Update_Zaposleni, ManageDB.Delete_Zaposleni],
                                'bindmethods': { 'fill_Form': SelectDB.fill_ZaposleniForm,
                                                 'double_click': SelectDB.Zaposleni_double_click }  }   )
        
        Controller.TableMKB_Columns = tuple(['ID']+RHMH.mkb10)
        SelectDB.selected_columns(Controller.TableMKB_Columns , Controller.Table_MKB , columnvar=False)

        Controller.TableZaposleni_Columns = tuple(['ID']+RHMH.zaposleni)
        SelectDB.selected_columns(Controller.TableZaposleni_Columns , Controller.Table_Zaposleni , columnvar=False)

            # NOTEBOOK Tab GRAPH -- 3
        Controller.Graph_Canvas = MainPanel.GraphTab_Create()

            # NOTEBOOK Tab LOGS -- 4
        Controller.Table_Logs, Controller.FreeQuery_Frame = MainPanel.LogsTab_Create('Logs', SelectDB.fill_LogsForm)
        Controller.TableLogs_Columns = tuple(['ID']+LOGS.logs)
        SelectDB.selected_columns(Controller.TableLogs_Columns , Controller.Table_Logs , columnvar=False)
        Controller.NoteBook.hide(4)

            # NOTEBOOK Tab SESSION -- 5
        Controller.Table_Session = MainPanel.SessionTab_Create('Session')
        Controller.TableSession_Columns = tuple(['ID']+LOGS.session)
        SelectDB.selected_columns(Controller.TableSession_Columns , Controller.Table_Session , columnvar=False)
        Controller.NoteBook.hide(5)

            # SETTINGS TAB -- 6
        Controller.Settings_Tab = MainPanel.SettingsTab_Create()

            # ABOUT TAB -- 7
        Controller.About_Tab = MainPanel.AboutTab_Create()

    @staticmethod
    def Roundbutton_Create(parent_frame:Frame):
        for i,(col,txt) in enumerate(Controller.FilterOptions.items()):
            Controller.FilterOptions[col] = [txt,IntVar()] # Ovde dodajen varijablu int da bi mogao da menjam sa json

            cb = tb.Checkbutton(parent_frame, text=txt, variable=Controller.FilterOptions[col][1], bootstyle='success, round-toggle')
            cb.grid(row=0, column=i, padx=padding_6, pady=(0,3))

            butt = ctk.CTkButton(parent_frame, text='FILTER', width=buttonX, height=buttonY//2, corner_radius=10,
                            font=font_medium(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'],text_color_disabled=ThemeColors['secondary'],
                                command=lambda column=col: SelectDB.filter_data(column))
            butt.grid(row=1, column=i, padx=padding_6, pady=(0,3))
            Controller.Buttons['Filter Patient'] += [cb,butt]

    @staticmethod
    def filter_maintable_switch(parent, savingplace, row, col, rowspan, sticky):
        cb = tb.Checkbutton(parent, text='      FILTER\n from Pacijenti', bootstyle='info, round-toggle')
        savingplace['Filter Main Table'] = (cb,IntVar())
        cb.configure(variable=savingplace['Filter Main Table'][1])
        cb.grid(row=row, column=col, rowspan=rowspan, padx=padding_12, pady=padding_6, sticky=sticky)
        cb.grid_remove()

    @staticmethod
    def SearchBar_StaticPart(searchButtonROW):
            # JUST LABEL for SEARCH (SEARCH BY, PRETRAZI)
        tb.Label(Controller.SearchBar, anchor=CENTER, bootstyle=color_labeltext, text='SEARCH BY', font=font_default).grid(
                            row=0, column=1, rowspan=Controller.max_SearchBars, padx=padding_6, pady=padding_6, sticky=NSEW)
            # FILTER OPTIONS
        filterFrame = Frame(Controller.SearchBar)
        filterFrame.grid(row=0,column=searchButtonROW,rowspan=Controller.max_SearchBars,sticky=SE)

        MainPanel.Roundbutton_Create(filterFrame)

        butf = ctk.CTkButton(filterFrame, text='FILTER\nBOTH', width=buttonX, height=buttonY, corner_radius=10,
                        font=font_medium(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                            command=lambda column=['Datum Operacije','Datum Otpusta']: SelectDB.filter_data(column))
        butf.grid(row=0, column=2, rowspan=Controller.max_SearchBars,
                padx=(padding_6[0],33), pady=padding_6, sticky=SE)
        Controller.Buttons['Filter Patient'].append(butf)

        MainPanel.filter_maintable_switch(parent=filterFrame,
                                          savingplace=Controller.Buttons,
                                          row=0, col=0, rowspan=Controller.max_SearchBars, sticky=SE)

            # BUTTONS for SEARCH and SHOWALL
        buts = ctk.CTkButton(Controller.SearchBar, text='SEARCH', width=buttonX, height=buttonY, corner_radius=10,
                        font=font_medium(), fg_color=ThemeColors['primary'],  text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=SelectDB.search_data)
        buts.grid(row=0, column=searchButtonROW+3, rowspan=Controller.max_SearchBars,
                padx=padding_6, pady=padding_6, sticky=SE)
        Controller.Buttons['Search'] = buts

        buta = ctk.CTkButton(Controller.SearchBar, text='SHOW ALL', width=buttonX, height=buttonY, corner_radius=10,
                        font=font_medium(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=SelectDB.showall_data)
        buta.grid(row=0, column=searchButtonROW+4, rowspan=Controller.max_SearchBars,
                padx=padding_6, pady=padding_6, sticky=SE)
        Controller.Buttons['Show All'] = buta

    @staticmethod
    def SearchBar_AddRemove():
                # BUTTONS for adding and removing SEARCH CRITERIA
        color_add, darker_add, color_remove, darker_remove = Media.label_ImageLoad(IMAGES['Add']+IMAGES['Remove'])

        add = tb.Label(Controller.SearchBar, image=color_add)
        add.grid(row=0, column=0, rowspan=Controller.max_SearchBars, sticky=NW)
        add.bind('<ButtonRelease-1>',SelectDB.search_bar_add)
        add.bind('<Enter>', lambda event,img=darker_add: Media.hover_label_button(event,img))
        add.bind('<Leave>', lambda event,img=color_add: Media.hover_label_button(event,img))

        remove = tb.Label(Controller.SearchBar, image=color_remove)
        remove.grid(row=0, column=0, rowspan=Controller.max_SearchBars, sticky=SW)
        remove.bind('<ButtonRelease-1>',SelectDB.search_bar_remove)
        remove.bind('<Enter>', lambda event,img=darker_remove: Media.hover_label_button(event,img))
        remove.bind('<Leave>', lambda event,img=color_remove: Media.hover_label_button(event,img))
        remove.grid_remove()

        return add,remove

    @staticmethod
    def SearchBar_DynamicPart():
        n = Controller.SearchBar_number
        ROW = Controller.SearchBar_number-1

        unite_frame = Frame(Controller.SearchBar)
        unite_frame.grid(row=ROW, column=4, sticky=EW)
        Controller.SearchBar_widgets[f'search_bar_{Controller.SearchBar_number}'] = unite_frame

        def create_widgets():
            # Selectin SEARCH Column
            col_val = Controller.TablePacijenti_Columns[1:] 
            Search_option = tb.Combobox(unite_frame, width=19, values=col_val, height=len(col_val), font=font_default, state='readonly')
            Search_option.grid(row=ROW, column=4, padx=padding_3, pady=padding_3, sticky=EW)

            Controller.SearchBar_widgets[f'search_option_{Controller.SearchBar_number}'] = Search_option
            Search_option.bind('<<ComboboxSelected>>', lambda event: SelectDB.search_options(n,event))
            
            # Selecting SEARCH Sign
            Controller.signimages = Media.label_ImageLoad(IMAGES['Signs'])
            Search_Sign = tb.Label(unite_frame, text=SIGNS[0], image=Controller.signimages[0])
            Search_Sign.grid(row=ROW, column=5, sticky=EW)
            Search_Sign.grid_remove()

            Controller.SearchBar_widgets[f'search_sign_{Controller.SearchBar_number}'] = Search_Sign
            Search_Sign.bind('<ButtonRelease-1>', lambda event: SelectDB.search_options_swap(event,Controller.signimages[:],SIGNS[:],n))
        
            # SEARCH Input FRAMES
            input_frame = Frame(unite_frame)
            input_frame.grid(row=ROW, column=6, sticky=EW)

            combo = tb.Combobox(input_frame, values=[], width=search_bigX, font=font_default, state='readonly')
            combo.grid(row=0, column=0, padx=padding_3, pady=padding_3, sticky=EW)
            combo.grid_remove()
            Controller.SearchBar_widgets[f'combo_{Controller.SearchBar_number}'] = combo

            for i in range(2):
                entry = tb.Entry(input_frame, width=search_bigX, font=font_default)
                entry.grid(row=0, column=i, padx=padding_3, pady=padding_3, sticky=EW)
                entry.grid_remove()
                Controller.SearchBar_widgets[f'entry{i+1}_{Controller.SearchBar_number}'] = entry

                date = widgets.DateEntry(input_frame, width=search_smallX+2, dateformat='%d-%b-%Y', firstweekday=0)
                date.grid(row=0, column=i, padx=padding_3, pady=padding_3, sticky=EW)
                date.grid_remove()
                date.entry.delete(0,END)
                Controller.SearchBar_widgets[f'date{i+1}_{Controller.SearchBar_number}'] = date

        create_widgets()
        Controller.SearchBar_number += 1

    @staticmethod
    def PacijentiTab_Create(tabname:str, method:callable) -> (tb.ttk.Treeview):
        table: tb.ttk.Treeview
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text=tabname)

        def PacijentiTable_Create():
            nonlocal table
            scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
            scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

            table = tb.ttk.Treeview(notebook_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=1, column=0, sticky=NSEW)
            
            for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
                table.bind(bindevent,method)
            table.bind('<Shift-Up>',SelectDB.shift_up)
            table.bind('<Shift-Down>',SelectDB.shift_down)

            scroll_x.grid(row=2, column=0, sticky=EW)
            scroll_y.grid(row=1, column=1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

        # Top Frame with CheckButtons
        extra_frame = Frame(notebook_frame)
        extra_frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        MainPanel.Checkbutton_Create(extra_frame)

        # Table Main Part
        PacijentiTable_Create()

        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)
        Controller.Table_Names[tabname] = table
        return table

    @staticmethod
    def Checkbutton_Create(parent_frame:Frame):
        swap = False
        grouping = [None, -1, 0]
        for orig_name,dicty in MainTablePacijenti.items():
            Controller.Pacijenti_ColumnVars[orig_name].set(1) # Svi ukljuceni na pocetku (prva 3 moraju biti jer su checkbutton: NONE)
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
                        lbl = tb.Label(frame,anchor=CENTER, bootstyle=color_labeltext, text=dicty['group'], font=font_medium())
                        lbl.grid(row=0, column=0, pady=4)
                if dicty['group']:
                    tb.Checkbutton(frame, text=dicty['checkbutton'], variable=Controller.Pacijenti_ColumnVars[orig_name],
                            bootstyle=style_checkbutton).grid(row=1, column=grouping[2], padx=6, pady=(0,4))
                    grouping[2] += 1

                else:
                    tb.Checkbutton(frame, text=dicty['checkbutton'], variable=Controller.Pacijenti_ColumnVars[orig_name],
                            bootstyle=style_checkbutton).grid(row=swap, column=grouping[2]-swap, padx=6, pady=(8*(not swap),4)) # ovo pady ce dati 8,4,4 padding
                    grouping[2] += 1
                    swap = not swap # vrti 0/1 za redove checkbuttona kod None grupe
        frame.grid_columnconfigure([i for i in range(grouping[2])], weight=1) # na kraju jos jednom za poslednju grupu
        frame.grid_rowconfigure([1,2],weight=1)
        parent_frame.grid_columnconfigure([i for i in range(grouping[1]+1)],weight=1)
    
    @staticmethod
    def SlikeTab_Create(tabname:str, tablewidth:int, method:callable, button_cmd:list) -> (tb.ttk.Treeview):
        table:tb.ttk.Treeview
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text=tabname)

        tableparent_frame = Frame(notebook_frame, width=tablewidth)
        tableparent_frame.grid(row=0, column=0, sticky=NSEW)
        tableparent_frame.grid_propagate(False) # Ovo je da table ne uzme prostor koliko joj treba za kolone
        tableparent_frame.grid_rowconfigure(1, weight=1) # Ovo je da se siri table a ne buttons
        tableparent_frame.grid_columnconfigure(0, weight=1) # Ovo je da se siri table a ne scroll

        Controller.Slike_HideTable = tableparent_frame # Ovo je da moze da se radi hide table frejma

        def ButtonsSlike_Create(parent, row, column):
            button_frame = Frame(parent)
            button_frame.grid(row=row, column=column, sticky=EW)
            button_frame.grid_columnconfigure(0, weight=1)

            ID = tb.Label(button_frame, bootstyle=color_labeltext, text='', font=font_medium('normal'))
            ID.grid(row=0, column=0, padx=padding_6, sticky=W)
            Controller.Slike_FormVariables['ID'] = ID

            for i,butt in enumerate(Image_buttons):
                button = ctk.CTkButton(button_frame, text=butt[0], width=buttonX, height=buttonY, corner_radius=10,
                                font=font_medium(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                command=button_cmd[i])
                button.grid(row=0, column=i+1, padx=padding_6, pady=padding_6, sticky=E)
                if butt[1]:
                    button.configure(fg_color=ThemeColors[butt[1]])
                Controller.Buttons[butt[0].replace('\n',' ')] = button

        def InputSlike_Create(parent, row, column):
            input_frame = Frame(parent)
            input_frame.grid(row=row, column=column, sticky=EW)
            input_frame.grid_columnconfigure(1, weight=1)

            for i,(txt,widget) in enumerate(zip(['Pacijent','Opis'],[tb.Entry,tb.Combobox])):
                Controller.Slike_FormVariables[txt] = StringVar()
                lbl = tb.Label(input_frame, anchor=CENTER, bootstyle=color_labeltext, text=txt, font=font_default)
                lbl.grid(row=0, column=i*2, padx=padding_6, pady=padding_6, sticky=E)
                ent = widget(input_frame, width=search_bigX, font=font_default, textvariable=Controller.Slike_FormVariables[txt])
                ent.grid(row=0, column=i*2+1, padx=padding_6, pady=padding_6, sticky=EW)
                if txt=='Opis':
                    ent.configure(values=RHMH.get_distinct('slike',*('Opis',)))
                else:
                    ent.configure(state='readonly')
                

        def TableSlike_Create(parent, row, column):
            nonlocal table
            scroll_x = tb.Scrollbar(parent, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
            scroll_y = tb.Scrollbar(parent, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

            table = tb.ttk.Treeview(parent, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=row, column=column, sticky=NSEW)
            
            for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
                table.bind(bindevent, method)
            table.bind('<Shift-Up>',SelectDB.shift_up)
            table.bind('<Shift-Down>',SelectDB.shift_down)

            scroll_x.grid(row=row+1, column=column, sticky=EW)
            scroll_y.grid(row=row, column=column+1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

        #editorparent_frame = Frame(notebook_frame, width=tablewidth)
        #editorparent_frame.grid(row=0, column=0, sticky=NSEW)

        def SlikeEditor_Create(row,column):
            pass

        # Table+ManageDB Left Side
        Slike_TopFrame = Frame(tableparent_frame, bd=2, relief=RAISED)
        Slike_TopFrame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        Slike_TopFrame.grid_columnconfigure(0,weight=1)
        ButtonsSlike_Create(parent=Slike_TopFrame, row=0, column=0)
        InputSlike_Create(parent=Slike_TopFrame, row=1, column=0)

        TableSlike_Create(parent=tableparent_frame, row=1, column=0)

        # CANVAS Right Side
        canvas_frame = Frame(notebook_frame, bd=3, relief=RAISED)
        canvas_frame.grid(row=0, column=1, sticky=NSEW)
        MainPanel.Slike_SideFrame(canvas_frame)

        notebook_frame.grid_rowconfigure(0, weight=1) # Ovo je da se sire nadole svi elementi
        notebook_frame.grid_columnconfigure(1, weight=1) # Ovo je da se siri canvas a ne table i editor
        Controller.Table_Names[tabname] = table
        return table

    @staticmethod
    def Slike_SideFrame(parent_frame:Frame):
        Media.Slike_Viewer = Canvas(parent_frame)
        Media.Slike_Viewer.pack(side=LEFT, fill=BOTH, expand=True)

        MainPanel.scroll_y = tb.Scrollbar(Media.Slike_Viewer, orient=VERTICAL, command=Media.Slike_Viewer.yview)
        MainPanel.scroll_y.pack(side=RIGHT, fill=Y)
        MainPanel.scroll_x = tb.Scrollbar(Media.Slike_Viewer, orient=HORIZONTAL, command=Media.Slike_Viewer.xview)
        MainPanel.scroll_x.pack(side=BOTTOM, fill=X)
        Media.Slike_Viewer.configure(yscrollcommand=MainPanel.scroll_y.set, xscrollcommand=MainPanel.scroll_x.set)

    @staticmethod
    def KatalogTab_Create(tabname:str, mkbside:dict, zaposleniside:dict) -> (tb.ttk.Treeview):
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text=tabname)
        notebook_frame.grid_columnconfigure(0,weight=1) # MKB se siri (tj left side)
        notebook_frame.grid_rowconfigure(0,weight=1) # MKB se siri (tj left side)

        def Create_One_Side(bindmethods:dict, *args):
            PartFrame = tb.Frame(notebook_frame)
            PartFrame.grid(row=0, column=COLUMN, sticky=NSEW) # Ovo sticky mora da bi se rasirio frame
            PartFrame.grid_rowconfigure(1, weight=1) # tabela se siri
            PartFrame.grid_columnconfigure(0, weight=1) # tabela se siri

            scroll_x = tb.Scrollbar(PartFrame, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
            scroll_y = tb.Scrollbar(PartFrame, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

            table = tb.ttk.Treeview(PartFrame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=1, column=0, sticky=NSEW)
            
            for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
                table.bind(bindevent,bindmethods['fill_Form'])
            table.bind('<Double-1>',bindmethods['double_click'])
            table.bind('<Shift-Up>',SelectDB.shift_up)
            table.bind('<Shift-Down>',SelectDB.shift_down)

            scroll_x.grid(row=2, column=0, sticky=EW)
            scroll_y.grid(row=1, column=1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

            entry_Frame = Frame(PartFrame, bd=2, relief=RAISED)
            entry_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
            MainPanel.Katalog_Entry_Create(entry_Frame,*args) # Katalog_Entry_Create

            return table

        COLUMN = 0 # Left Part -- (0,0) je za row,col za frejm ispod tabele
        tableMKB = Create_One_Side( mkbside['bindmethods'],
                                   *[Katalog_Entry['mkb10'],mkbside['buttons']])
        COLUMN += 1 # Right Part -- (1,-1) je za row,col za frejm ispod tabele
        tableZapo = Create_One_Side( zaposleniside['bindmethods'],
                                    *[Katalog_Entry['zaposleni'],zaposleniside['buttons']])
        Controller.Table_Names[tabname] = [tableMKB,tableZapo]
        return tableMKB,tableZapo

    @staticmethod
    def Katalog_Entry_Create(parent_frame:Frame,entry_dict:dict,buttons:list):  
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
                        button = ctk.CTkButton(frame, text=butt[0], width=buttonX, height=buttonY, corner_radius=10,
                            font=font_medium(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                            command=buttons[j-1])
                        button.grid(row=0, column=j-1, padx=padding_6, pady=padding_6)
                        if butt[1]:
                            button.configure(fg_color=ThemeColors[butt[1]])
                        Controller.Buttons[butt[0].replace('\n',' ')] = button
                        
            else:
                frame.grid(row=values[2][0], column=values[2][1], rowspan=values[2][2], columnspan=values[2][3], sticky=NSEW)
                if column == 'Combobox':
                    parent_frame.grid_columnconfigure(values[2][1], weight=1)
                    Controller.Katalog_FormVariables[values[0]] = StringVar()
                    VALUES = RHMH.dr_funkcija if values[0]=='Funkcija' else RHMH.dg_kategorija if values[0]=='Kategorija' else None
                    tb.Combobox(frame, values=VALUES, justify=CENTER,
                                textvariable=Controller.Katalog_FormVariables[values[0]],
                                width=values[1], font=font_default, state='readonly').grid(padx=12, pady=padding_3)
                    frame.grid_configure(sticky=E)
                    frame.grid_rowconfigure(0, weight=1)
                    parent_frame.grid_columnconfigure(values[2][1], weight=1)
                else:
                    Controller.Katalog_FormVariables[column] = StringVar()
                    tb.Label(frame, anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, text=values[0], font=font_default).grid(
                                row=0, column=0, padx=padding_3_12, pady=padding_3, sticky=EW)
                    tb.Entry(frame, width=values[1], font=font_default,
                                textvariable=Controller.Katalog_FormVariables[column]).grid(
                                    row=0, column=1, padx=padding_3_12, pady=padding_3, sticky=EW)
                    frame.grid_columnconfigure(1,weight=1) # Ovo kaze da se siri entry a ne label
                    frame.grid_rowconfigure(0,weight=1) # Ovo mora jer je Opis Dijagnoze u 2 reda da bi se rasirio prvi label          

    @staticmethod
    def LogsTab_Create(tabname:str, method:callable):      
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text=tabname)

        # Top FreeQuery Panel
        freequery_frame = Frame(notebook_frame)
        freequery_frame.grid(row=0, column=0, columnspan=3, sticky=NSEW)
        freequery_frame.grid_columnconfigure(0, weight=1)

        Controller.FreeQuery = StringVar()
        tb.Entry(freequery_frame, font=font_default, textvariable=Controller.FreeQuery).grid(
                    row=0, column=0, padx=padding_3_12, pady=padding_3, sticky=EW)
        
        button = ctk.CTkButton(freequery_frame, text='Free\nQuery', width=buttonX, height=buttonY, corner_radius=10,
            font=font_medium(), fg_color=ThemeColors['danger'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
            command=ManageDB.FreeQuery_Execute)
        button.grid(row=0, column=1, padx=padding_6, pady=padding_6)
        freequery_frame.grid_remove()
        Controller.Buttons['Free Query'] = button

        # Left Table Panel
        scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
        scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

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
        MainPanel.Log_SideFrame(text_frame)

        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=2)
        notebook_frame.grid_columnconfigure(2, weight=1)
        Controller.Table_Names[tabname] = table
        return table,freequery_frame

    @staticmethod
    def Log_SideFrame(parent_frame:Frame):
        lbl1 = tb.Label(parent_frame,text='Full Query', anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, font=font_medium())
        lbl1.grid(row=0, column=0)
        text1 = tb.Text(parent_frame, font=font_default)
        text1.grid(row=1, column=0, sticky=NSEW)
        Controller.Logs_FormVariables['Full Query'] = text1
        lbl1 = tb.Label(parent_frame,text='Full Error', anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, font=font_medium())
        lbl1.grid(row=2, column=0)
        text2 = tb.Text(parent_frame, font=font_default)
        text2.grid(row=3, column=0, sticky=NSEW)
        Controller.Logs_FormVariables['Full Error'] = text2

        parent_frame.grid_rowconfigure([1,3],weight=1)
        parent_frame.grid_columnconfigure(0,weight=1)

    @staticmethod
    def SessionTab_Create(tabname:str):
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text=tabname)

        scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
        scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

        table = tb.ttk.Treeview(notebook_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        table.grid(row=0, column=0, sticky=NSEW)
        
        scroll_x.grid(row=1, column=0, sticky=EW)
        scroll_y.grid(row=0, column=1, sticky=NS)
        scroll_x.config(command=table.xview)
        scroll_y.config(command=table.yview)


        side_panel = Frame(notebook_frame, bd=2, relief=RAISED)
        side_panel.grid(row=0, column=2, rowspan=2, sticky=NSEW)
        MainPanel.Session_SideFrame(side_panel)

        notebook_frame.grid_rowconfigure(0, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)
        notebook_frame.grid_columnconfigure(2, weight=4)
        Controller.Table_Names[tabname] = table
        return table

    @staticmethod
    def Session_SideFrame(parent_frame:Frame):

        def swapping_session_data(event):
            pass

        lbl1 = tb.Label(parent_frame,text='TESTING', anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, font=font_big('bold'))
        lbl1.grid(row=0, column=1)
        text1 = tb.Text(parent_frame, font=font_default)
        text1.grid(row=1, column=0, columnspan=3, sticky=NSEW)
        Controller.Logs_FormVariables['Session'] = text1

        color_buttonleft, darker_buttonleft, color_buttonright, darker_buttonright = Media.label_ImageLoad(IMAGES['Left']+IMAGES['Right'])

        buttonleft = tb.Label(parent_frame, image=color_buttonleft)
        buttonleft.grid(row=0, column=0, sticky=W)
        buttonleft.bind('<ButtonRelease-1>', swapping_session_data)
        buttonleft.bind('<Enter>', lambda event,img=darker_buttonleft: Media.hover_label_button(event,img))
        buttonleft.bind('<Leave>', lambda event,img=color_buttonleft: Media.hover_label_button(event,img))

        buttonright = tb.Label(parent_frame, image=color_buttonright)
        buttonright.grid(row=0, column=2, sticky=E)
        buttonright.bind('<ButtonRelease-1>', swapping_session_data)
        buttonright.bind('<Enter>', lambda event,img=darker_buttonright: Media.hover_label_button(event,img))
        buttonright.bind('<Leave>', lambda event,img=color_buttonright: Media.hover_label_button(event,img))

        parent_frame.grid_rowconfigure(1,weight=1)
        parent_frame.grid_columnconfigure(1,weight=1)

    @staticmethod
    def GraphTab_Create():
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text='Grafikon')
        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)

        optionsframe = Frame(notebook_frame, bd=3, relief=RAISED)
        optionsframe.grid(row=0, column=0, sticky=EW)
        
        values = list(Graph.Y_options.keys())
        width = len(max(values, key=len))-6
        labelY = tb.Label(optionsframe, text=' Y-axis\n(Values)')
        labelY.grid(row=0, column=0, rowspan=2, padx=(12,3), pady=padding_3)
        combo = tb.Combobox(optionsframe, values=values, width=width, font=font_default, state='readonly')
        Controller.Graph_FormVariables['Y'] = (combo,StringVar())
        combo.configure(textvariable=Controller.Graph_FormVariables['Y'][1])
        combo.grid(row=0, column=1, rowspan=2, padx=padding_3, pady=padding_3)
        combo.bind("<<ComboboxSelected>>", lambda event, opt='Y': SelectDB.graph_choice_analyze(event,opt))

        def create_X_combo(row,col):
            for i in range(col,col+3):
                name = f'X{row+1}-{1+i-col}'
                combo = tb.Combobox(optionsframe, values=[], font=font_default, state='readonly')
                Controller.Graph_FormVariables[name] = (combo,StringVar())
                combo.configure(textvariable=Controller.Graph_FormVariables[name][1])

                combo.grid(row=row, column=i, padx=padding_3, pady=padding_3,sticky=EW)
                combo.bind("<<ComboboxSelected>>", lambda event, opt=name: SelectDB.graph_choice_analyze(event,opt))
                combo.grid_remove()
    
        def add_button(col):
            color_add, darker_add = Media.label_ImageLoad(IMAGES['Add'])
            add = tb.Label(optionsframe, image=color_add)
            add.grid(row=0, column=col, sticky=W)
            add.bind('<ButtonRelease-1>', SelectDB.graph_activating_X2)
            add.bind('<Enter>', lambda event,img=darker_add: Media.hover_label_button(event,img))
            add.bind('<Leave>', lambda event,img=color_add: Media.hover_label_button(event,img))
            Controller.Graph_FormVariables['Add'] = add
            add.grid_remove()

        def colorvalues_options(col):
            frame_c = Frame(optionsframe)
            frame_c.grid(row=0, column=col, rowspan=2, padx=padding_3, pady=padding_3, sticky=NSEW)
            frame_c.grid_rowconfigure(0, weight=1)
            for i,txt in enumerate(['values','color']):
                cb = tb.Checkbutton(frame_c, text=txt, bootstyle=style_checkbutton)
                Controller.Graph_FormVariables['afterchoice'][txt] = (cb,IntVar())
                cb.configure(variable=Controller.Graph_FormVariables['afterchoice'][txt][1])

                cb.grid(row=i, column=col, padx=padding_6, pady=padding_6, sticky='nsw')
                cb.grid_remove()

        def radio_choice(col):
            frame_r = Frame(optionsframe)
            frame_r.grid(row=0, column=col, rowspan=2, padx=padding_3, pady=padding_3, sticky=NSEW)
            Controller.Graph_FormVariables['afterchoice']['radio'] = {'widgets':{},'choice':StringVar(value='bars')}
            for txt in ['bars','pie','stacked']:
                ROW = 0 if txt=='bars' else 1
                radio = tb.Radiobutton(frame_r, text=txt, variable=Controller.Graph_FormVariables['afterchoice']['radio']['choice'], value=txt)
                radio.grid(row=ROW, column=0, padx=padding_6, pady=padding_6, sticky=W)
                Controller.Graph_FormVariables['afterchoice']['radio']['widgets'][txt] = radio
                radio.grid_remove()

        def showgraph_button(col):
            button = ctk.CTkButton(optionsframe, text='SHOW\nGraph', width=buttonX, height=buttonY, corner_radius=10,
                font=font_medium(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                command=SelectDB.Show_Graph)
            button.grid(row=0, column=col, rowspan=2, padx=padding_12, pady=padding_3, sticky=E)
            Controller.Buttons['SHOW\nGraph'.replace('\n',' ')] = button
            button.configure(state=DISABLED)

        Controller.Graph_FormVariables['afterchoice'] = dict()

        labelY = tb.Label(optionsframe, text=' X-axis\n(Groups)')
        labelY.grid(row=0, column=2, rowspan=2, padx=padding_6, pady=padding_3)
        create_X_combo(row=0, col=3) 
        create_X_combo(row=1, col=3) 

        blankspace = 6
        add_button(col=blankspace)
        radio_choice(col=7)
        colorvalues_options(col=8)
        MainPanel.filter_maintable_switch(parent= optionsframe,
                                          savingplace= Controller.Graph_FormVariables['afterchoice'],
                                          row=0, col=9, rowspan=2, sticky=W)
        showgraph_button(col=10)

        optionsframe.grid_columnconfigure(blankspace, weight=1) # checkbuttoni zauzimaju prazan i ravnaju E
        optionsframe.grid_rowconfigure(0, weight=1)

        plotframe = Frame(notebook_frame, bd=3, relief=RAISED)
        plotframe.grid(row=1,column=0, sticky=NSEW)
        


        return plotframe

    @staticmethod
    def SettingsTab_Create():
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text='Settings')

        settings = ['Theme','Language','Title','Font','Showed Columns','Font Size']
        settings += ['Theme1','Language1','Title1','Font1','Showed Columns1','Font Size1']

        #notebook_frame.grid_rowconfigure([i for i in range(len(settings)//2)], weight=1)
        notebook_frame.grid_columnconfigure(0,weight=1)
        #notebook_frame.grid_columnconfigure(1,weight=1)

        frame = Frame(notebook_frame, bd=2, relief=RAISED)
        frame.grid(row=0, column=0, sticky=NSEW)
        Theme_Names = ['Fruit','Moon','Sunrise','Night','Flower','Sunset','Sea']
        frame.grid_columnconfigure([i for i in range(len(Theme_Names))], weight=1)

        theme_images = Media.label_ImageLoad(IMAGES['Themes'])
        Controller.Settings_FormVariables['Theme'] = StringVar(value='Moon')
        for i,(nam,img) in enumerate(zip(Theme_Names,theme_images)):
            Media.ThemeIcons.append(img)
            label = tb.Label(frame, image=Media.ThemeIcons[i])
            label.grid(row=0, column=i, padx=padding_6, pady=padding_6, sticky=NSEW)

            radio = tb.Radiobutton(frame, text=nam, variable=Controller.Settings_FormVariables['Theme'], value=nam)
            radio.grid(row=1, column=i, padx=padding_6, pady=padding_6, sticky=EW)

        '''
        frame = Frame(notebook_frame, bd=2, relief=RAISED)
        frame.grid(row=1, column=0, sticky=NSEW)
        Image_Names = ['God','Eye','Monkey','RHMH']
        frame.grid_columnconfigure([i for i in range(len(Image_Names))], weight=1)

        images = [v[0] for v in IMAGES['Title'].values()]
        pil_images = Media.label_ImageLoad(images)
        for img in pil_images:
            Media.TitleImages.append(Media.resize_image(img,max_height=200,max_width=300))

        Controller.Settings_FormVariables['Title Image'] = StringVar(value='God')
        for i,(nam,img) in enumerate(zip(Image_Names,Media.TitleImages)):
            label = tb.Label(frame, image=img)
            label.grid(row=0, column=i, padx=padding_6, pady=padding_6, sticky=NSEW)

            radio = tb.Radiobutton(frame, text=nam, variable=Controller.Settings_FormVariables['Theme'], value=nam)
            radio.grid(row=1, column=i, padx=padding_6, pady=padding_6, sticky=EW)
        #'''

        return notebook_frame
    
    @staticmethod
    def AboutTab_Create():
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text='About')

        return notebook_frame
    
if __name__=='__main__':
    pass