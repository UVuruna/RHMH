from A1_Variables import *
from A2_Decorators import method_efficency
from B3_Media import Media
from B2_SQLite import RHMH
from C1_DBMS import DBMS,Buttons

class FormFrame:
    def __init__(self, root:Tk) -> None:
        self.BUTT = Buttons()
        self.DBMS = DBMS()

        self.form_true = BooleanVar()
        self.form_true.set(True)
        self.root = root

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

        lbl = tb.Label(self.Form_Frame, anchor=CENTER, bootstyle=labelColor, text=formname, font=font_groups())
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
                                bootstyle=labelColor, text=group_names[n-1], font=font_groups('normal'))
                lbl.grid(row=i+n, column=0, columnspan=4,
                         padx=title_padding[0], pady=title_padding[1], sticky=NSEW)
                n +=1

            if txt in RHMH.pacijent:
                table = 'pacijent'
            elif txt in RHMH.dg_kategorija:
                table = 'dijagnoza'
            elif txt in RHMH.dr_funkcija:
                table = 'operacija'
            elif txt in RHMH.slike:
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
                                        self.valid_zaposleni if txt in RHMH.dr_funkcija else \
                                            self.valid_notblank
                    ent = tb.Entry(parent, width=data[2], textvariable=self.BUTT.Patient_FormVariables[table][txt], font=font_entry,
                                   validate='focus', validatecommand=(validcmd, '%P'))
                    self.BUTT.Validation_Widgets[form].append(ent)
            elif data[1] == 'Text':
                height = 4 if txt=='Dg Latinski' else 2
                ent = tb.Text(parent, width=data[2], height=height, font=font_entry)
                self.BUTT.Patient_FormVariables[table][txt] = ent
                if txt in RHMH.dr_funkcija:
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
            self.BUTT.buttons[but] = butt
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