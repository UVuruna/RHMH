from A1_Variables import *
from B2_SQLite import RHMH

class Controller:
    Admin = False
    GodMode = False
    FreeQuery_Frame:   Frame = None
    FreeQuery:         StringVar = None

    NoteBook:          tb.Notebook = None
    Table_Pacijenti:   tb.ttk.Treeview = None
    Table_Slike:       tb.ttk.Treeview = None
    Table_MKB:         tb.ttk.Treeview = None
    Table_Zaposleni:   tb.ttk.Treeview = None
    Table_Logs:        tb.ttk.Treeview = None
    Table_Session:     tb.ttk.Treeview = None

    Table_Names = dict()
    
    Graph_Frame:       Frame = None
    About_Tab:         Frame = None
    Settings_Tab:      Frame = None
    
    TablePacijenti_Columns =   tuple(MainTablePacijenti.keys())
    Pacijenti_ColumnVars =     dict()

    TableSlike_Columns =       tuple()
    TableMKB_Columns =         tuple()
    TableZaposleni_Columns =   tuple()
    TableLogs_Columns =        tuple()
    TableSession_Columns =     tuple()
    
    SearchBar: Frame = None
    SearchBar_widgets = dict()
    SearchBar_number = 1
    SearchAdd_Button: tb.Label = None
    SearchRemove_Button: tb.Label = None
    
    ROOT:Tk = None

    buttons = {'Filter Patient':[]}
    Slike_HideTable: Frame = None

    MessageBoxParent: Frame = None
    PatientFocus_ID = None

    Validation_Widgets = {'Default':[], 'Alternative':[]}
    Valid_Default: bool = True
    Valid_Alternative: bool = True


    FormTitle = None
    PatientInfo = None
    MainTable_IDS = list()
    Patient_FormVariables = {'pacijent':{},'dijagnoza':{},'operacija':{},'slike':{}}
    Katalog_FormVariables =    dict()
    Logs_FormVariables =       dict()
    Graph_FormVariables =      dict()
    FilterOptions =            dict()

    MKB_validation_LIST = [i[0] for i in RHMH.execute_select('mkb10',*('MKB - šifra',))]
    Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select('zaposleni',*('Zaposleni',))]

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
        elif isinstance(widget, Text):
            widget.delete('1.0', END)
        elif isinstance(widget, widgets.DateEntry):
            widget.entry.delete(0,END)
        elif isinstance(widget, tb.Entry):
            widget.delete(0,END)
        elif isinstance(widget, tb.Treeview):
            for item in widget.get_children():
                widget.delete(item)
        elif isinstance(widget,tb.Label):
            widget.config(text='')

    @staticmethod
    def is_DB_date(date_string): # Checks if it is RHMH Date Format
        try:
            datetime.strptime(str(date_string), '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def get_widget_value(widget):
        if isinstance(widget, StringVar):
            return widget.get()
        elif isinstance(widget, Text):
            return widget.get('1.0', END).strip()
        elif isinstance(widget, widgets.DateEntry):
            return widget.entry.get()
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
