from A1_Variables import *
from B2_SQLite import RHMH

class Graph:

    DateTypes = {
        'Godina': '%Y',
        'Mesec': '%m',
        'Dan u Sedmici': '%w',
        'Dan': '%d'
        }

    Y_options = {
        'Broj Pacijenata'                     :  1 ,
        'Broj dana Hospitalizovan'            : '(julianday(`Datum Otpusta`) - julianday(`Datum Prijema`))' ,
        'Broj dana od Prijema do Operacije'   : '(julianday(`Datum Operacije`) - julianday(`Datum Prijema`))'  ,
        'Broj dana od Operacije do Otpusta'   : '(julianday(`Datum Otpusta`) - julianday(`Datum Operacije`))' }

    X_options = {
        'Godina' :          'strftime("%Y", `Datum Prijema`) as Godina, ' ,
        'Mesec' :           'strftime("%m", `Datum Prijema`) as Mesec, ' ,
        'Dan u Sedmici' :   'strftime("%w", `Datum Prijema`) as DanuSedmici, ' ,
        'Dan' :             'strftime("%d", `Datum Prijema`) as Dan, ' ,
        'Trauma' : [ ['Trauma','Ostalo'], ['`MKB - šifra` LIKE "S%"' , '`MKB - šifra` NOT LIKE "S%"'] ] ,
        'Pol' :    [ ['Muško','Žensko'],  ['Pol = "Muško"' , 'Pol = "Žensko"'] ] ,
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
        Graph.figure    = None
        Graph.plot      = None

        Graph.create_figure_plot(width, height, title, X_label, Y_label)

    @staticmethod
    def create_figure_plot(width, height, title:str, X_label:str, Y_label:str ) -> None:
        Graph.figure = Figure(figsize=(width, height), dpi=100)
        Graph.plot = Graph.figure.add_subplot(1, 1, 1)
    
        Graph.figure.patch.set_facecolor(ThemeColors['bg'])
        Graph.plot.set_facecolor(ThemeColors['bg'])

        for spine in Graph.plot.spines.values():
            spine.set_edgecolor(ThemeColors[color_titletext])
            spine.set_linewidth(1)   

        Graph.plot.set_title(title, fontname=FONT, fontsize=int(F_SIZE*1.5), color=ThemeColors[color_titletext], fontweight='bold')
        Graph.plot.set_xlabel(X_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=ThemeColors[color_titletext])
        Graph.plot.set_ylabel(Y_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=ThemeColors[color_titletext])

        Graph.plot.tick_params(axis='x', colors=ThemeColors[color_titletext], labelsize=F_SIZE, labelrotation=45)
        Graph.plot.tick_params(axis='y', colors=ThemeColors[color_titletext], labelsize=F_SIZE)

    @staticmethod
    def create_1D_bar( colors=0, values=0 ) -> None:
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
        colors = cm.viridis(np.linspace(0, 1, len(Graph.X)))

        wedges, texts, autotexts = Graph.plot.pie(Graph.Y, labels=Graph.X, colors=colors, autopct='%1.1f%%', textprops={'color': ThemeColors[color_titletext]})
        for text in texts:
            text.set_fontsize(F_SIZE)
        for autotext in autotexts:
            autotext.set_fontsize(F_SIZE)

    @staticmethod
    def create_2D_bar(values = 0, width = 0.1) -> None:
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
        Graph.plot.legend()

    @staticmethod
    def create_2D_stackedbar(values = 1, width = 0.6) -> None:
        num_groups = len(Graph.X)
        num_bars_per_group = len(Graph.Y[0])

        colors = cm.viridis(np.linspace(0, 1, num_bars_per_group))

        bar_width = width
        index = np.arange(num_groups)
        bottom = np.zeros(num_groups)

        for i in range(num_bars_per_group):
            bar_values = [Graph.Y[j][i] for j in range(num_groups)]
            Graph.plot.bar(index, bar_values, bar_width, bottom=bottom, label=f'Group {i+1}', color=colors[i])
            bottom += bar_values

        if values == 1:
            bottom = np.zeros(num_groups)
            for i in range(num_bars_per_group):
                bar_values = [Graph.Y[j][i] for j in range(num_groups)]
                for j, val in enumerate(bar_values):
                    Graph.plot.text(index[j], bottom[j] + val / 2, round(val, 2), ha='center', va='center', fontsize=F_SIZE, color=ThemeColors[color_titletext])
                bottom += bar_values

        Graph.plot.set_xticks(index)
        Graph.plot.set_xticklabels(Graph.X)
        Graph.plot.legend()

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
    def Graph_DistinctDate(datetype,IDS=None) -> str:
        dates = RHMH.get_distinct_date(datetype,IDS)
        groups = []
        for d in dates:
            groups.append(f'strftime("{datetype}", `Datum Prijema`) = "{d}"')
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
        def get_Xgroups(X):
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
                select = Graph.Graph_DistinctDate(Graph.DateTypes[X[0]], IDS=Filter)

            return (select,where,jointable)
    
        y = Graph.Y_options[Y]
        where = set()
        if y!=1:
            for i in y.split('`'):
                if 'Datum' in i:
                    where.add(i)
        else:
            where.add('Datum Prijema')

        SELECT = 'SELECT '
        JOIN = []
        WHERE = ''
        for whe in where:
            WHERE += f'"{whe}" IS NOT NULL AND '
        GROUP = ''

        complexgroup = []
        for X in [X1,X2]:
            if X: # zbog X2
                select, where, join = get_Xgroups(X)
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

if __name__=='__main__':
    pass