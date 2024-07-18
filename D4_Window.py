from A1_Variables import *
from A2_Decorators import spam_stopper,PC,print_dict
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import RHMH,LOGS
from B5_AI import AI
from C1_Controller import Controller,GodMode
from C2_ManageDB import ManageDB
from C3_SelectDB import SelectDB
from D1_TopPanel import TopPanel
from D2_FormPanel import FormPanel
from D3_MainPanel import MainPanel

class GUI:
    root:Tk = None
    menu:Menu = None

    title_visible:BooleanVar = None

    @staticmethod
    def initialize(root:Tk) -> None:
        GUI.root = root
        LOGS.start_LOGS_db()
        RHMH.start_RHMH_db()
        threading.Thread(target=GUI.get_PC_info).start()
        
        Controller.MKB_validation_LIST = [i[0] for i in RHMH.execute_select(False,'mkb10',*('MKB - šifra',))]
        Controller.Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select(False,'zaposleni',*('Zaposleni',))]
        
        Controller.ROOT = GUI.root
        TopPanel.initialize(GUI.root)
        FormPanel.initialize(GUI.root)
        MainPanel.initialize(GUI.root)
        GUI.Buttons_SpamStopper()

        
        GUI.menu = GUI.RootMenu_Create()
        if os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
            GUI.root.bind('<Button-2>', GUI.do_popup)
        else:
            GUI.root.bind('<Button-3>', GUI.do_popup)
        GUI.root.bind('<Button-3>', GUI.do_popup)
        GUI.root.bind('<Control-a>', SelectDB.selectall_tables)
        GUI.root.bind('<Command-a>', SelectDB.selectall_tables)
        GUI.root.bind('\u004D\u0055\u0056\u0031\u0033', GodMode.GodMode_Password)
        GUI.root.protocol('WM_DELETE_WINDOW',GUI.EXIT)
        
        GUI.root.title(app_name)
        if os.name == 'nt':  # Windows
            root.iconbitmap(IMAGES['icon'][0])
        elif os.name == 'posix':  # macOS i Linux
            icon = PhotoImage(file=IMAGES['icon'][1])
            root.iconphoto(True, icon)
        GUI.root.grid_rowconfigure(1, weight=1)
        GUI.root.grid_columnconfigure(1, weight=1)

        threading.Thread(target=Controller.starting_application).start()
        UserSession['Logged IN'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        starting = (time.time_ns()-TIME_START)/10**9
        UserSession['GUI']['Start'] = starting
        GUI.root.geometry(f'{WIDTH}x{HEIGHT}')

    @staticmethod
    def get_PC_info() -> None:
        cpu = PC.get_cpu_info()
        gpu = PC.get_gpu_info()
        ram = PC.get_ram_info()
        UserSession['PC']['CPU'] = cpu
        UserSession['PC']['GPU'] = gpu
        UserSession['PC']['RAM'] = ram
        AI.initialize()

    @staticmethod
    def Buttons_SpamStopper() -> None:
        for button in Controller.Buttons.values():
            if isinstance(button,tuple):
                continue
            if not isinstance(button,list):
                last_cmd = button.cget('command')
                button.configure(command=spam_stopper(button,GUI.root)(last_cmd))
            else:
                for filterbutton in button:
                    if isinstance(filterbutton,tb.Checkbutton):
                        continue
                    last_cmd = filterbutton.cget('command')
                    filterbutton.configure(command=spam_stopper(filterbutton,GUI.root)(last_cmd))

    @staticmethod
    def EXIT() -> None:
        response = Messagebox.show_question('Do you want to save the changes before exiting?', 'Close', buttons=['Exit:secondary','Save:success'])
        if response == 'Save':
            upload = Controller.uploading_to_GoogleDrive()
            try:
                Controller.uploading_LOGS()
            finally:
                if upload is True:
                    GUI.root.after(1500,GUI.root.destroy)
                else:
                    report = 'Uploading Failed\nConnection problems\nTry again or EXIT without Saving'
                    Messagebox.show_warning(parent=Controller.SearchBar,title='Upload',message=report)
        if response == 'Exit':
            try:
                Controller.uploading_LOGS()
            finally:
                GUI.root.destroy()

    @staticmethod
    def show_form_frame() -> None:
        if not FormPanel.Form_Frame.winfo_ismapped():
            FormPanel.Form_Frame.grid(row=1, column=0, padx=padding_6, pady=padding_0_6, sticky=NSEW)
            FormPanel.form_visible.set(True)
        else:
            FormPanel.Form_Frame.grid_forget()
            FormPanel.form_visible.set(False) 

    @staticmethod
    def show_title_frame() -> None:
        if not Controller.Top_Frame.winfo_ismapped():
            Controller.Top_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
            GUI.title_visible.set(True)
        else:
            Controller.Top_Frame.grid_forget()
            GUI.title_visible.set(False) 

    @staticmethod
    def do_popup(event) -> None:
        GUI.menu:Menu
        try: 
            GUI.menu.tk_popup(event.x_root, event.y_root) 
        finally: 
            GUI.menu.grab_release() 

    @staticmethod
    def RootMenu_Create() -> Menu:
        m = Menu(GUI.root, tearoff = 0) 
        GUI.title_visible = BooleanVar()
        GUI.title_visible.set(True)
        m.add_checkbutton(label='Show Title', variable=GUI.title_visible, command=GUI.show_title_frame)
        m.add_checkbutton(label='Show Form', variable=FormPanel.form_visible, command=GUI.show_form_frame)
        m.add_separator() 
        m.add_command(label ='Export Selection', command= lambda: ManageDB.export_table(tb.ttk.Treeview.selection))
        m.add_command(label ='Export Table', command= lambda: ManageDB.export_table(tb.ttk.Treeview.get_children))
        m.add_command(label ='Clear Form', command= Controller.Clear_Form)
        m.add_command(label ='Empty Table', command= SelectDB.empty_tables)
        m.add_separator()
        m.add_command(label ='Settings', command= lambda: SelectDB.NoteBook.select(6))
        m.add_command(label ='About', command= lambda: SelectDB.NoteBook.select(7))
        m.add_separator()
        m.add_command(label ='Upload to Drive', command= Controller.uploading_to_GoogleDrive)
        return m
    
if __name__=='__main__':
    pass