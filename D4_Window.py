from A1_Variables import *
from A2_Decorators import spam_stopper
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import RHMH
from C1_Controller import Controller
from C2_ManageDB import ManageDB
from C3_SelectDB import SelectDB
from D1_TopFrame import TopPanel
from D2_FormFrame import FormPanel
from D3_TabelFrame import MainPanel

class GUI:
    root:Tk = None
    menu:Menu = None

    title_visible:BooleanVar = None

    def load_GUIapp(root:Tk):
        print(f'Vreme do LOAD GUI: {(time.time_ns()-TIME_START)/10**9:.2f} s')

        Controller.ROOT = root
        connected = GoogleDrive.connect()
        print(f"Connected = {connected}")

        #GoogleDrive.download_File(RHMH_DB['id'],'RHMH.db')
        UserSession['User'] = GoogleDrive.get_UserEmail()

        RHMH.start_RHMH_db()

        GUI.root = root
        GUI.root.title(app_name)
        GUI.root.geometry(f'{WIDTH}x{HEIGHT}')
        GUI.root.iconbitmap(IMAGES['icon'])
        GUI.root.grid_rowconfigure(1, weight=1)
        GUI.root.grid_columnconfigure(1, weight=1)

        TopPanel.load_TopFrame(GUI.root)
        FormPanel.load_FormFrame(GUI.root)
        MainPanel.load_MainPanel(GUI.root)
        GUI.Buttons_SpamStopper()
        
        GUI.menu = GUI.RootMenu_Create()
        GUI.root.bind('<Button-3>', GUI.do_popup)
        GUI.root.bind('<Control-a>', ManageDB.selectall_tables)
        GUI.root.bind('<Command-a>', ManageDB.selectall_tables)
        GUI.root.bind('\u004D\u0055\u0056', SelectDB.GodMode_Password)
        GUI.root.protocol('WM_DELETE_WINDOW',GUI.EXIT)

        print(f'Ukupno Vreme za pokretanje programa: {(time.time_ns()-TIME_START)/10**9:.2f} s')

    def Buttons_SpamStopper():
        for button in Controller.buttons.values():
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

    def EXIT():
        response = Messagebox.show_question('Do you want to save the changes before exiting?', 'Close', buttons=['Exit:secondary','Save:success'])
        if response == 'Save':
            threading.Thread(target=GUI.uploading_to_GoogleDrive).start()
            GUI.root.destroy()
        if response == 'Exit':
            GUI.root.destroy()
    
    def uploading_to_GoogleDrive():
        print('Uploading to Google Drive...')
        #GoogleDrive.upload_UpdateFile(RHMH_DB['id'],'RHMH.db',RHMH_DB['mime'])
        print('Upload finished')

    def show_form_frame():
        if not FormPanel.Form_Frame.winfo_ismapped():
            FormPanel.Form_Frame.grid(row=1, column=0, padx=shape_padding[0], pady=shape_padding[1], sticky=NSEW)
            FormPanel.form_visible.set(True)
        else:
            FormPanel.Form_Frame.grid_forget()
            FormPanel.form_visible.set(False) 

    def show_title_frame():
        if not TopPanel.Top_Frame.winfo_ismapped():
            TopPanel.Top_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)
            GUI.title_visible.set(True)
        else:
            TopPanel.Top_Frame.grid_forget()
            GUI.title_visible.set(False) 

    def do_popup(event):
        GUI.menu:Menu
        try: 
            GUI.menu.tk_popup(event.x_root, event.y_root) 
        finally: 
            GUI.menu.grab_release() 

    def RootMenu_Create():
        m = Menu(GUI.root, tearoff = 0) 
        GUI.title_visible = BooleanVar()
        GUI.title_visible.set(True)
        m.add_checkbutton(label='Show Title', variable=GUI.title_visible, command=GUI.show_title_frame)
        m.add_checkbutton(label='Show Form', variable=FormPanel.form_visible, command=GUI.show_form_frame)
        m.add_separator() 
        m.add_command(label ='Export Selection', command= lambda: SelectDB.export_table(tb.ttk.Treeview.selection))
        m.add_command(label ='Export Table', command= lambda: SelectDB.export_table(tb.ttk.Treeview.get_children))
        m.add_separator() 
        m.add_command(label ='Settings', command= lambda: SelectDB.NoteBook.select(6))
        m.add_command(label ='About', command= lambda: SelectDB.NoteBook.select(7))
        return m