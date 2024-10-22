from A1_Variables import *
from B1_GoogleDrive import GoogleDrive
from B3_Media import Media
from B2_SQLite import RHMH,LOGS

class GodMode(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.password = None
        self.eye_image = None
        super().__init__(parent, title)

    def body(self, master):
        self.eye_image = Media.label_ImageLoad(IMAGES['Password'])
        lbl = tb.Label(master, image=self.eye_image)
        lbl.grid(row=0, column=0, padx=6, pady=6, sticky=NSEW)
        self.password_entry = tb.Entry(master, show='*')
        self.password_entry.grid(row=1, column=0, padx=13, pady=13)
        return self.password_entry

    def apply(self):
        self.password = self.password_entry.get()

    @staticmethod
    def money():
        message = '    MUVS\n'
        message += f'{(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).total_seconds()//13*13:,.0f} $\n'
        message += f'{(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).days//13*13:,.0f} Million $'
        return message
    
    @staticmethod
    def GodMode_Password(event):
        def download_logs():
            GoogleDrive.download_DB(LOGS_dict['id'],LOGS_dict['path'])

        dialog = GodMode(Controller.SearchBar, 'Privileges Unlocking...')
        if dialog.password=='63636':
            Controller.Admin = True
            info = 'New tabs:\n\t-Logs'
            title = 'Admin unlocked'
        elif dialog.password in ['C12-Si28-C13-Si28-C12','C12-Li3-C13-Li3-C12']:
            Controller.Admin = True
            Controller.GodMode = True
            Controller.FreeQuery_Frame.grid()
            info = 'New tabs:\n\t-Logs\n\t-Session\n'
            info += 'New button:\n\t-Free Query'
            info += f'\n\n{GodMode.money()}'
            title = 'God Mode unlocked'
            Controller.ROOT.after(WAIT, lambda: Controller.NoteBook.select(5))
        else:
            return
        
        threading.Thread(target=download_logs).start()
        Controller.ROOT.after(WAIT*2, lambda: Controller.NoteBook.select(4))
        Messagebox.show_info(parent=Controller.SearchBar, message=info, title=title)

class Controller:
    ROOT:Tk = None
    Connected:bool = False
    DEFAULT:dict = None
    Buttons = {'Filter Patient':[]}
    
        # ADMIN
    Admin: bool             = False
    GodMode: bool           = False
    FreeQuery_Frame: Frame  = None
    FreeQuery: StringVar    = None

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

    FormTitle = None
    PatientInfo = None
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
                    Messagebox.show_warning(parent=Controller.SearchBar,
                        title=f'{func.__name__} failed!', message=report)
                else:
                    func(*args, **kwargs)
            return wrapper
        return decorator

    def message_download_fail():
        Messagebox.show_error(parent=Controller.SearchBar,title='Downloading failed',message='Can`t connect to Google Drive')

    @staticmethod
    def get_image_fromGD(GoogleID,queue=None):
        try:
            Media.Downloading = True
            Media.Blob_Data = GoogleDrive.download_BLOB(GoogleID)
            if queue:
                queue.put((Media.Blob_Data,None))
        except Exception as e:
            Media.Downloading = False
            if Media.TopLevel:
                Media.TopLevel.destroy()
            Controller.ROOT.after(WAIT,Controller.message_download_fail)
            if queue:
                queue.put((None, e))
            else:
                raise

    @staticmethod
    def starting_application():
        def message_success():
            report = 'Connection successfull\nOnline mode'
            Messagebox.show_info(parent=Controller.SearchBar,title='Connect',message=report)
        def message_fail():
                report = 'Connection failed\nOffline mode'
                Messagebox.show_error(parent=Controller.SearchBar,title='Connect',message=report)
        def update_message():
            report = 'Please Download latest version from Google Drive\n' + \
                'Unzip files and copy them into directory of RHMH app'
            download = Messagebox.show_question(parent=Controller.SearchBar,
                title='New Version', message=report, buttons=['Skip:warning','Download:success'])
            if download == 'Download':
                Controller.open_link(link=r'https://drive.google.com/drive/folders/1yvDczxK01aBO3xdm-Vlkr38hP8DGD2g0')

        try:
            GoogleDrive.setup_connection()
            if Controller.Connected == False:
                email = GoogleDrive.get_UserEmail()
                GoogleDrive.download_DB(RHMH_dict['id'],RHMH_dict['path'])
                GoogleDrive.download_DB(SETTINGS_dict['id'],SETTINGS_dict['path'])
                with open(os.path.join(directory,'Default.json'), 'r') as file:
                    Controller.DEFAULT = json.load(file)

                if SETTINGS['Version'] != Controller.DEFAULT['Version']:
                    Controller.ROOT.after(WAIT,update_message) # Message
                    
                Controller.Connected = True
                if Controller.Reconnect_window:
                    Controller.Top_Frame.delete(Controller.Reconnect_window)
                    Controller.Reconnect_window = None
                    Controller.ROOT.update()
                if email:
                    UserSession['Email'] = email
                Controller.ROOT.after(WAIT*2,message_success) # Message
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            Controller.ROOT.after(WAIT*2,message_fail) # Message
            width = Controller.Top_Frame.winfo_width()
            Controller.Top_Frame.create_window(width*0.93, 10, anchor=N, window=Controller.Reconnect_Button)

    @staticmethod
    def open_link(event=None, link=None, time=None):
        if time:
            new_link = f'{link}&t{time}s' # Otvara video na 42. sekundi ovo &t=42s
        # "https://www.https://www.youtube.com/@UV-Byzantine"  
        webbrowser.open_new(link)

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
        json_data = json.dumps(SETTINGS, indent=4)
        with open(os.path.join(directory,'Settings.json'), 'w') as file:
            file.write(json_data)

    @staticmethod
    def restore_default_settings() -> None:
        for k,v in Controller.DEFAULT.items():
            if k=='Version':
                continue
            SETTINGS[k] = v
        for col,val in SETTINGS.items():
            if col=='Version':
                continue
            if not isinstance(val,dict):
                Controller.Settings_FormVariables[col].set(val)
            else:
                for column,value in val.items():
                    try:
                        Controller.Settings_FormVariables[col][column].set(value)
                    except AttributeError:
                        Controller.Settings_FormVariables[col][column].amountusedvar.set(value)
                    except KeyError:
                        continue

    @staticmethod
    def uploading_to_GoogleDrive() -> None:
        def message_success():
            Messagebox.show_info(parent=Controller.SearchBar,title='Upload',message='Upload Database successfull')
        def message_fail():
            Messagebox.show_error(parent=Controller.SearchBar,title='Upload',message='Upload Database failed')

        rhmh = GoogleDrive.upload_UpdateFile(RHMH_dict['id'],RHMH_dict['path'],RHMH_dict['mime'])

        if rhmh:
            Controller.ROOT.after(WAIT,message_success)  # Message
            return True
        else:
            Controller.ROOT.after(WAIT,message_fail)  # Message
            return False

    @staticmethod
    def uploading_LOGS():
        Messagebox.show_info(parent=Controller.SearchBar,title='Upload',message='Ne radi ti upload')
        time.sleep(1)
        return
        email = UserSession['Email']
        logged_in = UserSession['Logged IN']
        logged_out = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        dt1 = datetime.strptime(logged_in, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(logged_out, "%Y-%m-%d %H:%M:%S")
        session = dt1 - dt2
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
            driveID = GoogleDrive.upload_NewFile_asFile(file_name=filename, GoogleDrive_folder=GD_MAIN,
                                          file_path=LOGS_dict['path'], mime_type=LOGS_dict['mime'])
            if driveID:
                LOGS.connect()
                LOGS.cursor.execute('DELETE FROM logs')
                LOGS.cursor.execute('DELETE FROM session')
                LOGS.connection.commit()
                LOGS.close_connection()
                LOGS.Vaccum_DB()

    @staticmethod
    def lose_focus(event):
        event.widget.focus()
        Controller.Table_Pacijenti.selection_set('')
        Controller.Table_Slike.selection_set('')
        Controller.Table_MKB.selection_set('')
        Controller.Table_Zaposleni.selection_set('')
        Controller.Table_Logs.selection_set('')
        Controller.Table_Session.selection_set('')

    @staticmethod
    def Clear_Form():
        Controller.PatientFocus_ID = None
        Controller.FormTitle[0].configure(bootstyle=Controller.FormTitle[1])
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
    def is_DB_date(date_string): # Checks if it is RHMH Date Format
        try:
            datetime.strptime(str(date_string), '%Y-%m-%d')
            return True
        except ValueError:
            return False

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
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['Email'],
                                                'Query':query_type,'Full Query':loggingdata})
            Controller.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
            return
        if result:
            def execute():
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['Email'],
                                                'Query':query_type,'Full Query':LOGS.LoggingQuery})
            Controller.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
        return result

if __name__=='__main__':
    pass