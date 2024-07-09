from A1_Variables import *
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import RHMH

class Controller:
    ROOT:Tk = None
    Connected:bool = False
    Buttons = {'Filter Patient':[]}
    MessageBoxParent: Frame = None
    
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

    Table_Pacijenti:   tb.ttk.Treeview  = None
    Pacijenti_ColumnVars                = dict()
    FilterOptions                       = dict()
    TablePacijenti_Columns              = tuple(MainTablePacijenti.keys())
    Patient_FormVariables               = {'pacijent':{},'dijagnoza':{},'operacija':{},'slike':{}}

    Table_Slike:       tb.ttk.Treeview  = None
    TableSlike_Columns: tuple           = None
    Slike_HideTable:    Frame           = None

    Table_MKB:         tb.ttk.Treeview  = None
    TableMKB_Columns:  tuple            = None
    Table_Zaposleni:   tb.ttk.Treeview  = None
    TableZaposleni_Columns: tuple       = None
    Katalog_FormVariables               = dict()

    Graph_Canvas: Frame = None
    Graph_FormVariables = dict()

    Table_Logs:        tb.ttk.Treeview  = None
    TableLogs_Columns: tuple            = None
    Logs_FormVariables                  = dict()
    Table_Session:     tb.ttk.Treeview  = None
    TableSession_Columns: tuple         = None

    About_Tab:      Frame = None
    Settings_Tab:   Frame = None

    Table_Names = dict()
    
    
        # SEARCH BAR
    SearchBar: Frame    = None
    SearchBar_widgets   = dict()
    SearchBar_number    = 1
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

    MKB_validation_LIST = [i[0] for i in RHMH.execute_select('mkb10',*('MKB - šifra',))]
    Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select('zaposleni',*('Zaposleni',))]

    @staticmethod
    def block_manageDB():
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if Controller.Connected is False:
                    report = 'You didnt download Database from Google Drive\n'
                    report += 'Offline mode can only View from Local Database\n'
                    report += 'Managing Database is forbidden in Offline mode\n'
                    report += f'Please Recconect if you want to "{func.__name__}"\n'
                    Messagebox.show_warning(parent=Controller.MessageBoxParent,
                        title=f'{func.__name__} failed!', message=report)
                else:
                    func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def starting_application():
        try:
            if Controller.Connected == False:
                email = GoogleDrive.get_UserEmail()
                GoogleDrive.download_DB(RHMH_DB['id'],'RHMH.db')

                Controller.Connected = True
                if Controller.Reconnect_window:
                    Controller.Top_Frame.delete(Controller.Reconnect_window)
                    Controller.Reconnect_window = None
                    Controller.ROOT.update()
                if email:
                    UserSession['User'] = email
        except Exception as e:
            width = Controller.Top_Frame.winfo_width()
            Controller.Top_Frame.create_window(width*0.93, 10, anchor=N, window=Controller.Reconnect_Button)

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
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['User'],
                                                'Query':query_type,'Full Query':loggingdata})
            Controller.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
            return
        if result:
            def execute():
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['User'],
                                                'Query':query_type,'Full Query':RHMH.LoggingQuery})
            Controller.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
        return result

if __name__=='__main__':
    pass