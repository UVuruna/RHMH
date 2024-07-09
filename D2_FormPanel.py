from A1_Variables import *
from B3_Media import Media
from B2_SQLite import RHMH
from C1_Controller import Controller
from C2_ManageDB import ManageDB

class FormPanel:
    Form_Frame:Frame = None
    form_visible:BooleanVar = None

    DefaultForm:Frame = None
    AlternativeForm:Frame = None

    valid_notblank = None
    valid_dijagnoza = None
    valid_godiste = None
    valid_zaposleni = None

    @staticmethod
    def initialize(root:Tk) -> None:
        
        FormPanel.form_visible = BooleanVar()
        FormPanel.form_visible.set(True)
        
        FormPanel.Form_button_fun =[ManageDB.Add_Patient,
                                    ManageDB.Update_Patient,
                                    ManageDB.Delete_Patient,
                                    ManageDB.Fill_FromImage,
                                    ManageDB.Clear_Form    ]

        FormPanel.valid_notblank = root.register(ManageDB.validate_notblank)
        FormPanel.valid_dijagnoza = root.register(ManageDB.validate_dijagnoza)
        FormPanel.valid_godiste = root.register(ManageDB.validate_godiste)
        FormPanel.valid_zaposleni = root.register(ManageDB.validate_zaposleni)

            # PARENT FRAME for FORMS
        FormPanel.Form_Frame = Frame(root, bd=4, relief=RIDGE)
        FormPanel.Form_Frame.grid(row=1, column=0, padx=padding_6, pady=padding_0_6, sticky=NSEW)
        FormPanel.Form_Frame.grid_rowconfigure(1,weight=1)

        Controller.FormTitle = (FormPanel.Form_TopLabel(form_name),color_labeltext)

            # DEFAULT FORM CREATE
        FormPanel.DefaultForm = Frame(FormPanel.Form_Frame)
        FormPanel.DefaultForm.grid(row=1, column=0, columnspan=4, sticky=NSEW)
        FormPanel.FormPatient_Create(FormPanel.DefaultForm, default_form_entry, form_groups['Default'], 'Default')
        FormPanel.FormPatient_Buttons(FormPanel.DefaultForm,[3],Form_buttons[:3],'Default')
            # ALTERNATIVE FORM CREATE
        FormPanel.AlternativeForm = Frame(FormPanel.Form_Frame)
        FormPanel.AlternativeForm.grid(row=1, column=0, columnspan=4, sticky=NSEW)
        FormPanel.AlternativeForm.grid_remove()
        FormPanel.FormPatient_Create(FormPanel.AlternativeForm, alternative_form_entry, form_groups['Alternative'], 'Alternative')
        FormPanel.FormPatient_Buttons(FormPanel.AlternativeForm,[3],Form_buttons,'Alternative')

    @staticmethod
    def Form_TopLabel(formname):
        gray_swap, color_swap, gray_hide, color_hide = Media.label_ImageLoad(IMAGES['Swap']+IMAGES['Hide'])

        swap = tb.Label(FormPanel.Form_Frame, image=gray_swap)
        swap.grid(row=0, column=0, sticky =NW)
        swap.bind('<ButtonRelease-1>',FormPanel.swap_forms)
        swap.bind('<Enter>', lambda event,img=color_swap: Media.hover_label_button(event,img))
        swap.bind('<Leave>', lambda event,img=gray_swap: Media.hover_label_button(event,img))

        hide = tb.Label(FormPanel.Form_Frame, image=gray_hide)
        hide.grid(row=0, column=3, sticky=NE)
        hide.bind('<ButtonRelease-1>',FormPanel.remove_form_frame)
        hide.bind('<Enter>', lambda event,img=color_hide: Media.hover_label_button(event,img))
        hide.bind('<Leave>', lambda event,img=gray_hide: Media.hover_label_button(event,img))

        lbl = tb.Label(FormPanel.Form_Frame, anchor=CENTER, bootstyle=color_labeltext, text=formname, font=font_big())
        lbl.grid(row=0, column=1, columnspan=2, padx=0, pady=padding_6, sticky=NSEW)

        swap.bind('<Button-1>', lambda event,form='Default': ManageDB.Validation_Method(event,form))
        lbl.bind('<Enter>', lambda event,form='Default': ManageDB.Validation_Method(event,form))
        return lbl

    @staticmethod
    def Images_MiniTable_Create(frame:Frame):
        scroll_x = tb.Scrollbar(frame, orient=HORIZONTAL, bootstyle=f'{style_scrollbar}-round')
        scroll_y = tb.Scrollbar(frame, orient=VERTICAL, bootstyle=f'{style_scrollbar}-round')

        table = tb.ttk.Treeview(frame, columns=['ID', 'Opis', 'Veličina', 'width', 'height'],
                                xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set, show='tree')
        table.grid(row=0, column=0, sticky=NSEW)
        table.bind('<Double-1>',ManageDB.Show_Image_FullScreen)

        def fill_Opis(event):
            try:
                opis:str = event.widget.item(event.widget.focus())['values'][1]
                opis = opis.split('_')[1]
                opis = opis.split('.')[0]
                Controller.Patient_FormVariables['slike']['Opis'].set(opis)
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

    @staticmethod
    def FormPatient_Create( parent:Frame, form_dict, group, form):
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
                                bootstyle=color_labeltext, text=group_names[n-1], font=font_big('normal'))
                lbl.grid(row=i+n, column=0, columnspan=4, pady=padding_3, sticky=NSEW)
                n +=1

            if txt in RHMH.pacijent:
                table = 'pacijent'
            elif txt in RHMH.dg_kategorija:
                table = 'dijagnoza'
            elif txt in RHMH.dr_funkcija:
                table = 'operacija'
            elif txt in RHMH.slike:
                table = 'slike'

            lbl = tb.Label(parent, anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, text=data[0], font=font_medium('normal'))
            lbl.grid(row=i+n, column=0, columnspan=2, padx=padding_3_12, sticky=NSEW)

            if data[1] in ['StringVar','Combobox','Validate']:
                Controller.Patient_FormVariables[table][txt] = StringVar()
                if data[1]=='StringVar':
                    ent = tb.Entry(parent, textvariable=Controller.Patient_FormVariables[table][txt], width=data[2], font=font_default)
                elif data[1]=='Combobox':
                    ent = tb.Combobox(parent, values=data[3], textvariable=Controller.Patient_FormVariables[table][txt], width=data[2],
                                      font=font_default, validate='focus', validatecommand=(FormPanel.valid_notblank, '%P'), state='readonly')
                    Controller.Validation_Widgets[form].append(ent)
                elif data[1] == 'Validate':
                    validcmd = FormPanel.valid_dijagnoza if ('dijagnoza' in txt or 'Uzrok' in txt) else \
                                    FormPanel.valid_godiste if txt=='Godište' else \
                                        FormPanel.valid_zaposleni if txt in RHMH.dr_funkcija else \
                                            FormPanel.valid_notblank
                    ent = tb.Entry(parent, width=data[2], textvariable=Controller.Patient_FormVariables[table][txt], font=font_default,
                                   validate='focus', validatecommand=(validcmd, '%P'))
                    Controller.Validation_Widgets[form].append(ent)
            elif data[1] == 'Text':
                height = 3 if txt=='Dg Latinski' else 2
                ent = tb.Text(parent, width=data[2], height=height, font=font_default)
                Controller.Patient_FormVariables[table][txt] = ent
                if txt in RHMH.dr_funkcija:
                    ent.bind('<FocusIn>', ManageDB.validate_zaposleni_Text)
                    ent.bind('<FocusOut>', ManageDB.validate_zaposleni_Text)
                    Controller.Validation_Widgets[form].append(ent)
            elif data[1] == 'DateEntry':
                ent = widgets.DateEntry(parent, width=data[2], dateformat='%d-%b-%Y', firstweekday=0)
                ent.entry.delete(0, END)
                Controller.Patient_FormVariables[table][txt] = ent
            elif data[1] == 'Info':
                ent = tb.Label(parent, anchor=CENTER, justify=CENTER, bootstyle=color_labeltext, text='\n', font=font_medium())
                ent.grid(row=i+n, column=0, columnspan=4,  padx=padding_3_12, pady=padding_3, sticky=NSEW)
                Controller.PatientInfo = ent
                ent = None
            elif data[1] == 'Slike':
                ent = Frame(parent)
                ent.grid(row=i+n, column=0, columnspan=4,  padx=(12,0), pady=padding_3, sticky=NSEW)
                parent.grid_rowconfigure(i+n, weight=1)
                sliketable = FormPanel.Images_MiniTable_Create(ent)
                Controller.Patient_FormVariables['slike'][txt] = sliketable
                ent = None
            if ent:
                ent.grid(row=i+n, column=2, columnspan=2, padx=padding_3_12, pady=padding_3, sticky='nsw')

    @staticmethod
    def FormPatient_Buttons(parent,split,buttons,validationform):
        Frame(parent).grid(row=16, columnspan=4, pady=padding_6)
        for i,((but,btype),cmd) in enumerate(zip(buttons,FormPanel.Form_button_fun)):
            if i in split or i==0:
                Buttons_Frame = Frame(parent)
                Buttons_Frame.grid(row=18+i, columnspan=4)
                Buttons_Frame.bind('<Enter>', lambda event,form=validationform: ManageDB.Validation_Method(event,form))

            butt = ctk.CTkButton(Buttons_Frame, text=but, width=buttonX,height=buttonY, corner_radius=12, font=font_medium(),
                                 fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                 command=cmd)
            butt.grid(row=0, column=i, padx=padding_6, pady=padding_6)
            Controller.Buttons[but] = butt
            if btype:
                butt.configure(fg_color=ThemeColors[btype])
        Frame(parent).grid(row=24, columnspan=4, pady=padding_6) 

    @staticmethod
    def remove_form_frame(event):
        FormPanel.Form_Frame.grid_forget()
        FormPanel.form_visible.set(False)
    
    @staticmethod
    def swap_forms(event):
        if FormPanel.DefaultForm.winfo_ismapped():
            FormPanel.AlternativeForm.grid()
            FormPanel.DefaultForm.grid_remove()
        elif FormPanel.AlternativeForm.winfo_ismapped():
            FormPanel.DefaultForm.grid()
            FormPanel.AlternativeForm.grid_remove()

if __name__=='__main__':
    pass