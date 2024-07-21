from A1_Variables import *

pillow_heif.register_heif_opener()

class AI:

    if os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
        if torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        if torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")
            
    torch.set_default_tensor_type(torch.FloatTensor)
    torch.set_default_device(device)
    ReaderSetup = easyocr.Reader(['rs_latin','en'], gpu=(device != torch.device("cpu"))) # ovo pravi True/False za device

    OperacionaChoice = {
        'Datum Operacije': None,
        'Dg Latinski': None,
        'Glavna Operativna dijagnoza': None,
        'Sporedna Operativna dijagnoza':  None,
        'Operator':  None,
        'Asistent':  None,
        'Anesteziolog':  None,
        'Anestetičar':  None,
        'Instrumentarka':  None,
        'Gostujući Specijalizant':  None,
    }

    Settings = {}
    Settings['Type'] = SETTINGS['Reader']['Type']
    Settings['VRAM'] = SETTINGS['Reader']['VRAM']
    Settings['Zoom'] = SETTINGS['Reader']['Zoom']/100
    
    @staticmethod
    def initialize():
        AI.Settings['Max VRAM'] = AI.get_gpu_vram()

    @staticmethod
    def get_gpu_vram():
        try:
            return int((UserSession['PC']['GPU']['VRAM'].replace(',','')).rstrip(' MB'))
        except KeyError:
            return int((UserSession['PC']['RAM'].replace(',','')).rstrip(' MB'))
        except Exception:
            return 4096

    @staticmethod
    def is_date(date_string):
        try:
            for string in [' ','-','_']:
                date_string = date_string.replace(string,'')
            if date_string[-1]=='.':
                date_string = date_string[:-1]
            date_string = date_string if date_string[-1].isdigit() else date_string[:-1]
            date = datetime.strptime(str(date_string), '%d.%m.%Y').strftime('%d-%b-%Y')
            return date
        except ValueError:
            return False
        
    @staticmethod
    def mkb_find(detection,result,i):
        def last_next_row_check(MKB):
            if len(MKB) < 6:
                count_digit = 0
                for i in MKB:
                    if i.isdigit():
                        count_digit+=1
                if count_digit > 1:
                    return MKB
        try:
            mkb = detection.split()[3]
            return mkb,0
        except IndexError:
            mkb = result[i+1].split()[0]
            if last_next_row_check(mkb):
                return mkb,1
            else:
                mkb = result[i-1].split()[0]
                if last_next_row_check(mkb):
                    return mkb,-1
                else:
                    None,None

    @staticmethod
    def mkb_fix(mkb):
        if mkb[0].isdigit():
            fix='X'
            if mkb[0] in ['5','8']:
                fix = 'S'
            elif mkb[0]=='2':
                fix = 'Z'
            elif mkb[0]=='0':
                fix = 'D'
            mkb = fix + mkb[1:]
        mkb = mkb[0]+mkb[1:].replace('O','0')
        mkb = mkb.replace('?','1')
        mkb = mkb.replace(',','')
        mkb = mkb.replace('.','')
        if len(mkb)==4:
            mkb = mkb[:3]+'.'+mkb[-1]
        return mkb

    @staticmethod
    def ImageReader_SettingUp(PARENT:Tk):

        def create_meter(parent,STYLE,text,ROW,COL,MIN,MAX,AMOUNT,unit,jump):
            meter = tb.Meter(
                master=parent,
                metersize=150,
                bootstyle=STYLE,
                subtextstyle=STYLE,
                subtext=text,
                textright=unit,
                padding=padding_6,
                amountused=AMOUNT,
                amountmin=MIN,
                amounttotal=MAX,
                stepsize=jump,
                stripethickness=math.ceil(270/((MAX-MIN)/jump)),
                metertype="semi",
                interactive=True,
            )
            meter.grid(row=ROW, column=COL, sticky=NSEW)
            return meter

        result = {'action':None}
        def run_command():
            AI.Settings['VRAM'] = ram.amountusedvar.get()
            AI.Settings['Zoom'] = zoom.amountusedvar.get()/100
            AI.Settings['Type'] = combobox.get()
            result['action'] = 'Run'
            toplevel.destroy()

        def savedefault_command():
            AI.Settings['VRAM'] = ram.amountusedvar.get()
            AI.Settings['Zoom'] = zoom.amountusedvar.get()/100
            AI.Settings['Type'] = combobox.get()
            SETTINGS['Reader']['VRAM'] = AI.Settings['VRAM']
            SETTINGS['Reader']['Zoom'] = zoom.amountusedvar.get()
            SETTINGS['Reader']['Type'] = AI.Settings['Type']

            json_data = json.dumps(SETTINGS, indent=4)
            with open(os.path.join(directory,'Settings.json'), 'w') as file:
                file.write(json_data)
            result['action'] = 'Save'
            toplevel.destroy()

        toplevel = tb.Toplevel()
        toplevel.iconify()
        
        toplevel.title('Reader - Configure')
        toplevel.grid_columnconfigure(0, weight=1)
        toplevel.resizable(False,False)
        if os.name == 'nt':  # Windows
            toplevel.attributes('-toolwindow', True)
        else:  # macOS/Linux
            toplevel.attributes('-type', 'dialog')

        titletxt = ' - Choose your settings for new AI Reading of document.\n'+\
                    ' - You can save your settings as default values for future readings.'
        title = tb.Label(toplevel, text=titletxt, anchor=W, wraplength=310)
        title.grid(row=0, column=0, padx=10, pady=(24,0)) 
        titleframe = Frame(toplevel)
        titleframe.grid(row=1, column=0, padx=10, sticky=W)
        titlelabels = [ (' Slower ','High Zoom and Less Ram','danger'),
                        (' Faster ','Low Zoom and More Ram','success'),
                        (' Precision ','Change Zoom and AI Type','primary') ]
        for i,(txt1,txt2,bt) in enumerate(titlelabels):
            tb.Label(titleframe, anchor=W, justify=CENTER, text=txt1, bootstyle=bt, wraplength=310).grid(row=i, column=0, padx=0)
            tb.Label(titleframe, anchor=W, justify=LEFT, text=txt2, wraplength=310).grid(row=i, column=1, padx=0)

        label = tb.Label(toplevel, text=f'Image Reader Type', anchor=CENTER, justify=CENTER)
        label.grid(row=2, column=0, padx=12, pady=(24,6)) 
        values = ['AI-Line Reader', 'AI-Paragraph Reader']
        combobox = tb.Combobox(toplevel, values=values, state='readonly')
        combobox.set(values[0])
        combobox.grid(row=3, column=0, padx=12, pady=6)

        meter_frame = Frame(toplevel)
        meter_frame.grid(row=4,column=0,sticky=NSEW)
        meter_frame.grid_columnconfigure([0,1],weight=1)

        zoom:tb.Meter = create_meter(parent=meter_frame,
                            STYLE='info', text='Zoom',
                            ROW=0, COL=0, MIN=70, MAX=230,
                            AMOUNT=int(AI.Settings['Zoom']*100),
                            unit='x', jump=1)
        ram:tb.Meter = create_meter(parent=meter_frame,
                            STYLE='warning', text='VRAM',
                            ROW=0, COL=1, MIN=1,
                            MAX=AI.Settings['Max VRAM'],
                            AMOUNT=AI.Settings['VRAM'],
                            unit='MB', jump=100)

        checkbutton_frame = Frame(toplevel)
        checkbutton_frame.grid(row=6, column=0, padx=12, pady=padding_6, sticky=NSEW)
        checkbutton_frame.grid_columnconfigure(1,weight=1)
   
        col = 0
        row = 0
        for check in list(AI.OperacionaChoice.keys()):
            txt = check.split(' ')
            txt = ' '.join(txt) if len(txt)!=3 else ' '.join(txt[:2])
            if col==2:
                col = 0
                row += 1
            tb.Checkbutton()
            cb = tb.Checkbutton(checkbutton_frame, text=txt, bootstyle=style_checkbutton)
            AI.OperacionaChoice[check] = IntVar()
            cb.configure(variable=AI.OperacionaChoice[check])
            if row>1:
                AI.OperacionaChoice[check].set(1)
            cb.grid(row=row, column=col, padx=padding_12, pady=padding_6, sticky=W)
            col += 1

        button_frame = Frame(toplevel)
        button_frame.grid(row=7, column=0, padx=12, pady=(24, 6), sticky=E)

        ctk.CTkButton(button_frame, text='SAVE\nDEFAULT', width=buttonX-2, height=buttonY, corner_radius=12, font=font_medium(),
                    fg_color=ThemeColors['success'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                    command=savedefault_command).grid(row=0, column=0, padx=padding_6[0], pady=padding_6[1])
        
        ctk.CTkButton(button_frame, text='RUN', width=buttonX-4, height=buttonY, corner_radius=12, font=font_medium(),
                    fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                    command=run_command).grid(row=0, column=1, padx=padding_6[0], pady=padding_6[1])

        toplevel.deiconify()
        toplevel.place_window_center()
        PARENT.wait_window(toplevel)
        return result['action']

    @staticmethod
    def Operaciona_Reader(image):
        if AI.Settings['Type'] == 'AI-Line Reader':
            return AI.Operaciona_LineReader(image)
        elif AI.Settings['Type'] == 'AI-Paragraph Reader':
            return AI.Operacion_ParagraphReader(image)

    @staticmethod
    def Operacion_ParagraphReader(image):
        pass

    @staticmethod
    def Operaciona_LineReader(image):
        result = AI.ReaderSetup.readtext(image, detail=0, mag_ratio=AI.Settings['Zoom'], batch_size=AI.Settings['VRAM'])

        def extend_variable(i, variable, searchlist, image_text):
            j = i + 1
            while j < len(image_text) and not any((image_text[j]).startswith(prefix) for prefix in searchlist):
                variable += (' ' + image_text[j])
                j += 1
            return variable

        OUTPUT = {}
        var:IntVar
        for col,var in AI.OperacionaChoice.items():
            if var.get() == True:
                OUTPUT[col] = None if col in ['Datum Operacije','Dg Latinski'] else list()

        DoctorsImage_dict = {'Operator':('Operator',['Operator']),
                             'Asist':('Asistent',['Asistent 1','Asistent 2','Asistent 3','Asistent']),
                            'Anestezio':('Anesteziolog',['Anesteziolog']),
                            'Anestet':('Anestetičar',['Anestetičar','Anesteticar']),
                            'Instru':('Instrumentarka',['Instrumentarka','Instrumentar']),
                            'Gostuju': ('Gostujući Specijalizant',['Gostujući specijalizant','Gostujuci specijalizant'])}
        prosao_datum = False
        for i, detection in enumerate(result):
            if 'Datum Operacije' in OUTPUT:
                if prosao_datum is False and detection in ['PACIJENT','OPERACIONA LISTA','godište']:
                    prosao_datum = True
                if  prosao_datum is False and not OUTPUT['Datum Operacije']:
                    date = AI.is_date(detection)
                    if date:
                        OUTPUT['Datum Operacije'] = date
                        prosao_datum = True
            if 'Glavna Operativna dijagnoza' in OUTPUT and 'Glavna operativna dijagnoza' in detection:
                mkb,line = AI.mkb_find(detection,result,i)
                if mkb is None:
                    continue
                elif line==1:
                    MKB = AI.mkb_fix('L'+mkb)
                else:
                    MKB = AI.mkb_fix(mkb)
                OUTPUT['Glavna Operativna dijagnoza'].append(MKB)
                if 'Dg Latinski' in OUTPUT and not OUTPUT['Dg Latinski']:
                    try:
                        Dg_Latinski = result[i+line].split(mkb)[1].strip()
                        Dg_Latinski = extend_variable(i+line, Dg_Latinski, ['Glavn', 'Spored', 'Operac','Operat'], result)
                        OUTPUT['Dg Latinski'] = Dg_Latinski.replace('|','l')
                    except IndexError:
                        continue
            elif 'Sporedna Operativna dijagnoza' in OUTPUT and 'Sporedna operativna dijagnoza' in detection:
                mkb,line = AI.mkb_find(detection,result,i)
                if mkb is None:
                    continue
                elif line==1:
                    MKB = AI.mkb_fix('L'+mkb)
                else:
                    MKB = AI.mkb_fix(mkb)
                OUTPUT['Sporedna Operativna dijagnoza'].append(MKB)
            else: # DOCTORS
                for prefix,(doctorType,fixlist) in DoctorsImage_dict.items():
                    if doctorType in OUTPUT and detection.capitalize().startswith(prefix):
                        doctors: str
                        doctors = extend_variable(i, detection, list(DoctorsImage_dict.keys())+['Preme','Anest'], result)
                        for fix in fixlist+['-','_',',','.',':',';']:
                            doctors = doctors.replace(fix,' ')
                        doctors = ' '.join(doctors.split())
                        if prefix == 'Gostuju':
                            DOCTORS = []
                            doctors = doctors.split()
                            for i,doc in enumerate(doctors):
                                if doc in ['Dr','dr']:
                                    DOCTORS.append(' '.join(doctors[i:i+3]).replace('Dr','dr'))
                            OUTPUT[doctorType] += DOCTORS
                        else:
                            if doctors:
                                if doctorType == 'Asistent':
                                    for word in doctors.split():
                                        if word in ['lekar', 'na', 'specijalizaciji','stažu']:
                                            break
                                    else:
                                        OUTPUT[doctorType].append(doctors.replace('Dr','dr'))
                                elif not OUTPUT[doctorType]:
                                    OUTPUT[doctorType] = [doctors.replace('Dr','dr')]
        return OUTPUT