from A1_Variables import *

pillow_heif.register_heif_opener()

class Media:
    TitleImages = []
    ThemeIcons = []
    TopLevel = None
    Downloading = False
    
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
    ReaderSetting = easyocr.Reader(['rs_latin','en'], gpu=(device != torch.device("cpu"))) # ovo pravi True/False za device

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
    
    Reader_Type = None
    GPU_VRAM_MB: int = None
    Image_Reader_RAM: int = None
    Image_Reader_Zoom: float = 1.13

    Slike_Viewer: Canvas = None
    Blob_Data = None
    Image_Active: Image.Image = None
    Image_Scale: int = 1
    Image_Zoomed_Width: int = None
    Image_Zoomed_Height: int = None
    delta = 1.18
    
    @staticmethod
    def initialize():
        Media.GPU_VRAM_MB = Media.get_gpu_vram()
        Media.Image_Reader_RAM = int(Media.GPU_VRAM_MB/2)

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
    def ProgressBar_DownloadingImages(parent:Frame, title:str, titletxt:list, width:int):
        Media.TopLevel = Toplevel(parent)
        Media.TopLevel.title(f'{title}...')
        Media.TopLevel.grid_columnconfigure(0, weight=1)
        Media.TopLevel.resizable(False,False)
        if os.name == 'nt':  # Windows
            Media.TopLevel.attributes('-toolwindow', True)
        else:  # macOS/Linux
            Media.TopLevel.attributes('-type', 'dialog')
        
        tb.Label(Media.TopLevel, text=f'{title} selected Images', anchor=CENTER, justify=CENTER, font=font_medium()).grid(
            row=0, column=0, columnspan=2, pady=24, sticky=NSEW)

        text_widget = tb.Text(Media.TopLevel, wrap=NONE, height=10, width=width, font=font_default)
        text_widget.grid(row=1, column=0, sticky=NSEW)

        scrollbar = tb.Scrollbar(Media.TopLevel, orient=VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=1, column=1, sticky=NS)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.tag_configure('success', foreground=ThemeColors['success'])

        for i, txt in enumerate(titletxt):
            text_widget.insert(END, f'{i+1}. {txt}\n')

        text_widget.configure(state=DISABLED)
       
        bar = tb.Floodgauge(Media.TopLevel, maximum=100, mode='determinate', value=0, bootstyle='primary', mask='Downloading...', font=font_big())
        bar.grid(row=2, column=0, columnspan=2, padx=24, pady=24, sticky=EW)
        return text_widget,bar

    @staticmethod
    def ImageReader_SettingUp(parent:Frame):
        Media.TopLevel = Toplevel(parent)
        Media.TopLevel.title('Scroll Window')
        Media.TopLevel.grid_columnconfigure(0, weight=1)
        Media.TopLevel.resizable(False,False)
        if os.name == 'nt':  # Windows
            Media.TopLevel.attributes('-toolwindow', True)
        else:  # macOS/Linux
            Media.TopLevel.attributes('-type', 'dialog')

        titletxt = ' - Choose your settings for new AI Reading of document.\n'+\
                    ' - You can save your settings as default values for future readings.'
        title = tb.Label(Media.TopLevel, text=titletxt, anchor=W, wraplength=310)
        title.grid(row=0, column=0, padx=10, pady=(24,0)) 
        titleframe = Frame(Media.TopLevel)
        titleframe.grid(row=1, column=0, padx=10, sticky=W)
        titlelabels = [ (' Slower ','High Zoom and Less Ram','danger'),
                        (' Faster ','Low Zoom and More Ram','success'),
                        (' Precision ','Change Zoom and AI Type','primary') ]
        for i,(txt1,txt2,bt) in enumerate(titlelabels):
            tb.Label(titleframe, anchor=W, justify=CENTER, text=txt1, bootstyle=bt, wraplength=310).grid(row=i, column=0, padx=0)
            tb.Label(titleframe, anchor=W, justify=LEFT, text=txt2, wraplength=310).grid(row=i, column=1, padx=0)

        label = tb.Label(Media.TopLevel, text=f'Image Reader Type', anchor=CENTER, justify=CENTER)
        label.grid(row=2, column=0, padx=12, pady=(24,6)) 
        values = ['AI-Line Reader', 'AI-Paragraph Reader']
        combobox = tb.Combobox(Media.TopLevel, values=values, state='readonly')
        combobox.set(values[0])
        combobox.grid(row=3, column=0, padx=12, pady=6)

        def create_scale(parent,row:int,fromto:tuple,text:str,default):
            if 'Zoom' in text:
                value = f'{default:.2f}x'
                def get_data(event):
                    label.config(text=f'{text}: {scale.get():.2f}x')
            elif 'Ram' in text:
                value = f'{default:,.0f} MB'
                def get_data(event):
                    label.config(text=f'{text}: {int(scale.get()):,} MB')

            label = tb.Label(parent, text=f'{text}: {value}', anchor=CENTER, justify=CENTER)
            label.grid(row=row, column=0, padx=20, pady=(16,6))    

            scale = tb.Scale(parent, from_=fromto[0], to=fromto[1], orient=HORIZONTAL, length=160, variable=StringVar())
            scale.grid(row=row+1, column=0, padx=20, pady=(6,16))
            scale.set(default)
            scale.bind('<Motion>', get_data)

            return scale
        
        zoom = create_scale(Media.TopLevel,4,(0.7,2.3),'Image Zoom',Media.Image_Reader_Zoom)
        ram = create_scale(Media.TopLevel,6,(1,Media.GPU_VRAM_MB),'Ram Usage',Media.Image_Reader_RAM)

        checkbutton_frame = Frame(Media.TopLevel)
        checkbutton_frame.grid(row=8, column=0, padx=12, pady=padding_6, sticky=NSEW)
        checkbutton_frame.grid_columnconfigure(1,weight=1)
   
        col = 0
        row = 0
        for check in list(Media.OperacionaChoice.keys()):
            txt = check.split(' ')
            txt = ' '.join(txt) if len(txt)!=3 else ' '.join(txt[:2])
            if col==2:
                col = 0
                row += 1
            tb.Checkbutton()
            cb = tb.Checkbutton(checkbutton_frame, text=txt, bootstyle=style_checkbutton)
            Media.OperacionaChoice[check] = IntVar()
            cb.configure(variable=Media.OperacionaChoice[check])
            if row>1:
                Media.OperacionaChoice[check].set(1)
            cb.grid(row=row, column=col, padx=padding_12, pady=padding_6, sticky=W)
            col += 1

        result = {'action':None}
        def run_command():
            Media.Image_Reader_RAM = int(ram.get())
            Media.Image_Reader_Zoom = round(zoom.get(),2)
            Media.Reader_Type = combobox.get()
            result['action'] = 'Run'
            Media.TopLevel.destroy()

        def savedefault_command():
            Media.Image_Reader_RAM = int(ram.get())
            Media.Image_Reader_Zoom = round(zoom.get(),2)
            Media.Reader_Type = combobox.get()
            result['action'] = 'Save'
            Media.TopLevel.destroy()

        button_frame = Frame(Media.TopLevel)
        button_frame.grid(row=9, column=0, padx=12, pady=(24, 6), sticky=E)

        ctk.CTkButton(button_frame, text='SAVE\nDEFAULT', width=buttonX-2, height=buttonY, corner_radius=12, font=font_medium(),
                    fg_color=ThemeColors['success'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                    command=savedefault_command).grid(row=0, column=0, padx=padding_6[0], pady=padding_6[1])
        
        ctk.CTkButton(button_frame, text='RUN', width=buttonX-4, height=buttonY, corner_radius=12, font=font_medium(),
                    fg_color=ThemeColors['primary'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                    command=run_command).grid(row=0, column=1, padx=padding_6[0], pady=padding_6[1])

        parent.wait_window(Media.TopLevel)
        return result['action']

    @staticmethod
    def Operaciona_Reader(image):
        if Media.Reader_Type == 'AI-Line Reader':
            return Media.Operaciona_LineReader(image)
        elif Media.Reader_Type == 'AI-Paragraph Reader':
            return Media.Operacion_ParagraphReader(image)

    @staticmethod
    def Operacion_ParagraphReader(image):
        pass

    @staticmethod
    def Operaciona_LineReader(image):
        result = Media.ReaderSetting.readtext(image, detail=0, mag_ratio=Media.Image_Reader_Zoom, batch_size=Media.Image_Reader_RAM)

        def extend_variable(i, variable, searchlist, image_text):
            j = i + 1
            while j < len(image_text) and not any((image_text[j]).startswith(prefix) for prefix in searchlist):
                variable += (' ' + image_text[j])
                j += 1
            return variable

        OUTPUT = {}
        var:IntVar
        for col,var in Media.OperacionaChoice.items():
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
                    date = Media.is_date(detection)
                    if date:
                        OUTPUT['Datum Operacije'] = date
                        prosao_datum = True
            if 'Glavna Operativna dijagnoza' in OUTPUT and 'Glavna operativna dijagnoza' in detection:
                mkb,line = Media.mkb_find(detection,result,i)
                if mkb is None:
                    continue
                elif line==1:
                    MKB = Media.mkb_fix('L'+mkb)
                else:
                    MKB = Media.mkb_fix(mkb)
                OUTPUT['Glavna Operativna dijagnoza'].append(MKB)
                if 'Dg Latinski' in OUTPUT and not OUTPUT['Dg Latinski']:
                    try:
                        Dg_Latinski = result[i+line].split(mkb)[1].strip()
                        Dg_Latinski = extend_variable(i+line, Dg_Latinski, ['Glavn', 'Spored', 'Operac','Operat'], result)
                        OUTPUT['Dg Latinski'] = Dg_Latinski.replace('|','l')
                    except IndexError:
                        continue
            elif 'Sporedna Operativna dijagnoza' in OUTPUT and 'Sporedna operativna dijagnoza' in detection:
                mkb,line = Media.mkb_find(detection,result,i)
                if mkb is None:
                    continue
                elif line==1:
                    MKB = Media.mkb_fix('L'+mkb)
                else:
                    MKB = Media.mkb_fix(mkb)
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

    @staticmethod
    def label_ImageLoad(images_list):
        return_images = []
        for (img,width,height) in images_list:
            raw_img = Image.open(img)
            resize_img = raw_img.resize((width,height))
            return_images.append(ImageTk.PhotoImage(resize_img))
        return return_images

    @staticmethod
    def hover_label_button(event,img):
        label:tb.Label = event.widget
        label.config(image=img)

    def image_to_blob(file_path):
        with open(file_path, 'rb') as f:
            blob_data = f.read()
        return blob_data

    @staticmethod
    def get_image(image_blob_data): # Format za Canvas
        image = Image.open(io.BytesIO(image_blob_data))
        return image

    @staticmethod
    def resize_image(image, max_width, max_height, savescale=False):
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        scale_ratio = min(width_ratio, height_ratio)
        if savescale is True:
            Media.Image_Scale = scale_ratio

        new_width = int(image.width * scale_ratio)
        new_height = int(image.height * scale_ratio)
        return image.resize((new_width, new_height), Image.LANCZOS)

    @staticmethod
    def create_video_thumbnail(video_data):
        if not os.path.exists(os.path.join(directory,'temporary')):
            os.makedirs(os.path.join(directory,'temporary'))
        video_file = os.path.join(directory,'temporary/temp_video.mp4')
        with open(video_file, 'wb') as f:
            f.write(video_data)

        # Capture the first frame of the video
        cap = cv2.VideoCapture(video_file)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception('Failed to capture video frame')

        # Convert the frame to a PIL image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Add play button overlay
        width, height = image.size
        play_button_size = min(width, height) // 4
        play_button = Image.open(IMAGES['Play Video']).resize((play_button_size, play_button_size))
        play_button_pos = ((width - play_button_size) // 2, (height - play_button_size) // 2)
        image.paste(play_button, play_button_pos, play_button)

        return image,video_file

    @staticmethod
    def play_video(event,video_data):
        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(video_data))
        elif os.name == 'posix':  # For macOS and Linux
            if os.uname().sysname == 'Darwin':  # macOS
                subprocess.call(['open', os.path.abspath(video_data)])
            else:  # Linux
                subprocess.call(['xdg-open', os.path.abspath(video_data)])

    @staticmethod
    def open_image(event,image_data):
        # Save video data to a temporary file
        if not os.path.exists(os.path.join(directory,'temporary')):
            os.makedirs(os.path.join(directory,'temporary'))
        image_file = os.path.join(directory,'temporary/temp_image.png')
        with open(image_file, 'wb') as f:
            f.write(image_data)

        if not os.path.exists(image_file):
            return

        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(image_file))
        elif os.name == 'posix':  # For macOS and Linux
            if os.uname().sysname == 'Darwin':  # macOS
                subprocess.call(['open', os.path.abspath(image_file)])
            else:  # Linux
                subprocess.call(['xdg-open', os.path.abspath(image_file)])

    @staticmethod
    def make_cropped_part():
        X_scroll = Media.Slike_Viewer.xview()
        Y_scroll = Media.Slike_Viewer.yview()
        left,right = (X_scroll[0]*Media.Image_Zoomed_Width,
                   X_scroll[1]*Media.Image_Zoomed_Width) # (NW,NE) od WIDTH (left i right)
        top,bottom = (Y_scroll[0]*Media.Image_Zoomed_Height,
                     Y_scroll[1]*Media.Image_Zoomed_Height) # (NE,SE) od HEIGHT (top i bottom)
        Media.Slike_Viewer.configure(scrollregion=(0,0,Media.Image_Zoomed_Width,Media.Image_Zoomed_Height))

        image = Media.Image_Active.crop((left,top,right,bottom))
        bytes_image = io.BytesIO()
        image.save(bytes_image, format='png')
        byte_data = bytes_image.getvalue()
        Media.open_image(event=None,image_data=byte_data)

    @staticmethod
    def zoom(event):
        # Skaliranje slike
        temp_scale = Media.Image_Scale
        if event.delta > 0 or event.num == 4:
            temp_scale *= 1.18
        elif event.delta < 0 or event.num == 5:
            temp_scale /= 1.18
        if min(Media.Image_Active.width,Media.Image_Active.height)*temp_scale < 33: return
        if max(Media.Image_Active.width,Media.Image_Active.height)*temp_scale > 6000: return

        Media.Image_Scale = temp_scale
        Media.Image_Zoomed_Width = int(Media.Image_Active.width * Media.Image_Scale)
        Media.Image_Zoomed_Height = int(Media.Image_Active.height * Media.Image_Scale)

        image = Media.Image_Active.crop()
        image = Media.Image_Active.resize((Media.Image_Zoomed_Width, Media.Image_Zoomed_Height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        Media.Slike_Viewer.delete('all')

        Media.Slike_Viewer.create_image(Media.Slike_Viewer.winfo_width()//2, Media.Slike_Viewer.winfo_height()//2, anchor=CENTER, image=image)
        Media.Slike_Viewer.image = image
        Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
   
        '''
        print(f'Canvas width: {Media.Slike_Viewer.winfo_width()}')
        print(f'Canvas height: {Media.Slike_Viewer.winfo_height()}')
        print(f'Image width: {Media.Image_Zoomed_Width}')
        print(f'Image height: {Media.Image_Zoomed_Height}')

        X_scroll = Media.Slike_Viewer.xview()
        Y_scroll = Media.Slike_Viewer.yview()
        left,right = (X_scroll[0]*Media.Image_Zoomed_Width,
                   X_scroll[1]*Media.Image_Zoomed_Width) # (NW,NE) od WIDTH (left i right)
        top,bottom = (Y_scroll[0]*Media.Image_Zoomed_Height,
                     Y_scroll[1]*Media.Image_Zoomed_Height) # (NE,SE) od HEIGHT (top i bottom)
        bbox = (Media.Slike_Viewer.canvasx(0),  # get visible area of the canvas
                 Media.Slike_Viewer.canvasy(0),
                 Media.Slike_Viewer.canvasx(Media.Slike_Viewer.winfo_width()),
                 Media.Slike_Viewer.canvasy(Media.Slike_Viewer.winfo_height()))
        print(f'LRTB: {left,right,top,bottom}')
        print(f'bbox: {bbox}')
        #'''

    @staticmethod
    def move_from(event):
        Media.Slike_Viewer.scan_mark(event.x, event.y)

    @staticmethod
    def move_to(event):
        if Media.Image_Zoomed_Height:
            Media.Slike_Viewer.scan_dragto(event.x, event.y, gain=1)
            '''
            X_scroll = Media.Slike_Viewer.xview()
            Y_scroll = Media.Slike_Viewer.yview()
            left,right = (X_scroll[0]*Media.Image_Zoomed_Width,
                    X_scroll[1]*Media.Image_Zoomed_Width) # (NW,NE) od WIDTH (left i right)
            top,bottom = (Y_scroll[0]*Media.Image_Zoomed_Height,
                        Y_scroll[1]*Media.Image_Zoomed_Height) # (NE,SE) od HEIGHT (top i bottom)
            bbox = (Media.Slike_Viewer.canvasx(0),  # get visible area of the canvas
                    Media.Slike_Viewer.canvasy(0),
                    Media.Slike_Viewer.canvasx(Media.Slike_Viewer.winfo_width()),
                    Media.Slike_Viewer.canvasy(Media.Slike_Viewer.winfo_height()))
            print(f'LRTB: {left,right,top,bottom}')
            print(f'bbox: {bbox}')
            #'''

if __name__=='__main__':
    pass