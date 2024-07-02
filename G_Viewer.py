from A_Variables import *
from B_Decorators import method_efficency,spam_stopper,error_catcher
from C_GoogleDrive import GoogleDrive
from D_Media import Media
from E_SQLite import Database
from F_DBMS import DBMS,Buttons


class TitleFrame:
    def __init__(self,root) -> None: 
        self.BUTT = Buttons()
        image, (title_txt, txt_X, txt_Y) = IMAGES['Title']
        
        self.title_image = Image.open(image)
        self.txt_X = txt_X
        self.txt_Y = txt_Y
        self.title_txt = title_txt
    
        self.Title_Frame = tb.Canvas(root, height=title_height)
        self.Title_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        self.Title_Frame.bind('<Button-1>' , self.BUTT.lose_focus)
        self.Title_Frame.bind('<Configure>' , self.adjust_title_window)
        
        self.reconect_button = ctk.CTkButton(root, text='Reconect', width=form_butt_width,height=form_butt_height//2, corner_radius=12, font=font_label(),
                                 fg_color=ThemeColors['warning'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                 command=self.reconecting)
        
    def reconecting(self):
        print('RECONECTING...')

    def remove_title_frame(self,event):
        self.Title_Frame.grid_forget()

    def adjust_title_window(self, event):
        new_width = event.width
        new_height = event.height
        resized_image = self.title_image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        
        self.Title_Frame.image = tk_image 
        self.Title_Frame.delete('all')
        self.Title_Frame.create_image(0, 0, anchor=NW, image=tk_image)
        self.Title_Frame.create_text( new_width * self.txt_X,
                                    new_height * self.txt_Y,
                                    text = self.title_txt,
                                    anchor = NW, font = font_title, fill = ThemeColors[titleTxtColor] )

        self.Title_Frame.create_window(new_width*0.93, 10, anchor=N, window=self.reconect_button) # position of button

class FormFrame:
    def __init__(self, root:Tk) -> None:
        self.form_true = BooleanVar()
        self.form_true.set(True)
        self.root = root
        
        self.DBMS = DBMS()
        self.BUTT = Buttons()
        self.DB = self.DBMS.DB

        FormFrame.Form_button_fun =[self.BUTT.Add_Patient,
                                    self.BUTT.Update_Patient,
                                    self.BUTT.Delete_Patient,
                                    self.BUTT.Fill_FromImage,
                                    self.BUTT.Clear_Form    ]

        self.valid_notblank = root.register(self.BUTT.validate_notblank)
        self.valid_dijagnoza = root.register(self.BUTT.validate_dijagnoza)
        self.valid_godiste = root.register(self.BUTT.validate_godiste)
        self.valid_zaposleni = root.register(self.BUTT.validate_zaposleni)

            # PARENT FRAME for FORMS
        self.Form_Frame = Frame(root, bd=bd_main_frame, relief=RIDGE)
        self.Form_Frame.grid(row=1, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky=NSEW)
        self.Form_Frame.grid_rowconfigure(1,weight=1)

        self.BUTT.FormTitle = (self.Form_TopLabel(form_name),labelColor)

            # DEFAULT FORM CREATE
        self.DefaultForm = Frame(self.Form_Frame)
        self.DefaultForm.grid(row=1, column=0, columnspan=4, sticky=NSEW)
        self.FormPatient_Create(self.DefaultForm, default_form_entry, form_groups['Default'], 'Default')
            # ALTERNATIVE FORM CREATE
        self.AlternativeForm = Frame(self.Form_Frame)
        self.AlternativeForm.grid(row=1, column=0, columnspan=4, sticky=NSEW)
        self.AlternativeForm.grid_remove()
        self.FormPatient_Create(self.AlternativeForm, alternative_form_entry, form_groups['Alternative'], 'Alternative')
        self.FormPatient_Buttons(self.AlternativeForm,[3],Form_buttons)

    def Form_TopLabel(self,formname):
        gray_swap, color_swap, gray_hide, color_hide = Media.label_ImageLoad(IMAGES['Swap']+IMAGES['Hide'])

        swap = tb.Label(self.Form_Frame, image=gray_swap)
        swap.grid(row=0, column=0, sticky =NW)
        swap.bind('<ButtonRelease-1>',self.swap_forms)
        swap.bind('<Enter>', lambda event,img=color_swap: Media.hover_label_button(event,img))
        swap.bind('<Leave>', lambda event,img=gray_swap: Media.hover_label_button(event,img))

        hide = tb.Label(self.Form_Frame, image=gray_hide)
        hide.grid(row=0, column=3, sticky=NE)
        hide.bind('<ButtonRelease-1>',self.remove_form_frame)
        hide.bind('<Enter>', lambda event,img=color_hide: Media.hover_label_button(event,img))
        hide.bind('<Leave>', lambda event,img=gray_hide: Media.hover_label_button(event,img))

        lbl = tb.Label(self.Form_Frame, anchor=CENTER, bootstyle=labelColor, text=formname, font=font_groups)
        lbl.grid(row=0, column=1, columnspan=2, padx=title_padding[0], pady=title_padding[1], sticky=NSEW)

        swap.bind('<FocusIn>', lambda event,form='Default': self.BUTT.Validation_Method(event,form))
        lbl.bind('<Enter>', lambda event,form='Default': self.BUTT.Validation_Method(event,form))
        return lbl

    def Images_MiniTable_Create(self,frame:Frame):
        scroll_x = tb.Scrollbar(frame, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
        scroll_y = tb.Scrollbar(frame, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

        table = tb.ttk.Treeview(frame, columns=['ID', 'Opis', 'Veličina', 'width', 'height'],
                                xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set, show='tree')
        table.grid(row=0, column=0, sticky=NSEW)
        table.bind('<Double-1>',self.BUTT.Show_Image_FullScreen)

        def fill_Opis(event):
            try:
                opis:str = event.widget.item(event.widget.focus())['values'][1]
                opis = opis.split('_')[1]
                opis = opis.split('.')[0]
                self.BUTT.Patient_FormVariables['slike']['Opis'].set(opis)
            except IndexError:
                return

        table.bind('<ButtonRelease-1>',fill_Opis)
        table.bind('<KeyRelease-Down>',fill_Opis)
        table.bind('<KeyRelease-Up>',fill_Opis)
        
        scroll_x.grid(row=1, column=0, sticky=EW)
        scroll_y.grid(row=0, column=1, sticky=NS)
        scroll_x.config(command=table.xview)
        scroll_y.config(command=table.yview)

        # Sprečavanje automatskog prilagođavanja frejma
        frame.grid_rowconfigure(0, weight=1) 
        frame.grid_columnconfigure(0, weight=1)

        table.column('#0', width=0, stretch=False)
        table.column('ID', width=F_SIZE*2, stretch=True)
        table.column('Opis', width=F_SIZE*16, stretch=True)
        table.column('Veličina', width=F_SIZE*7, stretch=True, anchor=E)
        table.column('width', width=F_SIZE*5, stretch=True, anchor=CENTER)
        table.column('height', width=F_SIZE*5, stretch=True, anchor=CENTER)

        frame.grid_propagate(False)
        return table

    def FormPatient_Create(self, parent:Frame, form_dict, group, form):
        n=1
        group_names = []
        group_childs = []

        for k,v in group.items():
            if k!='start':
                group_names.append(k)
            if v:
                group_childs.append(v+group_childs[-1]) if group_childs else group_childs.append(v)

        for i, (txt, data) in enumerate(form_dict.items()):           
            if i in group_childs:
                lbl = tb.Label(parent, anchor=CENTER, justify=CENTER,
                                bootstyle=labelColor, text=group_names[n-1], font=font_groups)
                lbl.grid(row=i+n, column=0, columnspan=4,
                         padx=title_padding[0], pady=title_padding[1], sticky=NSEW)
                n +=1

            if txt in self.DB.pacijent:
                table = 'pacijent'
            elif txt in self.DB.dg_kategorija:
                table = 'dijagnoza'
            elif txt in self.DB.dr_funkcija:
                table = 'operacija'
            elif txt in self.DB.slike:
                table = 'slike'

            lbl = tb.Label(parent, anchor=CENTER, justify=CENTER, bootstyle=labelColor, text=data[0], font=font_label('normal'))
            lbl.grid(row=i+n, column=0, columnspan=2,
                     padx=(form_padding_entry[0][0],form_padding_entry[0][1]), pady=form_padding_entry[1], sticky=NSEW)

            if data[1] in ['StringVar','Combobox','Validate']:
                self.BUTT.Patient_FormVariables[table][txt] = StringVar()
                if data[1]=='StringVar':
                    ent = tb.Entry(parent, textvariable=self.BUTT.Patient_FormVariables[table][txt], width=data[2], font=font_entry)
                elif data[1]=='Combobox':
                    ent = tb.Combobox(parent, values=data[3], textvariable=self.BUTT.Patient_FormVariables[table][txt], width=data[2],
                                      font=font_entry, validate='focus', validatecommand=(self.valid_notblank, '%P'), state='readonly')
                    self.BUTT.Validation_Widgets[form].append(ent)
                elif data[1] == 'Validate':
                    validcmd = self.valid_dijagnoza if ('dijagnoza' in txt or 'Uzrok' in txt) else \
                                    self.valid_godiste if txt=='Godište' else \
                                        self.valid_zaposleni if txt in self.DB.dr_funkcija else \
                                            self.valid_notblank
                    ent = tb.Entry(parent, width=data[2], textvariable=self.BUTT.Patient_FormVariables[table][txt], font=font_entry,
                                   validate='focus', validatecommand=(validcmd, '%P'))
                    self.BUTT.Validation_Widgets[form].append(ent)
            elif data[1] == 'Text':
                height = 4 if txt=='Dg Latinski' else 2
                ent = tb.Text(parent, width=data[2], height=height, font=font_entry)
                self.BUTT.Patient_FormVariables[table][txt] = ent
                if txt in self.DB.dr_funkcija:
                    ent.bind('<FocusIn>', self.BUTT.validate_zaposleni_Text)
                    ent.bind('<FocusOut>', self.BUTT.validate_zaposleni_Text)
                    self.BUTT.Validation_Widgets[form].append(ent)
            elif data[1] == 'DateEntry':
                ent = widgets.DateEntry(parent, width=data[2], borderwidth=2, dateformat='%d-%b-%Y', firstweekday=0)
                ent.entry.delete(0, END)
                self.BUTT.Patient_FormVariables[table][txt] = ent
            elif data[1] == 'Info':
                ent = tb.Label(parent, anchor=CENTER, justify=CENTER, bootstyle=labelColor, text='\n', font=font_label())
                ent.grid(row=i+n, column=0, columnspan=4,  padx=form_padding_entry[0], pady=form_padding_entry[1], sticky=NSEW)
                self.BUTT.PatientInfo = ent
                ent = None
            elif data[1] == 'Slike':
                ent = Frame(parent)
                ent.grid(row=i+n, column=0, columnspan=4,  padx=(12,0), pady=form_padding_entry[1], sticky=NSEW)
                parent.grid_rowconfigure(i+n, weight=1)
                sliketable = self.Images_MiniTable_Create(ent)
                self.BUTT.Patient_FormVariables['slike'][txt] = sliketable
                ent = None
            if ent:
                ent.grid(row=i+n, column=2, columnspan=2, padx=form_padding_entry[0], pady=form_padding_entry[1], sticky='nsw')

    def FormPatient_Buttons(self,parent,split,buttons):
        Frame(parent).grid(row=16, columnspan=4, pady=12) ## prazan frame za odvajanje (6*2 == 12)
        for i,((but,btype),cmd) in enumerate(zip(buttons,FormFrame.Form_button_fun)):
            if i in split or i==0:
                Buttons_Frame = Frame(parent)
                Buttons_Frame.grid(row=18+i, columnspan=4)
                Buttons_Frame.bind('<Enter>', lambda event,form='Alternative': self.BUTT.Validation_Method(event,form))

            butt = ctk.CTkButton(Buttons_Frame, text=but, width=form_butt_width,height=form_butt_height, corner_radius=12, font=font_label(),
                                 fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                 command=cmd)
            butt.grid(row=0, column=i, padx=form_padding_button[0], pady=form_padding_button[1])
            self.BUTT.Buttons[but] = butt
            if btype:
                butt.configure(fg_color=ThemeColors[btype])
        Frame(parent).grid(row=24, columnspan=4, pady=12) ## prazan frame za odvajanje (6*2 == 12)    

    def remove_form_frame(self,event):
        self.Form_Frame.grid_forget()
        self.form_true.set(False)
    
    def swap_forms(self,event):
        if self.DefaultForm.winfo_ismapped():
            self.AlternativeForm.grid()
            self.DefaultForm.grid_remove()
        elif self.AlternativeForm.winfo_ismapped():
            self.DefaultForm.grid()
            self.AlternativeForm.grid_remove()

class WindowFrame:
    def __init__(self, root:Tk,) -> None:
        self.DBMS = DBMS()
        self.DB = self.DBMS.DB
        self.BUTT = Buttons()
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

                # NOTEBOOK Tab PACIJENTI
        self.DBMS.Table_Pacijenti = self.PacijentiTab_Create(self.DBMS.fill_PatientForm)
        self.DBMS.selected_columns(self.DBMS.Pacijenti_ColumnVars.items(),self.DBMS.Table_Pacijenti)

                 # NOTEBOOK Tab SLIKE   
        self.DBMS.Table_Slike = self.SlikeTab_Create(F_SIZE*50, self.BUTT.Show_Image, list(self.DBMS.Slike_ColumnVars.values()),
                                [self.BUTT.Add_Image,self.BUTT.Edit_Image,self.BUTT.Delete_Image,self.BUTT.Download_SelectedImages])
        self.DBMS.selected_columns(self.DBMS.Slike_ColumnVars.items(),self.DBMS.Table_Slike)

                # NOTEBOOK Tab KATALOG
        self.DBMS.Table_MKB, self.DBMS.Table_Zaposleni = self.KatalogTab_Create(
                mkbside = {     'buttons': [self.BUTT.Add_MKB, self.BUTT.Update_MKB, self.BUTT.Delete_MKB],
                            'bindmethods': {    'fill_Form': self.DBMS.fill_MKBForm,
                                                'double_click': self.DBMS.MKB_double_click },
                         'active_columns': list(self.DBMS.MKB_ColumnVars.values())     },
                zaposleniside = {   'buttons': [self.BUTT.Add_Zaposleni, self.BUTT.Update_Zaposleni, self.BUTT.Delete_Zaposleni],
                                'bindmethods': { 'fill_Form': self.DBMS.fill_ZaposleniForm,
                                                 'double_click': self.DBMS.Zaposleni_double_click },
                             'active_columns': list(self.DBMS.Zaposleni_ColumnVars.values())   }   )
        self.DBMS.selected_columns(self.DBMS.MKB_ColumnVars.items(),self.DBMS.Table_MKB)
        self.DBMS.selected_columns(self.DBMS.Zaposleni_ColumnVars.items(),self.DBMS.Table_Zaposleni)


        def hide():
                # NOTEBOOK Tab LOGS
            self.DBMS.Table_Logs = self.NotebookTab_Create('Logs', table=True, expand=(1,5),
                                    extra=(self.Log_SideFrame,{'row':1,'column':5,'rowspan':2,'columnspan':1}))
            self.DBMS.Table_Logs.bind('<ButtonRelease-1>',self.DBMS.fill_LogsForm)
            self.DBMS.Table_Logs.bind('<KeyRelease-Down>',self.DBMS.fill_LogsForm)
            self.DBMS.Table_Logs.bind('<KeyRelease-Up>',self.DBMS.fill_LogsForm)
            for val in self.DBMS.Logs_ColumnVars.values():
                val.set(1)
            self.DBMS.selected_columns(self.DBMS.Logs_ColumnVars.items(),self.DBMS.Table_Logs)
            #self.DBMS.NoteBook.hide(3)

                # NOTEBOOK Tab SESSION
            self.DBMS.Table_Session = self.NotebookTab_Create('Session', table=True)
            for val in self.DBMS.Session_ColumnVars.values():
                val.set(1)
            self.DBMS.selected_columns(self.DBMS.Session_ColumnVars.items(),self.DBMS.Table_Session)
        hide()
        
            # SETTINGS TAB
        self.DBMS.Settings_Tab = self.NotebookTab_Create('Settings')

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
        self.BUTT.Buttons['Filter Patient'].append(butf)

            # BUTTONS for SEARCH and SHOWALL
        buts = ctk.CTkButton(self.DBMS.SearchBar, text='SEARCH', width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'],  text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=self.DBMS.search_data)
        buts.grid(row=0, column=searchButtonROW+3, rowspan=max_searchby,
                padx=form_padding_button[0], pady=form_padding_button[1], sticky=SE)
        self.BUTT.Buttons['Search'] = buts

        buta = ctk.CTkButton(self.DBMS.SearchBar, text='SHOW ALL', width=form_butt_width, height=form_butt_height, corner_radius=10,
                        font=font_label(), fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                        command=self.DBMS.showall_data)
        buta.grid(row=0, column=searchButtonROW+4, rowspan=max_searchby,
                padx=form_padding_button[0], pady=form_padding_button[1], sticky=SE)
        self.BUTT.Buttons['Show All'] = buta

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
    
    def SlikeTab_Create(self, tablewidth:int, method:callable, active_columns:list, button_cmd:list) -> (tb.ttk.Treeview):
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
                self.BUTT.Buttons[butt] = button

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

            for col in active_columns:
                col:IntVar
                col.set(1)

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
        canvas_frame = Frame(notebook_frame)
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

        def Create_One_Side(method:callable, bindmethods:dict, active_columns:list, *args):
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
            for col in active_columns:
                col:IntVar
                col.set(1)

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
                                   mkbside['active_columns'],
                                   *[Katalog_Entry['mkb10'],mkbside['buttons']])
        COLUMN += 1 # Right Part -- (1,-1) je za row,col za frejm ispod tabele
        tableZapo = Create_One_Side(self.Katalog_Entry_Create,
                                    zaposleniside['bindmethods'],
                                    zaposleniside['active_columns'],
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
                        self.BUTT.Buttons[butt] = button
                        
            else:
                frame.grid(row=values[2][0], column=values[2][1], rowspan=values[2][2], columnspan=values[2][3], sticky=NSEW)
                if column == 'Combobox':
                    parent_frame.grid_columnconfigure(values[2][1], weight=1)
                    self.BUTT.Katalog_FormVariables[values[0]] = StringVar()
                    VALUES = self.DB.dr_funkcija if values[0]=='Funkcija' else self.DB.dg_kategorija if values[0]=='Kategorija' else None
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

    def NotebookTab_Create(self,txt,table=False,extra=False,expand=(1,0)):
        notebook_frame = tb.Frame(self.DBMS.NoteBook)
        self.DBMS.NoteBook.add(notebook_frame, text=txt)
        if extra:
            extra_frame = Frame(notebook_frame)
            extra_frame.grid(row=extra[1]['row'], rowspan=extra[1]['rowspan'],
                             column=extra[1]['column'], columnspan=extra[1]['columnspan'], sticky=NSEW)
            extra[0](extra_frame)
        if table:
            if str(table).isdigit():
                parent_frame = Frame(notebook_frame, width=table)
                parent_frame.grid(row=1,rowspan=2,column=0, columnspan=2, sticky=NSEW)
                parent_frame.grid_propagate(False)
                parent_frame.grid_rowconfigure(1, weight=1)
                parent_frame.grid_columnconfigure(0, weight=1)
                if txt=='Slike':
                    self.BUTT.Slike_HideTable = parent_frame
            else:
                parent_frame = notebook_frame
            scroll_x = tb.Scrollbar(parent_frame, orient=HORIZONTAL, bootstyle=f'{bootstyle_table}-round')
            scroll_y = tb.Scrollbar(parent_frame, orient=VERTICAL, bootstyle=f'{bootstyle_table}-round')

            table = tb.ttk.Treeview(parent_frame, columns=[], xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
            table.grid(row=1, column=0, sticky=NSEW)
            
            scroll_x.grid(row=2, column=0, sticky=EW)
            scroll_y.grid(row=1, column=1, sticky=NS)
            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

            notebook_frame.grid_rowconfigure(expand[0], weight=1)
            notebook_frame.grid_columnconfigure(expand[1], weight=1)

        return table if table else notebook_frame

    def Log_SideFrame(self,parent_frame:Frame):
        lbl1 = tb.Label(parent_frame,text='Full Query', anchor=CENTER, justify=CENTER, bootstyle=labelColor, font=font_label())
        lbl1.grid(row=0, column=0)
        text1 = tb.Text(parent_frame, width=form_large_width, font=font_entry)
        text1.grid(row=1, column=0, sticky=NSEW)
        self.BUTT.Logs_FormVariables['Full Query'] = text1
        lbl1 = tb.Label(parent_frame,text='Full Error', anchor=CENTER, justify=CENTER, bootstyle=labelColor, font=font_label())
        lbl1.grid(row=2, column=0)
        text2 = tb.Text(parent_frame, width=form_large_width, font=font_entry)
        text2.grid(row=3, column=0, sticky=NSEW)
        self.BUTT.Logs_FormVariables['Full Error'] = text2

        parent_frame.grid_rowconfigure([1,3],weight=1)
        parent_frame.grid_columnconfigure(0,weight=1)  

    def Roundbutton_Create(self,parent_frame:Frame):
        for i,(col,txt) in enumerate(self.BUTT.FilterOptions.items()):
            self.BUTT.FilterOptions[col] = [txt,IntVar()] # Ovde dodajen varijablu int da bi mogao da menjam sa json

            cb = tb.Checkbutton(parent_frame, text=txt, variable=self.BUTT.FilterOptions[col][1], bootstyle='success, round-toggle')
            cb.grid(row=0, column=i, padx=form_padding_button[0], pady=(0,3))

            butt = ctk.CTkButton(parent_frame, text='FILTER', width=form_butt_width, height=form_butt_height//2, corner_radius=10,
                            font=font_label(), fg_color=ThemeColors['info'], text_color=ThemeColors['dark'],text_color_disabled=ThemeColors['secondary'],
                                command=lambda column=col: self.DBMS.filter_data(column))
            butt.grid(row=1, column=i, padx=form_padding_button[0], pady=(0,3))
            self.BUTT.Buttons['Filter Patient'] += [cb,butt]

class GUI:
    def GoogleDrive_Decorating(self):
        for name, method in inspect.getmembers(GoogleDrive, predicate=inspect.isfunction):
            decorated_method = method_efficency(self.DB.UserSession)(
                error_catcher(self.DB)(method)
                )
            setattr(self.GD, name, decorated_method.__get__(self.GD, type(self.GD)))

    def Media_Decorating(self):
        for name, method in inspect.getmembers(Media, predicate=inspect.isfunction):
            decorated_method = method_efficency(self.DB.UserSession)(
                error_catcher(self.DB)(method)
                )
            setattr(Media, name, decorated_method)

    def Database_Decorating(self):
        for name, method in inspect.getmembers(Database, predicate=inspect.isfunction):
            decorated_method = method_efficency(self.DB.UserSession)(
                error_catcher(self.DB)(method)
                ) 
            setattr(self.DB, name, decorated_method.__get__(self.DB, type(self.DB)))

    def Buttons_Decorating(self):
        for name, method in inspect.getmembers(Buttons, predicate=inspect.isfunction):
            decorated_method = method_efficency(self.DB.UserSession)(
            error_catcher(self.DB)(method)
            )
            setattr(self.BUTT, name, decorated_method.__get__(self.BUTT, type(self.BUTT)))

    def DBMS_Decorating(self):
        for name, method in inspect.getmembers(DBMS, predicate=inspect.isfunction):
            decorated_method = method_efficency(self.DB.UserSession)(
                error_catcher(self.DB)(method)
            )
            setattr(self.DBMS, name, decorated_method.__get__(self.DBMS, type(self.DBMS)))

    def Buttons_SpamStopper(self):
        for button in self.BUTT.Buttons.values():
            try:
                last_cmd = button.cget('command')
                button.configure(command=spam_stopper(button,self.root)(last_cmd))
            except AttributeError: # Ovo je zbog liste FILTER sa buttonima
                for filterbutton in button:
                    try: # Ovo je zato sto ta lista ne sadrzi samo buttona
                        last_cmd = filterbutton.cget('command')
                        filterbutton.configure(command=spam_stopper(filterbutton,self.root)(last_cmd))
                    except:
                        print(f"usao u except: {filterbutton}")
                        continue

    def EXIT(self):
        response = Messagebox.show_question('Do you want to save the changes before exiting?', 'Close', buttons=['Exit:secondary','Save:success'])
        if response == 'Save':
            threading.Thread(target=self.uploading_to_GoogleDrive).start()
            self.root.destroy()
        if response == 'Exit':
            self.root.destroy()
    
    def uploading_to_GoogleDrive(self):
        print('Uploading to Google Drive...')
        #self.GD.upload_UpdateFile(RHMH_DB['id'],'RHMH.db',RHMH_DB['mime'])
        print('Upload finished')

    def show_form_frame(self):
        if not self.Form.Form_Frame.winfo_ismapped():
            self.Form.Form_Frame.grid(row=1, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky=NSEW)
            self.Form.form_true.set(True)
        else:
            self.Form.Form_Frame.grid_forget()
            self.Form.form_true.set(False) 

    def show_title_frame(self):
        if not self.Title.Title_Frame.winfo_ismapped():
            self.Title.Title_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
            self.title_true.set(True)
        else:
            self.Title.Title_Frame.grid_forget()
            self.title_true.set(False) 

    def do_popup(self,event):
        self.menu:Menu
        try: 
            self.menu.tk_popup(event.x_root, event.y_root) 
        finally: 
            self.menu.grab_release() 

    def RootMenu_Create(self):
        m = Menu(self.root, tearoff = 0) 
        self.title_true = BooleanVar()
        self.title_true.set(True)
        m.add_checkbutton(label='Show Title', variable=self.title_true, command=self.show_title_frame)
        m.add_checkbutton(label='Show Form', variable=self.Form.form_true, command=self.show_form_frame)
        m.add_separator() 
        m.add_command(label ='Empty Table', command=self.BUTT.empty_tables) 
        m.add_command(label ='Export Selection') 
        m.add_command(label ='Reload')
        m.add_command(label ='Rename')
        return m

    def __init__(self, root:Tk):
        self.GD = GoogleDrive()
        thread = threading.Thread(target= lambda ID=RHMH_DB['id'],path='RHMH.db':
                          self.GD.download_File(ID,path))
        thread.start()
        thread.join()
        EMAIL = self.GD.get_UserEmail()
        self.DBMS = DBMS()
        self.BUTT = self.DBMS.BUTT
        self.BUTT.ROOT = root
        self.DB = self.DBMS.DB

        # DECORATING
        '''
        self.GoogleDrive_Decorating()
        self.Media_Decorating()
        self.Database_Decorating()
        self.Buttons_Decorating()
        self.DBMS_Decorating()
        #'''
        self.Buttons_SpamStopper()
        
        self.root = root
        self.root.title(app_name)
        self.root.geometry(f'{WIDTH}x{HEIGHT}')
        self.root.iconbitmap('C:/Users/vurun/Desktop/App/Slytherin-Emblem_icon.ico')
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.Title = TitleFrame(self.root)
        self.Form = FormFrame(self.root)
        self.Window = WindowFrame(self.root)
        
        self.menu = self.RootMenu_Create()
        self.root.bind('<Button-3>', self.do_popup)
        self.root.bind('<Control-a>',self.BUTT.selectall_tables)
        self.root.bind('<Command-a>',self.BUTT.selectall_tables)
        self.root.bind('\u004D\u0055\u0056',
                lambda event,root=self.root,notebook=self.DBMS.NoteBook: 
                        self.DBMS.DB.GodMode_Password(event,root,notebook))
        self.root.protocol('WM_DELETE_WINDOW',self.EXIT)

        print(f'Vreme za pokretanje programa: {(time.time_ns()-TIME_START)/10**9:.2f} s')