import time
TIME_START = time.time_ns()

from tkinter import *

# Decorators
from datetime import datetime, date
import functools
import traceback

# GoogleDrive
import io
import os
import ffmpeg
import pickle
import google.auth
from google.auth.transport.requests import AuthorizedSession, Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# Media
from PIL import Image, ImageTk, ImageDraw
import cv2
import pillow_heif
import subprocess
import easyocr
import numpy as np

# Graph
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties, findSystemFonts
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# SQLite
import sqlite3
import sqlparse
from tkinter import simpledialog,messagebox
import ttkbootstrap as tb

# DBMS
import pandas as pd
from tkinter import filedialog
from ttkbootstrap import widgets
from ttkbootstrap.dialogs.dialogs import Messagebox
import customtkinter as ctk
import queue
import shutil

# Viewer
import json
import inspect
from tkinter.font import nametofont
import threading
from ttkbootstrap.style import Colors
print(f"IMPORTINT time: {(time.time_ns()-TIME_START)/10**9:,.2f} s")

WIDTH = 1720
HEIGHT = 970
title_height = 180

THEME = 'dark_blue'

#FONT = 'Montserrat'
FONT = 'Arial'
F_SIZE = 11


UserSession = {'User':'offline_admin@gmail.com'}

row_height = 28
SIGNS = ['EQUAL', 'LIKE', 'NOT LIKE', 'BETWEEN']
IMAGES = {  'icon' : 'C:/Users/vurun/Desktop/App/RHMH.ico' ,
            'Title': ('C:/Users/vurun/Desktop/App/GodHand_Transparent_smallest.png' , ('Pacijenti RHMH', 0.007, 0.033 )) ,
            'Swap': [ ('C:/Users/vurun/Desktop/App/dark_swap.png',33,33) , ('C:/Users/vurun/Desktop/App/color_swap.png',33,33) ] ,
            'Hide': [ ('C:/Users/vurun/Desktop/App/dark_hide.png',48,33) , ('C:/Users/vurun/Desktop/App/color_hide.png',48,33) ] ,
            'Add': [ ('C:/Users/vurun/Desktop/App/color_add.png',28,28) , ('C:/Users/vurun/Desktop/App/dark_add.png',28,28) ] ,
            'Remove': [ ('C:/Users/vurun/Desktop/App/color_remove.png',28,28) , ('C:/Users/vurun/Desktop/App/dark_remove.png',28,28) ] ,
            'Play Video': 'C:/Users/vurun/Desktop/App/play_button.png' ,
            'Loading': 'C:/Users/vurun/Desktop/App/loading_circle.png' ,
            'Password': [('C:/Users/vurun/Desktop/App/eye.png',270,270)] , 
            'MUVS':     [('C:/Users/vurun/Desktop/App/muvs12.png',280,280)],
            'Signs': [  ('C:/Users/vurun/Desktop/App/sign_equal.png',42,28),
                        ('C:/Users/vurun/Desktop/App/sign_like.png',42,28),
                        ('C:/Users/vurun/Desktop/App/sign_notlike.png',42,28),
                        ('C:/Users/vurun/Desktop/App/sign_between.png',42,28)   ]   }

search_signs = {'EQUAL': {'sign':'=','sr':'JESTE','en':'EQUAL'},
                'LIKE': {'sign':'≈','sr':'PRIBLIŽNO','en':'LIKE'},
                'NOT': {'sign':'≠','sr':'NIJE','en':'NOT'},
                'BETWEEN': {'sign':'≤ ≥','sr':'IZMEĐU','en':'BETWEEN'},
                'YEAR': {'sign':'year','sr':'GODINA','en':'YEAR'},
                'MONTH': {'sign':'month','sr':'MESEC','en':'MONTH'},
                'DAY': {'sign':'day','sr':'DAN','en':'DAY'}        }

app_name = 'Restruktivna Hirurgija Ortopedije'
form_title = 'Pacijent'
font_title = lambda weight='bold': (FONT, int(F_SIZE*3.7), weight)
font_groups = lambda weight='bold': (FONT, int(F_SIZE*1.8), weight)
font_label = lambda weight='bold': (FONT, int(F_SIZE*1.1), weight)
font_entry = (FONT, F_SIZE)

font_plot_title = {'family':FONT, 'color':'#ABB6C2', 'size':F_SIZE*4, 'weight':'bold'}
font_plot_labels = {'family':FONT, 'color':'#ABB6C2', 'size':int(F_SIZE*3)}
font_plot_text = {'family':FONT, 'color':'#ABB6C2', 'size':int(F_SIZE*2)}





labelColor = 'light' if THEME!='light_blue' else 'active'
theme_fg = 'light' if THEME!='light_blue' else 'dark'
titleTxtColor = 'light' if THEME!='light_blue' else 'primary'
dangerButtTxtColor = 'active' if THEME!='light_blue' else 'dark'
bootstyle_table = 'primary'
bootstyle_check = 'primary'


# >>> PADDING <<<
shape_padding = ((6,6),(0,6))
main_title_padding = ((12,12),(12,12))
title_padding = ((0,0),(6,6))
form_padding_entry = ((3,12),(3,3))
search_padding = ((3,3),(3,3))
form_padding_button = ((6,6),(6,6))

#  >>> BORDER <<<
bd_entry = 2
bd_main_frame = 4
bd_inner_frame = 3

#  >>> FORM <<<
form_small_width = 7
form_medium_width = 18
form_large_width = 22
form_date_width = 13

form_butt_width = 80
form_butt_height = 40

#  >>> SEARCH BAR <<<

search_1_width = 18
search_2_width = 10

search_butt_width = 10

form_name = 'Pacijent'
form_groups = {'Default': {'start':4,'Hospitalizacija':3,'Dijagnoza':None},'Alternative': {'start':1,'Doktori':6,'Slike':None}}

default_form_entry = {  'Ime': ('Ime', 'Validate', form_medium_width),
                        'Prezime': ('Prezime', 'Validate', form_medium_width),
                        'Godište': ('Godište', 'Validate', form_small_width),
                        'Pol': ('Pol', 'Combobox', form_small_width, ('Muško', 'Žensko')),
                        'Datum Prijema': ('Prijem', 'DateEntry', form_date_width),
                        'Datum Operacije': ('Operacija', 'DateEntry', form_date_width),
                        'Datum Otpusta': ('Otpust', 'DateEntry', form_date_width),  
                        'Uputna dijagnoza': ('Uputna\nDijagnoza', 'Validate', form_small_width),
                        'Osnovni Uzrok Hospitalizacije': ('Osnovni Uzrok\nHospitalizacije', 'Validate', form_small_width),
                        'Glavna Operativna dijagnoza': ('Glavna\nOperativna', 'Validate', form_large_width),
                        'Sporedna Operativna dijagnoza': ('Sporedna\nOperativna', 'Validate', form_large_width),
                        'Prateća dijagnoza': ('Prateća\nDijagnoza', 'Validate', form_large_width),
                        'Dg Latinski': ('Dg Latin', 'Text', form_large_width) }

alternative_form_entry = {  'Patient Info':('','Info'),
                            'Operator': ('Operator', 'Validate', form_large_width),
                            'Asistent': ('Asistent', 'Text', form_large_width),
                            'Anesteziolog': ('Anesteziolog', 'Validate', form_large_width),
                            'Anestetičar': ('Anestetičar', 'Validate', form_large_width),
                            'Instrumentarka': ('Instrumentarka', 'Validate', form_large_width),
                            'Gostujući Specijalizant': ('Gostujući\nSpecijalizant', 'Text', form_large_width),
                            'Slike':('','Slike'),
                            'Opis':('Opis','StringVar',form_large_width-4) }

Form_buttons = [('ADD\nPatient',None),
                ('UPDATE\nPatient',None),
                ('DELETE\nPatient','danger'),
                ('FILL FORM\nFrom Image','info'),
                ('CLEAR\nFORM','warning')  ]

Image_buttons = [   ('ADD\nImage',None),
                    ('EDIT\nImage',None),
                    ('DELETE\nImage','warning'),
                    ('DOWNLOAD\nSelected Images','info')]

    # TUPLE == (lbl Text, entry width, (row,column,rowspan,columnspan))
Katalog_Entry = {   'mkb10':{   'MKB - šifra':( 'MKB Šifra', 10, (0,0,  1,1) ),
                                'Combobox':( 'Kategorija', 33, (0,1,  1,1) ),
                                'Opis Dijagnoze':( 'Opis\nDijagnoze', 20, (1,0,  2,3) ),
                                'Buttons':[ (0,2,  1,1),
                                            ( 'ADD\nmkb', None ),
                                            ( 'UPDATE\nmkb', None ),
                                            ( 'DELETE\nmkb', 'warning' ) ]   },
                    'zaposleni':{   'Combobox':( 'Funkcija', 22, (0,0,  1,1) ),
                                    'Zaposleni':( 'Ime', 10, (1,0,  1,1) ),
                                    'Buttons':[ (2,0,  1,1),
                                                ( 'ADD\nEmployee', 'info'),
                                                ( 'UPDATE\nEmployee', 'info'),
                                                ( 'DELETE\nEmployee', 'warning') ]   }   }

Slike_Editor = {
    'Info':{
        'txt': 'Ime',
        'widget': tb.Label },
    'Opis':{
        'txt': 'Opis',
        'widget': tb.Combobox,
        'width': 10}
}


max_searchby = 5

GD_Slike_folder = ['1e-KyYcDIt_V2Gn79blz0gESZLpeV4xVn']
GD_RHMH_folder = ['1ybEVItyB75BParYUN2-ab_oVe2tBj1NW']
RHMH_DB = {'id':'1vLJxgeqXMXfqGE_PTrtywdL69TPZDjhw','mime':'application/x-sqlite3'}

MIME = {'PNG' : 'image/png',
        'JPG' : 'image/jpeg',
        'JPEG' : 'image/jpeg',
        'HEIF' : 'image/heif',
        'HEIC' : 'image/heic',
        'MP4': 'video/mp4',
        'MOV': 'video/quicktime'}

MainTablePacijenti = {
    'ID': {'checkbutton':None , 'table':'ID' , 'group':None},
    'id_pacijent': {'checkbutton':None , 'table':'id_pacijent' , 'group':None},
    'Ime': {'checkbutton':None , 'table':'Ime' , 'group':None},
    'Prezime': {'checkbutton':None , 'table':'Prezime' , 'group':None},
    'Starost': {'checkbutton':'Starost' , 'table':'Starost' , 'group':'Pacijent'},
    'Godište': {'checkbutton':'Godište' , 'table':'Godište' , 'group':'Pacijent'},
    'Pol': {'checkbutton':'Pol' , 'table':'Pol' , 'group':'Pacijent'},
    'Uputna dijagnoza': {'checkbutton':'Uputna dijagnoza' , 'table':' Uputna\ndijagnoza' , 'group':None},
    'Prateća dijagnoza': {'checkbutton':'Prateća dijagnoza' , 'table':' Prateća\ndijagnoza' , 'group':None},
    'Glavna Operativna dijagnoza': {'checkbutton':'Glavna Operativna' , 'table':'  Glavna\nOperativna' , 'group':None},
    'Sporedna Operativna dijagnoza': {'checkbutton':'Sporedna Operativna' , 'table':' Sporedna\nOperativna' , 'group':None},
    'Dg Latinski': {'checkbutton':'Dijagnoza Latinski' , 'table':'   Dg\nLatinski' , 'group':None},
    'Osnovni Uzrok Hospitalizacije': {'checkbutton':'Uzrok Hospitalizacije' , 'table':'     Uzrok\nHospitalizacije' , 'group':None},
    'Datum Prijema': {'checkbutton':'Prijem' , 'table':' Datum\nPrijema' , 'group':'Datum'},
    'Datum Operacije': {'checkbutton':'Operacija' , 'table':'  Datum\nOperacije' , 'group':'Datum'},
    'Datum Otpusta': {'checkbutton':'Otpust' , 'table':' Datum\nOtpusta' , 'group':'Datum'},
    'Operator': {'checkbutton':'Operator' , 'table':'ID' , 'group':None},
    'Asistent': {'checkbutton':'Asistent' , 'table':'ID' , 'group':None},
    'Anesteziolog': {'checkbutton':'Anesteziolog' , 'table':'ID' , 'group':None},
    'Anestetičar': {'checkbutton':'Anestetičar' , 'table':'ID' , 'group':None},
    'Gostujući Specijalizant': {'checkbutton':'Specijalizant' , 'table':'  Gostujući\nSpecijalizant' , 'group':None},
    'Instrumentarka': {'checkbutton':'Instrumentarka' , 'table':'Instrumentarka' , 'group':None},
}


graph_Xoptions = [ 'Godina' , 'Mesec' , 'Dan u Sedmici' , 'Dan' , 'Trauma' , 'MKB Grupe' , 'MKB Pojedinačno' , 'Starost' , 'Pol' , 'Zaposleni' ]

WAIT = 10 # ms
BUTTON_LOCK = 500 # ms

ThemeColors = {}

