from A1_Variables import *
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import RHMH,LOGS, Database
from B3_Media import Media,Loading_Splash


class GodMode:
    password = None
    TopLevel: tb.Toplevel = None
    eye_image:Image.Image = None

    @staticmethod
    def Admin_Unlocking(PARENT:Tk):
        result = dict()
        def ok_command():
            result['Ok'] = password.get()
            toplevel.destroy()
        def hint_command():
            if 'Hint' not in result:
                report = 'There are 3 different valid passwords\n' +\
                            'Two of those unlock Super-Admin mode - "GodMode"\n' +\
                            'The easiest One unlocks Admin mode\n' +\
                            'All of the passwords are hidden inside LOGO visible in About Page'
                result['Hint'] = report
            Messagebox.show_info(message=report, title='Password Hint',
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            toplevel.lift()
            toplevel.focus_force()

        toplevel = tb.Toplevel(alpha=0.93, iconphoto=IMAGES['icon']['GodMode'])
        toplevel.withdraw()
        toplevel.transient(Controller.ROOT)
        
        toplevel.title('Privileges - unlocking')
        toplevel.grid_columnconfigure(0, weight=1)
        toplevel.resizable(False,False)
        
        if GodMode.eye_image == None:
            GodMode.eye_image = Media.label_ImageLoad(IMAGES['Password'])
        lbl = tb.Label(toplevel, image=GodMode.eye_image)
        lbl.grid(row=0, column=0, columnspan=2, padx=padding_6, pady=padding_6, sticky=NSEW)

        password = tb.Entry(toplevel, show='*')
        password.grid(row=1, column=0, columnspan=2, padx=padding_12, pady=padding_12, sticky=EW)

        butt_color = ThemeColors['info']
        ctk.CTkButton(toplevel, text='Get\nHint', width=buttonX, height=buttonY, corner_radius=12, font=font_medium('bold'),
                    fg_color=butt_color, text_color=ThemeColors['bg'],
                    text_color_disabled=ThemeColors['secondary'], hover_color=Media.darken_color(butt_color),
                    command=hint_command).grid(row=2, column=0, padx=padding_6, pady=padding_6)

        butt_color = ThemeColors['primary']
        ctk.CTkButton(toplevel, text='Activate', width=buttonX, height=buttonY, corner_radius=12, font=font_medium('bold'),
                    fg_color=butt_color, text_color=ThemeColors['bg'],
                    text_color_disabled=ThemeColors['secondary'], hover_color=Media.darken_color(butt_color),
                    command=ok_command).grid(row=2, column=1, padx=padding_6, pady=padding_6)
        
        toplevel.bind('<Return>', lambda event: ok_command())

        toplevel.place_window_center()
        toplevel.deiconify()
        password.focus_set()
        PARENT.wait_window(toplevel)
        return result

    @staticmethod
    def GodMode_Password(event):
        response = GodMode.Admin_Unlocking(Controller.ROOT)
        Controller.ROOT.revert_iconphoto()
        if 'Ok' in response:
            if response['Ok'] == '63636':
                info = 'New tabs:\n\t-Logs\n\t-Session\n' +\
                        f'\n{GodMode.money()}'
                title = 'Admin unlocked'
            elif response['Ok'] in ['C12-Si28-C13-Si28-C12','C12-Li3-C13-Li3-C12']:
                for frame in Controller.FreeQuery_Frame:
                    frame:Frame
                    frame.grid()
                info = 'New tabs:\n\t-Logs\n\t-Session\n' +\
                        'New button:\n\t-Free Query\n\t-Upload LOGS\n' +\
                        f'\n{GodMode.money()}'
                title = 'God Mode unlocked' 
            else:
                return
            Messagebox.show_info(message=info, title=title,
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            GodMode.JoiningLogs()
            Controller.ROOT.after(WAIT, lambda: Controller.NoteBook.select(5))
            Controller.ROOT.after(WAIT*2, lambda: Controller.NoteBook.select(4))

    @staticmethod
    def ProgressBar_JoiningLogs(count:int):
        GodMode.TopLevel = tb.Toplevel(alpha=0.93, iconphoto=IMAGES['icon']['GodMode'])
        GodMode.TopLevel.withdraw()

        GodMode.TopLevel.title(f'Joining Logs...')
        GodMode.TopLevel.grid_columnconfigure(0, weight=1)
        GodMode.TopLevel.resizable(False,False)
        GodMode.TopLevel.attributes('-topmost', True)

        label = tb.Label(GodMode.TopLevel, text=f'Importing Online Logs - {count} left', anchor=CENTER, justify=CENTER, font=font_medium())
        label.grid(row=0, column=0, columnspan=2, pady=padding_12, sticky=NSEW)
       
        text_widget = tb.Text(GodMode.TopLevel, wrap=NONE, height=10, width=40, font=font_default)
        text_widget.grid(row=1, column=0, sticky=NSEW)

        scrollbar = tb.Scrollbar(GodMode.TopLevel, orient=VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=1, column=1, sticky=NS)
        text_widget.configure(yscrollcommand=scrollbar.set)

        bar = tb.Floodgauge(GodMode.TopLevel, mode='indeterminate', bootstyle='primary', mask='Downloading...', font=font_default)
        bar.grid(row=2, column=0, columnspan=2, padx=padding_12, pady=padding_12, sticky=EW)

        frame = Frame(GodMode.TopLevel)
        frame.grid(row=3, column=0, columnspan=2, sticky=NSEW)
        gif:Loading_Splash = Media.Gif['GodMode']
        gif.create_splash(frame,1)

        GodMode.TopLevel.place_window_center()
        GodMode.TopLevel.deiconify()
        return bar,text_widget,label,gif

    @staticmethod
    def JoiningLogs():
        start = time.time()
        gd_logs_ids = GoogleDrive.find_logs(GD_MAIN[0])
        gd_logs_ids.update(GoogleDrive.find_logs(GD_LOGS[0]))
        TOTAL = len(gd_logs_ids)
        floodgauge,text_widget,label,gif = GodMode.ProgressBar_JoiningLogs(TOTAL)
        text_widget.tag_configure('success', foreground=ThemeColors['success'])
        text_widget.tag_configure('fail', foreground=ThemeColors['danger'])

        def join_logs():
            floodgauge.start()
            GoogleDrive.download_File(GD_LOGS_dict['id'],GD_LOGS_dict['path'])
            Controller.GD_LOGS = Database(GD_LOGS_dict['path'])

            floodgauge['mask'] = 'Joining...'
            if not os.path.exists(os.path.join(directory,'temporary')):
                os.makedirs(os.path.join(directory,'temporary'))

            for i,(name,log_id) in enumerate(gd_logs_ids.items()):
                path = os.path.join(directory,'temporary/temp.db')
                tempbase = Database(path)
                tempbase.connect()
                tempbase.close_connection()

                GoogleDrive.download_File(log_id,path)
                Database.execute_Insert_Many(tempbase,Controller.GD_LOGS,'logs',tempbase.show_columns('logs'))
                Database.execute_Insert_Many(tempbase,Controller.GD_LOGS,'session',tempbase.show_columns('session'))

                text_widget.insert(f'{i+1}.0', f'{i+1}. {name}\n')
                try:
                    GoogleDrive.delete_file(log_id)
                    text_widget.tag_add('success', f'{i+1}.0', f'{i+1}.end')
                except Exception:
                    text_widget.tag_add('fail', f'{i+1}.0', f'{i+1}.end')
                text_widget.update_idletasks()
                label.configure(text=f'Importing Online Logs - {TOTAL-(i+1)} left')
                label.update_idletasks()
            else:
                floodgauge['mask'] = 'Uploading...'
                GoogleDrive.upload_UpdateFile(GD_LOGS_dict['id'],GD_LOGS_dict['path'],GD_LOGS_dict['mime'])
                Database.email = [i[0] for i in Controller.GD_LOGS.execute_selectquery('SELECT Email FROM Logs UNION SELECT Email FROM Session')]
                floodgauge.grid_forget()
                gif.stop()
                print(time.time()-start)
                
        threading.Thread(target=join_logs).start()
        Controller.ROOT.revert_iconphoto()

    @staticmethod
    def upload_GD_LOGS():
        confirm = Messagebox.yesno(title=f'Uploading...', message=f'Are you sure you want to Upload Google Drive LOGS?', alert=True,
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        if confirm == 'Yes':
            def message_success():
                Messagebox.show_info(message='Uploading LOGS successful', title='Uploading LOGS',
                                        position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            def message_fail():
                Messagebox.show_info(message='Uploading LOGS failed', title='Uploading LOGS',
                                        position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            def upload():
                try:
                    gif:Loading_Splash = Media.Gif['GodMode']
                    gif.create_splash(Controller.ROOT,0.7)
                    GoogleDrive.upload_UpdateFile(GD_LOGS_dict['id'],GD_LOGS_dict['path'],GD_LOGS_dict['mime'])
                    gif.stop()
                    Controller.ROOT.after(WAIT,message_success)
                except Exception:
                    gif.stop()
                    Controller.ROOT.after(WAIT,message_fail)
            threading.Thread(target=upload).start()

    @staticmethod
    def FreeQuery_Execute():
        DB = Controller.QueryDatabase.get()
        DATABASE = RHMH if DB == 'RHMH' else Controller.GD_LOGS if DB == 'LOGS' else None
        query = Controller.FreeQuery.get()
        if not query:
            return
        report = f'{DB}\n' +\
                DATABASE.format_sql(query)
        response = Messagebox.yesno(title='Free Query executing...', message=report,
                                        position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        if response == 'Yes':
            DATABASE.connect()
            DATABASE.cursor.execute(query)
            DATABASE.connection.commit()
            DATABASE.close_connection()

    @staticmethod
    def money():
        message = '    MUVS\n'
        message += f'{(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).total_seconds()//13*13:,.0f} $\n'
        message += f'{(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).days//13*13:,.0f} Million $'
        return message


class Controller:
    
    queue = queue.Queue()

    ROOT:tb.Window = None
    GD_LOGS:Database = None
    
    Connected:bool = False
    DEFAULT:dict = None
    Buttons = {'Filter Patient':[]}
    
        # ADMIN
    SessionReport           = ''
    SessionLabel:tb.Label   = None
    QueryDatabase:StringVar = None
    FreeQuery_Frame:list    = list()
    FreeQuery:StringVar     = None

        # TOP - Title Frame
    Top_Frame: Canvas = None
    Reconnect_window = None
    Reconnect_Button: ctk.CTkButton = None

        # NOTEBOOK
    NoteBook:          tb.Notebook      = None

    SEARCH:dict = None

    Table_Pacijenti:   tb.ttk.Treeview  = None
    Pacijenti_ColumnVars                = dict()
    FilterOptions                       = dict()
    TablePacijenti_Columns              = tuple(MainTablePacijenti.keys())
    Patient_FormVariables               = {'pacijent':{},'dijagnoza':{},'operacija':{},'slike':{}}

    Table_Slike:       tb.ttk.Treeview  = None
    TableSlike_Columns: tuple           = None
    Slike_HideTable:    Frame           = None
    Slike_FormVariables               = dict()

    Table_MKB:         tb.ttk.Treeview  = None
    TableMKB_Columns:  tuple            = None
    Table_Zaposleni:   tb.ttk.Treeview  = None
    TableZaposleni_Columns: tuple       = None
    Katalog_FormVariables               = dict()

    Graph_Canvas: Frame = None
    graph_canvas: FigureCanvasTkAgg = None
    Graph_FormVariables = dict()

    Table_Logs:        tb.ttk.Treeview  = None
    TableLogs_Columns: tuple            = None
    Logs_FormVariables                  = dict()
    Table_Session:     tb.ttk.Treeview  = None
    TableSession_Columns: tuple         = None

    About_Tab:      Frame = None
    Settings_Tab:   Frame = None
    Settings_FormVariables = dict()

    Table_Names = dict()
    
        # SEARCH BAR
    max_SearchBars      = 7
    SearchBar_number    = 1
    SearchBar: Frame    = None
    SearchBar_widgets   = dict()
    
    SearchAdd_Button: tb.Label    = None
    SearchRemove_Button: tb.Label = None
    signimages: list    = None
    
        # FORM
    PatientFocus_ID = None
    FormTitle:tb.Label = None
    PatientInfo:tb.Label = None
    MainTable_IDS = list()

        # VALIDATION FORM
    Validation_Widgets = {'Default':[], 'Alternative':[]}
    Valid_Default: bool = True
    Valid_Alternative: bool = True

    MKB_validation_LIST:        list = None
    Zaposleni_validation_LIST:  list = None

    @staticmethod
    def block_manageDB(): # DECORATOR
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if Controller.Connected is False:
                    report = 'You didnt download Database from Google Drive\n'
                    report += 'Offline mode can only View from Local Database\n'
                    report += 'Managing Database is forbidden in Offline mode\n'
                    report += f'Please Reconnect if you want to "{func.__name__}"\n'
                    Messagebox.show_warning(title=f'{func.__name__} failed!', message=report,
                                position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
                else:
                    func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def toplevel_buttons(frame,commands:list):
        butt_color = ThemeColors['info']
        ctk.CTkButton(frame, text='RESTORE\nDefault', width=buttonX, height=buttonY, corner_radius=12, font=font_medium('bold'),
                    fg_color=butt_color, text_color=ThemeColors['bg'],
                    text_color_disabled=ThemeColors['secondary'], hover_color=Media.darken_color(butt_color),
                    command=commands[0]).grid(row=0, column=0, padx=padding_6, pady=padding_6)

        butt_color = ThemeColors['primary']
        ctk.CTkButton(frame, text='SAVE\nDefault', width=buttonX, height=buttonY, corner_radius=12, font=font_medium('bold'),
                    fg_color=butt_color, text_color=ThemeColors['bg'],
                    text_color_disabled=ThemeColors['secondary'], hover_color=Media.darken_color(butt_color),
                    command=commands[1]).grid(row=0, column=1, padx=padding_6, pady=padding_6)
        
        butt_color = ThemeColors['success']
        ctk.CTkButton(frame, text='RUN', width=buttonX-4, height=buttonY, corner_radius=12, font=font_medium('bold'),
                    fg_color=butt_color, text_color=ThemeColors['bg'],
                    text_color_disabled=ThemeColors['secondary'], hover_color=Media.darken_color(butt_color),
                    command=commands[2]).grid(row=0, column=2, padx=padding_6, pady=padding_6)

    @staticmethod
    def load_loading_GIF():
        for gif in ['AI','Graph','GodMode','Web']:
            folder = os.path.join(directory,f'Slike/gif_{gif}')
            def load_gif(GIF,FOLDER):
                Media.Gif[GIF] = Loading_Splash(folder=FOLDER, dimension=GIF_SIZE)
            threading.Thread(target=lambda gif_key=gif, folder_path=folder: Controller.queue.put((Controller.ROOT.after, (WAIT, lambda: load_gif(gif_key, folder_path))))).start()
            #Controller.queue.put((Controller.ROOT.after, (WAIT, lambda gif=gif,folder=folder: load_gif(gif,folder))))

    @staticmethod
    def process_queue():
        try:
            while True:
                func, args = Controller.queue.get_nowait()
                Controller.ROOT.after_idle(func, *args)
                Controller.queue.task_done()
        except queue.Empty:
            Controller.ROOT.after(100, Controller.process_queue)

    @staticmethod
    def starting_application():
        def message_success():
            report = f'Connection successful\nOnline mode\nHello {UserSession['Email']}'
            Messagebox.show_info(title='Connect',message=report,
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        def message_fail():
                report = 'Connection failed\nOffline mode'
                Messagebox.show_error(title='Connect',message=report,
                                        position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        def update_message():
            report = 'Please Download latest version from Google Drive\n' + \
                'Unzip files and copy them into directory of RHMH app'
            download = Messagebox.show_question(title='New Version', message=report, buttons=['Skip:warning','Download:success'],
                                                position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            if download == 'Download':
                Controller.open_link(link=r'https://drive.google.com/drive/folders/1yvDczxK01aBO3xdm-Vlkr38hP8DGD2g0')

        try:
            GoogleDrive.setup_connection()
            if Controller.Connected == False:
                email = GoogleDrive.get_UserEmail()
                
                if email and email != SETTINGS['Email']:
                    UserSession['Email'] = email
                    SETTINGS['Email'] = email
                    json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
                    with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
                        file.write(json_data)

                GoogleDrive.download_File(RHMH_dict['id'],RHMH_dict['path'])
                try:
                    GoogleDrive.download_File(DEFAULT_dict['id'],DEFAULT_dict['path'])
                except Exception:
                    pass
                with open(os.path.join(directory,'Default.json'), 'r', encoding='utf-8') as file:
                    Controller.DEFAULT = json.load(file)

                Controller.Connected = True
                if Controller.Reconnect_window:
                    Controller.Top_Frame.delete(Controller.Reconnect_window)
                    Controller.Reconnect_window = None
                    Controller.ROOT.update()

                if SETTINGS['Version'] != Controller.DEFAULT['Version']:
                    Controller.ROOT.after(WAIT,update_message)
                else:
                    Controller.ROOT.after(WAIT,message_success)
        except Exception as e:
            Controller.ROOT.after(WAIT,message_fail)
            width = Controller.Top_Frame.winfo_width()
            Controller.Top_Frame.create_window(width*0.93, 10, anchor=N, window=Controller.Reconnect_Button)
        finally:
            UserSession['Logged IN'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            UserSession['GUI']['Start'] = (time.time_ns()-TIME_START)/10**9
            print((time.time_ns()-TIME_START)/10**9)
    
    @staticmethod
    def create_new_user():
        def message_success():
            report = f'User changed\nHello {UserSession['Email']}'
            Messagebox.show_info(title='Changing User',message=report,
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        def message_fail():
                report = f'User unchanged\nOld User: {UserSession['Email']}'
                Messagebox.show_error(title='Changing User',message=report,
                                        position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        try:
            GoogleDrive.create_new_token()
            email = GoogleDrive.get_UserEmail()
            UserSession['Email'] = email
            SETTINGS['Email'] = email
            json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
            with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
                file.write(json_data)
            Controller.ROOT.after(WAIT,message_success)    
        except Exception:
            Controller.ROOT.after(WAIT,message_fail)    

    @staticmethod
    def update_settings():
        for col,value in Controller.Settings_FormVariables.items():
            if not isinstance(value,dict):
                SETTINGS[col] = value.get()
            else:
                for c,v in value.items():
                    try:
                        SETTINGS[col][c] = v.get()
                    except AttributeError:
                        v:tb.Meter
                        SETTINGS[col][c] = v.amountusedvar.get()
        json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
        with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
            file.write(json_data)
        Messagebox.show_info(message='Saving Settings successful', title='Saving Settings',
                                position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))

    @staticmethod
    def restore_default_settings() -> None:
        for k,v in Controller.DEFAULT.items():
            if k in ['Version','Reader','Graph']:
                continue
            SETTINGS[k] = v
        for col,val in SETTINGS.items():
            if col in ['Email','Version','Version','Reader','Graph']:
                continue
            if not isinstance(val,dict):
                Controller.Settings_FormVariables[col].set(val)
            else:
                for column,value in val.items():
                    try:
                        Controller.Settings_FormVariables[col][column].set(value)
                    except AttributeError:
                        Controller.Settings_FormVariables[col][column].amountusedvar.set(value)
        Messagebox.show_info(message='Restoring Default Settings successful', title='Restore Settings',
                                position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))

    @staticmethod
    def Upload_RHMH() -> None:
        def message_success():
            Messagebox.show_info(title='Upload',message='Upload Database successful',
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        def message_fail():
            Messagebox.show_error(title='Upload',message='Upload Database failed',
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))

        rhmh = GoogleDrive.upload_UpdateFile(RHMH_dict['id'],RHMH_dict['path'],RHMH_dict['mime'])

        if rhmh:
            Controller.ROOT.after(WAIT,message_success)  # Message
            return True
        else:
            Controller.ROOT.after(WAIT,message_fail)  # Message
            return False

    @staticmethod
    def Upload_local_LOGS():
        email = UserSession['Email']
        logged_in = UserSession['Logged IN']
        logged_out = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        dt1 = datetime.strptime(logged_in, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(logged_out, "%Y-%m-%d %H:%M:%S")
        session = dt2 - dt1
        gui:dict = UserSession['GUI']
        gui.update(UserSession['TopPanel'])
        gui.update(UserSession['FormPanel'])
        gui.update(UserSession['MainPanel'])
        inserted = LOGS.execute_Insert('session',**{'Email':email,'Logged IN':logged_in,'Logged OUT':logged_out,'Session':str(session),
                                         'PC':pickle.dumps(UserSession['PC']),'GUI':pickle.dumps(gui),'GoogleDrive':pickle.dumps(UserSession['GoogleDrive']),
                                         'Database':pickle.dumps(UserSession['Database']),'Media':pickle.dumps(UserSession['Media']),
                                         'Graph':pickle.dumps(UserSession['Graph']),'Controller':pickle.dumps(UserSession['Controller']),
                                         'ManageDB':pickle.dumps(UserSession['ManageDB']),'SelectDB':pickle.dumps(UserSession['SelectDB'])})
        if inserted:
            filename = f'LOG - {email} {logged_in}'
            driveID = GoogleDrive.upload_NewFile_asFile(file_name=filename, GoogleDrive_folder=GD_LOGS,
                                          file_path=LOGS_dict['path'], mime_type=LOGS_dict['mime'])
            if driveID:
                LOGS.connect()
                LOGS.cursor.execute('DELETE FROM logs')
                LOGS.cursor.execute('DELETE FROM session')
                LOGS.connection.commit()
                LOGS.close_connection()
                LOGS.Vaccum_DB()

    @staticmethod
    def Clear_Form():
        parent_name = Controller.FormTitle.winfo_parent()
        parent:Frame = Controller.FormTitle.nametowidget(parent_name)

        Controller.PatientFocus_ID = None
        Controller.FormTitle.configure(bootstyle=color_labeltext)
        Controller.PatientInfo.config(text='\n')
        for table_groups in Controller.Patient_FormVariables.values():
            for widget in table_groups.values():
                Controller.empty_widget(widget)

    @staticmethod
    def empty_widget(widget):
        if isinstance(widget, StringVar) or \
            isinstance(widget, tb.Combobox):
            widget.set('')
        elif isinstance(widget, tb.Entry):
            widget.delete(0,END)
        elif isinstance(widget, widgets.DateEntry):
            widget.entry.delete(0,END)
        elif isinstance(widget, Text):
            widget.delete('1.0', END)
        elif isinstance(widget,tb.Label) and widget.cget('text') not in SIGNS:
            widget.config(text='')
        elif isinstance(widget, tb.Treeview):
            for item in widget.get_children():
                widget.delete(item)

    @staticmethod
    def get_widget_value(widget):
        if  isinstance(widget, StringVar) or \
                isinstance(widget, tb.Combobox) or \
                    isinstance(widget, tb.Entry):
            return widget.get()
        elif isinstance(widget, widgets.DateEntry):
            return widget.entry.get()
        elif isinstance(widget,tb.Label):
            return widget.cget('text')
        elif isinstance(widget, Text):
            return widget.get('1.0', END).strip()
        else:
            return None

    @staticmethod    
    def set_widget_value(widget,value):
        if not value:
            return
        if Controller.is_DB_date(value):
            # From RHMH Date Format TO Form Date Format
            value = datetime.strptime(str(value),'%Y-%m-%d').strftime('%d-%b-%Y')
        if isinstance(widget, StringVar):
            widget.set(value)
        elif isinstance(widget, Text):
            widget.delete('1.0', END)
            widget.insert('1.0', value)
        elif isinstance(widget, widgets.DateEntry):
            widget.entry.delete(0,END)
            widget.entry.insert(0,value)
        elif isinstance(widget, tb.Treeview):
            for item in widget.get_children():
                widget.delete(item)
            if len(value)!=0:
                n = 4 # broj kolona u mini table
                VALUE = [value[i:i+n] for i in range(len(value))[::n]]
                for i,val in enumerate(VALUE):
                    val[0] = val[0].replace(f'{val[0].split('_')[1]}_','')
                    val[1] = f'{float(val[1]):.2f} MB'
                    row = [i+1]+val
                    widget.insert('', END, values=row)

    @staticmethod
    def LoggingData(result=None,query_type=None,loggingdata=None):
        Time = f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.{datetime.now().strftime('%f')[:3]}'
        if loggingdata:
            def execute():
                LOGS.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['Email'],
                                                'Query':query_type,'Full Query':loggingdata})
            Controller.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
            return
        if result:
            def execute():
                LOGS.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['Email'],
                                                'Query':query_type,'Full Query':LOGS.LoggingQuery})
            Controller.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
        return result
    
    @staticmethod
    def get_image_fromGD(GoogleID,queue=None):
        def message_download_fail():
            Messagebox.show_error(title='Downloading failed',message='Can`t connect to Google Drive',
                                position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
        try:
            Media.Downloading = True
            Media.Blob_Data = GoogleDrive.download_BLOB(GoogleID)
            if queue:
                queue.put((Media.Blob_Data,None))
        except Exception as e:
            Media.Downloading = False
            if Media.TopLevel:
                Media.TopLevel.destroy()
            Controller.ROOT.after(WAIT,message_download_fail)
            if queue:
                queue.put((None, e))
            else:
                raise

    @staticmethod
    def lose_focus(event):
        Controller.ROOT.focus_set()
        Controller.Table_Pacijenti.selection_set('')
        Controller.Table_Slike.selection_set('')
        Controller.Table_MKB.selection_set('')
        Controller.Table_Zaposleni.selection_set('')
        Controller.Table_Logs.selection_set('')
        Controller.Table_Session.selection_set('')

    @staticmethod
    def is_DB_date(date_string): # Checks if it is RHMH Date Format
        try:
            datetime.strptime(str(date_string), '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
    @staticmethod
    def open_link(event=None, link=None, time=None):
        if time:
            new_link = f'{link}&t{time}s' # Otvara video na 42. sekundi ovo &t=42s
        # "https://www.https://www.youtube.com/@UV-Byzantine"  
        webbrowser.open_new(link)

    @staticmethod
    def open_email(event, email):
        webbrowser.open_new(f'mailto:{email}')
    