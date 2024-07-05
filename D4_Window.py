from A1_Variables import *
from A2_Decorators import method_efficency,spam_stopper,error_catcher
from B1_GoogleDrive import GoogleDrive
from B3_Media import Media
from B2_SQLite import Database,RHMH
from C1_DBMS import DBMS,Buttons
from D1_TopFrame import TopFrame
from D2_FormFrame import FormFrame
from D3_TabelFrame import TableFrame

class GUI:
    def __init__(self, root:Tk):
        self.GD = GoogleDrive()
        self.GD.download_File(RHMH_DB['id'],'RHMH.db')
        UserSession['User'] = self.GD.get_UserEmail()
        RHMH.start_RHMH_db()
        
        self.BUTT = Buttons()
        self.DBMS = DBMS()
        
        self.BUTT.ROOT = root
        
        # DECORATING
        #'''
        self.GoogleDrive_Decorating()
        self.Media_Decorating()
        self.Database_Decorating()
        self.Buttons_Decorating()
        self.DBMS_Decorating()
        #'''
        
        self.root = root
        self.root.title(app_name)
        self.root.geometry(f'{WIDTH}x{HEIGHT}')
        self.root.iconbitmap(IMAGES['icon'])
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.Title =    TopFrame(self.root)
        self.Form =     FormFrame(self.root)
        self.Window =   TableFrame(self.root)
        self.Buttons_SpamStopper()
        
        self.menu = self.RootMenu_Create()
        self.root.bind('<Button-3>', self.do_popup)
        self.root.bind('<Control-a>', self.BUTT.selectall_tables)
        self.root.bind('<Command-a>', self.BUTT.selectall_tables)
        self.root.bind('\u004D\u0055\u0056', self.DBMS.GodMode_Password)
        self.root.protocol('WM_DELETE_WINDOW',self.EXIT)

        print(f'Vreme za pokretanje programa: {(time.time_ns()-TIME_START)/10**9:.2f} s')

    def GoogleDrive_Decorating(self):
        for name, method in inspect.getmembers(GoogleDrive, predicate=inspect.isfunction):
            decorated_method = method_efficency()(error_catcher(RHMH)(method))
            setattr(self.GD, name, decorated_method.__get__(self.GD, type(self.GD)))

    def Media_Decorating(self):
        for name, method in inspect.getmembers(Media, predicate=inspect.isfunction):
            decorated_method = method_efficency()(error_catcher(RHMH)(method))
            setattr(Media, name, decorated_method)

    def Database_Decorating(self):
        for name, method in inspect.getmembers(Database, predicate=inspect.isfunction):
            decorated_method = method_efficency()(error_catcher(RHMH)(method)) 
            setattr(RHMH, name, decorated_method.__get__(RHMH, type(RHMH)))

    def Buttons_Decorating(self):
        for name, method in inspect.getmembers(Buttons, predicate=inspect.isfunction):
            decorated_method = method_efficency()(error_catcher(RHMH)(method))
            setattr(self.BUTT, name, decorated_method.__get__(self.BUTT, type(self.BUTT)))

    def DBMS_Decorating(self):
        for name, method in inspect.getmembers(DBMS, predicate=inspect.isfunction):
            decorated_method = method_efficency()(error_catcher(RHMH)(method))
            setattr(self.DBMS, name, decorated_method.__get__(self.DBMS, type(self.DBMS)))

    def Buttons_SpamStopper(self):
        for button in self.BUTT.buttons.values():
            if not isinstance(button,list):
                last_cmd = button.cget('command')
                button.configure(command=spam_stopper(button,self.root)(last_cmd))
            else:
                for filterbutton in button:
                    if isinstance(filterbutton,tb.Checkbutton):
                        continue
                    last_cmd = filterbutton.cget('command')
                    filterbutton.configure(command=spam_stopper(filterbutton,self.root)(last_cmd))

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
        m.add_command(label ='Export Selection', command=self.DBMS.export_selection)
        m.add_command(label ='Export Table', command=self.DBMS.export_table)
        m.add_separator() 
        m.add_command(label ='Settings', command= lambda: self.DBMS.NoteBook.select(6))
        m.add_command(label ='About', command= lambda: self.DBMS.NoteBook.select(7))
        return m