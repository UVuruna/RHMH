from A_Variables import *
from B_Decorators import password,error_catcher,method_efficency
from C_GoogleDrive import GoogleDrive

class PasswordDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.password = None
        super().__init__(parent, title)

    def body(self, master):
        self.password_entry = tb.Entry(master, show='*')
        self.password_entry.grid(row=0, column=1, padx=10, pady=10)
        return self.password_entry

    def apply(self):
        self.password = self.password_entry.get()

class Database:
    def __init__(self,database) -> None:
        self.GD = GoogleDrive()
        self.UserSession = {'User':EMAIL,'ProccessingTime':{},'TotalTime':{}}
        self.Admin = False
        self.GodMode = False
        self.database = database

        self.connection = None
        self.cursor = None
        self.PatientQuery = str()
        self.LoggingQuery = None

        self.lock = threading.Lock()

        # KOLONE TABELA
        self.pacijent = self.show_columns('pacijent')[1:]
        self.slike = self.show_columns('slike')[2:-1]
        self.mkb10 = self.show_columns('mkb10')[1:]
        self.zaposleni = self.show_columns('zaposleni')[1:]      
        self.logs = self.show_columns('logs')[:-2]
        self.session = self.show_columns('session')[1:]

        self.dg_kategorija = [i[0] for i in self.execute_selectquery('SELECT Kategorija from kategorija')]
        self.dr_funkcija = [i[0] for i in self.execute_selectquery('SELECT Funkcija from funkcija')]

    def GodMode_Password(self,event,parent,notebook:tb.Notebook):
        if not self.Admin:
            dialog = PasswordDialog(parent, 'GodMode Unlocking...')
            if dialog.password=='666':
                self.Admin = True
                notebook.select(3)
            elif dialog.password==password():
                self.Admin = True
                self.GodMode = True
        else:
            txt = 'GodMode' if self.GodMode else 'Admin'
            dialog = PasswordDialog(parent, f'{txt} Removing...')
            if dialog.password=='33':
                self.Admin = False
                self.GodMode = False

    def connect(self):
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def show_columns(self,table):
        with self.lock:
            try:
                self.connect()
                table = f'`{table}`' if ' ' in table else table
                query = f'PRAGMA table_info({table})'

                self.cursor.execute(query)
                table = self.cursor.fetchall()
                return [i[1] for i in table]
            finally:
                self.close_connection()

    def format_sql(self,query):
        formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')
        return formatted_query

    def creating_where_part(self, col:str, value:str, andor:str):
        if isinstance(value,tuple) and len(value)==2:
            return f'( {col} BETWEEN "{value[0]}" AND "{value[1]}" ) {andor} '
        elif isinstance(value,tuple) and len(value)==1:
            TXT = col.replace('`','')
            if TXT in self.dg_kategorija:
                self.lock.release()
                kategorija = self.execute_selectquery(f'SELECT id_kategorija from kategorija WHERE Kategorija = "{TXT}"')[0][0]
                self.lock.acquire()
                return f'( `MKB - šifra` LIKE "%{value[0]}%" AND dijagnoza.id_kategorija = {kategorija} ) {andor} '
            elif TXT in self.dr_funkcija:
                self.lock.release()
                funkcija = self.execute_selectquery(f'SELECT id_funkcija from funkcija WHERE Funkcija = "{TXT}"')[0][0]
                self.lock.acquire()
                return f'( Zaposleni LIKE "%{value[0]}%" AND operacija.id_funkcija = {funkcija} ) {andor} '
            else:
                return f'{col} LIKE "%{value[0]}%" {andor} '
        else:
            return f'{col} = "{value}" {andor} '
         
    def execute_selectquery(self,query):
        with self.lock:
            try:
                self.connect()
                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                return view
            finally:
                self.close_connection()

    def execute_select(self, table, *args, **kwargs):
        try:
            self.lock.acquire()
            table = f'`{table}`' if ' ' in table else table       
            select_values = ','.join(f'`{a}`' if ' ' in a else a for a in args)
            where_pairs = ''

            for k,v in kwargs.items():
                if v:
                    col = f'`{k}`' if ' ' in k else k
                    if isinstance(v,set):
                        where_pairs += '( '
                        for val in v:
                            where_pairs += self.creating_where_part(col,val,'OR')
                        where_pairs = where_pairs.rstrip(' OR ') + ' ) AND '
                    else:
                        where_pairs += self.creating_where_part(col,v,'AND')
            where_pairs = where_pairs.rstrip(' AND ')
            
            query = f'SELECT {select_values} FROM {table}'
            if where_pairs:
                query += f' WHERE {where_pairs}'
            
            if 'FROM pacijent' in query:
                self.PatientQuery = query

            self.LoggingQuery = self.format_sql(query)
            self.connect()
            self.cursor.execute(query)
            view = self.cursor.fetchall()
            return view
        finally:
            self.close_connection()
            self.lock.release()
        
    def execute_join_select(self, table, *args, **kwargs):
        try:
            self.lock.acquire()
            table = f'`{table}`' if ' ' in table else table
            select_values = ''
            joindiagnose = False
            joinoperation = False
            for val in args:
                TXT = f'`{val}`' if ' ' in val else val
                if val in self.dg_kategorija:
                    joindiagnose = True
                    self.lock.release()
                    kategorija = self.execute_selectquery(f'SELECT id_kategorija from kategorija WHERE Kategorija = "{val}"')[0][0]
                    self.lock.acquire()
                    select_values += f'GROUP_CONCAT(DISTINCT CASE WHEN dijagnoza.id_kategorija={kategorija} THEN `MKB - šifra` END) AS {TXT},'
                elif val in self.dr_funkcija:
                    joinoperation = True
                    self.lock.release()
                    funkcija = self.execute_selectquery(f'SELECT id_funkcija from funkcija WHERE Funkcija = "{val}"')[0][0]
                    self.lock.acquire()
                    select_values += f'GROUP_CONCAT(DISTINCT CASE WHEN operacija.id_funkcija = {funkcija} THEN Zaposleni END) AS {TXT},'
                else:
                    select_values += f'{table}.{TXT},'
            select_values = select_values.rstrip(',')

            where_pairs = ''
            for k,v in kwargs.items():
                TXT = f'`{k}`' if ' ' in k else k
                if k in self.dg_kategorija:
                    joindiagnose = True
                elif k in self.dr_funkcija:
                    joinoperation = True

                if isinstance(v,set):
                    where_pairs += '( '
                    for val in v:
                        where_pairs += self.creating_where_part(TXT,val,'OR')
                    where_pairs = where_pairs.rstrip(' OR ') + ' ) AND '
                else:
                    where_pairs += self.creating_where_part(TXT,v,'AND')
            where_pairs = where_pairs.rstrip(' AND ')

            join_tables = ''
            if joindiagnose:
                join_tables += f'LEFT JOIN dijagnoza ON {table}.id_pacijent = dijagnoza.id_pacijent ' + \
                                f'LEFT JOIN mkb10 ON dijagnoza.id_dijagnoza = mkb10.id_dijagnoza ' + \
                                f'LEFT JOIN kategorija ON dijagnoza.id_kategorija = kategorija.id_kategorija '
                
            if joinoperation:
                join_tables += f'LEFT JOIN operacija ON {table}.id_pacijent = operacija.id_pacijent ' + \
                                f'LEFT JOIN funkcija ON operacija.id_funkcija = funkcija.id_funkcija ' + \
                                f'LEFT JOIN zaposleni ON operacija.id_zaposleni = zaposleni.id_zaposleni '

            query = f'SELECT {select_values} FROM {table} {join_tables} '
            if where_pairs:
                query += f' WHERE {where_pairs}'
            query += f' GROUP BY {table}.id_pacijent'

            if 'FROM pacijent' in query:
                self.PatientQuery = query
            self.LoggingQuery = self.format_sql(query)

            self.connect()
            self.cursor.execute(query)
            view = self.cursor.fetchall()
            return view
        finally:
            self.close_connection()
            self.lock.release()
 
    def execute_filter_select(self,columns):
        if not self.PatientQuery or 'FROM pacijent' not in self.PatientQuery:
            return
        with self.lock:
            try:
                wherenull = 'WHERE '
                for k,v in columns.items():
                    null = 'IS NOT NULL' if v else 'IS NULL'
                    txt = f'`{k}`' if ' ' in k else k
                    wherenull += f'pacijent.{txt} {null} AND '
                wherenull = wherenull.rstrip(' AND ')

                if 'WHERE' in self.PatientQuery:
                    fix = self.PatientQuery.split('WHERE')
                    query = fix[0]+f'{wherenull} AND '+fix[1]
                elif 'GROUP BY' in self.PatientQuery:
                    fix = self.PatientQuery.split('GROUP BY')
                    query = fix[0]+f'{wherenull} GROUP BY'+fix[1]
                else:
                    query = self.PatientQuery+f' {wherenull}'

                self.LoggingQuery = self.format_sql(query)
            
                self.connect()
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                return view
            finally:
                self.close_connection()

    def get_patient_data(self,ID):
        try:
            self.lock.acquire()
            SELECT = ''
            for col in self.pacijent:
                SELECT += 'pacijent.'
                SELECT += f'`{col}`, ' if ' ' in col else f'{col}, '
            for col in self.dg_kategorija:
                TXT = f'`{col}`' if ' ' in col else col
                self.lock.release()
                kategorija = self.execute_selectquery(f'SELECT id_kategorija from kategorija WHERE Kategorija = "{col}"')[0][0]
                self.lock.acquire()
                SELECT += f'GROUP_CONCAT(DISTINCT CASE WHEN dijagnoza.id_kategorija={kategorija} THEN `MKB - šifra` END) AS {TXT},'
            for col in self.dr_funkcija:
                TXT = f'`{col}`' if ' ' in col else col
                self.lock.release()
                funkcija = self.execute_selectquery(f'SELECT id_funkcija from funkcija WHERE funkcija.Funkcija = "{col}"')[0][0]
                self.lock.acquire()
                SELECT += f'GROUP_CONCAT(DISTINCT CASE WHEN operacija.id_funkcija={funkcija} THEN Zaposleni END) AS {TXT},'
            SELECT += 'GROUP_CONCAT(DISTINCT slike.Naziv || "," || slike.Veličina || "," || slike.width || "," || slike.height) AS Slike'


            diagnosejoin = f'LEFT JOIN dijagnoza ON pacijent.id_pacijent = dijagnoza.id_pacijent ' + \
                                f'LEFT JOIN mkb10 ON dijagnoza.id_dijagnoza = mkb10.id_dijagnoza ' + \
                                f'LEFT JOIN kategorija ON dijagnoza.id_kategorija = kategorija.id_kategorija '
            operationjoin = f'LEFT JOIN operacija ON pacijent.id_pacijent = operacija.id_pacijent ' + \
                                f'LEFT JOIN funkcija ON operacija.id_funkcija = funkcija.id_funkcija ' + \
                                f'LEFT JOIN zaposleni ON operacija.id_zaposleni = zaposleni.id_zaposleni '
            slikejoin = f'LEFT JOIN slike ON pacijent.id_pacijent = slike.id_pacijent'
            JOIN = diagnosejoin+operationjoin+slikejoin

            query = f'SELECT {SELECT} FROM pacijent {JOIN} ' + \
                    f'WHERE pacijent.id_pacijent = {ID} GROUP BY pacijent.id_pacijent'

            self.LoggingQuery = self.format_sql(query)
            self.connect()
            self.cursor.execute(query)
            view = self.cursor.fetchall()
            column_names = [desc[0] for desc in self.cursor.description]

            DICTY = {}
            for col,val in zip(column_names,view[0]):
                if val:
                    if col=='Slike':
                        if ',' in val:
                            LIST = val.split(',')
                            val = []
                            for i in LIST:
                                val.append(i)
                        else:
                            val = [val]
                    DICTY[col] = val
            return DICTY
        finally:
            self.close_connection()
            self.lock.release()
      
    def execute_Update(self,table,id:tuple,**kwargs):
        with self.lock:
            try:
                self.connect()
                settin = ''
                loggin = ''
                value = []
                for k,v in kwargs.items():
                    txt = k if ' ' not in k else f'`{k}`'
                    settin += f'{txt} = ?, '
                    loggin += f'{txt} = {v}, '
                    value.append(v)
                settin = settin.rstrip(', ')
                loggin = loggin.rstrip(', ')
                value.append(id[1])
                value = tuple(value)

                table = table if ' ' not in table else f'`{table}`'
                logginquery = f'UPDATE {table} SET {loggin} WHERE {id[0]} = {id[1]}'
                query = f'UPDATE {table} SET {settin} WHERE {id[0]} = ?'

                self.LoggingQuery = self.format_sql(logginquery)
                self.cursor.execute(query,value)
                self.connection.commit()
            finally:
                self.close_connection()
    
    def execute_Insert(self,table,**kwargs):
        with self.lock:
            try:
                self.connect()
                counter = 0
                columns = ''
                loggin = ''
                values = []
                for k,v in kwargs.items():
                    if v:
                        txt = k if ' ' not in k else f'`{k}`'
                        columns += f'{txt}, '
                        loggin += f'{v}, '
                        values.append(v)
                        counter+=1
                columns = columns.rstrip(', ')
                loggin = loggin.rstrip(', ')
                values = tuple(values)

                table = table if ' ' not in table else f'`{table}`'
                query = f'INSERT INTO {table} ({columns}) VALUES ({('?, '*counter).rstrip(', ')})'
                logginquery = f'INSERT INTO {table} ({columns}) VALUES ({loggin})'

                self.LoggingQuery = self.format_sql(logginquery)
                self.cursor.execute(query,values)
                self.connection.commit()
                self.cursor.execute('SELECT last_insert_rowid()')
                return self.cursor.fetchone()[0]
            finally:
                self.close_connection()
    
    def execute_Delete(self,table,ids:list):
        with self.lock:
            try:
                self.connect()
                self.cursor.execute('PRAGMA foreign_keys=ON')
                where = ''
                for ID in ids:
                    where += f'{ID[0]} = {ID[1]} AND '
                where = where.rstrip(' AND ')
                table = table if ' ' not in table else f'`{table}`'
                query = f'DELETE FROM {table} WHERE {where}'

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                self.connection.commit()
            finally:
                self.close_connection()

    #'''
    def get_imageBlob(self,id):
        with self.lock:
            try:
                self.connect()
                query = f'SELECT image_data FROM slike WHERE id_slike = {id}'
                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                if result:
                    return result[0]
            finally:
                self.close_connection()
                #'''

    def Vaccum_DB(self):
        with self.lock:
            try:
                self.connect()
                self.cursor.execute('VACUUM')
            finally:
                self.close_connection()

if __name__=='__main__':
    rhmh = Database('RHMH.db')
    print(rhmh.get_patient_data(15))