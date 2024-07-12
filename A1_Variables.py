import time
TIME_START = time.time_ns()

from tkinter import *

# Decorators
import cpuinfo
import psutil
from datetime import datetime, date
import functools
import traceback

# GoogleDrive
import io
import os
#import ffmpeg
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

# Media
import GPUtil
from GPUtil import GPU

from PIL import Image, ImageTk
import cv2
import pillow_heif
import subprocess
import easyocr
import numpy as np

# Graph
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties, findSystemFonts
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# SQLite
from moviepy.editor import VideoFileClip
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

directory = os.path.dirname(os.path.abspath(__file__))

UserSession = {'User':'offline_admin@gmail.com','PC':{}}
WAIT = 10 # ms
BUTTON_LOCK = 500 # ms

WIDTH = 1720
HEIGHT = 930
app_name = 'Restruktivna Hirurgija Ortopedije'

form_name = 'Pacijent'
title_height = 180

ThemeColors = {}
THEME = 'dark_blue'
FONT = 'Arial'
F_SIZE = 11

font_verybig = lambda weight='bold': (FONT, int(F_SIZE*3.7), weight)
font_big = lambda weight='bold': (FONT, int(F_SIZE*1.8), weight)
font_medium = lambda weight='bold': (FONT, int(F_SIZE*1.1), weight)
font_default = (FONT, F_SIZE)


color_labeltext =   'light' if THEME!='light_blue' else 'active'
color_notebooktab = 'light' if THEME!='light_blue' else 'dark'
color_titletext = 'light' if THEME!='light_blue' else 'primary'

style_scrollbar = 'primary'
style_checkbutton = 'primary'

padding_12 = (12,12)
padding_6 = (6,6)
padding_3 = (3,3)
padding_3_12 = (3,12)
padding_0_6 = (0,6)

small_width = 7
medium_width = 13
large_width = 18
verylarge_width = 22

buttonX = 80
buttonY = 40

search_bigX = 18
search_smallX = 10

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

SIGNS = ['EQUAL', 'LIKE', 'NOT LIKE', 'BETWEEN']
IMAGES = {  'icon' :    os.path.join(directory,'_internal/Slike/RHMH.ico') ,
            'Title':  [ os.path.join(directory,'_internal/Slike/GodHand_Transparent_smallest.png') ,
                            ('Pacijenti RHMH', 0.007, 0.033 ) ] ,
            'Swap':   [ (os.path.join(directory,'_internal/Slike/dark_swap.png'),33,33) ,
                            (os.path.join(directory,'_internal/Slike/color_swap.png'),33,33)  ] ,
            'Hide':   [ (os.path.join(directory,'_internal/Slike/dark_hide.png'),48,33) ,
                            (os.path.join(directory,'_internal/Slike/color_hide.png'),48,33)  ] ,
            'Add':    [ (os.path.join(directory,'_internal/Slike/color_add.png'),28,28) ,
                            (os.path.join(directory,'_internal/Slike/dark_add.png'),28,28)    ] ,
            'Remove': [ (os.path.join(directory,'_internal/Slike/color_remove.png'),28,28) ,
                            (os.path.join(directory,'_internal/Slike/dark_remove.png'),28,28) ] ,
            'Play Video': os.path.join(directory,'_internal/Slike/play_button.png') ,
            'Loading':    os.path.join(directory,'_internal/Slike/loading_circle.png') ,
            'Password':  [ (os.path.join(directory,'_internal/Slike/eye.png'),270,270) ] , 
            'MUVS':      [ (os.path.join(directory,'_internal/Slike/muvs.png'),280,280) ],
            'Signs':  [ (os.path.join(directory,'_internal/Slike/sign_equal.png'),42,28),
                            (os.path.join(directory,'_internal/Slike/sign_like.png'),42,28),
                                (os.path.join(directory,'_internal/Slike/sign_notlike.png'),42,28),
                                    (os.path.join(directory,'_internal/Slike/sign_between.png'),42,28)   ]   }

Image_buttons = [   ('ADD\nImage',None),
                    ('EDIT\nImage',None),
                    ('DELETE\nImage','warning'),
                    ('DOWNLOAD\nSelected Images','info')]

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


GD_Slike_folder = ['1e-KyYcDIt_V2Gn79blz0gESZLpeV4xVn']
GD_RHMH_folder = ['1ybEVItyB75BParYUN2-ab_oVe2tBj1NW']
RHMH_dict = {
    'path':'_internal/RHMH.db',
    'id':'1vLJxgeqXMXfqGE_PTrtywdL69TPZDjhw',
    'mime':'application/x-sqlite3'}

MIME = {'PNG' : 'image/png',
        'JPG' : 'image/jpeg',
        'JPEG' : 'image/jpeg',
        'HEIF' : 'image/heif',
        'HEIC' : 'image/heic',
        'MP4': 'video/mp4',
        'MOV': 'video/quicktime'}