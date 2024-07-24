from A1_Variables import *
from B2_SQLite import RHMH
from B3_Media import Media
from C1_Controller import Controller

class Graph:
    Settings = {}
    Checkbuttons = {}
    X_Groups  = list()

    figure:Figure = None
    plot   = None
    legend = None

    for k,v in SETTINGS['Graph'].items():
        if k in ['left','right','top','bottom']:
            Settings[k] = v/100
        else:
            Settings[k] = v
    
    DateTypes = {
        'Godina': '%Y',
        'Mesec': '%m',
        'Dan u Sedmici': '%w',
        'Dan': '%d'
        }

    Y_options = {
        'Broj Pacijenata'                     : ( 1, 'Datum Prijema') ,
        'Broj Operacija'                      : ( 1, 'Datum Operacije') ,
        'Broj dana Hospitalizovan'            : ('(julianday(`Datum Otpusta`) - julianday(`Datum Prijema`))', 'Datum Prijema') ,
        'Broj dana od Prijema do Operacije'   : ('(julianday(`Datum Operacije`) - julianday(`Datum Prijema`))', 'Datum Prijema')  ,
        'Broj dana od Operacije do Otpusta'   : ('(julianday(`Datum Otpusta`) - julianday(`Datum Operacije`))', 'Datum Operacije') }

    X_options = {
        'Godina' :          '' ,
        'Mesec' :           '' ,
        'Dan u Sedmici' :   '' ,
        'Dan' :             '' ,
        'Trauma' : [ ['Trauma','Ostalo'], ['`MKB - šifra` LIKE "S%"', '`MKB - šifra` NOT LIKE "S%"'] ] ,
        'Pol' :    [ ['Muško','Žensko'],  ['Pol = "Muško"', 'Pol = "Žensko"'] ] ,
        'MKB Grupe' :       '' ,
        'MKB Pojedinačno' : '' ,
        'Starost' :         '' ,
        'Zaposleni' :       '' }

    SQL_date_num = {
        'Dan u Sedmici' : {
            '0': 'Nedelja',
            '1': 'Ponedeljak',
            '2': 'Utorak',
            '3': 'Sreda',
            '4': 'Četvrtak',
            '5': 'Petak',
            '6': 'Subota'
        } ,
        'Mesec' : {
            '01': 'Januar',
            '02': 'Februar',
            '03': 'Mart',
            '04': 'April',
            '05': 'Maj',
            '06': 'Jun',
            '07': 'Jul',
            '08': 'Avgust',
            '09': 'Septembar',
            '10': 'Oktobar',
            '11': 'Novembar',
            '12': 'Decembar'
        }
    }

    @staticmethod
    def initialize(width, height, X, Y, title:str, X_label:str, Y_label:str, X2=None ) -> None:
        Graph.X: list   = X     # ovo su labeli X
        Graph.X2: list  = X2    # ovo su labeli X2
        Graph.Y: list   = Y     # ovo su values na Y osi --> moze da bude za 1D = [1,2,3] ili za 2D = [ [1,2,3],[4,5,6],[7,8,9] ]

        Graph.width = width
        Graph.height = height
        Graph.title = title
        Graph.X_label = X_label
        Graph.Y_label = Y_label

    @staticmethod
    def create_figure_plot() -> None:
        Graph.figure    = None
        Graph.plot      = None
        Graph.legend    = None

        Graph.figure = Figure(figsize=(Graph.width, Graph.height), dpi=100)
        Graph.plot = Graph.figure.add_subplot(1, 1, 1)
    
        Graph.figure.patch.set_facecolor(ThemeColors['bg'])
        Graph.plot.set_facecolor(ThemeColors['bg'])

        for spine in Graph.plot.spines.values():
            spine.set_edgecolor(ThemeColors[color_titletext])
            spine.set_linewidth(1)   

        Graph.plot.set_title(Graph.title, fontname=FONT, fontsize=int(F_SIZE*1.8), color=ThemeColors[color_titletext], fontweight='bold')
        Graph.plot.set_xlabel(Graph.X_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=ThemeColors[color_titletext])
        Graph.plot.set_ylabel(Graph.Y_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=ThemeColors[color_titletext])

        Graph.plot.tick_params(axis='x', colors=ThemeColors[color_titletext], labelsize=F_SIZE, labelrotation=28)
        Graph.plot.tick_params(axis='y', colors=ThemeColors[color_titletext], labelsize=F_SIZE)

    @staticmethod
    def save_and_open_graph_figure(event):
        if not os.path.exists(os.path.join(directory,'temporary')):
            os.makedirs(os.path.join(directory,'temporary'))
        graph_image = os.path.join(directory,'temporary/temp_image.png')
        Graph.figure.savefig(graph_image)
        
        if not os.path.exists(graph_image):
            return
        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(graph_image))
        elif os.name == 'posix':  # For macOS and Linux
            if os.uname().sysname == 'Darwin':  # macOS
                subprocess.call(['open', os.path.abspath(graph_image)])
            else:  # Linux
                subprocess.call(['xdg-open', os.path.abspath(graph_image)])

    @staticmethod
    def create_1D_bar( colors=0, values=0 ) -> None:
        Graph.create_figure_plot()

        if colors == 1:
            num_bars = len(Graph.X)
            colors = cm.viridis(np.linspace(0, 1, num_bars))
            bars = Graph.plot.bar(Graph.X, Graph.Y, color=colors)
        else:
            bars = Graph.plot.bar(Graph.X, Graph.Y)

        if values == 1:
            for bar in bars:
                bar: Rectangle
                yval = bar.get_height()
                Graph.plot.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), 
                        ha='center', va='bottom', fontsize=F_SIZE, color=ThemeColors[color_titletext])

    @staticmethod
    def create_1D_pie() -> None:
        Graph.create_figure_plot()

        colors = cm.viridis(np.linspace(0, 1, len(Graph.X)))
        wedges, texts, autotexts = Graph.plot.pie(Graph.Y, labels=Graph.X, colors=colors, autopct='%1.1f%%')
        for text in texts:
            text.set_color(ThemeColors[color_labeltext])
            text.set_fontsize(int(F_SIZE*1.1))
        for autotext in autotexts:
            autotext.set_color('#ffffff')
            autotext.set_fontsize(F_SIZE)

    @staticmethod
    def create_2D_bar(values = 0, width = 0.1) -> None:
        Graph.create_figure_plot()

        num_groups = len(Graph.X)
        num_bars_per_group = len(Graph.Y[0])

        colors = cm.viridis(np.linspace(0, 1, num_bars_per_group))

        bar_width = width
        index = np.arange(num_groups)

        for i in range(num_bars_per_group):
            bar_positions = index + i * bar_width
            bar_values = [Graph.Y[j][i] for j in range(num_groups)]
            Graph.plot.bar(bar_positions, bar_values, bar_width, label=Graph.X2[i], color=colors[i])

        if values == 1:
            for i in range(num_bars_per_group):
                bar_positions = index + i * bar_width
                bar_values = [Graph.Y[j][i] for j in range(num_groups)]
                for j, val in enumerate(bar_values):
                    Graph.plot.text(bar_positions[j], val, round(val, 2), ha='center', va='bottom', fontsize=F_SIZE, color=ThemeColors[color_titletext])

        Graph.plot.set_xticks(index + bar_width * (num_bars_per_group - 1) / 2)
        Graph.plot.set_xticklabels(Graph.X)
        Graph.legend = Graph.plot.legend()

    @staticmethod
    def create_2D_stackedbar(values = 1, width = 0.6) -> None:
        Graph.create_figure_plot()

        num_groups = len(Graph.X)
        num_bars_per_group = len(Graph.Y[0])

        colors = cm.viridis(np.linspace(0, 1, num_bars_per_group))

        bar_width = width
        index = np.arange(num_groups)
        bottom = np.zeros(num_groups)

        for i in range(num_bars_per_group):
            bar_values = [Graph.Y[j][i] for j in range(num_groups)]
            Graph.plot.bar(index, bar_values, bar_width, bottom=bottom, label=Graph.X2[i], color=colors[i])
            bottom += bar_values

        if values == 1:
            bottom = np.zeros(num_groups)
            for i in range(num_bars_per_group):
                bar_values = [Graph.Y[j][i] for j in range(num_groups)]
                for j, val in enumerate(bar_values):
                    Graph.plot.text(index[j], bottom[j] + val / 2, round(val, 2), ha='center', va='center', fontsize=F_SIZE, color='#ffffff')
                bottom += bar_values

        Graph.plot.set_xticks(index)
        Graph.plot.set_xticklabels(Graph.X)
        Graph.legend = Graph.plot.legend()

    @staticmethod
    def Graph_DistinctMKB(mkb=None,IDS=None) -> str:
        MKBGroup = RHMH.get_distinct_mkb(mkb,IDS)
        groups = []
        for m in MKBGroup:
            groups.append(f'`MKB - šifra` LIKE "{m}%"')
        return groups

    @staticmethod
    def Graph_DistinctZaposleni(funkcija=None,IDS=None) -> str:
        Zaposleni = RHMH.get_distinct_zaposleni(funkcija,IDS)
        groups = []
        for z in Zaposleni:
            groups.append(f'Zaposleni = "{z}"')
        return groups

    @staticmethod
    def Graph_DistinctDate(datetype, column, IDS=None) -> str:
        dates = RHMH.get_distinct_date(datetype,column,IDS)
        groups = []
        for d in dates:
            groups.append(f'strftime("{datetype}", `{column}`) = "{d}"')
        return groups

    @staticmethod
    def Graph_StarostGroups(jump:int) -> str:
        groups = []
        i = 0
        j = 20
        while j <= 80:
            groups.append(f'Starost BETWEEN {i} AND {j-1}')
            i = int(j)
            j += jump
        else:
            groups.append(f'Starost >= {i}')
        return groups

    @staticmethod
    def Graph_makeQuery(Y,X1,X2,Filter):

        def get_Xgroups(X,datewhere):
            jointable = None
            where = None
            if 'MKB' in X[0]:
                mkb = None
                if len(X)==3: # mkb pojedinacno
                    mkb = X[1]
                where = f'Kategorija = "{X[-1]}"'
                select = Graph.Graph_DistinctMKB(mkb=mkb, IDS=Filter)
                jointable = 'mkb'
            elif X[0] == 'Zaposleni':
                select = Graph.Graph_DistinctZaposleni(funkcija=X[-1], IDS=Filter)
                where = f'Funkcija = "{X[-1]}"'
                jointable = 'zaposleni'
            elif  X[0] == 'Starost':
                select = Graph.Graph_StarostGroups(jump=int(X[1]))
            elif X[0] in ['Trauma','Pol']:
                lista = Graph.X_options[X[0]]
                select = lista[1]
                if len(X)==2:
                    where = f'Kategorija = "{X[-1]}"'
                    jointable = 'mkb'
            else:
                select = Graph.Graph_DistinctDate(Graph.DateTypes[X[0]], datewhere, IDS=Filter)

            return (select,where,jointable)
    
        y,datewhere = Graph.Y_options[Y]
        where = set()
        if y!=1:
            for i in y.split('`'):
                if 'Datum' in i:
                    where.add(i)
        else:
            where.add(datewhere)

        SELECT = 'SELECT '
        JOIN = []
        WHERE = ''
        for whe in where:
            WHERE += f'"{whe}" IS NOT NULL AND '
        GROUP = ''

        complexgroup = []
        for X in [X1,X2]:
            if X: # zbog X2
                select, where, join = get_Xgroups(X,datewhere)
                complexgroup.append(select)
                WHERE += f'{where} AND ' if where else ''
                if join:
                    JOIN.append(join)

        oper = 'SUM' if y==1 else 'AVG'
        if len(complexgroup)==2:
            for i,g1 in enumerate(complexgroup[0]):
                for j,g2 in enumerate(complexgroup[1]):
                    group = f'X{i}{j}'
                    SELECT += f'{oper}(CASE WHEN {g1} AND {g2} THEN {y} ELSE NULL END) AS {group}, '
        elif len(complexgroup)==1:
            for i,g1 in enumerate(complexgroup[0]):
                group = f'X{i}'
                SELECT += f'{oper}(CASE WHEN {g1} THEN {y} ELSE NULL END) AS {group}, '

        join_tables=''
        for j in JOIN:
            if j=='mkb':
                join_tables += f'LEFT JOIN dijagnoza ON pacijent.id_pacijent = dijagnoza.id_pacijent ' + \
                                f'LEFT JOIN mkb10 ON dijagnoza.id_dijagnoza = mkb10.id_dijagnoza ' + \
                                f'LEFT JOIN kategorija ON dijagnoza.id_kategorija = kategorija.id_kategorija '  
            if j=='zaposleni':
                join_tables += f'LEFT JOIN operacija ON pacijent.id_pacijent = operacija.id_pacijent ' + \
                                f'LEFT JOIN funkcija ON operacija.id_funkcija = funkcija.id_funkcija ' + \
                            f'LEFT JOIN zaposleni ON operacija.id_zaposleni = zaposleni.id_zaposleni '

        if Filter:
            WHERE += f'pacijent.id_pacijent IN ({', '.join([str(i) for i in Filter])}) AND '

        QUERY = f'{SELECT.rstrip(', ')} FROM pacijent '

        if JOIN:
            QUERY += f'{join_tables} '

        QUERY += f'WHERE {WHERE.rstrip(' AND ')} '

        if GROUP:
            QUERY += f'GROUP BY {GROUP.rstrip(', ')} '
            QUERY += f'ORDER BY {GROUP.rstrip(', ')} '

        return QUERY

    @staticmethod
    def Graph_SettingUp(PARENT:Tk):

        def create_meter(parent,STYLE,text,ROW,COL,MIN,MAX,AMOUNT):
            meter = tb.Meter(
                master=parent,
                metersize=150,
                bootstyle=STYLE,
                subtextstyle=STYLE,
                subtext=text,
                textright='%',
                padding=padding_6,
                amountused=AMOUNT,
                amountmin=MIN,
                amounttotal=MAX,
                stepsize=1,
                stripethickness=math.ceil(270/(MAX-MIN)),
                metertype="semi",
                interactive=True,
            )
            meter.grid(row=ROW, column=COL, sticky=NSEW)
            return meter

        result = {'action':None}
        def run_command():
            for widget,text in zip([left,right,top,bottom],['left','right','top','bottom']):
                Graph.Settings[text] = widget.amountusedvar.get()/100

            for col,check in Graph.Checkbuttons.items():
                check:BooleanVar
                Graph.Settings[col] = check.get()

            result['action'] = 'Show'
            toplevel.destroy()

        def savedefault_command():
            for widget,text in zip([left,right,top,bottom],['left','right','top','bottom']):
                Graph.Settings[text] = widget.amountusedvar.get()/100
                SETTINGS['Graph'][text] = widget.amountusedvar.get()

            for col,check in Graph.Checkbuttons.items():
                check:BooleanVar
                boolean = check.get()
                Graph.Settings[col] = boolean
                SETTINGS['Graph'][col] = boolean

            json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
            with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
                file.write(json_data)
            Messagebox.show_info(message='Saving Settings successful', title='Saving Settings',
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            toplevel.lift()
            toplevel.focus_force()

        def restoredefault_command():
            for widget,text in zip([left,right,top,bottom],['left','right','top','bottom']):
                default_value = Controller.DEFAULT['Graph'][text]
                Graph.Settings[text] = default_value/100
                SETTINGS['Graph'][text] = default_value
                widget.amountusedvar.set(default_value)

            for col in Graph.Checkbuttons.keys():
                default_value = Controller.DEFAULT['Graph'][col]
                Graph.Settings[col] = default_value
                SETTINGS['Graph'][col] = default_value
                Graph.Checkbuttons[col].set(default_value)

            json_data = json.dumps(SETTINGS, indent=4, ensure_ascii=False)
            with open(os.path.join(directory,'Settings.json'), 'w', encoding='utf-8') as file:
                file.write(json_data)
            Messagebox.show_info(message='Restoring Default Settings successful', title='Restore Settings',
                                    position=(Controller.ROOT.winfo_width()//2,Controller.ROOT.winfo_height()//2))
            toplevel.lift()
            toplevel.focus_force()

        toplevel = tb.Toplevel(alpha=0, iconphoto=IMAGES['icon']['Graph'])
        toplevel.transient(Controller.ROOT)
        toplevel.place_window_center()
        toplevel.title('Graph - Configure')
        toplevel.grid_columnconfigure(0, weight=1)
        toplevel.grid_rowconfigure([0,1,2],weight=1)
        toplevel.resizable(False,False)

        meter_frame = Frame(toplevel)
        meter_frame.grid(row=0,column=0,sticky=NSEW)
        meter_frame.grid_columnconfigure([0,1],weight=1)

        left:tb.Meter = create_meter(parent=meter_frame,
                            STYLE='primary', text='Left',
                            ROW=0, COL=0, MIN=0, MAX=30,
                            AMOUNT=int(Graph.Settings['left']*100)  )
        right:tb.Meter = create_meter(parent=meter_frame,
                            STYLE='primary', text='Right',
                            ROW=0, COL=1, MIN=70, MAX=100,
                            AMOUNT=int(Graph.Settings['right']*100) )
        top:tb.Meter = create_meter(parent=meter_frame,
                            STYLE='primary', text='Top',
                            ROW=1, COL=0, MIN=70, MAX=100,
                            AMOUNT=int(Graph.Settings['top']*100)   )
        bottom:tb.Meter = create_meter(parent=meter_frame,
                            STYLE='primary', text='Bottom',
                            ROW=1, COL=1, MIN=0, MAX=40,
                            AMOUNT=int(Graph.Settings['bottom']*100))

        checkbutton_frame = Frame(toplevel)
        checkbutton_frame.grid(row=1, column=0, padx=padding_12, pady=padding_6, sticky=NSEW)
        checkbutton_frame.grid_columnconfigure([0,1],weight=1)
        ROW = 0
        for i,txt in enumerate(['tight','legend','x label', 'y label']):
            txt:str
            if i==2:
                ROW = 1
            try:
                Graph.Checkbuttons[txt].set(Graph.Settings[txt])
            except KeyError:
                Graph.Checkbuttons[txt] = BooleanVar()
                Graph.Checkbuttons[txt].set(Graph.Settings[txt])
            tb.Checkbutton(checkbutton_frame, text=txt.title(), bootstyle='primary, round-toggle',
                    variable=Graph.Checkbuttons[txt]).grid(row=ROW, column=i%2, padx=padding_6, pady=padding_6, sticky=NSEW)
        
        button_frame = Frame(toplevel)
        button_frame.grid(row=2, column=0, padx=padding_12, pady=padding_12, sticky=E)
        Controller.toplevel_buttons(button_frame,[restoredefault_command,savedefault_command,run_command])
        
        toplevel.bind('<Return>', lambda event: run_command())
        toplevel.bind('<Command-s>', lambda event: savedefault_command())
        toplevel.bind('<Control-s>', lambda event: savedefault_command())
        toplevel.bind('<Command-r>', lambda event: restoredefault_command())
        toplevel.bind('<Control-r>', lambda event: restoredefault_command())
        toplevel.attributes('-alpha', 0.93)
        PARENT.wait_window(toplevel)
        return result['action']