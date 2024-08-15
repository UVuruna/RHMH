from A1_Variables import *
from A2_Decorators import spam_stopper,PC
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
    root:tb.Window = None
    menu:Menu = None
    title_visible:BooleanVar = None

    @staticmethod
    def initialize(root:tb.Window) -> None:
        App.ROOT = root
        LOGS.start_LOGS_db()
        RHMH.start_RHMH_db()

        threading.Thread(target=Controller.load_loading_GIF).start()
        App.ROOT.after(WAIT,Controller.process_queue)
        threading.Thread(target=GUI.get_PC_info).start()
        threading.Thread(target=Controller.starting_application).start()
        
        Controller.MKB_validation_LIST = [i[0] for i in RHMH.execute_select(False,'mkb10',*('MKB - šifra',))]
        Controller.Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select(False,'zaposleni',*('Zaposleni',))]
        
        TopPanel.initializeTP(App.ROOT)
        FormPanel.initializeFP(App.ROOT)
        MainPanel.initializeMP(App.ROOT)
        App.ROOT.after(WAIT,App.ROOT.place_window_center)
        GUI.Buttons_SpamStopper()
        
        GUI.menu = GUI.RootMenu_Create()
        if os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
            App.ROOT.bind('<Button-2>', GUI.do_popup)
            App.ROOT.bind('<Command-a>', SelectDB.selectall_tables)
            App.ROOT.bind('<Command-s>', lambda event: Controller.Upload_RHMH())
        else:
            App.ROOT.bind('<Button-3>', GUI.do_popup)
            App.ROOT.bind('<Control-a>', SelectDB.selectall_tables)
            App.ROOT.bind('<Control-s>', lambda event: Controller.Upload_RHMH())

        App.ROOT.bind('<Return>', lambda event: GUI.show_bind(event,True))
        App.ROOT.bind('<space>', lambda event: GUI.show_bind(event,False))
        App.ROOT.bind('\u004D\u0055\u0056\u0031\u0033', GodMode.GodMode_Password)
        App.ROOT.protocol('WM_DELETE_WINDOW',GUI.EXIT)
        
        App.ROOT.title(app_name)
        if os.name == 'nt':  # Windows
            root.iconbitmap(IMAGES['icon']['RHMH']['ico'])
        elif os.name == 'posix':  # macOS i Linux
            icon = PhotoImage(file=IMAGES['icon']['RHMH']['png'])
            root.iconphoto(True, icon)
        App.ROOT.grid_rowconfigure(1, weight=1)
        App.ROOT.grid_columnconfigure(1, weight=1)
        App.ROOT.deiconify()

    @staticmethod
    def show_bind(event,showall):
        focus = App.ROOT.focus_get()
        if not (isinstance(focus, tb.Text) or \
                    isinstance(focus, tb.Entry) or \
                            isinstance(focus,widgets.DateEntry)):
            if showall is True:
                SelectDB.showall_data()
            else:
                SelectDB.search_data()

    @staticmethod
    def get_PC_info() -> None:
        cpu = PC.get_cpu_info()
        gpu = PC.get_gpu_info()
        ram = PC.get_ram_info()
        pc = platform.uname()

        UserSession['PC']['User'] = {'User': pc.node,
                                     'OS': f'{pc.system} {pc.release}', 
                                     'Version': pc.version}
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
                button.configure(command=spam_stopper(button,App.ROOT)(last_cmd))
            else:
                for filterbutton in button:
                    if isinstance(filterbutton,tb.Checkbutton):
                        continue
                    last_cmd = filterbutton.cget('command')
                    filterbutton.configure(command=spam_stopper(filterbutton,App.ROOT)(last_cmd))

    @staticmethod
    def EXIT() -> None:
        response = Messagebox.show_question('Do you want to save the changes before exiting?', 'Close', buttons=['Exit:secondary','Save:success'],
                                            position=App.get_window_center())
        if response == 'Save':
            upload = Controller.Upload_RHMH()
            try:
                Controller.Upload_local_LOGS()
            finally:
                if upload is True:
                    App.ROOT.destroy()
                else:
                    report = 'Uploading Failed\nConnection problems\nTry again or EXIT without Saving'
                    Messagebox.show_warning(title='Upload',message=report,
                                            position=App.get_window_center())
        if response == 'Exit':
            try:
                Controller.Upload_local_LOGS()
            finally:
                App.ROOT.destroy()

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
        m = Menu(App.ROOT, tearoff = 0) 
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
        m.add_command(label ='New User Authorization', command= Controller.create_new_user)
        m.add_command(label ='Upload to Drive', command= Controller.Upload_RHMH)
        return m
    
if __name__=='__main__':
    pass