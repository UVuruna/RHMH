from A1_Variables import *
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import RHMH
from B3_Media import Media
from C1_Controller import Controller
from C3_SelectDB import SelectDB

class ManageDB(Controller):

    @Controller.block_manageDB()
    @staticmethod
    def Add_Patient():

        def message_success():
            SelectDB.refresh_tables(table_names=['Pacijenti','Slike'])
            Messagebox.show_info(parent=Controller.MessageBoxParent,
                    title=f'New Patient added', message=f'{ime}\n\n{report[:-1]}')
        def message_fail():
            Messagebox.show_warning(parent=Controller.MessageBoxParent,
                    title=f'Inserting failed!', message='Wrong data in Patient Form')

        if not (Controller.Valid_Default and Controller.Valid_Alternative):
            Controller.ROOT.after(WAIT,message_fail)
            return
        reportDict = {}
        for table in Controller.Patient_FormVariables.keys():
            insertDict = {}
            if table=='pacijent':
                trenutna_godina = datetime.now().year
                for col,widget in Controller.Patient_FormVariables[table].items():
                    value = ManageDB.get_widget_value(widget)
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
                for col,widget in Controller.Patient_FormVariables[table].items():
                    value = ManageDB.get_widget_value(widget)
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
                for col,widget in Controller.Patient_FormVariables[table].items():
                    value = ManageDB.get_widget_value(widget)
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

        ManageDB.LoggingData(query_type='Add Patient',loggingdata=f'{ime}\n\n{logging[:-1]}')
        Controller.ROOT.after(WAIT,message_success)

    @Controller.block_manageDB()
    @staticmethod
    def Add_Image():
        def message_success():
            report = 'Add Image successfull\nImage added to Database and Google Drive'
            Messagebox.show_info(parent=Controller.MessageBoxParent,title='Add Image',message=report)
            SelectDB.refresh_tables(['Slike'])
            SelectDB.fill_PatientForm()
        def message_fail():
            report = 'Image Data added to Database\nFailed to Add Image to Google Drive\nConnection problem'
            Messagebox.show_warning(parent=Controller.MessageBoxParent,
                    title=f'Add Image failed', message=report)
                
        ime = Controller.Slike_FormVariables['Pacijent'].get()
        opis = Controller.Slike_FormVariables['Opis'].get()
        id_pacijent = Controller.Slike_FormVariables['ID'].cget('text')
        id_pacijent = id_pacijent.split('/')[0]

        if not (ime and opis):
            Messagebox.show_warning(parent=Controller.MessageBoxParent,title='Add Image Failed',message='Please fill required Fields')
            return
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
        if file_path:

            def execute_adding_media():
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

                if file_path.lower().endswith(('.mp4', '.mov')):
                    media = VideoFileClip(file_path)
                    duration = media.duration
                    width = media.size[0]
                    height = media.size[1]
                    
                elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.heif', '.heic')):
                    media = Image.open(file_path)
                    width, height = media.size                    

                mime = file_path.split('.')[-1]
                FORMAT = MIME[mime.upper()]
                dicty = {'id_pacijent':id_pacijent,
                            'Naziv': '0_xxx_xxx.xx',
                            'Opis':opis,
                            'Format': FORMAT,
                            'Veličina': file_size_mb,
                            'width': width,
                            'height': height,
                            'pixels': width*height,
                            'image_data': 'temp'}

                id_slike = RHMH.execute_Insert('slike',**dicty)
                Naziv = f'{id_slike}_{ime}_{opis}.{mime.lower()}'
                
                BLOB = Media.image_to_blob(file_path)
                try:
                    GOOGLE_ID = GoogleDrive.upload_NewFile_asBLOB(file_name=Naziv,GoogleDrive_folder=GD_Slike_folder, blob_data=BLOB, mime_type=FORMAT)
                    RHMH.execute_Update('slike',('id_slike',id_slike),**{'Naziv':Naziv,'image_data':GOOGLE_ID})
                    Controller.ROOT.after(WAIT,message_success)
                except Exception:
                    Controller.ROOT.after(WAIT,message_fail)

            threading.Thread(target=execute_adding_media).start()


    @Controller.block_manageDB()
    @staticmethod
    def Add_MKB():
        mkb = ManageDB.get_widget_value(Controller.Katalog_FormVariables['MKB - šifra'])
        opis = ManageDB.get_widget_value(Controller.Katalog_FormVariables['Opis Dijagnoze'])

        if mkb and opis:
            RHMH.execute_Insert('mkb10',**{'MKB - šifra':mkb,'Opis Dijagnoze':opis})
            report = ''
            for col,val in {'MKB - šifra':mkb,'Opis Dijagnoze':opis}.items():
                report += f' - {col}:\n{val}\n\n'

            Messagebox.show_info(parent=Controller.MessageBoxParent,
                    title=f'New MKB added', message=report[:-1], alert=True)
            
            Controller.MKB_validation_LIST = [i[0] for i in RHMH.execute_select(False,'mkb10',*('MKB - šifra',))]
            ManageDB.LoggingData(query_type='Add MKB',loggingdata=report[:-1])
            SelectDB.refresh_tables(['Katalog'])
        else:
            Messagebox.show_warning(parent=Controller.MessageBoxParent,
                    title=f'Inserting failed!', message='You didn`t fill the form')
    
    @Controller.block_manageDB()
    @staticmethod
    def Add_Zaposleni():
        name = ManageDB.get_widget_value(Controller.Katalog_FormVariables['Zaposleni'])
        if name:
            RHMH.execute_Insert('zaposleni',**{'Zaposleni':name})
            report = f' - Ime:\n{name}'

            Messagebox.show_info(parent=Controller.MessageBoxParent,
                    title=f'New Employee added', message=report, alert=True)
            
            Controller.Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select(False,'zaposleni',*('Zaposleni',))]
            ManageDB.LoggingData(query_type='Add Employee',loggingdata=report)
            SelectDB.refresh_tables(['Katalog'])
        else:
            Messagebox.show_warning(parent=Controller.MessageBoxParent,
                    title=f'Inserting failed!', message='You didn`t enter Name of Employee')

    @Controller.block_manageDB()
    @staticmethod
    def Update_Patient():
        if not (Controller.Valid_Default and Controller.Valid_Alternative):
            report = 'You have entered incorrect data'
            Messagebox.show_error(parent=Controller.MessageBoxParent,
                    title='Updating failed!', message=report)
            return
        if Controller.PatientFocus_ID:    
            patient = RHMH.get_patient_data(Controller.PatientFocus_ID)
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
                            
            for table,tabledict in Controller.Patient_FormVariables.items(): # {'pacijent':{},'dijagnoza':{},'operacija':{},'slike':{}}
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
                    NEW = str(ManageDB.get_widget_value(widget))

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
                    confirmation = Messagebox.yesno(parent=Controller.MessageBoxParent,
                            title=f'Patient Updating...', message=reportquestion+report[:-1], alert=True)
            else:
                report = 'You made no changes to current patient'
        else:
            report = 'You didn`t select Patient'

        try:
            if confirmation=='Yes':
                if update_Dict:
                    RHMH.execute_Update('pacijent',('id_pacijent',Controller.PatientFocus_ID),**update_Dict)
                for table,insertdict in insert_Dict.items():
                    if not insertdict:
                        continue
                    for column,setvalues in insertdict.items():
                        if table == 'dijagnoza':
                            idkategorija = RHMH.execute_selectquery(f'SELECT id_kategorija FROM kategorija WHERE Kategorija = "{column}"')[0][0]
                            for value in setvalues: 
                                iddijagnoza = RHMH.execute_selectquery(f'SELECT id_dijagnoza from mkb10 WHERE `MKB - šifra` = "{value}"')[0][0]
                                inserting = {'id_dijagnoza': iddijagnoza, 'id_pacijent': Controller.PatientFocus_ID, 'id_kategorija': idkategorija }
                                RHMH.execute_Insert('dijagnoza',**inserting)
                        elif table == 'operacija':
                            idfunkcija = RHMH.execute_selectquery(f'SELECT id_funkcija FROM funkcija WHERE Funkcija = "{column}"')[0][0]
                            for value in setvalues:
                                idzaposleni = RHMH.execute_selectquery(f'SELECT id_zaposleni FROM zaposleni WHERE Zaposleni = "{value}"')[0][0]
                                inserting = {'id_zaposleni': idzaposleni, 'id_pacijent': Controller.PatientFocus_ID, 'id_funkcija': idfunkcija }
                                RHMH.execute_Insert('operacija',**inserting)
                for table,deletedict in delete_Dict.items():
                    if not deletedict:
                        continue
                    for column,setvalues in deletedict.items():
                        if table == 'dijagnoza':
                            idkategorija = RHMH.execute_selectquery(f'SELECT id_kategorija FROM kategorija WHERE Kategorija = "{column}"')[0][0]
                            for value in setvalues:
                                iddijagnoza = RHMH.execute_selectquery(f'SELECT id_dijagnoza FROM mkb10 WHERE `MKB - šifra` = "{value}"')[0][0]
                                deleting = [('id_dijagnoza', iddijagnoza), ('id_pacijent', Controller.PatientFocus_ID), ('id_kategorija', idkategorija)]
                                RHMH.execute_Delete('dijagnoza',deleting)
                        elif table == 'operacija':
                            idfunkcija = RHMH.execute_selectquery(f'SELECT id_funkcija FROM funkcija WHERE Funkcija = "{column}"')[0][0]
                            for value in setvalues:
                                idzaposleni = RHMH.execute_selectquery(f'SELECT id_zaposleni FROM zaposleni WHERE Zaposleni = "{value}"')[0][0]
                                deleting = [('id_zaposleni', idzaposleni), ('id_pacijent', Controller.PatientFocus_ID), ('id_funkcija', idfunkcija)]
                                RHMH.execute_Delete('operacija',deleting)

                Messagebox.show_info(parent=Controller.MessageBoxParent,
                        title=f'Updating successfull', message=PATIENT)
                
                ManageDB.LoggingData(query_type='Update Patient',loggingdata=logging)
                SelectDB.refresh_tables(table_names=['Pacijenti','Slike'])

        except UnboundLocalError:
            Messagebox.show_error(parent=Controller.MessageBoxParent,
                    title='Update failed!', message=report)
    
    @Controller.block_manageDB()
    @staticmethod
    def Edit_Image():
        opis = Controller.Slike_FormVariables['Opis'].get()
        id_slike = Controller.Slike_FormVariables['ID'].cget('text')
        id_slike = id_slike.split('/')[1]

        if not id_slike or not opis:
            if not id_slike:
                report = 'Please select Image'
            elif not opis:
                report = 'Please fill required Fields'
            Messagebox.show_warning(parent=Controller.MessageBoxParent,title='Edit Image Failed',message=report)
            return

        RHMH.execute_Update('slike',('id_slike',id_slike),**{'Opis':opis})
        report = f'Editing successfull.\nImage id: {id_slike}\nNew Opis: {opis}'
        Messagebox.show_info(parent=Controller.MessageBoxParent,title='Edit Image',message=report)
        SelectDB.refresh_tables(['Slike'])
        SelectDB.fill_PatientForm()

    @Controller.block_manageDB()
    @staticmethod
    def Update_MKB():
        mkb = ManageDB.get_widget_value(Controller.Katalog_FormVariables['MKB - šifra'])
        opis = ManageDB.get_widget_value(Controller.Katalog_FormVariables['Opis Dijagnoze'])

        try:
            ID, selected_mkb, selected_opis = Controller.Table_MKB.item(Controller.Table_MKB.focus())['values'][1:]
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
                        reportquestion = 'Do you want to process update?\n\n'
                        confirmation = Messagebox.yesno(parent=Controller.MessageBoxParent,
                                title=f'MKB Updating...', message=reportquestion+report[:-1], alert=True)
                        if confirmation == 'Yes':
                            RHMH.execute_Update(table='mkb10', id=('id_dijagnoza',ID), **{'MKB - šifra':mkb,'Opis Dijagnoze':opis})

                            Messagebox.show_info(parent=Controller.MessageBoxParent,
                                    title=f'Updating successfull', message=report[:-1])
                            
                            Controller.MKB_validation_LIST = [i[0] for i in RHMH.execute_select(False,'mkb10',*('MKB - šifra',))]
                            ManageDB.LoggingData(query_type='Update MKB',loggingdata=report[:-1])
                            SelectDB.refresh_tables(table_names=['Katalog'])
                        return
                    else:
                        report = 'You made no changes'
                else:
                    report = 'You didn`t enter required data'
        except IndexError:
            report = 'You didn`t select MKB you want to update'
        Messagebox.show_warning(parent=Controller.MessageBoxParent,
                title=f'Updating failed!', message=report)

    @Controller.block_manageDB()
    @staticmethod        
    def Update_Zaposleni():
        name = ManageDB.get_widget_value(Controller.Katalog_FormVariables['Zaposleni'])
        try:
            ID, selected_name = Controller.Table_Zaposleni.item(Controller.Table_Zaposleni.focus())['values'][1:]
            if selected_name:
                if name:
                    if name != selected_name:
                        reportquestion = 'Do you want to process update?\n\n'
                        report = f' - Ime (new):\n{name}\n'
                        report += f'\n - Ime (old):\n{selected_name}\n'
                        confirmation = Messagebox.yesno(parent=Controller.MessageBoxParent,
                                title=f'Employee Updating...', message=reportquestion+report[:-1], alert=True)
                        if confirmation == 'Yes':
                            RHMH.execute_Update(table='zaposleni', id=('id_zaposleni',ID), **{'Zaposleni':name})

                            Messagebox.show_info(parent=Controller.MessageBoxParent,
                                    title=f'Updating successfull', message=report[:-1])
                            
                            Controller.Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select(False,'zaposleni',*('Zaposleni',))]
                            ManageDB.LoggingData(query_type='Update Employee',loggingdata=report[:-1])
                            SelectDB.refresh_tables(table_names=['Katalog'])
                        return
                    else:
                        report = 'You made no changes'
                else:
                    report = 'You didn`t enter required data'
        except IndexError:
            report = 'You didn`t select Employee you want to update'
        Messagebox.show_warning(parent=Controller.MessageBoxParent,
                title=f'Updating failed!', message=report)

    @Controller.block_manageDB()
    @staticmethod
    def Delete_Patient():
        patient = Controller.get_widget_value(Controller.PatientInfo)
        confirm = Messagebox.yesno(parent=Controller.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete\n{patient}?', alert=True)
        if confirm=='Yes':
            patientdict = RHMH.get_patient_data(Controller.PatientFocus_ID)
            RHMH.execute_Delete('pacijent',[('id_pacijent',Controller.PatientFocus_ID)])
            ManageDB.Clear_Form()

            Messagebox.show_info(parent=Controller.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {patient}')
            
            patient += '\n'
            for col,val in patientdict.items():
                if isinstance(val,list):
                    val = ',\n'.join(val)
                patient += f'\n - {col}\n{val}\n'

            ManageDB.LoggingData(query_type='Delete Patient',loggingdata=patient)
            SelectDB.refresh_tables(table_names=['Pacijenti','Slike'])
    
    @Controller.block_manageDB()
    @staticmethod
    def Delete_Image():
        selected_image:list = Controller.Table_Slike.item(Controller.Table_Slike.focus())['values'][1:7]
        print(selected_image)
        ID, id_pacijent, PatientName, Opis, Format, Velicina = selected_image
        selected_image_description = f'{ID}: {PatientName} - {Opis} : ({Format} - {Velicina})'
        confirm = Messagebox.yesno(parent=Controller.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete\n{selected_image_description}?', alert=True)
        if confirm == 'Yes':
            def message_success():
                Messagebox.show_info(parent=Controller.MessageBoxParent,
                        title=f'Deleting successfull', message=f'Deleted {selected_image_description}\nfrom Database and Google Drive')
                SelectDB.refresh_tables(['Slike'])
                SelectDB.fill_PatientForm()
            def message_fail():
                Messagebox.show_info(parent=Controller.MessageBoxParent,
                        title=f'Deleting failed', message=f'Deleted {selected_image_description}\nfrom Database\nFailed to delete from Google Drive\nConnection problem')
                SelectDB.refresh_tables(['Slike'])
                SelectDB.fill_PatientForm()

            def execute_delete_image():   
                GoogleID = RHMH.execute_selectquery(f'SELECT image_data from slike WHERE id_slike = {ID}')[0][0]
                RHMH.execute_Delete('slike',[('id_slike',ID)])
                print('DELETING ',GoogleID)
                try:
                    GoogleDrive.delete_file(GoogleID)
                    Controller.ROOT.after(WAIT,message_success)
                except Exception:
                    Controller.ROOT.after(WAIT,message_fail)

            threading.Thread(target=execute_delete_image).start()

    @Controller.block_manageDB()
    @staticmethod
    def Delete_MKB():
        ID, mkb, opis = Controller.Table_MKB.item(Controller.Table_MKB.focus())['values'][1:]
        confirm = Messagebox.yesno(parent=Controller.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete {mkb}?', alert=True)
        if confirm=='Yes':
            RHMH.execute_Delete('mkb10',[('id_dijagnoza',ID)])

            Messagebox.show_info(parent=Controller.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {mkb}')
            
            logging = f' - MKB:\n{mkb}\n'
            logging += f'\n - Opis:\n{opis}'

            Controller.MKB_validation_LIST = [i[0] for i in RHMH.execute_select(False,'mkb10',*('MKB - šifra',))]
            ManageDB.LoggingData(query_type='Delete MKB',loggingdata=logging)
            SelectDB.refresh_tables(table_names=['Katalog'])
    
    @Controller.block_manageDB()
    @staticmethod
    def Delete_Zaposleni():
        ID, name = Controller.Table_Zaposleni.item(Controller.Table_Zaposleni.focus())['values'][1:]
        confirm = Messagebox.yesno(parent=Controller.MessageBoxParent,
                title=f'Deleting...', message=f'Are you sure you want to delete {name}?', alert=True)
        if confirm=='Yes':
            RHMH.execute_Delete('zaposleni',[('id_zaposleni',ID)])
            Messagebox.show_info(parent=Controller.MessageBoxParent,
                    title=f'Deleting successfull', message=f'Deleted {name}')
            
            Controller.Zaposleni_validation_LIST = [i[0] for i in RHMH.execute_select(False,'zaposleni',*('Zaposleni',))]
            ManageDB.LoggingData(query_type='Delete Employee',loggingdata=f' - Ime:\n{name}')
            SelectDB.refresh_tables(table_names=['Katalog'])

    @staticmethod
    def Download_SelectedImages():
        images = Controller.Table_Slike.selection()
        if not images:
            Messagebox.show_warning(parent=Controller.MessageBoxParent,
                title=f'Download Images!', message='You need to select atleast one row')
            return
        imagesID = []
        imagesName = []
        imageSize = []
        width = 0

        def get_db_data():
            nonlocal width
            for image in images:
                ID = Controller.Table_Slike.item(image)['values'][1]
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
            text_widget,floodgauge = Media.ProgressBar_DownloadingImages(Controller.MessageBoxParent,'Downloading',imagesName,width)
            def download():
                progress = 0
                totalMB = sum(imageSize)
                if not os.path.exists(save_directory):
                    os.makedirs(save_directory)
                for i,(GoogleID,imageName) in enumerate(zip(imagesID,imagesName)):
                    if i>5:
                        text_widget.yview_scroll(1,'units')
                    destination_path = os.path.join(save_directory, imageName)
                    media_data = GoogleDrive.download_BLOB(GoogleID)
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
                        Controller.MessageBoxParent.update_idletasks()
                    except Exception:
                        return # Ovo je da se prekine download na close 
            thread = threading.Thread(target=download)
            thread.start()

    @staticmethod
    def Image_Read( result_queue):
        try:
            data = result_queue.get_nowait()
            report = ''
            for col,val in data.items():
                if val:
                    if isinstance(val,list):
                        val = ' , '.join(val) if col not in ['Asistent','Gostujući Specijalizant'] else ',\n'.join(val)
                    for table in Controller.Patient_FormVariables.keys():
                        try:
                            widget = Controller.Patient_FormVariables[table][col]
                            break
                        except KeyError:
                            continue
                    report += f'{col}\n  - {val}\n'
                    ManageDB.set_widget_value(widget,val)
            else:
                retry = Messagebox.show_question(parent=Controller.MessageBoxParent,
                        title='Fill From Image', message=report, buttons=['Retry:secondary','Ok:primary'])
                if retry == 'Retry':
                    ManageDB.Fill_FromImage(firsttry=False)
        except queue.Empty:
            Controller.ROOT.after(50, ManageDB.Image_Read, result_queue)

    @staticmethod
    def Fill_FromImage(firsttry=True):
        try:
            slika = Controller.Patient_FormVariables['slike']['Slike'].item(
                    Controller.Patient_FormVariables['slike']['Slike'].focus()
                    )['values'][1].split('_')
        except IndexError:
            Messagebox.show_error(parent=Controller.MessageBoxParent,
                    title=f'Fill From Image', message='No image selected!')
            return
        if 'Operaciona' in slika[1]:
            GoogleID = RHMH.execute_selectquery(f'SELECT image_data FROM slike WHERE id_slike = {slika[0]}')[0][0]

            queue_get_blob = queue.Queue()
            thread = threading.Thread(target=Controller.get_image_fromGD,args=(GoogleID,queue_get_blob))
            thread.start()

            response = Media.ImageReader_SettingUp(Controller.MessageBoxParent)
            if response != 'Run':
                return

            thread.join()
            Media.Downloading = False
            image_blob = queue_get_blob.get()

            queue_analyzed_data = queue.Queue()
            def execute_fullscreen():
                SelectDB.Show_Image_FullScreen(BLOB=image_blob)
            def image_reader_with_queue(image, queue):
                data = Media.Operaciona_Reader(image)
                queue.put(data)

            if firsttry is True:
                thread1 = threading.Thread(target=execute_fullscreen)
                thread1.start()
            thread2 = threading.Thread(target=image_reader_with_queue, args=(image_blob,queue_analyzed_data))
            thread2.start()
            ManageDB.Image_Read(queue_analyzed_data)
        else:
            report = 'Image description ("Opis")\nhave to be "Operaciona Lista" or "Otupusna lista"'
            Messagebox.show_error(parent=Controller.MessageBoxParent,
                    title=f'Fill From Image', message=report)

    @staticmethod
    def Validation_Method(event=None,form=None):
        if form is None or form == 'Default':
            Controller.Valid_Default = True

            for col,widget in Controller.Patient_FormVariables['pacijent'].items():
                if 'Datum' in col:
                    if widget:
                        value = ManageDB.get_widget_value(widget)
                        if value:
                            try:
                                datetime.strptime(value, '%d-%b-%Y')
                            except:
                                Controller.Valid_Default = False
        elif form is None or form == 'Alternative':
            Controller.Valid_Alternative = True

        
        form = ['Default','Alternative'] if form is None else [form]
        print(form)
        for FORM in form:
            for widget in Controller.Validation_Widgets[FORM]:
                widget:Widget
                widget.focus_force()

        Controller.MessageBoxParent.focus_force()

    @staticmethod
    def validate_notblank(x) -> bool:
        if not x.strip():
            Controller.Valid_Default = False
            return False
        else:
            return True        

    @staticmethod
    def validate_godiste(x:str) -> bool:
        if x.isdigit() and len(x)==4:
            return True
        else:
            Controller.Valid_Default = False
            return False

    @staticmethod
    def validate_dijagnoza(x) -> bool:
        if ',' in x:
            mkb = x.split(',')
            for i in mkb:
                fix = i.strip()
                if fix not in Controller.MKB_validation_LIST:
                    Controller.Valid_Default = False
                    return False
            else:
                return True
        elif x.strip() and not (x.strip() in Controller.MKB_validation_LIST):
            Controller.Valid_Default = False
            return False
        else:
            return True

    @staticmethod    
    def validate_zaposleni(x) -> bool:
        if x.strip() and not (x.strip() in Controller.Zaposleni_validation_LIST):
            Controller.Valid_Alternative = False
            return False
        else:
            return True
    
    @staticmethod
    def validate_zaposleni_Text(event) -> bool:
        widget:Text = event.widget
        parent:Frame = widget.master
        value = widget.get('1.0', END)
        if ',' in value:
            zaposleni = value.split(',')
            for i in zaposleni:
                fix = i.strip()
                if fix not in Controller.Zaposleni_validation_LIST:
                    Controller.Valid_Alternative = False
                    parent.config(highlightbackground=ThemeColors['danger'], highlightcolor=ThemeColors['danger'])
            else:
                parent.config(highlightbackground=ThemeColors['selectbg'], highlightcolor=ThemeColors['primary'])
        elif value.strip() and not (value.strip() in Controller.Zaposleni_validation_LIST):
            Controller.Valid_Alternative = False
            parent.config(highlightbackground=ThemeColors['danger'], highlightcolor=ThemeColors['danger'])
        else:
            parent.config(highlightbackground=ThemeColors['selectbg'], highlightcolor=ThemeColors['primary'])

    @staticmethod
    def export_table(method:callable):
        focus = Controller.NoteBook.index(Controller.NoteBook.select())
        TAB = Controller.NoteBook.tab(focus,'text')
        table:tb.ttk.Treeview = Controller.Table_Names[TAB]
        table = table if not isinstance(table,tuple) else table[0]

        data_frame = dict()
        headings = SelectDB.table_headings(table)

        for i,item_id in enumerate(method(table)):
            item_data = table.item(item_id)['values']
            for col,val in zip(headings,item_data):
                if col=='ID' or 'id_' in col:
                    continue
                if col not in data_frame:
                    data_frame[col] = {}
                data_frame[col][i+1] = val

        export_data = pd.DataFrame(data_frame)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                    filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            export_data.to_excel(file_path)

    @staticmethod
    def FreeQuery_Execute():
        query = Controller.FreeQuery.get()
        if not query:
            return
        report = RHMH.format_sql(query)
        response = Messagebox.yesno(parent=Controller.MessageBoxParent, title='Free Query executing...', message=report)
        if response == 'Yes':
            RHMH.connect()
            RHMH.cursor.execute(query)
            RHMH.connection.commit()
            RHMH.close_connection()

    @staticmethod
    def Upload_DB():
        print("Uploading")

if __name__=='__main__':
    pass