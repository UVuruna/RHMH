from A1_Variables import *

def get_available_fonts():
    flist = findSystemFonts()

    font_names = {FontProperties(fname=font).get_name() for font in flist}
    font_names = list(font_names)
    font_names.sort()

    for font in font_names:
        print(font)

class Graph:

    @staticmethod
    def initialize( X, Y, title:str, X_label:str, Y_label:str, X2=None ) -> None:
        Graph.X: list   = X     # ovo su labeli X
        Graph.X2: list  = X2    # ovo su labeli X2
        Graph.Y: list   = Y     # ovo su values na Y osi --> moze da bude za 1D = [1,2,3] ili za 2D = [ [1,2,3],[4,5,6],[7,8,9] ]
        Graph.figure    = None
        Graph.plot      = None

        Graph.create_figure_plot(title, X_label, Y_label)

    @staticmethod
    def create_figure_plot(title:str, X_label:str, Y_label:str ) -> None:
        Graph.figure = Figure(figsize=(10, 8), dpi=100)
        Graph.plot = Graph.figure.add_subplot(1, 1, 1)
    
        Graph.figure.patch.set_facecolor(ThemeColors['bg'])
        Graph.plot.set_facecolor(ThemeColors['bg'])

        for spine in Graph.plot.spines.values():
            spine.set_edgecolor(color_titletext)
            spine.set_linewidth(1)   

        Graph.plot.set_title(title, fontname=FONT, fontsize=int(F_SIZE*2.2), color=color_titletext, fontweight='bold')
        Graph.plot.set_xlabel(X_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=color_titletext)
        Graph.plot.set_ylabel(Y_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=color_titletext)

        Graph.plot.tick_params(axis='x', colors=color_titletext, labelsize=F_SIZE, labelrotation=45)
        Graph.plot.tick_params(axis='y', colors=color_titletext, labelsize=F_SIZE)

    @staticmethod
    def create_1D_bar( colors:bool=False, values:bool=False ) -> None:
        if colors is True:
            num_bars = len(Graph.X)
            colors = cm.viridis(np.linspace(0, 1, num_bars))

        bars = Graph.plot.bar(Graph.X, Graph.Y, color=colors)
        if values is True:
            for bar in bars:
                bar: Rectangle
                yval = bar.get_height()
                Graph.plot.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), 
                        ha='center', va='bottom', fontsize=F_SIZE, color=color_titletext)   
    
    @staticmethod
    def create_1D_pie() -> None:
        colors = cm.viridis(np.linspace(0, 1, len(Graph.X)))

        wedges, texts, autotexts = Graph.plot.pie(Graph.Y, labels=Graph.X, colors=colors, autopct='%1.1f%%', textprops={'color': color_titletext})
        for text in texts:
            text.set_fontsize(F_SIZE)
        for autotext in autotexts:
            autotext.set_fontsize(F_SIZE)

    @staticmethod
    def create_2D_bar(values: bool = False) -> None:
        num_groups = len(Graph.X)
        num_bars_per_group = len(Graph.Y[0])

        colors = cm.viridis(np.linspace(0, 1, num_bars_per_group))

        bar_width = 0.2
        index = np.arange(num_groups)

        for i in range(num_bars_per_group):
            bar_positions = index + i * bar_width
            bar_values = [Graph.Y[j][i] for j in range(num_groups)]
            Graph.plot.bar(bar_positions, bar_values, bar_width, label=Graph.X2[i], color=colors[i])

        if values is True:
            for i in range(num_bars_per_group):
                bar_positions = index + i * bar_width
                bar_values = [Graph.Y[j][i] for j in range(num_groups)]
                for j, val in enumerate(bar_values):
                    Graph.plot.text(bar_positions[j], val, round(val, 2), ha='center', va='bottom', fontsize=F_SIZE, color=color_titletext)

        Graph.plot.set_xticks(index + bar_width * (num_bars_per_group - 1) / 2)
        Graph.plot.set_xticklabels(Graph.X)
        Graph.plot.legend()

    @staticmethod
    def create_2D_stackedbar(values: bool = False) -> None:
        num_groups = len(Graph.X)
        num_bars_per_group = len(Graph.Y[0])

        colors = cm.viridis(np.linspace(0, 1, num_bars_per_group))

        bar_width = 0.6
        index = np.arange(num_groups)
        bottom = np.zeros(num_groups)

        for i in range(num_bars_per_group):
            bar_values = [Graph.Y[j][i] for j in range(num_groups)]
            Graph.plot.bar(index, bar_values, bar_width, bottom=bottom, label=f'Group {i+1}', color=colors[i])
            bottom += bar_values

        if values is True:
            bottom = np.zeros(num_groups)
            for i in range(num_bars_per_group):
                bar_values = [Graph.Y[j][i] for j in range(num_groups)]
                for j, val in enumerate(bar_values):
                    Graph.plot.text(index[j], bottom[j] + val / 2, round(val, 2), ha='center', va='center', fontsize=F_SIZE, color=color_titletext)
                bottom += bar_values

        Graph.plot.set_xticks(index)
        Graph.plot.set_xticklabels(Graph.X)
        Graph.plot.legend()

if __name__=='__main__':
    pass