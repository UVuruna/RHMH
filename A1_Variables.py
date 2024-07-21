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

import math
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
import torch
import psutil
import GPUtil
import cpuinfo

import webbrowser
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

directory = os.path.dirname(os.path.abspath(__file__))

IMAGES = {
    'icon' :    [os.path.join(directory,'Slike/RHMH.ico'),
                     os.path.join(directory,'Slike/RHMH.png')] ,
    'Title': {
       'Creation':[
               os.path.join(directory,'Slike/GodHand.png') ,
               ('Pacijenti RHMH', 0.007, 0.033 ) ] ,
       'Eye':[
           os.path.join(directory,'Slike/GodHand_Eye.png') ,
           ('Pacijenti RHMH', 0.007, 0.033 ) ] ,
       'Evolution':[
           os.path.join(directory,'Slike/GodHand_Monkey.png') ,
           ('Pacijenti RHMH', 0.007, 0.033 ) ] ,
       'Egypt': os.path.join(directory,'Slike/God_Egypt.png') ,
       'RHMH':(
           os.path.join(directory,'Slike/God_Moon.png'),
           os.path.join(directory,'Slike/God_Fruit.png'),
           os.path.join(directory,'Slike/God_Sea.png'),     
           os.path.join(directory,'Slike/God_Sunrise.png'),
           os.path.join(directory,'Slike/God_Night.png'),
           os.path.join(directory,'Slike/God_Flower.png'),
           os.path.join(directory,'Slike/God_Sunset.png')
            )
       } ,
       'Swap': [
           (os.path.join(directory,'Slike/dark_swap.png'),33,33) ,
           (os.path.join(directory,'Slike/color_swap.png'),33,33)
       ] ,
       'Hide': [
           (os.path.join(directory,'Slike/dark_hide.png'),48,33) ,
           (os.path.join(directory,'Slike/color_hide.png'),48,33)
       ] ,
       'Add': [
           (os.path.join(directory,'Slike/color_add.png'),28,28) ,
           (os.path.join(directory,'Slike/dark_add.png'),28,28)
       ] ,
       'Remove': [
           (os.path.join(directory,'Slike/color_remove.png'),28,28) ,
           (os.path.join(directory,'Slike/dark_remove.png'),28,28)
       ] ,
       'Left': [
           (os.path.join(directory,'Slike/color_left.png'),48,33) ,
           (os.path.join(directory,'Slike/dark_left.png'),48,33)
       ] ,
       'Right': [
           (os.path.join(directory,'Slike/color_right.png'),48,33) ,
           (os.path.join(directory,'Slike/dark_right.png'),48,33)
       ] ,
       'Play Video': os.path.join(directory,'Slike/play_button.png') ,
       'Loading':    os.path.join(directory,'Slike/loading_circle.png') ,
       'Password':  [ (os.path.join(directory,'Slike/eye.png'),270,270) ] , 
       'MUVS':      [ (os.path.join(directory,'Slike/muvs.png'),280,280) ],
       'Signs': [
           (os.path.join(directory,'Slike/sign_equal.png'),42,28),
           (os.path.join(directory,'Slike/sign_like.png'),42,28),
           (os.path.join(directory,'Slike/sign_notlike.png'),42,28),
           (os.path.join(directory,'Slike/sign_greater.png'),42,28),
           (os.path.join(directory,'Slike/sign_less.png'),42,28),
           (os.path.join(directory,'Slike/sign_between.png'),42,28)
       ],
       'Themes': [
           os.path.join(directory,'Slike/theme_moon.png'),
           os.path.join(directory,'Slike/theme_fruit.png'),
           os.path.join(directory,'Slike/theme_sea.png'),
           os.path.join(directory,'Slike/theme_sunrise.png'),
           os.path.join(directory,'Slike/theme_night.png'),
           os.path.join(directory,'Slike/theme_flower.png'),
           os.path.join(directory,'Slike/theme_sunset.png')
       ]
}


with open(os.path.join(directory,'Settings.json'), 'r') as file:
    SETTINGS = json.load(file)

Theme_Names = ['Moon','Fruit','Sea','Sunrise','Night','Flower','Sunset']
Title_Names = ['Creation','Eye','Evolution','Egypt','RHMH']

LANGUAGE = SETTINGS['System']['Language']
FONT = SETTINGS['System']['Font']
F_SIZE = SETTINGS['System']['Font Size']

BUTTON_LOCK = SETTINGS['System']['Button cooldown']
WAIT = SETTINGS['System']['Thread cooldown']

WIDTH = SETTINGS['System']['Width']
HEIGHT = SETTINGS['System']['Height']
TITLE_HEIGHT = SETTINGS['System']['Title Height']/100

THEME = SETTINGS['Theme']
TITLE_IMAGE = IMAGES['Title'][SETTINGS['Title']]
TITLE_IMAGE = TITLE_IMAGE if not isinstance(TITLE_IMAGE,tuple) else TITLE_IMAGE[Theme_Names.index(THEME)]



UserSession = {'Email':SETTINGS['Email'],'PC':{},'GUI':{},'GoogleDrive':{},'Database':{},
               'AI':{},'Media':{},'Graph':{},'Controller':{},'ManageDB':{},'SelectDB':{}}
app_name = 'Restruktivna Hirurgija Ortopedije'
form_name = 'Pacijent'
ThemeColors = {}

font_verybig = lambda weight='bold': (FONT, int(F_SIZE*3.7), weight)
font_big = lambda weight='bold': (FONT, int(F_SIZE*1.8), weight)
font_medium = lambda weight='bold': (FONT, int(F_SIZE*1.1), weight)
font_default = (FONT, F_SIZE)

color_labeltext =   'light' if THEME not in ['Sunrise','Fruit','Flower','Sea'] else 'primary'
color_titletext = 'light' if THEME not in ['Sunrise','Fruit','Flower','Sea'] else 'primary'
color_highlight = 'selectbg' if THEME not in ['Sunrise','Fruit','Flower'] else 'border' 

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
       'ID': {'checkbutton':None , 'group':None,
              'table':'\nID' , 'column_width':F_SIZE*4, 'column_anchor':W},
       'id_pacijent': {'checkbutton':None , 'group':None,
              'table':'id_pacijent' , 'column_width':0, 'column_anchor':W},

       'Ime': {'checkbutton':None , 'group':None,
              'table':'\nIme' , 'column_width':F_SIZE*8, 'column_anchor':W},
       'Prezime': {'checkbutton':None , 'group':None,
              'table':'\nPrezime' , 'column_width':F_SIZE*13, 'column_anchor':W},
       'Starost': {'checkbutton':'Starost' , 'group':'Pacijent',
              'table':'\nStarost' , 'column_width':F_SIZE*6, 'column_anchor':CENTER},
       'Godište': {'checkbutton':'Godište' , 'group':'Pacijent',
              'table':'\nGodište' , 'column_width':F_SIZE*6, 'column_anchor':CENTER},
       'Pol': {'checkbutton':'Pol' , 'group':'Pacijent',
              'table':'\nPol' , 'column_width':F_SIZE*7, 'column_anchor':CENTER},

       'Datum Prijema': {'checkbutton':'Prijem' , 'group':'Datum',
              'table':' Datum\nPrijema' , 'column_width':F_SIZE*9, 'column_anchor':CENTER},
       'Datum Operacije': {'checkbutton':'Operacija' , 'group':'Datum',
              'table':'  Datum\nOperacije' , 'column_width':F_SIZE*9, 'column_anchor':CENTER},
       'Datum Otpusta': {'checkbutton':'Otpust' , 'group':'Datum',
              'table':' Datum\nOtpusta' , 'column_width':F_SIZE*9, 'column_anchor':CENTER},

       'Uputna dijagnoza': {'checkbutton':'Uputna dijagnoza' , 'group':None,
              'table':'  Uputna\nDijagnoza' , 'column_width':F_SIZE*7, 'column_anchor':CENTER},
       'Osnovni Uzrok Hospitalizacije': {'checkbutton':'Uzrok Hospitalizacije' , 'group':None,
              'table':'Osnovni Uzrok\nHospitalizacije' , 'column_width':F_SIZE*10, 'column_anchor':CENTER},
       'Glavna Operativna dijagnoza': {'checkbutton':'Glavna Operativna' , 'group':None,
              'table':'      Glavna\nOperativna Dijagnoza' , 'column_width':F_SIZE*18, 'column_anchor':W},
       'Sporedna Operativna dijagnoza': {'checkbutton':'Sporedna Operativna' , 'group':None,
              'table':'     Sporedna\nOperativna Dijagnoza' , 'column_width':F_SIZE*18, 'column_anchor':W},
       'Prateća dijagnoza': {'checkbutton':'Prateća dijagnoza' , 'group':None,
              'table':' Prateća\nDijagnoza' , 'column_width':F_SIZE*18, 'column_anchor':W},
       'Dg Latinski': {'checkbutton':'Dijagnoza Latinski' , 'group':None,
              'table':'   Dg\nLatinski' , 'column_width':F_SIZE*27, 'column_anchor':W},
    
       'Operator': {'checkbutton':'Operator' , 'group':False,
              'table': '\nOperator' , 'column_width':F_SIZE*20, 'column_anchor':W},
       'Asistent': {'checkbutton':'Asistent' , 'group':False,
              'table': '\nAsistent' , 'column_width':F_SIZE*28, 'column_anchor':W},
       'Anesteziolog': {'checkbutton':'Anesteziolog' , 'group':False,
              'table': '\nAnesteziolog' , 'column_width':F_SIZE*20, 'column_anchor':W},
       'Anestetičar': {'checkbutton':'Anestetičar' , 'group':False,
              'table': '\nAnestetičar' , 'column_width':F_SIZE*16, 'column_anchor':W},
       'Gostujući Specijalizant': {'checkbutton':'Specijalizant' , 'group':False,
              'table': '\nGostujući Specijalizant' , 'column_width':F_SIZE*28, 'column_anchor':W},
       'Instrumentarka': {'checkbutton':'Instrumentarka' , 'group':False,
              'table': '\nInstrumentarka' , 'column_width':F_SIZE*16, 'column_anchor':W},
       }

SlikeTable = {
       'ID': { 'table':'\nID' , 'column_width':F_SIZE*4, 'column_anchor':W },
       'id_slike': { 'table':'id_slike' , 'column_width':0, 'column_anchor':W },
       'id_pacijent': { 'table':'id_pacijent' , 'column_width':0, 'column_anchor':W },

       'Naziv': { 'table':'\nPacijent' , 'column_width':F_SIZE*24, 'column_anchor':W },
       'Opis': { 'table':'\nOpis' , 'column_width':F_SIZE*13, 'column_anchor':W },
       'Format': { 'table':'\nFormat' , 'column_width':F_SIZE*8, 'column_anchor':W },
       'Veličina': { 'table':'\nVeličina' , 'column_width':F_SIZE*8, 'column_anchor':E },
       'width': { 'table':'\nwidth' , 'column_width':F_SIZE*6, 'column_anchor':CENTER },
       'height': { 'table':'\nheight' , 'column_width':F_SIZE*6, 'column_anchor':CENTER },
       'pixels': { 'table':'\npixels' , 'column_width':F_SIZE*8, 'column_anchor':E },
       'image_data': { 'table':'image_data' , 'column_width':0, 'column_anchor':E}
       }

MKBTable = {
       'ID': { 'table':'\nID' , 'column_width':F_SIZE*4, 'column_anchor':W },
       'id_dijagnoza': { 'table':'id_dijagnoza' , 'column_width':0, 'column_anchor':W} ,

       'MKB - šifra': { 'table':'\nMKB - šifra' , 'column_width':F_SIZE*7, 'column_anchor':W },
       'Opis Dijagnoze': { 'table':'\nOpis Dijagnoze' , 'column_width':F_SIZE*48, 'column_anchor':W },
       }

ZaposleniTable = {
       'ID': { 'table':'\nID' , 'column_width':F_SIZE*4, 'column_anchor':W },
       'id_zaposleni': { 'table':'id_zaposleni' , 'column_width':0, 'column_anchor':W} ,

       'Zaposleni': { 'table':'\nZaposleni' , 'column_width':F_SIZE*27, 'column_anchor':W }
       }

LogsTable = {
       'ID': { 'table':'\nID' , 'column_width':F_SIZE*4, 'column_anchor':W },

       'ID Time': { 'table':'\nID Time' , 'column_width':F_SIZE*16, 'column_anchor':W },
       'Email': { 'table':'\nEmail' , 'column_width':F_SIZE*16, 'column_anchor':W },
       'Query': { 'table':'\nQuery' , 'column_width':F_SIZE*16, 'column_anchor':W },
       'Error': { 'table':'\nError' , 'column_width':F_SIZE*27, 'column_anchor':W }
       }

SessionTable = {
       'ID': { 'table':'\nID' , 'column_width':F_SIZE*4, 'column_anchor':W },

       'Email': { 'table':'\nEmail' , 'column_width':0, 'column_anchor':W} ,
       'Logged IN': { 'table':'\nLogged IN' , 'column_width':F_SIZE*16, 'column_anchor':W },
       'Logged OUT': { 'table':'\nLogged OUT' , 'column_width':F_SIZE*16, 'column_anchor':W },
       'Session': { 'table':'\nSession' , 'column_width':F_SIZE*16, 'column_anchor':W }
       }

SIGNS = [ 'EQUAL', 'LIKE', 'NOT LIKE' , 'GREATER', 'LESS', 'BETWEEN' ]

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
                                    'Zaposleni':( 'Zaposleni', 10, (1,0,  1,1) ),
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

GD_SLIKE = ['1e-KyYcDIt_V2Gn79blz0gESZLpeV4xVn']
GD_MAIN = ['1ybEVItyB75BParYUN2-ab_oVe2tBj1NW']

RHMH_dict = {
    'path':os.path.join(directory,'RHMH.db'),
    'id':'1vLJxgeqXMXfqGE_PTrtywdL69TPZDjhw',
    'mime':'application/x-sqlite3'}
LOGS_dict = {
    'path':os.path.join(directory,'LOGS.db'),
    'mime':'application/x-sqlite3'}
GD_LOGS_dict = {
    'path':os.path.join(directory,'GD_LOGS.db'),
    'id':'1uvz-BN2DI4_7xcs7-dwJmfz-Z7jrpMU2',
    'mime':'application/x-sqlite3'}

SETTINGS_dict = {
    'path':os.path.join(directory,'Default.json'),
    'id':'1h5n_FSEKEQQoed2yjJOsXMSaQYefP0cx',
    'mime':'application/json'}

MIME = {'PNG' : 'image/png',
        'JPG' : 'image/jpeg',
        'JPEG' : 'image/jpeg',
        'HEIF' : 'image/heif',
        'HEIC' : 'image/heic',
        'MP4': 'video/mp4',
        'MOV': 'video/quicktime'}