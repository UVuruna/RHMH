from A_Variables import *
from G_Viewer import GUI



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
default_font.configure(size=def_font[1])
entry_font.configure(size=def_font[1])

'''
GUI = error_catcher()(GUI)
TitleFrame = error_catcher()(TitleFrame)
FormFrame = error_catcher()(FormFrame)
WindowFrame = error_catcher()(WindowFrame)
DBMS = error_catcher()(DBMS)
Buttons = error_catcher()(Buttons)
Database = error_catcher()(Database)
GoogleDrive = error_catcher()(GoogleDrive)
#'''

app = GUI(root)
root.mainloop()