from A1_Variables import *
from A2_Decorators import method_efficency,error_catcher
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import Database
from B3_Media import Media
from B4_Graph import Graph
from C1_Controller import Controller
from C2_ManageDB import ManageDB
from C3_SelectDB import SelectDB
from D1_TopFrame import TopPanel
from D2_FormFrame import FormPanel
from D3_TabelFrame import MainPanel
from D4_Window import GUI

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
                                       ('!selected', ThemeColors[theme_fg])])
style.configure('Treeview', rowheight=int(F_SIZE*2.2))
style.map('Treeview.Heading', background=[('active',ThemeColors['primary'])])
style.configure('Treeview.Heading',font=font_label('normal'), padding=(0 , 2 , 0 , int(2.2*F_SIZE)))

# Menja samo FONT SIZE za TABLE i DATAENTRY
default_font = nametofont('TkDefaultFont')
entry_font = nametofont('TkTextFont')
default_font.configure(size=F_SIZE)
entry_font.configure(size=F_SIZE)

def GoogleDrive_Decorating():
    for name, method in inspect.getmembers(GoogleDrive, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(GoogleDrive, name, decorated_method)

def Database_Decorating():
    for name, method in inspect.getmembers(Database, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(Database, name, decorated_method)

def Media_Decorating():
    for name, method in inspect.getmembers(Media, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(Media, name, decorated_method)

def Graph_Decorating():
    for name, method in inspect.getmembers(Graph, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(Graph, name, decorated_method)

def Controller_Decorating():
    for name, method in inspect.getmembers(Controller, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(Controller, name, decorated_method)

def ManageDB_Decorating():
    for name, method in inspect.getmembers(ManageDB, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(ManageDB, name, decorated_method)

def SelectDB_Decorating():
    for name, method in inspect.getmembers(SelectDB, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(SelectDB, name, decorated_method)

def TopPanel_Decorating():
    for name, method in inspect.getmembers(TopPanel, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(TopPanel, name, decorated_method)

def FormPanel_Decorating():
    for name, method in inspect.getmembers(FormPanel, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(FormPanel, name, decorated_method)

def MainPanel_Decorating():
    for name, method in inspect.getmembers(MainPanel, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(MainPanel, name, decorated_method)

def GUI_Decorating():
    for name, method in inspect.getmembers(GUI, predicate=inspect.isfunction):
        decorated_method = method_efficency()(error_catcher()(method))
        setattr(GUI, name, decorated_method)

GoogleDrive_Decorating()
Database_Decorating()
Media_Decorating()
Graph_Decorating()

Controller_Decorating()
ManageDB_Decorating()
SelectDB_Decorating()

TopPanel_Decorating()
FormPanel_Decorating()
MainPanel_Decorating()
GUI_Decorating()

GUI.load_GUIapp(root) # Starting Program
root.mainloop()