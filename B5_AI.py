from A1_Variables import *
from B3_Media import Media
from C1_Controller import Controller

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

    OperacionaChoice = dict()

    Settings = {}
    for k,v in SETTINGS['Reader'].items():
        if k == 'Zoom':
            Settings[k] = v/100
        else:
            if isinstance(v,dict):
                Settings[k] = {}
                for col,val in v.items():
                    Settings[k][col] = val
            else:
                Settings[k] = v
    
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
    def ImageReader_SettingUp(PARENT:tb.Window):

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

            for column,boolvar in AI.OperacionaChoice.items():
                boolvar:BooleanVar
                SETTINGS['Reader']['Entry'][column] = boolvar.get()
                AI.Settings['Entry'][column] = boolvar.get()

            json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
            with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
                file.write(json_data)
            Messagebox.show_info(message='Saving Settings successful', title='Saving Settings',
                                    position=App.get_window_center())
            toplevel.lift()
            toplevel.focus_force()

        def restoredefault_command():
            for k,v in Controller.DEFAULT['Reader'].items():
                if k == 'Zoom':
                    AI.Settings[k] = v/100
                    zoom.amountusedvar.set(v)
                    SETTINGS['Reader'][k] = v
                else:
                    if isinstance(v,dict):
                        for col,val in v.items():
                            AI.Settings[k][col] = val
                            AI.OperacionaChoice[col].set(val)
                            SETTINGS['Reader'][k][col] = val
                    else:
                        AI.Settings[k] = v
                        if k == 'VRAM':
                            ram.amountusedvar.set(v)
                        elif k == 'Type':
                            combobox.set(v)
                        SETTINGS['Reader'][k] = v

            json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
            with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
                file.write(json_data)
            Messagebox.show_info(message='Restoring Default Settings successful', title='Restore Settings',
                                    position=App.get_window_center())
            toplevel.lift()
            toplevel.focus_force()

        toplevel = tb.Toplevel(alpha=0.93, iconphoto=IMAGES['icon']['AI'], windowposition=App.get_window_center())
        toplevel.withdraw()
        toplevel.transient(App.ROOT)
        
        toplevel.title('Reader - Configure')
        toplevel.grid_columnconfigure(0, weight=1)
        toplevel.resizable(False,False)

        titletxt = ' - Choose your settings for new AI Reading of document.\n'+\
                    ' - You can save your settings as default values for future readings.'
        title = tb.Label(toplevel, text=titletxt, anchor=W, wraplength=310)
        title.grid(row=0, column=0, padx=padding_12, pady=padding_12) 
        titleframe = Frame(toplevel)
        titleframe.grid(row=1, column=0, padx=padding_12, sticky=W)
        titlelabels = [ (' Slower ','High Zoom and Less Ram','danger'),
                        (' Faster ','Low Zoom and More Ram','success'),
                        (' Precision ','Change Zoom and AI Type','primary') ]
        for i,(txt1,txt2,bt) in enumerate(titlelabels):
            tb.Label(titleframe, anchor=W, justify=CENTER, text=txt1, bootstyle=bt, wraplength=310).grid(row=i, column=0, padx=0)
            tb.Label(titleframe, anchor=W, justify=LEFT, text=txt2, wraplength=310).grid(row=i, column=1, padx=0)

        label = tb.Label(toplevel, text=f'Image Reader Type', anchor=CENTER, justify=CENTER)
        label.grid(row=2, column=0, padx=padding_12, pady=padding_12) 
        values = ['AI-Line Reader', 'AI-Paragraph Reader']
        combobox = tb.Combobox(toplevel, values=values, state='readonly')
        combobox.set(values[0])
        combobox.grid(row=3, column=0, padx=padding_12, pady=padding_6)

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
        checkbutton_frame.grid(row=6, column=0, padx=padding_12, pady=padding_6, sticky=NSEW)
        checkbutton_frame.grid_columnconfigure(1,weight=1)
   
        col = 0
        row = 0
        
        for column in list(AI.Settings['Entry'].keys()):
            txt = column.split(' ')
            txt = ' '.join(txt) if len(txt)!=3 else ' '.join(txt[:2])
            if col==2:
                col = 0
                row += 1
            try:
                AI.OperacionaChoice[column].set(AI.Settings['Entry'][column])
            except KeyError:
                AI.OperacionaChoice[column] = BooleanVar()
                AI.OperacionaChoice[column].set(AI.Settings['Entry'][column])

            tb.Checkbutton(checkbutton_frame, text=txt, bootstyle=style_checkbutton, variable=AI.OperacionaChoice[column]).grid(
                row=row, column=col, padx=padding_12, pady=padding_6, sticky=W)
            col += 1

        button_frame = Frame(toplevel)
        button_frame.grid(row=7, column=0, padx=padding_12, pady=padding_6, sticky=E)
        Controller.toplevel_buttons(button_frame,[restoredefault_command,savedefault_command,run_command])

        toplevel.bind('<Return>', lambda event: run_command())
        toplevel.bind('<Command-s>', lambda event: savedefault_command())
        toplevel.bind('<Control-s>', lambda event: savedefault_command())
        toplevel.bind('<Command-r>', lambda event: restoredefault_command())
        toplevel.bind('<Control-r>', lambda event: restoredefault_command())

        toplevel.place_window_center()
        toplevel.deiconify()
        PARENT.wait_window(toplevel)
        return result['action']

    @staticmethod
    def Operaciona_Reader(image):
        if AI.Settings['Type'] == 'AI-Line Reader':
            result = AI.ReaderSetup.readtext(image, detail=0, mag_ratio=AI.Settings['Zoom'], batch_size=AI.Settings['VRAM'])
            return AI.Operaciona_LineReader(result)
        elif AI.Settings['Type'] == 'AI-Paragraph Reader':
            result = AI.ReaderSetup.readtext(image, detail=0, mag_ratio=AI.Settings['Zoom'], batch_size=AI.Settings['VRAM'], paragraph=True)
            AI.Operacion_ParagraphReader(result)

    @staticmethod
    def Operacion_ParagraphReader(result):
        print(result)

    @staticmethod
    def Operaciona_LineReader(result):
        def extend_variable(i, variable, searchlist, image_text):
            j = i + 1
            while j < len(image_text) and not any((image_text[j]).startswith(prefix) for prefix in searchlist):
                variable += (' ' + image_text[j])
                j += 1
            return variable

        OUTPUT = {}
        var:BooleanVar
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