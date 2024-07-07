from A1_Variables import *

def get_available_fonts():
    flist = findSystemFonts()

    font_names = {FontProperties(fname=font).get_name() for font in flist}
    font_names = list(font_names)
    font_names.sort()

    for font in font_names:
        print(font)

class Graph:
    X:list = None
    def __init__(self, X:list, Y:list, color:str) -> None:
        self.X = X
        self.Y = Y
        self.color = color


    def create_plot(self, title:str, X_label:str, Y_label:str, colors=None, values:bool=False):
        fig = Figure(figsize=(6, 4), dpi=100)
        plot = fig.add_subplot(1, 1, 1)
    
        fig.patch.set_facecolor('#2b3e50') # bg in tb
        plot.set_facecolor('#2b3e50')     # bg in tb

        for spine in plot.spines.values():
            spine.set_edgecolor(self.color)
            spine.set_linewidth(1)   

        plot.set_title(title, fontname=FONT, fontsize=int(F_SIZE*2.2), color=self.color, fontweight='bold')
        plot.set_xlabel(X_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=self.color)
        plot.set_ylabel(Y_label, fontname=FONT, fontsize=int(F_SIZE*1.5), color=self.color)

        plot.tick_params(axis='x', colors=self.color, labelsize=F_SIZE, labelrotation=45)
        plot.tick_params(axis='y', colors=self.color, labelsize=F_SIZE)

        if colors is True:
            num_bars = len(self.X)
            colors = cm.viridis(np.linspace(0, 1, num_bars))

        bars = plot.bar(self.X, self.Y, color=colors)

        if values is True:
            for bar in bars:
                yval = bar.get_height()
                plot.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), 
                        ha='center', va='bottom', fontsize=F_SIZE, color=self.color)
                
        
        return fig



if __name__=='__main__':

    # Kreiraj Tkinter aplikaciju
    root = Tk()
    style = tb.Style(theme=THEME)
    root.title("Tkinter sa Matplotlib stubičastim grafikom")




    # Kreiraj Frame za grafik
    # Postavi canvas
    topframe = tb.Frame(root)
    topframe.grid(row=0,column=0,padx=10, pady=10, sticky=EW)
    for i in range(5):
        label = tb.Label(topframe,text='PROBNO')
        label.grid(row=0,column=i)
    topframe.grid_columnconfigure([i for i in range(5)],weight=1)
    frame = tb.Frame(root)
    frame.grid(row=1,column=0,padx=10, pady=10, sticky=NSEW)


    X = []
    Y = []
    for i in range(1,20):
        X.append(f"M{i}")
        Y.append(2*i)



    graph = Graph(X,Y,'#ABB6C2')



    fig = graph.create_plot('Po Dijagnozi M','Dijagnoze','Broj Pacijenata',colors=True, values=True)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()

    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

    # Kreiraj dugme za izlaz
    exit_button = ctk.CTkButton(root, text="Izlaz", command=root.quit)
    exit_button.grid(row=2,column=0,pady=10)

    root.grid_columnconfigure(0,weight=1)
    root.grid_rowconfigure(1,weight=1)

    # Pokreni Tkinter main loop
    root.mainloop()


    import matplotlib.pyplot as plt
    import numpy as np

    # Podaci za grafikon
    categories = ['Category 1', 'Category 2', 'Category 3']
    x_labels = ['Label 1', 'Label 2', 'Label 3', 'Label 4']  # Opcije za svaku kategoriju
    values = np.random.rand(len(categories), len(x_labels))  # Slučajni podaci za prikaz

    # Broj kategorija i širina stubića
    num_categories = len(categories)
    bar_width = 0.2  # Širina svakog stubića

    # Podešavanje položaja stubića za svaku kategoriju
    x = np.arange(len(x_labels))

    # Kreiranje figure i podešavanje osa
    fig, ax = plt.subplots()
    for i, category in enumerate(categories):
        ax.bar(x + i * bar_width, values[i], width=bar_width, label=category)

    # Podešavanje oznaka i naslova
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_title('2D Bar Chart with Grouped Categories')
    ax.set_xticks(x + (num_categories - 1) * bar_width / 2)  # Centriranje oznaka x-ose
    ax.set_xticklabels(x_labels)
    ax.legend()

    # Prikaz grafikona
    plt.show()
