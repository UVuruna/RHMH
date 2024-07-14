from A1_Variables import *

class Database:
    def __init__(self,database) -> None:
        self.database = database
        self.connection = None
        self.cursor = None
        self.lock = threading.Lock()

    def start_RHMH_db(self):
        self.PatientQuery = str()
        self.LoggingQuery:str = None

        self.LastQuery = {
            'pacijent': None,
            'slike': None,
            'mkb10': None,
            'zaposleni': None,
            'logs': None,
            'session': None
        }

        self.pacijent = self.show_columns('pacijent')
        self.slike = self.show_columns('slike')[:-1]
        self.mkb10 = self.show_columns('mkb10')
        self.zaposleni = self.show_columns('zaposleni')     
        self.logs = self.show_columns('logs')[:-2]
        self.session = self.show_columns('session')

        self.email = [i[0] for i in RHMH.execute_selectquery('SELECT Email FROM Logs UNION SELECT Email FROM Session')]
        self.pol = [i[0] for i in RHMH.execute_selectquery("SELECT DISTINCT Pol from pacijent")]
        self.opis_slike = [i[0] for i in RHMH.execute_selectquery("SELECT DISTINCT Opis from slike")]
        self.format_slike = [i[0] for i in RHMH.execute_selectquery("SELECT DISTINCT Format from slike")]
        
        self.dg_kategorija = [i[0] for i in self.execute_selectquery('SELECT Kategorija from kategorija')]
        self.dr_funkcija = [i[0] for i in self.execute_selectquery('SELECT Funkcija from funkcija')]

    def format_sql(self,query):
        formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')
        return formatted_query

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
                query = f'PRAGMA table_info({table})'

                self.cursor.execute(query)
                table = self.cursor.fetchall()
                return [i[1] for i in table]
            finally:
                self.close_connection()

    def creating_where_part(self, column:str, values:dict):
        returnquery = ''
        for sign,value in values.items():
            if sign == 'EQUAL':
                if len(value)>1:
                    value = [f'"{v}"' for v in value]
                    returnquery += f'{column} IN ({', '.join(value)}) OR '
                else:
                    returnquery += f'{column} = "{list(value)[0]}" OR '
            elif sign in ['LIKE','NOT LIKE']:
                operator = 'OR' if sign=='LIKE' else 'AND'
                for val in value:
                    returnquery += f'{column} {sign} "%{val}%" {operator} '
            elif sign == 'BETWEEN':
                for val in value:
                    returnquery += f'( {column} {sign} "{val[0]}" AND "{val[1]}" ) OR '


        returnquery = returnquery.rstrip(' OR ')
        returnquery = returnquery.rstrip(' AND ')
        return returnquery
         
    def execute_selectquery(self,query,columns=False):
        with self.lock:
            try:
                self.connect()
                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                view = self.cursor.fetchall()
                if columns is True:
                    column_names = [description[0] for description in self.cursor.description]
                    return view,column_names
                return view
            finally:
                self.close_connection()

    def execute_select(self, log:bool, table:str, *args, **kwargs):
        try:
            self.lock.acquire()
            select_values = ','.join(f'`{a}`' if ' ' in a else a for a in args)
            where_pairs = ''

            self.lock.release()
            for col,values in kwargs.items():
                col = col if ' ' not in col else f'`{col}`'
                where_pairs += f'( {self.creating_where_part(col,values)} ) AND '

            where_pairs = where_pairs.rstrip(' AND ')
            self.lock.acquire()
            
            query = f'SELECT {select_values} FROM {table}'
            if where_pairs:
                query += f' WHERE {where_pairs}'
            
            if 'FROM pacijent' in query:
                self.PatientQuery = query

            self.LoggingQuery = self.format_sql(query)
            if log is True:
                self.LastQuery[table] = query

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
            select_values = ''
            joindiagnose = False
            joinoperation = False
            for val in args:
                column = f'`{val}`' if ' ' in val else val
                if val in self.dg_kategorija:
                    joindiagnose = True
                    self.lock.release()
                    kategorija = self.execute_selectquery(f'SELECT id_kategorija from kategorija WHERE Kategorija = "{val}"')[0][0]
                    self.lock.acquire()
                    select_values += f'GROUP_CONCAT(DISTINCT CASE WHEN dijagnoza.id_kategorija={kategorija} THEN `MKB - šifra` END) AS {column},'
                elif val in self.dr_funkcija:
                    joinoperation = True
                    self.lock.release()
                    funkcija = self.execute_selectquery(f'SELECT id_funkcija from funkcija WHERE Funkcija = "{val}"')[0][0]
                    self.lock.acquire()
                    select_values += f'GROUP_CONCAT(DISTINCT CASE WHEN operacija.id_funkcija = {funkcija} THEN Zaposleni END) AS {column},'
                else:
                    select_values += f'{table}.{column},'
            select_values = select_values.rstrip(',')

            self.lock.release()
            where_pairs = ''
            having_pairs=''
            for col,values in kwargs.items():
                COL = col if ' ' not in col else f'`{col}`'
                if col in self.dg_kategorija:
                    joindiagnose = True
                    having_pairs += f'( {self.creating_where_part(COL,values)} ) AND '
                elif col in self.dr_funkcija:
                    joinoperation = True
                    having_pairs += f'( {self.creating_where_part(COL,values)} ) AND '
                else:
                    where_pairs += f'( {self.creating_where_part(COL,values)} ) AND '

            having_pairs = having_pairs.rstrip(' AND ')
            where_pairs = where_pairs.rstrip(' AND ')
            self.lock.acquire()

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
                query += f'WHERE {where_pairs} '
            query += f'GROUP BY {table}.id_pacijent'
            if having_pairs:
                query += f' HAVING {having_pairs}'

            if 'FROM pacijent' in query:
                self.PatientQuery = query
            self.LoggingQuery = self.format_sql(query)
            self.LastQuery[table] = query
            print(self.LoggingQuery)

            self.connect()
            self.cursor.execute(query)
            view = self.cursor.fetchall()
            return view
        finally:
            self.close_connection()
            self.lock.release()
 
    def execute_filter_select(self,columns:dict):
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
                self.LastQuery['pacijent'] = query

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
                query = f'DELETE FROM {table} WHERE {where}'

                self.LoggingQuery = self.format_sql(query)
                self.cursor.execute(query)
                self.connection.commit()
            finally:
                self.close_connection()

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

    def get_distinct_mkb(self,mkb=None,IDS=None):
        mkb = '' if not mkb else mkb
        with self.lock:
            try:
                self.connect()
                query = f'SELECT DISTINCT SUBSTR(mkb10.`MKB - šifra`,1,{len(mkb)+1}) FROM dijagnoza JOIN mkb10 ON dijagnoza.id_dijagnoza = mkb10.id_dijagnoza'
                if mkb:
                    query += f' WHERE `MKB - šifra` LIKE "{mkb}%"'
                    if IDS:
                        query += f' AND dijagnoza.id_pacijent IN ({', '.join([str(i) for i in IDS])}) '
                else:
                    if IDS:
                        query += f' WHERE dijagnoza.id_pacijent IN ({', '.join([str(i) for i in IDS])}) '
                    
                query += ' GROUP BY `MKB - šifra`'
                self.LoggingQuery = self.format_sql(query)

                self.cursor.execute(query)
                result = self.cursor.fetchall()
                return [i[0] for i in result]
            finally:
                self.close_connection()
    
    def get_distinct_zaposleni(self,funkcija=None,IDS=None):
        with self.lock:
            try:
                self.connect()
                query = f'SELECT DISTINCT Zaposleni FROM operacija '
                query += 'JOIN zaposleni ON operacija.id_zaposleni = zaposleni.id_zaposleni '
                if funkcija:
                    query += 'JOIN funkcija ON operacija.id_funkcija = funkcija.id_funkcija '
                    query += f'WHERE funkcija.Funkcija = "{funkcija}" '
                    if IDS:
                        query += f' AND operacija.id_pacijent IN ({', '.join([str(i) for i in IDS])}) '
                else:
                    if IDS:
                        query += f' WHERE operacija.id_pacijent IN ({', '.join([str(i) for i in IDS])}) '
                query += 'GROUP BY Zaposleni'
                self.LoggingQuery = self.format_sql(query)

                self.cursor.execute(query)
                result = self.cursor.fetchall()
                return [i[0] for i in result]
            finally:
                self.close_connection()

    def get_distinct_date(self,datetype,datewhere,IDS=None):
        with self.lock:
            try:
                self.connect()
                query = f'SELECT DISTINCT strftime("{datetype}", `{datewhere}`) FROM pacijent '
                query += f'WHERE `{datewhere}` IS NOT NULL'
                if IDS:
                    query += f' AND pacijent.id_pacijent IN ({', '.join([str(i) for i in IDS])}) '
                self.LoggingQuery = self.format_sql(query)

                self.cursor.execute(query)
                result = self.cursor.fetchall()
                result = [i[0] for i in result]
                result.sort()
                return result
            finally:
                self.close_connection()

    def get_distinct(self,table,*args):
        with self.lock:
            try:
                self.connect()
                query = f'SELECT DISTINCT {', '.join([*args])} FROM {table}'
                self.LoggingQuery = self.format_sql(query)

                self.cursor.execute(query)
                result = self.cursor.fetchall()
                result = [' '.join(i) for i in result]
                result.sort()
                return result
            finally:
                self.close_connection()

    def Vaccum_DB(self):
        with self.lock:
            try:
                self.connect()
                self.cursor.execute('VACUUM')
            finally:
                self.close_connection()

RHMH = Database(RHMH_dict['path'])
SLIKE = Database('SLIKE.db')

if __name__=='__main__':
    RHMH = Database('RHMH.db')
    RHMH.start_RHMH_db()
    print(RHMH.pacijent)
    print(RHMH.slike)
    print(RHMH.mkb10)
    print(RHMH.zaposleni)
    print(RHMH.dg_kategorija)
    print(RHMH.dr_funkcija)
    print(RHMH.logs)
    print(RHMH.session)

    print(RHMH.opis_slike)
    print(RHMH.format_slike)
    print(RHMH.pol)
    

    table = RHMH.execute_selectquery('SELECT Email FROM Logs UNION SELECT Email FROM Session')
    print(table)

    print(RHMH.get_distinct('slike',*('Opis',)))

    print(RHMH.execute_select('slike','*'))