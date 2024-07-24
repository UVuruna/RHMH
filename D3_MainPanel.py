from A1_Variables import *
from B2_SQLite import RHMH,LOGS
from B3_Media import Media
from B4_Graph import Graph
from C1_Controller import Controller,GodMode
from C2_ManageDB import ManageDB
from C3_SelectDB import SelectDB

class MainPanel:

    @staticmethod
    def initializeMP(root:Tk) -> None:
        MainPanel.disabled_txtcolor = ThemeColors['secondary']
        MainPanel.txtcolor = ThemeColors['bg']
        Controller.FilterOptions = {'Datum Operacije':'Operisan', 'Datum Otpusta':'Otpušten'}

        # PARENT FRAME for RIGHT PANEL
        notebookROW = 9
        Window_Frame = Frame(root)
        Window_Frame.grid(row=1, column=1, padx=padding_6, pady=padding_0_6, sticky=NSEW)
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
        Controller.TableLogs_Columns = tuple(['ID']+LOGS.logs[:4])
        SelectDB.selected_columns(Controller.TableLogs_Columns , Controller.Table_Logs , columnvar=False)
        Controller.NoteBook.hide(4)

            # NOTEBOOK Tab SESSION -- 5
        Controller.Table_Session = MainPanel.SessionTab_Create('Session', SelectDB.fill_SessionForm)
        Controller.TableSession_Columns = tuple(['ID']+LOGS.session[:4])
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

            butt_color = ThemeColors['info']
            butt = ctk.CTkButton(parent_frame, text='FILTER', width=buttonX, height=buttonY//2, corner_radius=10,
                            font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                            text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
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

        butt_color = ThemeColors['info']
        butf = ctk.CTkButton(filterFrame, text='FILTER\nBOTH', width=buttonX, height=buttonY, corner_radius=10,
                        font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                        text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
                            command=lambda column=['Datum Operacije','Datum Otpusta']: SelectDB.filter_data(column))
        butf.grid(row=0, column=2, rowspan=Controller.max_SearchBars,
                padx=(padding_6[0],33), pady=padding_6, sticky=SE)
        Controller.Buttons['Filter Patient'].append(butf)

        MainPanel.filter_maintable_switch(parent=filterFrame,
                                          savingplace=Controller.Buttons,
                                          row=0, col=0, rowspan=Controller.max_SearchBars, sticky=SE)

            # BUTTONS for SEARCH and SHOWALL
        butt_color = ThemeColors['primary']
        buts = ctk.CTkButton(Controller.SearchBar, text='SEARCH', width=buttonX, height=buttonY, corner_radius=10,
                        font=font_medium('bold'), fg_color=butt_color,  text_color=MainPanel.txtcolor,
                        text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
                        command=SelectDB.search_data)
        buts.grid(row=0, column=searchButtonROW+3, rowspan=Controller.max_SearchBars,
                padx=padding_6, pady=padding_6, sticky=SE)
        Controller.Buttons['Search'] = buts

        buta = ctk.CTkButton(Controller.SearchBar, text='SHOW ALL', width=buttonX, height=buttonY, corner_radius=10,
                        font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                        text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
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
        MainPanel.Checkbutton_Create(extra_frame, settings=False)

        # Table Main Part
        PacijentiTable_Create()

        notebook_frame.grid_rowconfigure(1, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)
        Controller.Table_Names[tabname] = table
        return table

    @staticmethod
    def Checkbutton_Create(parent_frame:Frame, settings:bool):
        swap = False
        grouping = [None, -1, 0]
        var:BooleanVar

        if settings is True:
            Controller.Settings_FormVariables['Columns'] = {}
        for orig_name,dicty in MainTablePacijenti.items():
            if orig_name not in ['Ime','Prezime','id_pacijent','ID']:
                if settings is True:
                    Controller.Settings_FormVariables['Columns'][orig_name] = BooleanVar()
                    var = Controller.Settings_FormVariables['Columns'][orig_name]
                else:
                    var = Controller.Pacijenti_ColumnVars[orig_name]
                var.set(SETTINGS['Columns'][orig_name])
                
            else:
                Controller.Pacijenti_ColumnVars[orig_name].set(1)

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
                    frame = Frame(parent_frame)
                    if settings is False:
                        frame.configure(bd=2, relief=RAISED)
                    frame.grid(row=0, column=grouping[1], sticky=NSEW)
                    if dicty['group']:
                        lbl = tb.Label(frame,anchor=CENTER, bootstyle=color_labeltext, text=dicty['group'], font=font_medium())
                        lbl.grid(row=0, column=0, pady=4)

                cb = tb.Checkbutton(frame, text=dicty['checkbutton'], bootstyle=style_checkbutton, variable=var)
                if dicty['group']:
                    cb.grid(row=1, column=grouping[2], padx=6, pady=(0,4))
                    grouping[2] += 1
                else:
                    cb.grid(row=swap, column=grouping[2]-swap, padx=6, pady=(8*(not swap),4)) # ovo pady ce dati 8,4,4 padding
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
                butt_color = ThemeColors['primary']
                button = ctk.CTkButton(button_frame, text=butt[0], width=buttonX, height=buttonY, corner_radius=10,
                                font=font_medium('bold'), text_color=MainPanel.txtcolor, text_color_disabled=MainPanel.disabled_txtcolor,
                                command=button_cmd[i])
                button.grid(row=0, column=i+1, padx=padding_6, pady=padding_6, sticky=E)
                if butt[1]:
                    butt_color = ThemeColors[butt[1]]
                    button.configure(fg_color=butt_color, hover_color=Media.darken_color(butt_color))
                else:
                    butt_color = ThemeColors['primary']
                    button.configure(fg_color=butt_color, hover_color=Media.darken_color(butt_color))

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
                            font=font_medium('bold'), text_color=MainPanel.txtcolor, text_color_disabled=MainPanel.disabled_txtcolor,
                            command=buttons[j-1])
                        button.grid(row=0, column=j-1, padx=padding_6, pady=padding_6)
                        if butt[1]:
                            butt_color = ThemeColors[butt[1]]
                            button.configure(fg_color=butt_color, hover_color=Media.darken_color(butt_color))
                        else:
                            butt_color = ThemeColors['primary']
                            button.configure(fg_color=butt_color, hover_color=Media.darken_color(butt_color))
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

        Controller.QueryDatabase = StringVar()
        tb.Combobox(freequery_frame, values=['RHMH','LOGS'], textvariable=Controller.QueryDatabase, width=5,
                    font=font_medium('normal'), state='readonly').grid(
                        row=0, column=0, padx=padding_6, pady=padding_3, sticky=EW)

        Controller.FreeQuery = StringVar()
        tb.Entry(freequery_frame, font=font_default, textvariable=Controller.FreeQuery).grid(
                    row=0, column=1, padx=padding_6, pady=padding_3, sticky=EW)
        
        butt_color = ThemeColors['danger']
        button = ctk.CTkButton(freequery_frame, text='Free\nQuery', width=buttonX, height=buttonY, corner_radius=10,
            font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
            text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
            command=GodMode.FreeQuery_Execute)
        button.grid(row=0, column=2, padx=padding_6, pady=padding_6)
        freequery_frame.grid_remove()
        Controller.Buttons['Free Query'] = button

        button = ctk.CTkButton(freequery_frame, text='Upload\nLOGS', width=buttonX, height=buttonY, corner_radius=10,
            font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
            text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
            command=GodMode.upload_GD_LOGS)
        button.grid(row=0, column=3, padx=padding_6, pady=padding_6)
        freequery_frame.grid_remove()
        Controller.Buttons['Upload LOGS'] = button

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
    def SessionTab_Create(tabname:str, method:callable):
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text=tabname)

        scroll_x = tb.Scrollbar(notebook_frame, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
        scroll_y = tb.Scrollbar(notebook_frame, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

        table = tb.ttk.Treeview(notebook_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        table.grid(row=0, column=0, sticky=NSEW)
        
        for bindevent in ['<ButtonRelease-1>','<KeyRelease-Down>','<KeyRelease-Up>']:
            table.bind(bindevent,method)

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

        Controller.SessionLabel = tb.Label(parent_frame,text='PC', anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, font=font_big('bold'))
        Controller.SessionLabel.grid(row=0, column=1)
        text1 = tb.Text(parent_frame, font=font_medium('normal'))
        text1.grid(row=1, column=0, columnspan=3, sticky=NSEW)
        Controller.Logs_FormVariables['Session'] = text1

        color_buttonleft, darker_buttonleft, color_buttonright, darker_buttonright = Media.label_ImageLoad(IMAGES['Left']+IMAGES['Right'])

        buttonleft = tb.Label(parent_frame, image=color_buttonleft)
        buttonleft.grid(row=0, column=0, sticky=W)
        buttonleft.bind('<ButtonRelease-1>', lambda event,direction=-1: SelectDB.swapping_session_data(event, direction))
        buttonleft.bind('<Enter>', lambda event,img=darker_buttonleft: Media.hover_label_button(event,img))
        buttonleft.bind('<Leave>', lambda event,img=color_buttonleft: Media.hover_label_button(event,img))

        buttonright = tb.Label(parent_frame, image=color_buttonright)
        buttonright.grid(row=0, column=2, sticky=E)
        buttonright.bind('<ButtonRelease-1>', lambda event, direction=1: SelectDB.swapping_session_data(event, direction))
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
            butt_color = ThemeColors['primary']
            button = ctk.CTkButton(optionsframe, text='SHOW\nGraph', width=buttonX, height=buttonY, corner_radius=10,
                font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
                command=SelectDB.Show_Graph)
            button.grid(row=0, column=col, rowspan=2, padx=padding_3_12, pady=padding_3, sticky=E)
            Controller.Buttons['SHOW Graph'] = button
            button.configure(state=DISABLED)
        
        def configure_button(col):
            butt_color = ThemeColors['info']
            button = ctk.CTkButton(optionsframe, text='CONFIGURE\nGraph', width=buttonX, height=buttonY, corner_radius=10,
                font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
                command=SelectDB.Configure_Graph)
            button.grid(row=0, column=col, rowspan=2, padx=padding_6, pady=padding_3, sticky=E)
            Controller.Buttons['CONFIGURE Graph'] = button
            button.grid_remove()

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
        configure_button(col=10)
        showgraph_button(col=11)

        optionsframe.grid_columnconfigure(blankspace, weight=1) # checkbuttoni zauzimaju prazan i ravnaju E
        optionsframe.grid_rowconfigure(0, weight=1)

        plotframe = Frame(notebook_frame, bd=3, relief=RAISED)
        plotframe.grid(row=1,column=0, sticky=NSEW)

        return plotframe

    @staticmethod
    def SettingsTab_Create():
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text='Settings')

        setting_width = int(WIDTH/1.4)

        def create_setting_title(row, text, buffer=True):
            frame = Frame(notebook_frame, bd=2, relief=SUNKEN)
            frame.grid(row=row, column=0, sticky=NSEW)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(1,weight=1)

            tb.Label(frame, text=text, anchor=W, font=font_big('normal'), bootstyle=color_labeltext).grid(
                row=0, column=0, padx=33, pady=padding_6, sticky=NSEW)
            
            options_frame = Frame(frame)
            options_frame.grid(row=1,column=0, sticky=NSEW)

            if buffer is True:
                Frame(frame).grid(row=2,column=0,pady=6) # Spacing
            
 
            return options_frame

        def Theme(row):
            options_frame = create_setting_title(row, 'Theme Option')

            count = len(Theme_Names)
            options_frame.grid_columnconfigure([i for i in range(count)], weight=1)

            width = setting_width//count
            height = int(width/1.8)
            theme_big_images = [(i,width,height) for i in IMAGES['Themes']]
            theme_label_images = Media.label_ImageLoad(theme_big_images)
            Controller.Settings_FormVariables['Theme'] = StringVar(value=SETTINGS['Theme'])
            for i,(nam,img) in enumerate(zip(Theme_Names,theme_label_images)):
                Media.ThemeIcons.append(img)
                label = Label(options_frame, image=Media.ThemeIcons[i], highlightbackground=ThemeColors[color_highlight], highlightthickness=2)
                label.grid(row=0, column=i, padx=padding_6, pady=padding_6, sticky=NSEW)

                radio = tb.Radiobutton(options_frame, text=nam, variable=Controller.Settings_FormVariables['Theme'], value=nam)
                radio.grid(row=1, column=i, sticky=N)

        def Title(row):
            options_frame = create_setting_title(row, 'Title Image Option')

            count = len(Title_Names)
            options_frame.grid_columnconfigure([i for i in range(count)], weight=1)
            width = setting_width//count
            height = width//4

            title_big_images = []
            for img in IMAGES['Title'].values():
                if isinstance(img,tuple):
                    title_big_images.append((img[Theme_Names.index(THEME)],width,height))
                elif isinstance(img,list):
                    title_big_images.append((img[0],width,height))
                else:
                    title_big_images.append((img,width,height))
            title_label_images = Media.label_ImageLoad(title_big_images)

            Controller.Settings_FormVariables['Title'] = StringVar(value=SETTINGS['Title'])
            for i,(nam,img) in enumerate(zip(Title_Names,title_label_images)):
                Media.TitleIcons.append(img)
                label = Label(options_frame, image=Media.TitleIcons[i], highlightbackground=ThemeColors[color_highlight], highlightthickness=2)
                label.grid(row=0, column=i, padx=padding_6, pady=padding_6, sticky=NSEW)

                radio = tb.Radiobutton(options_frame, text=nam, variable=Controller.Settings_FormVariables['Title'], value=nam)
                radio.grid(row=1, column=i, sticky=N)
        
        def MainTable(row):
            options_frame = create_setting_title(row, 'Starting Columns for "Pacijenti" Table')

            MainPanel.Checkbutton_Create(options_frame, settings=True)

        def System(row):
            options_frame = create_setting_title(row, 'System Settings', buffer=False)

            Values = {
                'Fonts': [
                    'Arial',
                    'Courier New',
                    'Georgia',
                    'Times New Roman',
                    'Trebuchet MS',
                    'Verdana'
                ],
                'Language': [
                    'English',
                    'Serbian',
                    'Latin'
                ]}

            SYSTEM = {
                'Language': Values['Language'],
                'Font': Values['Fonts'],
                'Font Size': (6,18,'',1),
                'Width': (1300,3300,'p',20),
                'Height': (600,1800,'p',10),
                'Title Height': (10,33,'%',1),
                'Button cooldown': (50,1000,'ms',25),
                'Thread cooldown': (5,100,'ms',5)
            }

            Controller.Settings_FormVariables['System'] = {} 
            
            for i,(txt,values) in enumerate(SYSTEM.items()):    
                AMOUNT = SETTINGS['System'][txt]
                STYLE = 'success' if i < 3 else 'warning' if i > 5 else 'info' 

                if i>1:
                    MIN,MAX,unit,jump = values
                    meter = tb.Meter(
                        master=options_frame,
                        metersize=140,
                        bootstyle=STYLE,
                        subtextstyle=STYLE,
                        subtext=txt,
                        textright=unit,
                        padding=padding_3,
                        amountused=AMOUNT,
                        amountmin=MIN,
                        amounttotal=MAX,
                        stepsize=jump,
                        stripethickness=math.ceil(270/((MAX-MIN)/jump)),
                        metertype="semi",
                        interactive=True,
                    )
                    meter.grid(row=0, column=i, rowspan=2, sticky=N)
                    Controller.Settings_FormVariables['System'][txt] = meter

                else:
                    width = len(max(values, key=len))
                    Controller.Settings_FormVariables['System'][txt] = StringVar()
                    combo = tb.Combobox(options_frame, values=values, justify=CENTER, bootstyle=STYLE,
                                textvariable=Controller.Settings_FormVariables['System'][txt],
                                width=width, font=font_medium('normal'), state='readonly')
                    combo.grid(row=0, column=i, padx=padding_6, pady=padding_6, sticky=EW)
                    combo.set(AMOUNT)

                    tb.Label(options_frame, text=txt, anchor=CENTER, font=font_big('bold'), bootstyle=STYLE).grid(
                    row=1, column=i, padx=padding_6, pady=padding_6, sticky=N)

            cols = len(SYSTEM)

            butt_color = ThemeColors['info']
            restore = ctk.CTkButton(options_frame, text='RESTORE\nDefault', width=buttonX, height=buttonY, corner_radius=10,
                    font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                    text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
                    command=Controller.restore_default_settings)
            restore.grid(row=0, column=cols, rowspan=2, padx=padding_6, pady=padding_6, sticky=SE)

            butt_color = ThemeColors['success']
            save = ctk.CTkButton(options_frame, text='SAVE\nSettings', width=buttonX, height=buttonY, corner_radius=10,
                    font=font_medium('bold'), fg_color=butt_color, text_color=MainPanel.txtcolor,
                    text_color_disabled=MainPanel.disabled_txtcolor, hover_color=Media.darken_color(butt_color),
                    command=Controller.update_settings)
            save.grid(row=0, column=cols+1, rowspan=2, padx=padding_6, pady=padding_6, sticky=SE)

            options_frame.grid_columnconfigure([i for i in range(cols+2)],weight=1)
            options_frame.grid_rowconfigure(1,weight=1)

        Theme(0)
        Title(1)
        MainTable(2)
        System(3)
        notebook_frame.grid_rowconfigure(3,weight=1)
        notebook_frame.grid_columnconfigure(0,weight=1)
        return notebook_frame
    
    @staticmethod
    def AboutTab_Create():
        notebook_frame = tb.Frame(Controller.NoteBook)
        Controller.NoteBook.add(notebook_frame, text='About')
        notebook_frame.grid_rowconfigure(2,weight=1)
        notebook_frame.grid_columnconfigure(1,weight=1)

        def Top_Panel():
            TEXT = 'MUVS - Rekonstruktivna hirurgija i Mikrohirurgija'
            ABOUT = ('  Ova aplikacija napravljena je u naučne svrhe praćenja podataka o pacijentima '
                    'na Kliničkom Centru na Klinici za Ortopedsku Hirurgiju i Traumatologiju '
                    'za odeljenje Rekonstruktivne Hirurgije i Mikrohirurgije\n\n'
                    '  Aplikacija je bazirana na SQL jeziku i radjena je u Python-u. '
                    'Opremljena je Veštačkom Inteligencijom za izvlačenje teksta iz formulara i automatsko unošenje novih pacijenata '
                    'Takođe je opremljena automatskim kreiranjem Grafikona na osnovu željenih parametara za praćenje ')

            title = tb.Label(notebook_frame, text=TEXT, anchor=CENTER, font=font_big('bold'), wraplength=WIDTH//1.33, bootstyle='primary')
            title.grid(row=0, column=0, columnspan=2, padx=padding_12, pady=(12,2), sticky=NSEW)

            top_panel = tb.Label(notebook_frame, text=ABOUT, anchor=W, font=font_medium('normal'), wraplength=WIDTH//1.33, bootstyle=color_labeltext)
            top_panel.grid(row=1, column=0, columnspan=2, padx=padding_3, pady=padding_3_12, sticky=NSEW)

        def Left_Panel():

            left_panel = tb.Frame(notebook_frame)
            left_panel.grid(row=2, column=0, sticky=NSEW)

            TEXT = dict()
            TEXT['Product Manager:'] = ('Uroš Vuruna',)
            TEXT['Project Manager:'] = ('Miloš Vuruna',)
            TEXT['UI Developer:'] = ('Uroš Vuruna','Miloš Vuruna')
            TEXT['UX Developer:'] = ('Uroš Vuruna','Miloš Vuruna')
            TEXT['Backend Developer:'] = ('Uroš Vuruna',)
            TEXT['MAC OS Adaptation:'] = ('Miloš Vuruna','Uroš Vuruna','Jovan Grčić')
            TEXT['Database Administrator:'] = ('Miloš Vuruna','Uroš Vuruna')
            left = len(max(TEXT.keys(),key=len))

            for i,(role,developers) in enumerate(TEXT.items()):
                role:str
                frame = tb.Frame(left_panel)
                frame.grid(row=i, column=0, columnspan=2, sticky=NSEW, padx=padding_3, pady=padding_3)
                frame.grid_columnconfigure(1,weight=1)

                label = tb.Label(frame, text=role, anchor=E, width=left+2, font=font_medium('bold'), bootstyle=color_labeltext)
                label.grid(row=0, column=0, rowspan=len(developers), padx=padding_6, pady=padding_3, sticky=NE)
                for j,developer in enumerate(developers):
                    label = tb.Label(frame, text=developer, anchor=W, font=font_medium('normal'), bootstyle=color_labeltext)
                    label.grid(row=j, column=1, padx=padding_6, pady=padding_3, sticky=W)


            label1_l = tb.Label(left_panel, text='Technical support email: ', anchor=E, font=font_medium('normal'), bootstyle=color_labeltext)
            label1_l.grid(row=i+1, column=0, padx=padding_6, pady=padding_3, sticky=E)
            label1_r = tb.Label(left_panel, text='vurunam@gmail.com', anchor=W, font=font_medium('bold'), bootstyle='primary')
            label1_r.grid(row=i+1, column=1, padx=padding_6, pady=padding_3, sticky=NSEW)
            label1_r.bind("<Button-1>", lambda event, email='vurunam@gmail.com': Controller.open_email(event,email))

            label2_l = tb.Label(left_panel, text='Git Code: ', anchor=E, font=font_medium('normal'), bootstyle=color_labeltext)
            label2_l.grid(row=i+2, column=0, padx=padding_6, pady=padding_3, sticky=E)
            label2_r = tb.Label(left_panel, text='https://github.com/UVuruna/RHMH', anchor=W, font=font_medium('bold'), bootstyle='primary')
            label2_r.grid(row=i+2, column=1, padx=padding_6, pady=padding_3, sticky=NSEW)
            label2_r.bind("<Button-1>", lambda event, link='https://github.com/UVuruna/RHMH': Controller.open_link(event,link))

            label3 = tb.Label(left_panel, text='Copyright © 2024 MUVS Inc., Serbia', anchor=W, font=font_medium('normal'), bootstyle=color_labeltext)
            label3.grid(row=i+3, column=0, columnspan=2, padx=padding_6, pady=padding_3, sticky=E)

            left_panel.grid_rowconfigure([j for j in range(i+3)], weight=1)
            
        def Right_Panel():
            image = IMAGES['MUVS'][0][0]
            Media.AboutImage = Image.open(image)

            Media.AboutCanvas = tb.Canvas(notebook_frame)
            Media.AboutCanvas.grid(row=2, column=1, sticky=NSEW)

            Media.AboutCanvas.bind('<Configure>' , Media.ajdust_About_logo)

        Top_Panel()
        Left_Panel()
        Right_Panel()
        return notebook_frame