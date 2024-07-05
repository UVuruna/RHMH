from A1_Variables import *
from A2_Decorators import Singleton,PasswordDialog,money
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import RHMH
from B3_Media import Media

class Buttons(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            Buttons._initialized=True

            self.ROOT:Tk = None
            self.GD = GoogleDrive()
            self.DBMS = DBMS()

            self.buttons = {'Filter Patient':[]}
            self.Slike_HideTable: Frame = None

            self.MessageBoxParent: Frame = None
            self.PatientFocus_ID = None

            self.Validation_Widgets = {'Default':[], 'Alternative':[]}
            self.Valid_Default: bool = True
            self.Valid_Alternative: bool = True


            self.FormTitle = None
            self.PatientInfo = None
            self.Patient_FormVariables = {'pacijent':{},'dijagnoza':{},'operacija':{},'slike':{}}
            self.Katalog_FormVariables =    dict()
            self.Logs_FormVariables =       dict()
            self.Graph_FormVariables =      dict()
            self.FilterOptions =            dict()
            self.MKB_validation_LIST = [i[0] for i in RHMH.execute_select('mkb10',*('MKB - šifra',))]
            self.Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select('zaposleni',*('Zaposleni',))]
    
    def is_DB_date(self,date_string): # Checks if it is RHMH Date Format
        try:
            datetime.strptime(str(date_string), '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def empty_widget(self,widget):
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

    def get_widget_value(self,widget):
        if isinstance(widget, StringVar):
            return widget.get()
        elif isinstance(widget, Text):
            return widget.get('1.0', END).strip()
        elif isinstance(widget, widgets.DateEntry):
            return widget.entry.get()
        else:
            return None
        
    def set_widget_value(self,widget,value):
        if not value:
            return
        if self.is_DB_date(value):
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

    def Clear_Form(self):
        self.PatientFocus_ID = None
        self.FormTitle[0].configure(bootstyle=self.FormTitle[1])
        self.PatientInfo.config(text='\n')
        for table_groups in self.Patient_FormVariables.values():
            for widget in table_groups.values():
                self.empty_widget(widget)
    
    def empty_tables(self):
        focus = self.DBMS.NoteBook.index(self.DBMS.NoteBook.select())
        TAB = self.DBMS.NoteBook.tab(focus,'text')
        if TAB == 'Pacijenti':
            for item in self.DBMS.Table_Pacijenti.get_children():
                self.DBMS.Table_Pacijenti.delete(item)
        elif TAB == 'Slike':
            for item in self.DBMS.Table_Slike.get_children():
                self.DBMS.Table_Slike.delete(item)
        elif TAB == 'Katalog':
            for item in self.DBMS.Table_MKB.get_children():
                self.DBMS.Table_MKB.delete(item)
        elif TAB == 'Logs':
            for item in self.DBMS.Table_Logs.get_children():
                self.DBMS.Table_Logs.delete(item)
        elif TAB == 'Session':
            for item in self.DBMS.Table_Session.get_children():
                self.DBMS.Table_Session.delete(item)

    def refresh_tables(self,table_names:list):
        for table in table_names:
            self.DBMS.showall_data(TAB=table)

    def selectall_tables(self,event):
        if event.state == 8:
            return
        focus = self.DBMS.NoteBook.index(self.DBMS.NoteBook.select())
        TAB = self.DBMS.NoteBook.tab(focus,'text')
        if TAB == 'Pacijenti':
            items = self.DBMS.Table_Pacijenti.get_children()
            self.DBMS.Table_Pacijenti.selection_set(items)
        elif TAB == 'Slike':
            items = self.DBMS.Table_Slike.get_children()
            self.DBMS.Table_Slike.selection_set(items)
        elif TAB == 'Katalog':
            items = self.DBMS.Table_MKB.get_children()
            self.DBMS.Table_MKB.selection_set(items)
        elif TAB == 'Logs':
            items = self.DBMS.Table_Logs.get_children()
            self.DBMS.Table_Logs.selection_set(items)
        elif TAB == 'Session':
            items = self.DBMS.Table_Session.get_children()
            self.DBMS.Table_Session.selection_set(items)

    def shift_up(self, event):
        table: tb.ttk.Treeview = event.widget
        current = table.focus()
        if current:
            previous = table.prev(current)
            if previous:
                if previous not in table.selection():
                    table.selection_add(previous)
                    table.focus(previous)
                    table.see(previous)
                else:
                    table.selection_remove(current)
                    table.focus(previous)
                    table.see(previous)
        return 'break'
    
    def shift_down(self, event):
        table: tb.ttk.Treeview = event.widget
        current = table.focus()
        if current:
            next_item = table.next(current)
            if next_item:
                if next_item not in table.selection():
                    table.selection_add(next_item)
                    table.focus(next_item)
                    table.see(next_item)
                else:
                    table.selection_remove(current)
                    table.focus(next_item)
                    table.see(next_item)
        return 'break'

    def lose_focus(self,event):
        event.widget.focus()
        self.DBMS.Table_Pacijenti.selection_set('')
        self.DBMS.Table_Slike.selection_set('')
        self.DBMS.Table_MKB.selection_set('')
        self.DBMS.Table_Zaposleni.selection_set('')
        self.DBMS.Table_Logs.selection_set('')
        self.DBMS.Table_Session.selection_set('')

    def Add_Patient(self):
        if not (self.Valid_Default and self.Valid_Alternative):
            Messagebox.show_warning(parent=self.MessageBoxParent,
                    title=f'Inserting failed!', message='Wrong data in Patient Form')
            return
        reportDict = {}
        for table in self.Patient_FormVariables.keys():
            insertDict = {}
            if table=='pacijent':
                trenutna_godina = datetime.now().year
                for col,widget in self.Patient_FormVariables[table].items():
                    value = self.get_widget_value(widget)
                    if value:
                        if 'Datum' in col: # FROM Form Date Format TO RHMH Date Format
                            value = datetime.strptime(value, '%d-%b-%Y').strftime('%Y-%m-%d')
                            if col=='Datum Prijema':
                                trenutna_godina = datetime.strptime(value, '%Y-%m-%d').year
                        elif col=='Godište':
                            godiste = int(value)
                        insertDict[col] = value
                        reportDict[col] = value
                insertDict['Starost'] = trenutna_godina-godiste
                ID = RHMH.execute_Insert(table,**insertDict)
            elif table == 'dijagnoza':
                for col,widget in self.Patient_FormVariables[table].items():
                    value = self.get_widget_value(widget)
                    if value:
                        value = value.replace(',',' ')
                        value = value.split()
                        for mkb in value:
                            insertDict.clear()
                            insertDict['id_pacijent'] = ID
                            insertDict['id_dijagnoza'] = RHMH.execute_selectquery(f'SELECT id_dijagnoza FROM mkb10 WHERE `MKB - šifra` = "{mkb}"')[0][0]
                            insertDict['id_kategorija'] = RHMH.execute_selectquery(f'SELECT id_kategorija FROM kategorija WHERE Kategorija = "{col}"')[0][0]
                            RHMH.execute_Insert(table,**insertDict)
                        reportDict[col] = value
            elif table=='operacija':
                for col,widget in self.Patient_FormVariables[table].items():
                    value = self.get_widget_value(widget)
                    if value:
                        if ',' in value:
                            value = value.split(',')
                            names = []
                            for doc in value:
                                names.append(doc.strip())
                        else:
                            names = [value]
                        for name in names:
                            insertDict['id_pacijent'] = ID
                            insertDict['id_zaposleni'] = RHMH.execute_selectquery(f'SELECT id_zaposleni FROM zaposleni WHERE Zaposleni = "{name}"')[0][0]
                            insertDict['id_funkcija'] = RHMH.execute_selectquery(f'SELECT id_funkcija FROM funkcija WHERE Funkcija = "{col}"')[0][0]
                            RHMH.execute_Insert(table,**insertDict)
                        reportDict[col] = value
        report = ''
        ime = ''
        logging = ''
        for col,val in reportDict.items():
            if col in ['Ime','Prezime']:
                ime += f'{val} '
                continue
            if isinstance(val,list):
                VAL = ',\n'.join(val)
                val = ' , '.join(val)
            else:
                VAL = val
            report += f' - {col}: {val}\n'
            logging += f'\n - {col}:\n{VAL}\n'

        Messagebox.show_info(parent=self.MessageBoxParent,
                title=f'New Patient added', message=f'{ime}\n\n{report[:-1]}')
        
        self.DBMS.LoggingData(query_type='Add Patient',loggingdata=f'{ime}\n\n{logging[:-1]}')
        self.refresh_tables(table_names=['Pacijenti','Slike'])

    def Add_Image(self):
        def open_file_dialog():
            file_types = [  ('PNG files', '*.png'),
                            ('JPG files', '*.jpg'),
                            ('JPEG files', '*.jpeg'),
                            ('HEIF files', '*.heif'),
                            ('HEIC files', '*.heic'),
                            ('MP4 files', '*.mp4'),
                            ('MOV files', '*.mov'),
                            ('All files', '*.*')    ]
            file_path = filedialog.askopenfilename(
                title='Select Media file',
                initialdir='/',  # Početni direktorijum
                filetypes=file_types)
            return file_path
        
        file_path = open_file_dialog()
        print(file_path)
        self.refresh_tables(['Slike']) # plus vratiti panel sa tabelom i slikom
        print(UserSession)

    def Add_MKB(self):
        mkb = self.get_widget_value(self.Katalog_FormVariables['MKB - šifra'])
        opis = self.get_widget_value(self.Katalog_FormVariables['Opis Dijagnoze'])

        if mkb and opis:
            RHMH.execute_Insert('mkb10',**{'MKB - šifra':mkb,'Opis Dijagnoze':opis})
            report = ''
            for col,val in {'MKB - šifra':mkb,'Opis Dijagnoze':opis}.items():
                report += f' - {col}:\n{val}\n\n'

            Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f'New MKB added', message=report[:-1], alert=True)
            
            self.DBMS.LoggingData(query_type='Add MKB',loggingdata=report[:-1])
            self.refresh_tables(['Katalog'])
        else:
            Messagebox.show_warning(parent=self.MessageBoxParent,
                    title=f'Inserting failed!', message='You didn`t fill the form')
    
    def Add_Zaposleni(self):
        name = self.get_widget_value(self.Katalog_FormVariables['Zaposleni'])
        if name:
            RHMH.execute_Insert('zaposleni',**{'Zaposleni':name})
            report = f' - Ime:\n{name}'

            Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f'New Employee added', message=report, alert=True)
            
            self.DBMS.LoggingData(query_type='Add Employee',loggingdata=report)
            self.refresh_tables(['Katalog'])
        else:
            Messagebox.show_warning(parent=self.MessageBoxParent,
                    title=f'Inserting failed!', message='You didn`t enter Name of Employee')

    def Update_Patient(self):
        if not (self.Valid_Default and self.Valid_Alternative):
            report = 'You have entered incorrect data'
            Messagebox.show_error(parent=self.MessageBoxParent,
                    title='Updating failed!', message=report)
            return
        if self.PatientFocus_ID:    
            patient = RHMH.get_patient_data(self.PatientFocus_ID)
            update_Dict = {}
            insert_Dict = {}
            delete_Dict = {}

            report_Dict = {}

            PATIENT = f'{patient['Ime']} {patient['Prezime']}'
            try:
                # FROM RHMH Date Formate TO Patient Report Date Format
                datumprijema = f' ({datetime.strptime(str(patient['Datum Prijema']),'%Y-%m-%d').strftime('%d-%b-%y')})'
                PATIENT += datumprijema
            except KeyError:
                pass
                            
            for table,tabledict in self.Patient_FormVariables.items(): # {'pacijent':{},'dijagnoza':{},'operacija':{},'slike':{}}
                if table == 'slike':
                    continue
                if table != 'pacijent':
                    insert_Dict[table] = {}
                    delete_Dict[table] = {}
                for col,widget in tabledict.items():
                    try:
                        OLD = str(patient[col])
                        if table=='pacijent' and 'Datum' in col:
                            # FROM RHMH Date Format TO Form Date Format
                            OLD = datetime.strptime(OLD,'%Y-%m-%d').strftime('%d-%b-%Y')
                    except KeyError:
                        OLD = ''
                    NEW = str(self.get_widget_value(widget))

                    NEW = ' '.join(NEW.split()) # da se srede visak razmaka
                    OLD = ' '.join(OLD.split()) # mora str zbog int values
                    NEW = ' , '.join([i.strip() for i in NEW.split(',')]) # da se srede visak razmaka
                    OLD = ' , '.join([i.strip() for i in OLD.split(',')]) # mora str zbog int values
                    if NEW!=OLD:
                        report_Dict[col] = {'New':NEW,'Old':OLD}
                        if table in ['dijagnoza','operacija']:
                            oldlist = OLD.split(' , ')
                            newlist = NEW.split(' , ')
                            INSERT = set(newlist)-set(oldlist) ; INSERT.remove('') if '' in INSERT else None
                            DELETE = set(oldlist)-set(newlist) ; DELETE.remove('') if '' in DELETE else None
                            if DELETE:
                                delete_Dict[table][col] = DELETE
                            if INSERT:
                                insert_Dict[table][col] = INSERT
                        else: # Table pacijent
                            if 'Datum' in col:
                                # FROM Form Date Format TO RHMH Date Format
                                NEW = datetime.strptime(NEW,'%d-%b-%Y').strftime('%Y-%m-%d')
                            update_Dict[col] = NEW

            if report_Dict:
                logging = f'\n{PATIENT}\n\n'
                report = f'\n{PATIENT}\n\n'
                for k,v in report_Dict.items():
                    report += f' - {k}: {v['New']}\n'

                    if ',' in v:
                        v = ',\n'.join(v.split(' , '))
                    logging += f'\n - {k} (new):\n{v['New']}\n'
                    if v['Old']:
                        logging += f'\n - {k} (old):\n{v['Old']}\n'
                else:
                    reportquestion = 'Do You Want to Process Update?'
                    confirmation = Messagebox.yesno(parent=self.MessageBoxParent,
                            title=f'Patient Updating...', message=reportquestion+report[:-1], alert=True)
            else:
                report = 'You made no changes to current patient'
        else:
            report = 'You didn`t select Patient'

        try:
            if confirmation=='Yes':
                if update_Dict:
                    RHMH.execute_Update('pacijent',('id_pacijent',self.PatientFocus_ID),**update_Dict)
                for table,insertdict in insert_Dict.items():
                    if not insertdict:
                        continue
                    for column,setvalues in insertdict.items():
                        if table == 'dijagnoza':
                            idkategorija = RHMH.execute_selectquery(f'SELECT id_kategorija FROM kategorija WHERE Kategorija = "{column}"')[0][0]
                            for value in setvalues: 
                                iddijagnoza = RHMH.execute_selectquery(f'SELECT id_dijagnoza from mkb10 WHERE `MKB - šifra` = "{value}"')[0][0]
                                inserting = {'id_dijagnoza': iddijagnoza, 'id_pacijent': self.PatientFocus_ID, 'id_kategorija': idkategorija }
                                RHMH.execute_Insert('dijagnoza',**inserting)
                        elif table == 'operacija':
                            idfunkcija = RHMH.execute_selectquery(f'SELECT id_funkcija FROM funkcija WHERE Funkcija = "{column}"')[0][0]
                            for value in setvalues:
                                idzaposleni = RHMH.execute_selectquery(f'SELECT id_zaposleni FROM zaposleni WHERE Zaposleni = "{value}"')[0][0]
                                inserting = {'id_zaposleni': idzaposleni, 'id_pacijent': self.PatientFocus_ID, 'id_funkcija': idfunkcija }
                                RHMH.execute_Insert('operacija',**inserting)
                for table,deletedict in delete_Dict.items():
                    if not deletedict:
                        continue
                    for column,setvalues in deletedict.items():
                        if table == 'dijagnoza':
                            idkategorija = RHMH.execute_selectquery(f'SELECT id_kategorija FROM kategorija WHERE Kategorija = "{column}"')[0][0]
                            for value in setvalues:
                                iddijagnoza = RHMH.execute_selectquery(f'SELECT id_dijagnoza FROM mkb10 WHERE `MKB - šifra` = "{value}"')[0][0]
                                deleting = [('id_dijagnoza', iddijagnoza), ('id_pacijent', self.PatientFocus_ID), ('id_kategorija', idkategorija)]
                                RHMH.execute_Delete('dijagnoza',deleting)
                        elif table == 'operacija':
                            idfunkcija = RHMH.execute_selectquery(f'SELECT id_funkcija FROM funkcija WHERE Funkcija = "{column}"')[0][0]
                            for value in setvalues:
                                idzaposleni = RHMH.execute_selectquery(f'SELECT id_zaposleni FROM zaposleni WHERE Zaposleni = "{value}"')[0][0]
                                deleting = [('id_zaposleni', idzaposleni), ('id_pacijent', self.PatientFocus_ID), ('id_funkcija', idfunkcija)]
                                RHMH.execute_Delete('operacija',deleting)

                Messagebox.show_info(parent=self.MessageBoxParent,
                        title=f'Updating successfull', message=PATIENT)
                
                self.DBMS.LoggingData(query_type='Update Patient',loggingdata=logging)
                self.refresh_tables(table_names=['Pacijenti','Slike'])

        except UnboundLocalError:
            Messagebox.show_error(parent=self.MessageBoxParent,
                    title='Update failed!', message=report)
    
    def Edit_Image(self):
        pass

    def Update_MKB(self):
        mkb = self.get_widget_value(self.Katalog_FormVariables['MKB - šifra'])
        opis = self.get_widget_value(self.Katalog_FormVariables['Opis Dijagnoze'])

        try:
            selected_mkb = self.DBMS.Table_MKB.item(self.DBMS.Table_MKB.focus())['values'][1]
            selected_opis = self.DBMS.Table_MKB.item(self.DBMS.Table_MKB.focus())['values'][2]
            if selected_mkb:
                if mkb and opis:
                    report = ''

                    report += f' - MKB (new):\n{mkb}\n'
                    if mkb != selected_mkb:
                        report += f' - MKB (old):\n{selected_mkb}\n'
                    report += f'\n - Opis (new):\n{opis}\n'
                    if opis != selected_opis:
                        report += f' - Opis (old):\n{selected_opis}\n'

                    if report:
                        ID = RHMH.execute_selectquery(f'SELECT id_dijagnoza from mkb10 WHERE `MKB - šifra` = "{selected_mkb}"')[0][0]
                        reportquestion = 'Do you want to process update?\n\n'
                        confirmation = Messagebox.yesno(parent=self.MessageBoxParent,
                                title=f'MKB Updating...', message=reportquestion+report[:-1], alert=True)
                        if confirmation == 'Yes':
                            RHMH.execute_Update(table='mkb10', id=('id_dijagnoza',ID), **{'MKB - šifra':mkb,'Opis Dijagnoze':opis})

                            Messagebox.show_info(parent=self.MessageBoxParent,
                                    title=f'Updating successfull', message=report[:-1])
                            
                            self.DBMS.LoggingData(query_type='Update MKB',loggingdata=report[:-1])
                            self.refresh_tables(table_names=['Katalog'])
                        return
                    else:
                        report = 'You made no changes'
                else:
                    report = 'You didn`t enter required data'
        except IndexError:
            report = 'You didn`t select MKB you want to update'
        Messagebox.show_warning(parent=self.MessageBoxParent,
                title=f'Updating failed!', message=report)
            
    def Update_Zaposleni(self):
        name = self.get_widget_value(self.Katalog_FormVariables['Zaposleni'])
        try:
            selected_name = self.DBMS.Table_Zaposleni.item(self.DBMS.Table_Zaposleni.focus())['values'][1]
            if selected_name:
                if name:
                    if name != selected_name:
                        ID = RHMH.execute_selectquery(f'SELECT id_zaposleni from zaposleni WHERE Zaposleni = "{selected_name}"')[0][0]
                        reportquestion = 'Do you want to process update?\n\n'
                        report = f' - Ime (new):\n{name}\n'
                        report += f'\n - Ime (old):\n{selected_name}\n'
                        confirmation = Messagebox.yesno(parent=self.MessageBoxParent,
                                title=f'Employee Updating...', message=reportquestion+report[:-1], alert=True)
                        if confirmation == 'Yes':
                            RHMH.execute_Update(table='zaposleni', id=('id_zaposleni',ID), **{'Zaposleni':name})

                            Messagebox.show_info(parent=self.MessageBoxParent,
                                    title=f'Updating successfull', message=report[:-1])
                            
                            self.DBMS.LoggingData(query_type='Update Employee',loggingdata=report[:-1])
                            self.refresh_tables(table_names=['Katalog'])
                        return
                    else:
                        report = 'You made no changes'
                else:
                    report = 'You didn`t enter required data'
        except IndexError:
            report = 'You didn`t select Employee you want to update'
        Messagebox.show_warning(parent=self.MessageBoxParent,
                title=f'Updating failed!', message=report)

    def Delete_Patient(self):
        patient = self.PatientInfo.cget('text')
        confirm = Messagebox.yesno(parent=self.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete\n{patient}?', alert=True)
        if confirm=='Yes':
            patientdict = RHMH.get_patient_data(self.PatientFocus_ID)
            RHMH.execute_Delete('pacijent',[('id_pacijent',self.PatientFocus_ID)])
            self.Clear_Form()

            Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {patient}')
            
            patient += '\n'
            for col,val in patientdict.items():
                if isinstance(val,list):
                    val = ',\n'.join(val)
                patient += f'\n - {col}\n{val}\n'

            self.DBMS.LoggingData(query_type='Delete Patient',loggingdata=patient)
            self.refresh_tables(table_names=['Pacijenti','Slike'])
    
    def Delete_Image(self):
        selected_image:list = self.DBMS.Table_Slike.item(self.DBMS.Table_Slike.focus())['values'][1:6]
        ID = selected_image[0]
        PatientName = selected_image[2]
        selected_image_description = f'{ID}: {PatientName} - {selected_image[3]} : ({selected_image[4]} - {selected_image[5]})'
        confirm = Messagebox.yesno(parent=self.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete\n{selected_image_description}?', alert=True)
        if confirm == 'Yes':
            GoogleID = RHMH.execute_selectquery(f'SELECT image_date from slike WHERE id_slike = {ID}')[0][0]
            RHMH.execute_Delete('slike',[('id_slike',ID)])
            print('DELETING ',GoogleID)
            #self.GD.delete_file(GoogleID)
            Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {selected_image_description}\nfrom Database and Google Drive')
            self.refresh_tables(table_names=['Slike'])

    def Delete_MKB(self):
        mkb,opis = self.DBMS.Table_MKB.item(self.DBMS.Table_MKB.focus())['values'][1:3]
        confirm = Messagebox.yesno(parent=self.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete {mkb}?', alert=True)
        if confirm=='Yes':
            ID = RHMH.execute_selectquery(f'SELECT id_dijagnoza from mkb10 WHERE `MKB - šifra` = "{mkb}"')[0][0]
            RHMH.execute_Delete('mkb10',[('id_dijagnoza',ID)])

            Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {mkb}')
            
            logging = f' - MKB:\n{mkb}\n'
            logging += f'\n - Opis:\n{opis}'
            self.DBMS.LoggingData(query_type='Delete MKB',loggingdata=logging)
            self.refresh_tables(table_names=['Katalog'])
    
    def Delete_Zaposleni(self):
        name = self.DBMS.Table_Zaposleni.item(self.DBMS.Table_Zaposleni.focus())['values'][1]
        confirm = Messagebox.yesno(parent=self.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete {name}?', alert=True)
        if confirm=='Yes':
            ID = RHMH.execute_selectquery(f'SELECT id_zaposleni from zaposleni WHERE Zaposleni = "{name}"')[0][0]
            RHMH.execute_Delete('zaposleni',[('id_zaposleni',ID)])
            Messagebox.show_info(parent=self.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {name}')
            
            self.DBMS.LoggingData(query_type='Delete Employee',loggingdata=f' - Ime:\n{name}')
            self.refresh_tables(table_names=['Katalog'])

    def Download_SelectedImages(self):
        images = self.DBMS.Table_Slike.selection()
        if not images:
            Messagebox.show_warning(parent=self.MessageBoxParent,
                title=f'Download Images!', message='You need to select atleast one row')
            return
        imagesID = []
        imagesName = []
        imageSize = []
        width = 0

        def get_db_data():
            nonlocal width
            for image in images:
                ID = self.DBMS.Table_Slike.item(image)['values'][1]
                imageName,size,GoogleID = RHMH.execute_selectquery(f'SELECT Naziv,Veličina,image_data FROM slike WHERE id_slike = {ID}')[0]
                imagesID.append(GoogleID)
                imageNameParts = imageName.split('.')
                imageSize.append(size)
                txt = f'{imageNameParts[0]} - {size} MB.{imageNameParts[1]}'
                if len(txt) > width:
                    width = len(txt)
                imagesName.append(txt)

        thread_db = threading.Thread(target=get_db_data)
        thread_db.start()
        save_directory = filedialog.askdirectory(title='Izaberite direktorijum za čuvanje slika')
        thread_db.join()
        if save_directory:
            text_widget,floodgauge = Media.ProgressBar_DownloadingImages(self.MessageBoxParent,'Downloading',imagesName,width)
            def download():
                progress = 0
                totalMB = sum(imageSize)
                if not os.path.exists(save_directory):
                    os.makedirs(save_directory)
                for i,(GoogleID,imageName) in enumerate(zip(imagesID,imagesName)):
                    if i>5:
                        text_widget.yview_scroll(1,'units')
                    destination_path = os.path.join(save_directory, imageName)
                    media_data = self.GD.download_BLOB(GoogleID)
                    media_file = destination_path
                    with open(media_file, 'wb') as f:
                        f.write(media_data)
                    try:
                        progress += (imageSize[i]/totalMB) * 100
                        if i!=(len(imageSize)-1):
                            floodgauge['mask'] = f'Downloading... {progress:.1f}%'
                        else:
                            floodgauge['mask'] = 'Download completed'
                            floodgauge.configure(bootstyle='success')
                        floodgauge['value'] = progress
                        
                        text_widget.tag_add('success', f'{i+1}.0', f'{i+1}.end')
                        self.MessageBoxParent.update_idletasks()
                    except Exception:
                        return # Ovo je da se prekine download na close 
            thread = threading.Thread(target=download)
            thread.start()

    def Show_Image_FullScreen(self,event=None,BLOB=None):
        if not BLOB:
            ID = event.widget.item(event.widget.focus())['values'][1].split('_')[0]
            def execute():
                self.Slike_HideTable.grid_remove()
                self.Show_Image(ID=ID)
        else:
            def execute():
                self.Slike_HideTable.grid_remove()
                self.Show_Image(BLOB=BLOB)
        self.DBMS.NoteBook.select(1)

        self.ROOT.after(WAIT,execute)

    def Show_Image(self,event=None,ID=False,BLOB=False):
        if Media.Loading is True:
            return
        if event:
            shift_pressed = event.state & 0x1
            ctrl_pressed = event.state & 0x4
            if shift_pressed or ctrl_pressed:
                return
        Media.Slike_Viewer.delete('all')
        Media.Image_Active = None

        if BLOB is False:
            if ID is False:
                try:
                    ID = self.DBMS.Table_Slike.item(self.DBMS.Table_Slike.focus())['values'][1]
                except IndexError:
                    return
            media_type,google_ID = RHMH.execute_selectquery(f'SELECT Format,image_data from slike WHERE id_slike={ID}')[0]

        events = ['<Button-1>','<Double-1>','<MouseWheel>','<Button-4>','<Button-5>','<ButtonPress-1','<B1-Motion>']
        for event in events:
            Media.Slike_Viewer.unbind(event)
        self.ROOT.update() # CEKA SREDJIVANJE WIDGET

        width = Media.Slike_Viewer.winfo_width()
        height = Media.Slike_Viewer.winfo_height()
        image = Image.open(IMAGES['Loading'])
        image = Media.resize_image(image, width, height)
        image = ImageTk.PhotoImage(image)

        Media.Slike_Viewer.create_image(width//2, height//2, anchor='center', image=image)
        Media.Slike_Viewer.image = image
        Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
        
        # AFTER LOADING.. png Actual Image
        if BLOB is False:
            self.ROOT.after(WAIT,
                            lambda ID=google_ID,mediatype=media_type: 
                            self.Show_Image_execute(ID=ID,MediaType=mediatype))
        else:
            self.ROOT.after(WAIT,
                            lambda mediatype='image',blob=BLOB: 
                            self.Show_Image_execute(MediaType=mediatype,blob_data=blob))

    def Show_Image_execute(self,ID=None,MediaType=None,blob_data=False):
        if blob_data is False:
            queue_get_blob = queue.Queue()
            def get_image_fromGD(GoogleID,queue):
                image_blob = self.GD.download_BLOB(GoogleID)
                queue.put(image_blob)
            thread = threading.Thread(target=get_image_fromGD,args=(ID,queue_get_blob))
            thread.start()
            
            def check_queue():
                try:
                    Media.Blob_Data = queue_get_blob.get_nowait()
                    showing_media()
                except queue.Empty:
                    self.ROOT.after(50,check_queue)
            Media.Loading = True
            check_queue()
        else:
            Media.Blob_Data = blob_data
            showing_media()

        def showing_media():   
            width = Media.Slike_Viewer.winfo_width()
            height = Media.Slike_Viewer.winfo_height()
            
            if 'image' in MediaType:
                Media.Image_Active = Media.get_image(Media.Blob_Data)
                image = Media.resize_image(Media.Image_Active, width, height, savescale=True)
                image = ImageTk.PhotoImage(image)

                Media.Slike_Viewer.create_image(width//2, height//2,  anchor='center', image=image)
                Media.Slike_Viewer.image = image
                Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
                Media.Slike_Viewer.bind('<Double-1>',lambda event,image_data=Media.Blob_Data: Media.open_image(event,image_data))
                Media.Slike_Viewer.bind('<MouseWheel>', Media.zoom)
                Media.Slike_Viewer.bind('<Button-4>', Media.zoom)
                Media.Slike_Viewer.bind('<Button-5>', Media.zoom)
                Media.Slike_Viewer.bind('<ButtonPress-1>', Media.move_from)
                Media.Slike_Viewer.bind('<B1-Motion>',     Media.move_to)  
            elif 'video' in MediaType:
                thumbnail,video_data = Media.create_video_thumbnail(Media.Blob_Data)
                thumbnail = Media.resize_image(thumbnail, width, height)
                thumbnail = ImageTk.PhotoImage(thumbnail)
                
                Media.Slike_Viewer.create_image(width//2, height//2, anchor='center', image=thumbnail)
                Media.Slike_Viewer.image = thumbnail
                Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))
                Media.Slike_Viewer.bind('<Button-1>',lambda event,video=video_data: Media.play_video(event,video))
            Media.Loading = False 

    def Image_Read(self, result_queue):
        try:
            data = result_queue.get_nowait()
            report = ''
            for col,val in data.items():
                if val:
                    if isinstance(val,list):
                        val = ' , '.join(val) if col not in ['Asistent','Gostujući Specijalizant'] else ',\n'.join(val)
                    for table in self.Patient_FormVariables.keys():
                        try:
                            widget = self.Patient_FormVariables[table][col]
                            break
                        except KeyError:
                            continue
                    report += f'{col}\n  - {val}\n'
                    self.set_widget_value(widget,val)
            else:
                retry = Messagebox.show_question(parent=self.MessageBoxParent,
                        title='Fill From Image', message=report, buttons=['Retry:secondary','Ok:primary'])
                if retry == 'Retry':
                    self.Fill_FromImage(firsttry=False)
        except queue.Empty:
            self.ROOT.after(50, self.Image_Read, result_queue)

    def Fill_FromImage(self,firsttry=True):
        try:
            slika = self.Patient_FormVariables['slike']['Slike'].item(
                    self.Patient_FormVariables['slike']['Slike'].focus()
                    )['values'][1].split('_')
        except IndexError:
            Messagebox.show_error(parent=self.MessageBoxParent,
                    title=f'Fill From Image', message='No image selected!')
            return
        if 'Operaciona' in slika[1]:
            GoogleID = RHMH.execute_selectquery(f'SELECT image_data FROM slike WHERE id_slike = {slika[0]}')[0][0]

            queue_get_blob = queue.Queue()
            def get_image_fromGD(GoogleID,queue):
                image_blob = self.GD.download_BLOB(GoogleID)
                queue.put(image_blob)
            thread = threading.Thread(target=get_image_fromGD,args=(GoogleID,queue_get_blob))
            thread.start()

            response = Media.ImageReader_SettingUp(self.MessageBoxParent)
            if response != 'Run':
                return

            thread.join()
            image_blob = queue_get_blob.get()

            queue_analyzed_data = queue.Queue()
            def execute_fullscreen():
                self.Show_Image_FullScreen(BLOB=image_blob)
            def image_reader_with_queue(image, queue):
                data = Media.OperacionaLista_ImageReader(image)
                queue.put(data)

            if firsttry is True:
                thread1 = threading.Thread(target=execute_fullscreen)
                thread1.start()
            thread2 = threading.Thread(target=image_reader_with_queue, args=(image_blob,queue_analyzed_data))
            thread2.start()
            self.Image_Read(queue_analyzed_data)
        else:
            report = 'Image description ("Opis")\nhave to be "Operaciona Lista" or "Otupusna lista"'
            Messagebox.show_error(parent=self.MessageBoxParent,
                    title=f'Fill From Image', message=report)

    def Validation_Method(self,event=None,form=None):
        if form == 'Default':
            self.Valid_Default = True

            self.Patient_FormVariables['operacija']['Asistent'].focus_force()
            self.Patient_FormVariables['operacija']['Gostujući Specijalizant'].focus_force()
            for col,widget in self.Patient_FormVariables['pacijent'].items():
                if 'Datum' in col:
                    if widget:
                        value = self.get_widget_value(widget)
                        if value:
                            try:
                                datetime.strptime(value, '%d-%b-%Y')
                            except:
                                self.Valid_Default = False
        elif form == 'Alternative':
            self.Valid_Alternative = True

        for widget in self.Validation_Widgets[form]:
            widget:Widget
            widget.focus_force()

        self.MessageBoxParent.focus_force()

    def validate_notblank(self,x) -> bool:
        if not x.strip():
            self.Valid_Default = False
            return False
        else:
            return True        

    def validate_godiste(self,x) -> bool:
        if x.isdigit() and len(x)==4:
            return True
        else:
            self.Valid_Default = False
            return False

    def validate_dijagnoza(self,x) -> bool:
        if ',' in x:
            mkb = x.split(',')
            for i in mkb:
                fix = i.strip()
                if fix not in self.MKB_validation_LIST:
                    self.Valid_Default = False
                    return False
            else:
                return True
        elif x.strip() and not (x.strip() in self.MKB_validation_LIST):
            self.Valid_Default = False
            return False
        else:
            return True
        
    def validate_zaposleni(self,x) -> bool:
        if x.strip() and not (x.strip() in self.Zaposleni_validation_LIST):
            self.Valid_Alternative = False
            return False
        else:
            return True
    
    def validate_zaposleni_Text(self,event) -> bool:
        widget:Text = event.widget
        value = widget.get('1.0', END)
        if ',' in value:
            zaposleni = value.split(',')
            for i in zaposleni:
                fix = i.strip()
                if fix not in self.Zaposleni_validation_LIST:
                    self.Valid_Alternative = False
        elif value.strip() and not (value.strip() in self.Zaposleni_validation_LIST):
            self.Valid_Alternative = False

class DBMS(Singleton):
    _initialized = False
    def __init__(self) -> None:
        if not self._initialized:
            DBMS._initialized = True

            self.Admin = False
            self.GodMode = False
            self.FreeQuery_Frame:   Frame = None
            self.FreeQuery:         StringVar = None

            self.GD = GoogleDrive()
            self.BUTT = Buttons()

            self.NoteBook:          tb.Notebook = None
            self.Table_Pacijenti:   tb.ttk.Treeview = None
            self.Table_Slike:       tb.ttk.Treeview = None
            self.Table_MKB:         tb.ttk.Treeview = None
            self.Table_Zaposleni:   tb.ttk.Treeview = None
            self.Table_Logs:        tb.ttk.Treeview = None
            self.Table_Session:     tb.ttk.Treeview = None
            
            self.Graph_Frame:       Frame = None
            self.About_Tab:         Frame = None
            self.Settings_Tab:      Frame = None
            
            self.TablePacijenti_Columns =   tuple(MainTablePacijenti.keys())
            self.Pacijenti_ColumnVars =     {column: IntVar() for column in self.TablePacijenti_Columns}

            self.TableSlike_Columns =       tuple(['ID']+RHMH.slike)
            self.TableMKB_Columns =         tuple(['ID']+RHMH.mkb10)
            self.TableZaposleni_Columns =   tuple(['ID']+RHMH.zaposleni)
            self.TableLogs_Columns =        tuple(['ID']+RHMH.logs)
            self.TableSession_Columns =     tuple(['ID']+RHMH.session)

            self.SearchBar: Frame = None
            self.SearchBar_widgets = dict()
            self.SearchBar_number = 1
            self.SearchAdd_Button: tb.Label = None
            self.SearchRemove_Button: tb.Label = None

    def GodMode_Password(self,event):
        dialog = PasswordDialog(self.BUTT.MessageBoxParent, 'Privileges Unlocking...')
        if dialog.password=='63636':
            self.Admin = True
            info = 'New tabs:\n\t-Logs\n\t-Session'
            title = 'Admin unlocked'
        elif dialog.password=='C12-Si28-C13-Si28-C12':
            self.Admin = True
            self.GodMode = True
            self.FreeQuery_Frame.grid()
            info = 'New tabs:\n\t-Logs\n\t-Session\n\n'
            info += 'New button:\n\t-Free Query'
            info += f'\n\n{money()}'
            title = 'God Mode unlocked'
        else:
            return
        self.BUTT.ROOT.after(WAIT, lambda: self.NoteBook.select(5))
        self.BUTT.ROOT.after(WAIT*2, lambda: self.NoteBook.select(4))
        Messagebox.show_info(parent=self.BUTT.MessageBoxParent, message=info, title=title,)

    def FreeQuery_Execute(self):
        query = self.FreeQuery.get()
        if not query:
            return
        report = RHMH.format_sql(query)
        response = Messagebox.yesno(parent=self.BUTT.MessageBoxParent, title='Free Query executing...', message=report)
        if response == 'Yes':
            RHMH.connect()
            RHMH.cursor.execute(query)
            RHMH.connection.commit()
            RHMH.close_connection()

    def export_selection(self):
        focus = self.NoteBook.index(self.NoteBook.select())
        TAB = self.NoteBook.tab(focus,'text')

        if TAB == 'Pacijenti':
            table = self.Table_Pacijenti.selection_get()
            print(table)

        elif TAB == 'Slike':
            table = self.Table_Slike.selection_get()
            print(table)

        elif TAB == 'Katalog':
            table = self.Table_MKB.selection_get()
            print(table)
   
        elif TAB == 'Logs':
            table = self.Table_Logs.selection_get()
            print(table)
        
        elif TAB == 'Session':
            table = self.Table_Session.selection_get()
            print(table)

    def export_table(self):
        focus = self.NoteBook.index(self.NoteBook.select())
        TAB = self.NoteBook.tab(focus,'text')

        if TAB == 'Pacijenti':
            table = self.Table_Pacijenti
            print(table)

        elif TAB == 'Slike':
            table = self.Table_Slike
            print(table)

        elif TAB == 'Katalog':
            table = self.Table_MKB
            print(table)
   
        elif TAB == 'Logs':
            table = self.Table_Logs
            print(table)
        
        elif TAB == 'Session':
            table = self.Table_Session
            print(table)

    def search_bar_remove(self,event=None):
        to_remove = [k for k in self.SearchBar_widgets.keys() if int(k[-1]) == self.SearchBar_number]
        for key in to_remove:
            self.BUTT.empty_widget(self.SearchBar_widgets[key])
            self.SearchBar_widgets[key].grid_remove()
        self.SearchBar_number-=1

        if not self.SearchAdd_Button.winfo_ismapped():
            self.SearchAdd_Button.grid()
        if self.SearchBar_number==1:
            self.SearchRemove_Button.grid_remove()

    def search_bar_add(self,event=None):
        if not self.SearchRemove_Button.winfo_ismapped():
            self.SearchRemove_Button.grid()
        self.SearchBar_number+=1
        self.SearchBar_widgets[f'search_option_{self.SearchBar_number}'].grid()

        if self.SearchBar_number==max_searchby:
            self.SearchAdd_Button.grid_remove()

    def selected_columns(self, columns, table:tb.ttk.Treeview, columnvar:bool):

        Columns = [column for column, var in columns if var.get()==1] if columnvar else columns

        def sort_treeview(column, reverse):
            def convert_date(date_str):
                try:
                    return datetime.strptime(date_str, '%d-%b-%y')
                except ValueError:
                    return datetime.min
            def convert_int(val):
                try:
                    if ' MP' in val:
                        val = val.replace(' MP','')
                    elif ' MB' in val:
                        val = val.replace(' MB','')
                    return float(val)
                except ValueError:
                    return val
            if 'Datum' in column:
                data = [(convert_date(table.set(child, column)), child) for child in table.get_children('')]
            else:
                data = [(convert_int(table.set(child, column)), child) for child in table.get_children('')]

            data.sort(reverse=reverse, key=lambda x: x[0])
            for index, (_, child) in enumerate(data):
                table.move(child, '', index)
                table.set(child, 'ID', index+1)
            table.heading(column, command=lambda col=column: sort_treeview(col, not reverse))

        table.configure(columns=Columns)
        for i,col in enumerate(Columns):
            TXT = f'\n{col}'
            if col in RHMH.pacijent+RHMH.dg_kategorija+RHMH.dr_funkcija:
                FIX = col.split()
                if len(FIX)==2:
                    TXT = '\n'.join(FIX)
                elif len(FIX)==3:
                    if 'dijagnoza' in col:
                        TXT = '\n'.join(FIX[:-1])
                    else:
                        TXT = f'{FIX[0]} {FIX[1]}\n{FIX[2]}'
            elif col in RHMH.session:
                if 'efficency' in col:
                    TXT = col.replace(' ','\n')
            elif table==self.Table_Zaposleni and col=='Zaposleni':
                TXT = f'\nIme'
            elif col=='Naziv':
                TXT = f'\nPacijent'

            table.heading(col, text=TXT, anchor=W, command=lambda c=col: sort_treeview(c, False))
            table.column(col, stretch=False)
            if 'id_' in col:
                print(col)
                table.column(col, width=0)
            elif i==0: # counting column
                table.column(col, width=int(F_SIZE*4), minwidth=F_SIZE*2)
            elif col in ['Pol','Godište','Starost','Veličina', 'width', 'height', 'pixels']:
                table.column(col, width=int(F_SIZE*7), minwidth=F_SIZE*3, anchor=E)
            elif col in ['Modifying','Download','Upload'] or 'Datum' in col or 'Efficency' in col:
                table.column(col, width=F_SIZE*9, minwidth=F_SIZE*4)
            elif col in ['Opis'] or table==self.Table_Session :
                table.column(col, width=F_SIZE*13, minwidth=F_SIZE*6)
            elif col in ['Dg Latinski','Error'] or (col == 'Zaposleni' and table == self.Table_Zaposleni):
                table.column(col, width=F_SIZE*27, minwidth=F_SIZE*13)
            elif col in ['Opis Dijagnoze']:
                table.column(col, width=F_SIZE*100)
            elif col in ['Naziv','Gostujući Specijalizant','Asistent'] or table == self.Table_Logs:
                table.column(col, width=F_SIZE*16, minwidth=F_SIZE*7)
            else:
                table.column(col, width=F_SIZE*12, minwidth=F_SIZE*6)
        table['show'] = 'headings'
        return Columns[1:]
    
    def Options(self,n,event):
        search_option = self.SearchBar_widgets[f'search_option_{n}'].get()
        if search_option == 'Pol':
            for k,v in self.SearchBar_widgets.items():
                if k==f'search_type_{n}':
                    v.configure(text='=')
                v.grid() if k==f'equal_{n}' or ('search' in k  and k[-1]==str(n)) \
                    else v.grid_remove() if k[-1]==str(n) else None
        elif search_option in ['Godište','Starost']:
            for k,v in self.SearchBar_widgets.items():
                if k==f'search_type_{n}':
                    v.configure(text='od-do')
                v.grid() if k==f'from_{n}' or k==f'to_{n}' or ('search' in k and k[-1]==str(n))  \
                    else v.grid_remove() if k[-1]==str(n) else None
        elif 'Datum' in search_option:
            for k,v in self.SearchBar_widgets.items():
                if k==f'search_type_{n}':
                    v.configure(text='od-do')
                v.grid() if ('date' in k or 'search' in k) and k[-1]==str(n) \
                    else v.grid_remove() if k[-1]==str(n) else None
        else:
            for k,v in self.SearchBar_widgets.items():
                if k==f'search_type_{n}':
                    v.configure(text='≈')
                v.grid() if k==f'like_{n}' or ('search' in k and k[-1]==str(n)) \
                    else v.grid_remove() if k[-1]==str(n) else None

    def Graph_afterchoice(self):
        show = ('bars','pie')
        hide = ()
        if self.BUTT.Graph_FormVariables['X2-1'][1].get():
            show = ('bars','stacked')
            hide = ('color')
        for k,v in self.BUTT.Graph_FormVariables['afterchoice'].items():
            if k=='radio':
                for txt,widget in v['widgets'].items():
                    widget:tb.Radiobutton
                    if txt in show:
                        widget.grid()
                    else:
                        widget.grid_remove()
                
            elif not k in hide:
                v[0].grid()
            else:
                v[0].grid_forget()

    def Graph_Options(self,event,option:str):
        widget:tb.Combobox = event.widget
        execute_button:ctk.CTkButton = self.BUTT.buttons['SHOW Graph']
        add_button:tb.Label = self.BUTT.Graph_FormVariables['Add']
        choice = widget.get()
        Values = []
        
        def removing_widgets(widgets_to_remove):
            widget:tb.Combobox
            stringvar:StringVar
            print(widgets_to_remove)
            for widgetname in widgets_to_remove:
                widget,stringvar = self.BUTT.Graph_FormVariables[widgetname]
                if widget.winfo_ismapped():
                    widget.grid_remove()
                stringvar.set('')
            execute_button.configure(state=DISABLED)  

        if option == 'Y':
            Values.append(graph_Xoptions[:])
            if choice != 'Broj Pacijenata':
                for val in ['Dan u Sedmici' , 'Dan']:
                    Values[0].remove(val)
            Next_Names = ['X1-1']
            
        elif option in ['X1-1','X2-1']:
            Next_Names = [option]
            if choice == 'Starost':
                Next_Names = [option.replace('-1','-2')]
                Values.append([str(i) for i in range(5,31,5)])
            elif choice == 'MKB Pojedinačno':
                check = True
                if option == 'X2-1':
                    first_stringvars:StringVar = self.BUTT.Graph_FormVariables['X1-1'][1]
                    check = not (first_stringvars.get() in ['Trauma', 'MKB Grupe','MKB Pojedinačno'])
                if check:
                    Next_Names = [option.replace('-1','-2')]
                    Values.append(RHMH.get_distinct_mkb())
                    Next_Names.append(option.replace('-1','-3'))
                    Values.append(RHMH.dg_kategorija)
                else:
                    Next_Names = [option.replace('-1','-3')]
                    Values.append(RHMH.get_distinct_mkb())
            elif choice in ['MKB Grupe', 'Trauma']:
                check = True
                if option == 'X2-1':
                    first_stringvars:StringVar = self.BUTT.Graph_FormVariables['X1-1'][1]
                    check = not (first_stringvars.get() in ['Trauma', 'MKB Grupe','MKB Pojedinačno'])
                if check:
                    Next_Names = [option.replace('-1','-2')]
                    Values.append(RHMH.dg_kategorija)
            elif choice == 'Zaposleni':
                Next_Names = [option.replace('-1','-2')]
                Values.append(RHMH.dr_funkcija)
            else:
                self.Graph_afterchoice()
                add_button.grid()

        elif option in ['X1-2','X2-2']:
            combo3:tb.Combobox = self.BUTT.Graph_FormVariables['X1-3'][0]
            if combo3.winfo_ismapped():
                if combo3.get():
                    self.Graph_afterchoice()
                    if int(option[1])==1:
                        add_button.grid()
            else:
                self.Graph_afterchoice()
                if int(option[1])==1:
                        add_button.grid()
            return
        elif option in ['X1-3','X2-3']:
            combo2:tb.Combobox = self.BUTT.Graph_FormVariables['X1-2'][1]
            if combo2.get():
                self.Graph_afterchoice()
                if int(option[1])==1:
                        add_button.grid()
            return

        print(Next_Names)
        widgetnames = ['Y','X1-1','X1-2','X1-3','X2-1','X2-2','X2-3']
        removing_widgets(widgetnames[widgetnames.index(Next_Names[-1])+1:])
        if not Values:
            return
        for name,value in zip(Next_Names,Values):
            next_widget:tb.Combobox
            stringvar:StringVar
            next_widget,stringvar = self.BUTT.Graph_FormVariables[name]

            width = len(max(value, key=len))
            width = width-5 if width>20 else 3 if width<3 else width-2
            next_widget.configure(values=value, width=width)
            stringvar.set('')
            if not next_widget.winfo_ismapped():
                next_widget.grid()

    def Show_Graph(self):
        print('showing graph')
        for k,v in self.BUTT.Graph_FormVariables.items():
            print(f'{k}: {v.get()}')
        print(self.Graph_Frame)

    def fill_TablePacijenti(self,table):
        for i, row in enumerate(table):
            # FROM RHMH Date Format TO Table Date Format
            formatted_row = [i+1] + [datetime.strptime(cell,'%Y-%m-%d').strftime('%d-%b-%y') if self.BUTT.is_DB_date(cell) \
                                        else ' , '.join(cell.split(',')) if isinstance(cell,str) and ',' in cell \
                                            else '' if str(cell)=='None' \
                                                else cell for cell in row]
            self.Table_Pacijenti.insert('', END, values=formatted_row)

    def fill_Tables_Other(self,view,table):
        for i, row in enumerate(view):
            formatted_row = [i+1] + [cell for cell in row]
            table.insert('', END, values=formatted_row)

    def fill_TableSlike(self,table,condition=False):
        for i, row in enumerate(table):
            # ovo je filter sta se nalazi u patient tabeli
            if condition is False or row[0] in condition:
                formatted_row = [i+1] + [f'{cell:.2f} MB' if isinstance(cell,float) \
                                            else f'{cell/10**6:.2f} MP' if j==8 \
                                                else cell.split('_')[1] if j==2\
                                                    else cell for j,cell in enumerate(row)]
                self.Table_Slike.insert('', END, values=formatted_row)

    def LoggingData(self,result=None,query_type=None,loggingdata=None):
        Time = f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.{datetime.now().strftime('%f')[:3]}'
        if loggingdata:
            def execute():
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['User'],
                                                'Query':query_type,'Full Query':loggingdata})
            self.BUTT.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
            return
        if result:
            def execute():
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['User'],
                                                'Query':query_type,'Full Query':RHMH.LoggingQuery})
            self.BUTT.ROOT.after(WAIT, lambda: threading.Thread(target=execute).start())
        return result

    def showall_data(self,TAB=None):
        if TAB is None:
            focus = self.NoteBook.index(self.NoteBook.select())
            TAB = self.NoteBook.tab(focus,'text')

        if TAB == 'Pacijenti':
            columns = self.selected_columns(self.Pacijenti_ColumnVars.items() , self.Table_Pacijenti , columnvar=True)
            view = RHMH.execute_join_select('pacijent',*(columns))
          
            for item in self.Table_Pacijenti.get_children():
                self.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                self.fill_TablePacijenti(view)

        elif TAB == 'Slike':
            view = RHMH.execute_select('slike',*(self.TableSlike_Columns[1:]))

            for item in self.Table_Slike.get_children():
                self.Table_Slike.delete(item)
            if view and len(view)!=0:
                self.fill_TableSlike(view)

        elif TAB == 'Katalog':
            view = RHMH.execute_select('mkb10',*(self.TableMKB_Columns[1:]))
   
            for item in self.Table_MKB.get_children():
                self.Table_MKB.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_MKB)

            view = RHMH.execute_select('zaposleni',*(self.TableZaposleni_Columns[1:]))
   
            for item in self.Table_Zaposleni.get_children():
                self.Table_Zaposleni.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Zaposleni)

        elif TAB == 'Logs':
            view = RHMH.execute_select('logs',*(self.TableLogs_Columns[1:]))
 
            for item in self.Table_Logs.get_children():
                self.Table_Logs.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Logs)
        
        elif TAB == 'Session':
            view = RHMH.execute_select('session',*(self.TableSession_Columns[1:]))

            for item in self.Table_Session.get_children():
                self.Table_Session.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Session)

    def search_data(self):
        focus = self.NoteBook.index(self.NoteBook.select())
        TAB = self.NoteBook.tab(focus,'text')

        def searching_dict_create():
            searching = dict()
            for n in range(1,self.SearchBar_number+1):
                option = self.SearchBar_widgets[f'search_option_{n}'].get()
                try:
                    searching[option]
                except KeyError:
                    searching[option] = set()
                if not option:
                    continue
                else:
                    search_type = self.SearchBar_widgets[f'search_type_{n}'].cget('text')

                if search_type == 'od-do':
                    if 'Datum' in option:
                        # FROM Form Date Formate TO RHMH Date Format
                        searching[option].add((datetime.strptime(self.SearchBar_widgets[f'date_from_{n}'].entry.get(),'%d-%b-%Y').strftime('%Y-%m-%d'),
                                            datetime.strptime(self.SearchBar_widgets[f'date_to_{n}'].entry.get(),'%d-%b-%Y').strftime('%Y-%m-%d')))
                    else:
                        searching[option].add((self.SearchBar_widgets[f'from_{n}'].get(),self.SearchBar_widgets[f'to_{n}'].get()))
                elif search_type == '=':
                    searching[option].add(self.SearchBar_widgets[f'equal_{n}'].get())
                else: # Like ≈
                    searching[option].add((self.SearchBar_widgets[f'like_{n}'].get(),))

            for k,v in searching.items(): # OVO JE ZBOG SETOVA DA PREBACI U LISTU
                if len(v)==1:   # Uvek je prvo set jer pretpostavlja da ce ih biti vise istih
                    searching[k] = list(v)[0]
            return searching

        if TAB != 'Slike': # Ovo je da bi SLIKE table mogao sa prazan search da filtrira sta se nalazi u PACIJENT tabeli
            for element in self.SearchBar.winfo_children():
                if element.winfo_ismapped():
                    if isinstance(element,Entry):
                        if element.get():
                            continue
                        else:
                            return
                    elif isinstance(element,widgets.DateEntry):
                        if element.entry.get():
                            continue
                        else:
                            return

        if TAB == 'Pacijenti':
            columns = self.selected_columns(self.Pacijenti_ColumnVars.items() , self.Table_Pacijenti , columnvar=True)
            searching = searching_dict_create()
            view = self.LoggingData(RHMH.execute_join_select('pacijent',*(columns),**searching),'Pacijenti Search SELECT')

            for item in self.Table_Pacijenti.get_children():
                self.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                self.fill_TablePacijenti(view)

        elif TAB == 'Slike':
            searching = searching_dict_create()
            view = self.LoggingData(RHMH.execute_select('slike',*(self.TableSlike_Columns[1:]),**searching),'Slike Search SELECT')
  
            for item in self.Table_Slike.get_children():
                self.Table_Slike.delete(item)
            if view and len(view)!=0:
                self.fill_TableSlike(view)

        elif TAB == 'Katalog':
            searching = searching_dict_create()
            view = self.LoggingData(RHMH.execute_select('mkb10',*(self.TableMKB_Columns[1:]),**searching),'MKB Search SELECT')

            for item in self.Table_MKB.get_children():
                self.Table_MKB.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_MKB)

        elif TAB == 'Logs':
            searching = searching_dict_create()
            view = RHMH.execute_select('logs',*(self.TableLogs_Columns[1:]),**searching)
 
            for item in self.Table_Logs.get_children():
                self.Table_Logs.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Logs)

        elif TAB == 'Session':
            searching = searching_dict_create()
            view = RHMH.execute_select('session',*(self.TableSession_Columns[1:]),**searching)

            for item in self.Table_Session.get_children():
                self.Table_Session.delete(item)
            if view and len(view)!=0:
                self.fill_Tables_Other(view,self.Table_Session)

    def filter_data(self,columns):
        where = {}
        for k,v in self.BUTT.FilterOptions.items():
            if k in columns:
                where[k]=v[1].get()
        
        view = self.LoggingData(RHMH.execute_filter_select(where),'FILTER SELECT')
        for item in self.Table_Pacijenti.get_children():
            self.Table_Pacijenti.delete(item)
        if view and len(view)!=0:
            for i, row in enumerate(view):
                # FROM RHMH Date Formate TO Table Date Format
                formatted_row = [i+1] + [datetime.strptime(cell,'%Y-%m-%d').strftime('%d-%b-%y') if isinstance(cell, date) \
                                         else '' if str(cell)=='None' \
                                            else cell for cell in row]
                self.Table_Pacijenti.insert('', END, values=formatted_row)

    def fill_MKBForm(self,event):
        try:
            row = self.Table_MKB.item(self.Table_MKB.focus())['values'][2:]
            for col,val in zip(self.TableMKB_Columns[2:],row):
                self.BUTT.Katalog_FormVariables[col].set(val)
        except IndexError:
            return

    def MKB_double_click(self, event):
        try:
            column = self.BUTT.get_widget_value(self.BUTT.Katalog_FormVariables['Kategorija'])
            if column:
                mkb = self.Table_MKB.item(self.Table_MKB.focus())['values'][2]
                dg_Widget = self.BUTT.Patient_FormVariables['dijagnoza'][column]
                dg_Value = self.BUTT.get_widget_value(dg_Widget)
                if not dg_Value:
                    self.BUTT.set_widget_value(dg_Widget,mkb)
                else:
                    self.BUTT.set_widget_value(dg_Widget,f'{dg_Value} , {mkb}')
        except IndexError:
            return
    
    def fill_ZaposleniForm(self,event):
        try:
            name = self.Table_Zaposleni.item(self.Table_Zaposleni.focus())['values'][2]
            self.BUTT.Katalog_FormVariables['Zaposleni'].set(name)
        except IndexError:
            return
        
    def Zaposleni_double_click(self,event):
        try:
            column = self.BUTT.get_widget_value(self.BUTT.Katalog_FormVariables['Funkcija'])
            if column:
                mkb = self.Table_Zaposleni.item(self.Table_Zaposleni.focus())['values'][2]
                dg_Widget = self.BUTT.Patient_FormVariables['operacija'][column]
                dg_Value = self.BUTT.get_widget_value(dg_Widget)
                if not dg_Value:
                    self.BUTT.set_widget_value(dg_Widget,mkb)
                else:
                    self.BUTT.set_widget_value(dg_Widget,f'{dg_Value} , {mkb}')
        except IndexError:
            return

    def fill_PatientForm(self,event):
        self.BUTT.Clear_Form()
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            self.BUTT.PatientFocus_ID = self.Table_Pacijenti.item(self.Table_Pacijenti.focus())['values'][1] 
            patient = RHMH.get_patient_data(self.BUTT.PatientFocus_ID)
        except IndexError:
            return
        for col,val in patient.items():
            for table in self.BUTT.Patient_FormVariables.keys():
                try:
                    widget = self.BUTT.Patient_FormVariables[table][col]
                    break
                except KeyError:
                    continue
            else:
                continue
            if isinstance(val,str) and ',' in val:
                val = val.split(',')
                fix = []
                for v in val:
                    fix.append(v.strip())
                else:
                    val = ' , '.join(fix) if col not in ['Asistent','Gostujući Specijalizant'] else ',\n'.join(fix)    
            self.BUTT.set_widget_value(widget,val)
        TEXT = f'{patient['Ime']} {patient['Prezime']}'
        try:
            # FROM RHMH Date Formate TO Patient print Date Format
            TEXT += f'\n({datetime.strptime(patient['Datum Prijema'],'%Y-%m-%d').strftime('%d-%b-%y')})'
        except KeyError:
            pass
        self.BUTT.PatientInfo.config(text=TEXT)
        self.BUTT.FormTitle[0].configure(bootstyle='success')
  
    def fill_LogsForm(self,event):
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            time = self.Table_Logs.item(self.Table_Logs.focus())['values'][1]
            query = f'SELECT `Full Query`,`Full Error` from logs WHERE `ID Time` = "{time}"'
            FullQuery,FullError = RHMH.execute_selectquery(query)[0]
            self.BUTT.set_widget_value(self.BUTT.Logs_FormVariables['Full Query'],FullQuery)
            self.BUTT.set_widget_value(self.BUTT.Logs_FormVariables['Full Error'],FullError)
        except IndexError:
            return

    def tab_change(self,event):

        def filter_buttons_state(state):
            for widget in self.BUTT.buttons['Filter Patient']:
                if state is False:
                    widget.grid_remove()
                else:
                    widget.grid()


        def tab_swapping(values):
            if not self.SearchBar.winfo_ismapped():
                self.SearchBar.grid()

            for i in range(self.SearchBar_number,1,-1):
                self.search_bar_remove()
            for i in range(1,max_searchby+1):
                self.SearchBar_widgets[f'search_option_{i}'].configure(values=values)

            for Type,Widget in self.SearchBar_widgets.items():
                self.BUTT.empty_widget(Widget)
                if 'search_option' not in Type:
                    if Widget.winfo_ismapped():
                        Widget.grid_remove() 

        focus = self.NoteBook.index(self.NoteBook.select())
        TAB = self.NoteBook.tab(focus,'text')
        if TAB == 'Pacijenti':
            for index in [6,7]:
                if self.NoteBook.tab(index, "state") == "normal":
                    self.NoteBook.hide(index)
            tab_swapping(self.TablePacijenti_Columns[2:])
            filter_buttons_state(True)
        elif TAB == 'Slike':
            for index in [6,7]:
                if self.NoteBook.tab(index, "state") == "normal":
                    self.NoteBook.hide(index)
            self.BUTT.Slike_HideTable.grid()
            tab_swapping(self.TableSlike_Columns[3:])
            filter_buttons_state(False)
        elif TAB == 'Katalog':
            for index in [6,7]:
                if self.NoteBook.tab(index, "state") == "normal":
                    self.NoteBook.hide(index)
            tab_swapping(self.TableMKB_Columns[2:])
            filter_buttons_state(False)
        elif TAB == 'Logs':
            for index in [6,7]:
                if self.NoteBook.tab(index, "state") == "normal":
                    self.NoteBook.hide(index)
            tab_swapping(self.TableLogs_Columns[1:])
            filter_buttons_state(False)
        elif TAB == 'Session':
            for index in [6,7]:
                if self.NoteBook.tab(index, "state") == "normal":
                    self.NoteBook.hide(index)
            tab_swapping(self.TableSession_Columns[1:])
            filter_buttons_state(False)
        elif TAB == 'Grafikon':
            for index in [6,7]:
                if self.NoteBook.tab(index, "state") == "normal":
                    self.NoteBook.hide(index)
            tab_swapping(['test1','test2','test3','test4'])
            filter_buttons_state(False)
        elif TAB == 'Settings':
            self.SearchBar.grid_remove()
            if self.NoteBook.tab(7, "state") == "normal":
                self.NoteBook.hide(7)
        elif TAB == 'About':
            self.SearchBar.grid_remove()
            if self.NoteBook.tab(6, "state") == "normal":
                self.NoteBook.hide(6)