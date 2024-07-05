from A1_Variables import *
from A2_Decorators import error_catcher
from B1_GoogleDrive import GoogleDrive
from B2_SQLite import Database,RHMH
from B3_Media import Media
from C1_DBMS import Buttons, DBMS
from D4_Window import GUI, TopFrame, FormFrame, TableFrame

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

#'''

GoogleDrive = error_catcher(RHMH)(GoogleDrive)
Database = error_catcher(RHMH)(Database)
Media = error_catcher(RHMH)(Media)

Buttons = error_catcher(RHMH)(Buttons)
DBMS = error_catcher(RHMH)(DBMS)

TopFrame = error_catcher(RHMH)(TopFrame)
FormFrame = error_catcher(RHMH)(FormFrame)
TableFrame = error_catcher(RHMH)(TableFrame)
GUI = error_catcher(RHMH)(GUI)
#'''

app = GUI(root)
root.mainloop()