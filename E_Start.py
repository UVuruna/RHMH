from A1_Variables import *
from A2_Decorators import method_efficency,error_catcher
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import Database
from B3_Media import Media
from B4_Graph import Graph
from C1_Controller import Controller,GodMode
from C2_ManageDB import ManageDB
from C3_SelectDB import SelectDB
from D1_TopPanel import TopPanel
from D2_FormPanel import FormPanel
from D3_MainPanel import MainPanel
from D4_Window import GUI



import sys
if getattr(sys, 'frozen', False):
    import pyi_splash

def start():
    root = Tk()
    style = tb.Style(theme=THEME)

    # CUVA u dicty BOJE iz TEME
    for color_label in Colors.label_iter():
        color = style.colors.get(color_label)
        ThemeColors[color_label] = color

    style.configure('TNotebook.Tab')
    style.map('TNotebook.Tab', background=[('selected', ThemeColors['selectbg']),
                                        ('!selected', ThemeColors['active'])])
    style.map('TNotebook.Tab', foreground=[('selected', ThemeColors['selectfg']),
                                        ('!selected', ThemeColors[color_notebooktab])])
    style.configure('Treeview', rowheight=int(F_SIZE*2.2))
    style.map('Treeview.Heading', background=[('active',ThemeColors['primary'])])
    style.configure('Treeview.Heading',font=font_medium('normal'), padding=(0 , 2 , 0 , int(2.2*F_SIZE)))

    # Menja samo FONT SIZE za TABLE i DATAENTRY
    default_font = nametofont('TkDefaultFont')
    entry_font = nametofont('TkTextFont')
    default_font.configure(size=F_SIZE)
    entry_font.configure(size=F_SIZE)

    def Classes_Decorating(CLASS_list:list):
        for CLASS in CLASS_list:
            CLASS:object
            for i,(name,method) in enumerate(inspect.getmembers(CLASS, predicate=inspect.isfunction)):
                decorated_method = method_efficency()(error_catcher()(method))
                setattr(CLASS, name, decorated_method)
            print(f'Decorated --> {CLASS.__qualname__} - {i+1} methods')

    Classes_Decorating([GoogleDrive,Database,Media,Graph,Controller,GodMode,ManageDB,SelectDB,TopPanel,FormPanel,MainPanel,GUI])

    GUI.initialize(root) # Load
    if getattr(sys,'frozen',False):
        pyi_splash.close() # Finished Loading
    root.mainloop()

if __name__=='__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    start()