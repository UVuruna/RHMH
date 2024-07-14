import time
TIME_START = time.time_ns()
from datetime import datetime, date

from tkinter import *
from tkinter import simpledialog,messagebox
from tkinter.font import nametofont
from tkinter import filedialog
import ttkbootstrap as tb
from ttkbootstrap import widgets
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.style import Colors
import customtkinter as ctk

import sqlite3
import sqlparse

import os
import threading
import queue
import shutil
import json
import inspect
import functools
import traceback
import io
import re
import subprocess

import psutil
import GPUtil
import cpuinfo

#import ffmpeg
import httplib2
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

import easyocr
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties, findSystemFonts
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from PIL import Image, ImageTk
import pillow_heif
import cv2
from moviepy.editor import VideoFileClip

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
    'ID': {'checkbutton':None , 'table':'ID' , 'group':None,
           'column_width':F_SIZE*2, 'column_anchor':W},
    'id_pacijent': {'checkbutton':None , 'table':'id_pacijent' , 'group':None,
           'column_width':0, 'column_anchor':W},

    'Ime': {'checkbutton':None , 'table':'Ime' , 'group':None,
           'column_width':F_SIZE*8, 'column_anchor':W},
    'Prezime': {'checkbutton':None , 'table':'Prezime' , 'group':None,
           'column_width':F_SIZE*13, 'column_anchor':W},
    'Starost': {'checkbutton':'Starost' , 'table':'Starost' , 'group':'Pacijent',
           'column_width':F_SIZE*4, 'column_anchor':E},
    'Godište': {'checkbutton':'Godište' , 'table':'Godište' , 'group':'Pacijent',
           'column_width':F_SIZE*4, 'column_anchor':E},
    'Pol': {'checkbutton':'Pol' , 'table':'Pol' , 'group':'Pacijent',
           'column_width':F_SIZE*7, 'column_anchor':CENTER},

    'Datum Prijema': {'checkbutton':'Prijem' , 'table':' Datum\nPrijema' , 'group':'Datum',
           'column_width':F_SIZE*9, 'column_anchor':CENTER},
    'Datum Operacije': {'checkbutton':'Operacija' , 'table':'  Datum\nOperacije' , 'group':'Datum',
           'column_width':F_SIZE*9, 'column_anchor':CENTER},
    'Datum Otpusta': {'checkbutton':'Otpust' , 'table':' Datum\nOtpusta' , 'group':'Datum',
           'column_width':F_SIZE*9, 'column_anchor':CENTER},

    'Uputna dijagnoza': {'checkbutton':'Uputna dijagnoza' , 'table':' Uputna\ndijagnoza' , 'group':None,
           'column_width':F_SIZE*7, 'column_anchor':CENTER},
    'Osnovni Uzrok Hospitalizacije': {'checkbutton':'Uzrok Hospitalizacije' , 'table':'     Uzrok\nHospitalizacije' , 'group':None,
           'column_width':F_SIZE*8, 'column_anchor':CENTER},
    'Glavna Operativna dijagnoza': {'checkbutton':'Glavna Operativna' , 'table':'  Glavna\nOperativna' , 'group':None,
           'column_width':F_SIZE*16, 'column_anchor':W},
    'Sporedna Operativna dijagnoza': {'checkbutton':'Sporedna Operativna' , 'table':' Sporedna\nOperativna' , 'group':None,
           'column_width':F_SIZE*16, 'column_anchor':W},
    'Prateća dijagnoza': {'checkbutton':'Prateća dijagnoza' , 'table':' Prateća\ndijagnoza' , 'group':None,
           'column_width':F_SIZE*16, 'column_anchor':W},
    'Dg Latinski': {'checkbutton':'Dijagnoza Latinski' , 'table':'   Dg\nLatinski' , 'group':None,
           'column_width':F_SIZE*27, 'column_anchor':W},
    
    'Operator': {'checkbutton':'Operator' , 'table':'ID' , 'group':False,
           'column_width':F_SIZE*18, 'column_anchor':W},
    'Asistent': {'checkbutton':'Asistent' , 'table':'ID' , 'group':False,
           'column_width':F_SIZE*28, 'column_anchor':W},
    'Anesteziolog': {'checkbutton':'Anesteziolog' , 'table':'ID' , 'group':False,
           'column_width':F_SIZE*18, 'column_anchor':W},
    'Anestetičar': {'checkbutton':'Anestetičar' , 'table':'ID' , 'group':False,
           'column_width':F_SIZE*16, 'column_anchor':W},
    'Gostujući Specijalizant': {'checkbutton':'Specijalizant' , 'table':'  Gostujući\nSpecijalizant' , 'group':False,
           'column_width':F_SIZE*28, 'column_anchor':W},
    'Instrumentarka': {'checkbutton':'Instrumentarka' , 'table':'Instrumentarka' , 'group':False,
           'column_width':F_SIZE*16, 'column_anchor':W},
}

SIGNS = ['EQUAL', 'LIKE', 'NOT LIKE', 'BETWEEN']
IMAGES = {  'icon' :    [os.path.join(directory,'Slike/RHMH.ico'),
                            os.path.join(directory,'Slike/RHMH.png')] ,
            'Title':  [ os.path.join(directory,'Slike/GodHand_Transparent_smallest.png') ,
                            ('Pacijenti RHMH', 0.007, 0.033 ) ] ,
            'Swap':   [ (os.path.join(directory,'Slike/dark_swap.png'),33,33) ,
                            (os.path.join(directory,'Slike/color_swap.png'),33,33)  ] ,
            'Hide':   [ (os.path.join(directory,'Slike/dark_hide.png'),48,33) ,
                            (os.path.join(directory,'Slike/color_hide.png'),48,33)  ] ,
            'Add':    [ (os.path.join(directory,'Slike/color_add.png'),28,28) ,
                            (os.path.join(directory,'Slike/dark_add.png'),28,28)    ] ,
            'Remove': [ (os.path.join(directory,'Slike/color_remove.png'),28,28) ,
                            (os.path.join(directory,'Slike/dark_remove.png'),28,28) ] ,
            'Play Video': os.path.join(directory,'Slike/play_button.png') ,
            'Loading':    os.path.join(directory,'Slike/loading_circle.png') ,
            'Password':  [ (os.path.join(directory,'Slike/eye.png'),270,270) ] , 
            'MUVS':      [ (os.path.join(directory,'Slike/muvs.png'),280,280) ],
            'Signs':  [ (os.path.join(directory,'Slike/sign_equal.png'),42,28),
                            (os.path.join(directory,'Slike/sign_like.png'),42,28),
                                (os.path.join(directory,'Slike/sign_notlike.png'),42,28),
                                    (os.path.join(directory,'Slike/sign_between.png'),42,28)   ]   }

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
    'path':'RHMH.db',
    'id':'1vLJxgeqXMXfqGE_PTrtywdL69TPZDjhw',
    'mime':'application/x-sqlite3'}

MIME = {'PNG' : 'image/png',
        'JPG' : 'image/jpeg',
        'JPEG' : 'image/jpeg',
        'HEIF' : 'image/heif',
        'HEIC' : 'image/heic',
        'MP4': 'video/mp4',
        'MOV': 'video/quicktime'}