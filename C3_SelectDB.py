from A1_Variables import *
from A2_Decorators import PasswordDialog,money
from B3_Media import Media
from B2_SQLite import RHMH
from C1_Controller import Controller


class SelectDB(Controller):
    
    @staticmethod
    def GodMode_Password(event):
        dialog = PasswordDialog(Controller.MessageBoxParent, 'Privileges Unlocking...')
        if dialog.password=='63636':
            Controller.Admin = True
            info = 'New tabs:\n\t-Logs\n\t-Session'
            title = 'Admin unlocked'
        elif dialog.password=='C12-Si28-C13-Si28-C12':
            Controller.Admin = True
            Controller.GodMode = True
            Controller.FreeQuery_Frame.grid()
            info = 'New tabs:\n\t-Logs\n\t-Session\n\n'
            info += 'New button:\n\t-Free Query'
            info += f'\n\n{money()}'
            title = 'God Mode unlocked'
        else:
            return
        Controller.ROOT.after(WAIT, lambda: Controller.NoteBook.select(5))
        Controller.ROOT.after(WAIT*2, lambda: Controller.NoteBook.select(4))
        Messagebox.show_info(parent=Controller.MessageBoxParent, message=info, title=title,)

    def table_headings(treeview:tb.ttk.Treeview):
        columns = treeview["columns"]
        headings = []
        for col in columns:
            headings.append(col)
        return headings

    @staticmethod
    def export_selection():
        focus = Controller.NoteBook.index(Controller.NoteBook.select())
        TAB = Controller.NoteBook.tab(focus,'text')
        table:tb.ttk.Treeview = Controller.Table_Names[TAB]
        
        data_frame = dict()
        headings = SelectDB.table_headings(table)

        for i,item_id in enumerate(table.selection()):
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
    def export_table(method:callable):
        focus = Controller.NoteBook.index(Controller.NoteBook.select())
        TAB = Controller.NoteBook.tab(focus,'text')
        table:tb.ttk.Treeview = Controller.Table_Names[TAB]

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
    def search_bar_remove(event=None):
        to_remove = [k for k in Controller.SearchBar_widgets.keys() if int(k[-1]) == Controller.SearchBar_number]
        for key in to_remove:
            widget:Frame = Controller.SearchBar_widgets[key]
            if 'bar' in key:
                widget.grid_remove()
            else:
                SelectDB.empty_widget(widget)
                if not ('option' in key):
                    widget.grid_remove()
        Controller.SearchBar_number-=1

        if not Controller.SearchAdd_Button.winfo_ismapped():
            Controller.SearchAdd_Button.grid()
        if Controller.SearchBar_number==1:
            Controller.SearchRemove_Button.grid_remove()

    @staticmethod
    def search_bar_add(event=None):
        if not Controller.SearchRemove_Button.winfo_ismapped():
            Controller.SearchRemove_Button.grid()
        Controller.SearchBar_number+=1
        Controller.SearchBar_widgets[f'search_option_{Controller.SearchBar_number}'].grid()
        Controller.SearchBar_widgets[f'search_bar_{Controller.SearchBar_number}'].grid()

        if Controller.SearchBar_number==max_searchby:
            Controller.SearchAdd_Button.grid_remove()

    @staticmethod
    def selected_columns( columns, table:tb.ttk.Treeview, columnvar:bool):

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
            elif table==Controller.Table_Zaposleni and col=='Zaposleni':
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
            elif col in ['Opis'] or table==Controller.Table_Session :
                table.column(col, width=F_SIZE*13, minwidth=F_SIZE*6)
            elif col in ['Dg Latinski','Error'] or (col == 'Zaposleni' and table == Controller.Table_Zaposleni):
                table.column(col, width=F_SIZE*27, minwidth=F_SIZE*13)
            elif col in ['Opis Dijagnoze']:
                table.column(col, width=F_SIZE*100)
            elif col in ['Naziv','Gostujući Specijalizant','Asistent'] or table == Controller.Table_Logs:
                table.column(col, width=F_SIZE*16, minwidth=F_SIZE*7)
            else:
                table.column(col, width=F_SIZE*12, minwidth=F_SIZE*6)
        table['show'] = 'headings'
        return Columns[1:]
    
    @staticmethod
    def search_options(n,event):
        search_option = Controller.SearchBar_widgets[f'search_option_{n}'].get()

        if search_option in ['Datum Prijema', 'Datum Operacije', 'Datum Otpusta', 'ID Time']:
            for widget_type,widget in Controller.SearchBar_widgets.items():
                if widget_type == f'search_sign_{n}':
                    widget:tb.Label # SAMO BETWEEN
                    widget.unbind('<ButtonRelease-1>')
                    widget.configure(image=Controller.signimages[-1], text=SIGNS[-1])

                widget.grid() if widget_type in [f'date1_{n}',f'date2_{n}'] or ('search' in widget_type and widget_type[-1]==str(n))  \
                    else widget.grid_remove() if widget_type[-1]==str(n) else None
                    
        elif search_option in ['Godište', 'Starost', 'Veličina', 'width', 'height', 'pixels']:
            for widget_type,widget in Controller.SearchBar_widgets.items():
                if widget_type == f'search_sign_{n}':
                    widget:tb.Label
                    images = Controller.signimages[::-1]
                    signs = SIGNS[::-1]
                    out = signs.index('LIKE')
                    images.pop(out)
                    signs.pop(out)
                    widget.bind('<ButtonRelease-1>', lambda event: SelectDB.search_options_swap(event,images,signs,n))
                    widget.configure(image=images[0], text=signs[0])

                widget.grid() if widget_type in [f'entry1_{n}',f'entry2_{n}'] or ('search' in widget_type and widget_type[-1]==str(n))  \
                    else widget.grid_remove() if widget_type[-1]==str(n) else None
                
        elif search_option in ['Pol', 'Format', 'Opis', 'Email']:
            for widget_type,widget in Controller.SearchBar_widgets.items():
                if widget_type == f'search_sign_{n}':
                    widget:tb.Label
                    images = Controller.signimages[:]
                    signs = SIGNS[:]
                    for out in [SIGNS.index('BETWEEN'),SIGNS.index('LIKE')]:
                        images.pop(out)
                        signs.pop(out)
                    widget.bind('<ButtonRelease-1>', lambda event: SelectDB.search_options_swap(event,images,signs,n))
                    widget.configure(image=images[0], text=signs[0])

                if widget_type==f'combo_{n}':
                    widget:tb.Combobox
                    values = RHMH.email if search_option=='Email' else \
                                RHMH.pol if search_option=='Pol' else \
                                    RHMH.opis_slike if search_option=='Opis' else \
                                        RHMH.format_slike if search_option=='Format' else None
                    widget.configure(values=values, height=len(values))

                widget.grid() if widget_type==f'combo_{n}' or ('search' in widget_type and widget_type[-1]==str(n)) \
                    else widget.grid_remove() if widget_type[-1]==str(n) else None
        else:
            for widget_type,widget in Controller.SearchBar_widgets.items():
                if widget_type == f'search_sign_{n}':
                    widget:tb.Label
                    images = Controller.signimages[:]
                    signs = SIGNS[:]
                    out = signs.index('BETWEEN')
                    images.pop(out)
                    signs.pop(out)
                    widget.bind('<ButtonRelease-1>', lambda event: SelectDB.search_options_swap(event,images,signs,n))
                    widget.configure(image=images[0], text=signs[0])

                widget.grid() if widget_type == f'entry1_{n}' or ('search' in widget_type and widget_type[-1]==str(n))  \
                    else widget.grid_remove() if widget_type[-1]==str(n) else None

    @staticmethod
    def search_options_swap(event, signimages:list, signorder:list, n:int):
        signlabel:tb.Label = event.widget
        for order in [signimages,signorder]: # rotation
            last_choice = order.pop(0) 
            order.append(last_choice)

        widg_type:str ; widget:tb.Entry ; widget:widgets.DateEntry
        for widg_type,widget in Controller.SearchBar_widgets.items():
            if widg_type[-1]!=str(n):
                continue
            if 'BETWEEN' in signorder:
                if widg_type == f'entry2_{n}':
                    if signorder[0] != 'BETWEEN':
                        widget.grid_remove()
                        Controller.empty_widget(widget)
                    else:
                        widget.grid()
                    break

        signlabel.configure(image=signimages[0], text=signorder[0])
        signlabel.bind('<ButtonRelease-1>', lambda event: SelectDB.search_options_swap(event, signimages, signorder, n))

    @staticmethod
    def Graph_afterchoice():
        show = ('bars','pie')
        hide = ()
        if Controller.Graph_FormVariables['X2-1'][1].get():
            show = ('bars','stacked')
            hide = ('color')
        for k,v in Controller.Graph_FormVariables['afterchoice'].items():
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

    @staticmethod
    def Graph_Options(event,option:str):
        widget:tb.Combobox = event.widget
        execute_button:ctk.CTkButton = Controller.buttons['SHOW Graph']
        add_button:tb.Label = Controller.Graph_FormVariables['Add']
        choice = widget.get()
        Values = []
        
        def removing_widgets(widgets_to_remove):
            widget:tb.Combobox
            stringvar:StringVar
            for widgetname in widgets_to_remove:
                widget,stringvar = Controller.Graph_FormVariables[widgetname]
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
                    first_stringvars:StringVar = Controller.Graph_FormVariables['X1-1'][1]
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
                    first_stringvars:StringVar = Controller.Graph_FormVariables['X1-1'][1]
                    check = not (first_stringvars.get() in ['Trauma', 'MKB Grupe','MKB Pojedinačno'])
                if check:
                    Next_Names = [option.replace('-1','-2')]
                    Values.append(RHMH.dg_kategorija)
            elif choice == 'Zaposleni':
                Next_Names = [option.replace('-1','-2')]
                Values.append(RHMH.dr_funkcija)
            else:
                SelectDB.Graph_afterchoice()
                add_button.grid()

        elif option in ['X1-2','X2-2']:
            combo3:tb.Combobox = Controller.Graph_FormVariables['X1-3'][0]
            if combo3.winfo_ismapped():
                if combo3.get():
                    SelectDB.Graph_afterchoice()
                    if int(option[1])==1:
                        add_button.grid()
            else:
                SelectDB.Graph_afterchoice()
                if int(option[1])==1:
                        add_button.grid()
            return
        elif option in ['X1-3','X2-3']:
            combo2:tb.Combobox = Controller.Graph_FormVariables['X1-2'][1]
            if combo2.get():
                SelectDB.Graph_afterchoice()
                if int(option[1])==1:
                        add_button.grid()
            return

        widgetnames = ['Y','X1-1','X1-2','X1-3','X2-1','X2-2','X2-3']
        removing_widgets(widgetnames[widgetnames.index(Next_Names[-1])+1:])
        if not Values:
            return
        for name,value in zip(Next_Names,Values):
            next_widget:tb.Combobox
            stringvar:StringVar
            next_widget,stringvar = Controller.Graph_FormVariables[name]

            width = len(max(value, key=len))
            width = width-5 if width>20 else 3 if width<3 else width-2
            next_widget.configure(values=value, width=width)
            stringvar.set('')
            if not next_widget.winfo_ismapped():
                next_widget.grid()

    @staticmethod
    def fill_TablePacijenti(table):
        Controller.MainTable_IDS.clear()
        for i, row in enumerate(table):
            # FROM RHMH Date Format TO Table Date Format
            formatted_row = [i+1] + [datetime.strptime(cell,'%Y-%m-%d').strftime('%d-%b-%y') if SelectDB.is_DB_date(cell) \
                                        else ' , '.join(cell.split(',')) if isinstance(cell,str) and ',' in cell \
                                            else '' if str(cell)=='None' \
                                                else cell for cell in row]
            Controller.MainTable_IDS.append(row[0])
            Controller.Table_Pacijenti.insert('', END, values=formatted_row)

    @staticmethod
    def fill_Tables_Other(view,table):
        for i, row in enumerate(view):
            formatted_row = [i+1] + [cell for cell in row]
            table.insert('', END, values=formatted_row)

    @staticmethod
    def fill_TableSlike(table):
        check = lambda x: True
        if Controller.buttons['Filter Main Table'][1].get():
            check = lambda col: col in Controller.MainTable_IDS
        for i, row in enumerate(table):
            if check(row[1]):
                formatted_row = [i+1] + [f'{cell:.2f} MB' if isinstance(cell,float) \
                                            else f'{cell/10**6:.2f} MP' if j==8 \
                                                else cell.split('_')[1] if j==2\
                                                    else cell for j,cell in enumerate(row)]
                Controller.Table_Slike.insert('', END, values=formatted_row)

    @staticmethod
    def showall_data(TAB=None):
        if TAB is None:
            focus = Controller.NoteBook.index(Controller.NoteBook.select())
            TAB = Controller.NoteBook.tab(focus,'text')

        if TAB == 'Pacijenti':
            columns = SelectDB.selected_columns(Controller.Pacijenti_ColumnVars.items() , Controller.Table_Pacijenti , columnvar=True)
            view = RHMH.execute_join_select('pacijent',*(columns))
          
            for item in Controller.Table_Pacijenti.get_children():
                Controller.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_TablePacijenti(view)

        elif TAB == 'Slike':
            view = RHMH.execute_select('slike',*(Controller.TableSlike_Columns[1:]))

            for item in Controller.Table_Slike.get_children():
                Controller.Table_Slike.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_TableSlike(view)

        elif TAB == 'Katalog':
            view = RHMH.execute_select('mkb10',*(Controller.TableMKB_Columns[1:]))
   
            for item in Controller.Table_MKB.get_children():
                Controller.Table_MKB.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_MKB)

            view = RHMH.execute_select('zaposleni',*(Controller.TableZaposleni_Columns[1:]))
   
            for item in Controller.Table_Zaposleni.get_children():
                Controller.Table_Zaposleni.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_Zaposleni)

        elif TAB == 'Logs':
            view = RHMH.execute_select('logs',*(Controller.TableLogs_Columns[1:]))
 
            for item in Controller.Table_Logs.get_children():
                Controller.Table_Logs.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_Logs)
        
        elif TAB == 'Session':
            view = RHMH.execute_select('session',*(Controller.TableSession_Columns[1:]))

            for item in Controller.Table_Session.get_children():
                Controller.Table_Session.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_Session)

    @staticmethod
    def search_data():
        focus = Controller.NoteBook.index(Controller.NoteBook.select())
        TAB = Controller.NoteBook.tab(focus,'text')

        def searching_dict_create() -> set:
            def saving_location(SIGN):
                if not SIGN in searching[option]:
                    searching[option][SIGN] = set()
                return searching[option][SIGN]
            
            searching = dict()

            for n in range(1,Controller.SearchBar_number+1):
                column_widget:tb.Combobox = Controller.SearchBar_widgets[f'search_option_{n}']
                if not column_widget.winfo_ismapped(): 
                    break # Stane cim prvi nije mapiran dalje nema nista

                option = Controller.get_widget_value(column_widget) # COLUMN
                if not option: 
                    return # Izlazi iz funkcija ako ima prazan SEARCH
                
                try:
                    searching[option]
                except KeyError:
                    searching[option] = dict()

                sign = Controller.get_widget_value(Controller.SearchBar_widgets[f'search_sign_{n}']) # SIGN
                searchlocation:set = saving_location(sign) # DICT lokacija gde ce ubacivati vrednost

                if sign == 'BETWEEN': # Dodaje TUPLE (x,y)
                    if 'Datum' in option or option=='ID Time':
                        # FROM Form Date Formate TO RHMH Date Format
                        fromdate = Controller.get_widget_value(Controller.SearchBar_widgets[f'date1_{n}'])
                        todate = Controller.get_widget_value(Controller.SearchBar_widgets[f'date2_{n}'])
                        try:
                            fromdate = datetime.strptime(fromdate,'%d-%b-%Y').strftime('%Y-%m-%d')
                            todate = datetime.strptime(todate,'%d-%b-%Y').strftime('%Y-%m-%d')
                        except Exception:
                            pass
                        searchlocation.add( ( fromdate, todate ) )
                    else:
                        From = Controller.get_widget_value(Controller.SearchBar_widgets[f'entry1_{n}'])
                        To = Controller.get_widget_value(Controller.SearchBar_widgets[f'entry2_{n}'])
                        searchlocation.add( ( From,To ) )

                elif sign in ['EQUAL','LIKE','NOT LIKE']:
                    if option in ['Pol', 'Format', 'Opis', 'Email']:
                        result = Controller.get_widget_value(Controller.SearchBar_widgets[f'combo_{n}'])
                    else:
                        result = Controller.get_widget_value(Controller.SearchBar_widgets[f'entry1_{n}'])
                    searchlocation.add( result )
            return searching

        if TAB == 'Pacijenti':
            columns = SelectDB.selected_columns(Controller.Pacijenti_ColumnVars.items() , Controller.Table_Pacijenti , columnvar=True)
            searching = searching_dict_create()
            view = RHMH.execute_join_select('pacijent',*(columns),**searching)

            for item in Controller.Table_Pacijenti.get_children():
                Controller.Table_Pacijenti.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_TablePacijenti(view)

        elif TAB == 'Slike':
            searching = searching_dict_create()
            view = RHMH.execute_select('slike',*(Controller.TableSlike_Columns[1:]),**searching)
  
            for item in Controller.Table_Slike.get_children():
                Controller.Table_Slike.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_TableSlike(view)

        elif TAB == 'Katalog':
            searching = searching_dict_create()
            view = RHMH.execute_select('mkb10',*(Controller.TableMKB_Columns[1:]),**searching)

            for item in Controller.Table_MKB.get_children():
                Controller.Table_MKB.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_MKB)

        elif TAB == 'Logs':
            searching = searching_dict_create()
            view = RHMH.execute_select('logs',*(Controller.TableLogs_Columns[1:]),**searching)
 
            for item in Controller.Table_Logs.get_children():
                Controller.Table_Logs.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_Logs)

        elif TAB == 'Session':
            searching = searching_dict_create()
            view = RHMH.execute_select('session',*(Controller.TableSession_Columns[1:]),**searching)

            for item in Controller.Table_Session.get_children():
                Controller.Table_Session.delete(item)
            if view and len(view)!=0:
                SelectDB.fill_Tables_Other(view,Controller.Table_Session)

    @staticmethod
    def filter_data(columns):
        where = {}
        for k,v in Controller.FilterOptions.items():
            if k in columns:
                where[k]=v[1].get()
        
        view = SelectDB.LoggingData(RHMH.execute_filter_select(where),'FILTER SELECT')
        for item in Controller.Table_Pacijenti.get_children():
            Controller.Table_Pacijenti.delete(item)
        if view and len(view)!=0:
            SelectDB.fill_TablePacijenti(view)

    @staticmethod
    def fill_MKBForm(event):
        try:
            row = Controller.Table_MKB.item(Controller.Table_MKB.focus())['values'][2:]
            for col,val in zip(Controller.TableMKB_Columns[2:],row):
                Controller.Katalog_FormVariables[col].set(val)
        except IndexError:
            return

    @staticmethod
    def MKB_double_click( event):
        try:
            column = SelectDB.get_widget_value(Controller.Katalog_FormVariables['Kategorija'])
            if column:
                mkb = Controller.Table_MKB.item(Controller.Table_MKB.focus())['values'][2]
                dg_Widget = Controller.Patient_FormVariables['dijagnoza'][column]
                dg_Value = SelectDB.get_widget_value(dg_Widget)
                if not dg_Value:
                    SelectDB.set_widget_value(dg_Widget,mkb)
                else:
                    SelectDB.set_widget_value(dg_Widget,f'{dg_Value} , {mkb}')
        except IndexError:
            return
    
    @staticmethod
    def fill_ZaposleniForm(event):
        try:
            name = Controller.Table_Zaposleni.item(Controller.Table_Zaposleni.focus())['values'][2]
            Controller.Katalog_FormVariables['Zaposleni'].set(name)
        except IndexError:
            return

    @staticmethod    
    def Zaposleni_double_click(event):
        try:
            column = SelectDB.get_widget_value(Controller.Katalog_FormVariables['Funkcija'])
            if column:
                mkb = Controller.Table_Zaposleni.item(Controller.Table_Zaposleni.focus())['values'][2]
                dg_Widget = Controller.Patient_FormVariables['operacija'][column]
                dg_Value = SelectDB.get_widget_value(dg_Widget)
                if not dg_Value:
                    SelectDB.set_widget_value(dg_Widget,mkb)
                else:
                    SelectDB.set_widget_value(dg_Widget,f'{dg_Value} , {mkb}')
        except IndexError:
            return

    @staticmethod
    def fill_PatientForm(event):
        SelectDB.Clear_Form()
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            Controller.PatientFocus_ID = Controller.Table_Pacijenti.item(Controller.Table_Pacijenti.focus())['values'][1] 
            patient = RHMH.get_patient_data(Controller.PatientFocus_ID)
        except IndexError:
            return
        for col,val in patient.items():
            for table in Controller.Patient_FormVariables.keys():
                try:
                    widget = Controller.Patient_FormVariables[table][col]
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
            SelectDB.set_widget_value(widget,val)
        TEXT = f'{patient['Ime']} {patient['Prezime']}'
        try:
            # FROM RHMH Date Formate TO Patient print Date Format
            TEXT += f'\n({datetime.strptime(patient['Datum Prijema'],'%Y-%m-%d').strftime('%d-%b-%y')})'
        except KeyError:
            pass
        Controller.PatientInfo.config(text=TEXT)
        Controller.FormTitle[0].configure(bootstyle='success')
  
    @staticmethod
    def fill_LogsForm(event):
        try:
            # DAJ RED GDE JE FOKUS i daj prvi VALUE i oduzmi 1 i pogleda ko je na toj poziciji u ID listi
            time = Controller.Table_Logs.item(Controller.Table_Logs.focus())['values'][1]
            query = f'SELECT `Full Query`,`Full Error` from logs WHERE `ID Time` = "{time}"'
            FullQuery,FullError = RHMH.execute_selectquery(query)[0]
            SelectDB.set_widget_value(Controller.Logs_FormVariables['Full Query'],FullQuery)
            SelectDB.set_widget_value(Controller.Logs_FormVariables['Full Error'],FullError)
        except IndexError:
            return

    @staticmethod
    def tab_change(event):

        def filter_buttons_swap(maintable, switch):
            filtermain:tb.Checkbutton = Controller.buttons['Filter Main Table'][0]
            if switch is True:
                filtermain.grid()
            else:
                filtermain.grid_remove()

            widget:ctk.CTkButton ; widget:tb.Checkbutton
            for widget in Controller.buttons['Filter Patient']:
                if maintable is False:
                    widget.grid_remove()
                else:
                    widget.grid()


        def tab_swapping(values):
            if not Controller.SearchBar.winfo_ismapped():
                Controller.SearchBar.grid()

            for i in range(Controller.SearchBar_number,1,-1):
                SelectDB.search_bar_remove()
            for i in range(1,max_searchby+1):
                Controller.SearchBar_widgets[f'search_option_{i}'].configure(values=values)

            Widget:tb.Entry
            for Type,Widget in Controller.SearchBar_widgets.items(): # Ovo sredjuje samo prvu search liniju sto je ostala
                if Type[-1]!='1':
                    continue
                if not ('option' in Type or 'bar' in Type):
                    if Widget.winfo_ismapped():
                        Widget.grid_remove()
                SelectDB.empty_widget(Widget)


        focus = Controller.NoteBook.index(Controller.NoteBook.select())
        TAB = Controller.NoteBook.tab(focus,'text')
        if TAB == 'Pacijenti':
            for index in [6,7]:
                if Controller.NoteBook.tab(index, "state") == "normal":
                    Controller.NoteBook.hide(index)
            tab_swapping(Controller.TablePacijenti_Columns[2:])
            filter_buttons_swap(maintable = True, switch = False)
        elif TAB == 'Slike':
            for index in [6,7]:
                if Controller.NoteBook.tab(index, "state") == "normal":
                    Controller.NoteBook.hide(index)
            Controller.Slike_HideTable.grid()
            tab_swapping(Controller.TableSlike_Columns[3:])
            filter_buttons_swap(maintable = False, switch = True)
        elif TAB == 'Katalog':
            for index in [6,7]:
                if Controller.NoteBook.tab(index, "state") == "normal":
                    Controller.NoteBook.hide(index)
            tab_swapping(Controller.TableMKB_Columns[2:])
            filter_buttons_swap(maintable = False, switch = True)
        elif TAB == 'Logs':
            for index in [6,7]:
                if Controller.NoteBook.tab(index, "state") == "normal":
                    Controller.NoteBook.hide(index)
            tab_swapping(Controller.TableLogs_Columns[1:])
            filter_buttons_swap(maintable = False, switch = False)
        elif TAB == 'Session':
            for index in [6,7]:
                if Controller.NoteBook.tab(index, "state") == "normal":
                    Controller.NoteBook.hide(index)
            tab_swapping(Controller.TableSession_Columns[1:])
            filter_buttons_swap(maintable = False, switch = False)
        elif TAB == 'Grafikon':
            for index in [6,7]:
                if Controller.NoteBook.tab(index, "state") == "normal":
                    Controller.NoteBook.hide(index)
            Controller.SearchBar.grid_remove()
        elif TAB == 'Settings':
            Controller.SearchBar.grid_remove()
            if Controller.NoteBook.tab(7, "state") == "normal":
                Controller.NoteBook.hide(7)
        elif TAB == 'About':
            Controller.SearchBar.grid_remove()
            if Controller.NoteBook.tab(6, "state") == "normal":
                Controller.NoteBook.hide(6)