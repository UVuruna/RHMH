from A1_Variables import *

pillow_heif.register_heif_opener()

class Media:
    TitleIcons = []
    ThemeIcons = []
    TopLevel = None
    Downloading = False
    
    Slike_Viewer: Canvas = None
    Blob_Data = None
    Image_Active: Image.Image = None
    Image_Scale: int = 1
    Image_Zoomed_Width: int = None
    Image_Zoomed_Height: int = None
    delta = 1.18

    AboutImage:  Image.Image = None
    AboutCanvas:      Canvas = None
    
    @staticmethod
    def ProgressBar_DownloadingImages(title:str, titletxt:list, width:int):
        Media.TopLevel = tb.Toplevel()
        Media.TopLevel.iconify()
        Media.TopLevel.title(f'{title}...')
        Media.TopLevel.grid_columnconfigure(0, weight=1)
        Media.TopLevel.resizable(False,False)
        if os.name == 'nt':  # Windows
            Media.TopLevel.attributes('-toolwindow', True)
        else:  # macOS/Linux
            Media.TopLevel.attributes('-type', 'dialog')
        
        tb.Label(Media.TopLevel, text=f'{title} selected Images', anchor=CENTER, justify=CENTER, font=font_medium()).grid(
            row=0, column=0, columnspan=2, pady=24, sticky=NSEW)

        text_widget = tb.Text(Media.TopLevel, wrap=NONE, height=10, width=width, font=font_default)
        text_widget.grid(row=1, column=0, sticky=NSEW)

        scrollbar = tb.Scrollbar(Media.TopLevel, orient=VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=1, column=1, sticky=NS)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.tag_configure('success', foreground=ThemeColors['success'])

        for i, txt in enumerate(titletxt):
            text_widget.insert(END, f'{i+1}. {txt}\n')

        text_widget.configure(state=DISABLED)
       
        bar = tb.Floodgauge(Media.TopLevel, maximum=100, mode='determinate', value=0, bootstyle='primary', mask='Downloading...', font=font_big())
        bar.grid(row=2, column=0, columnspan=2, padx=24, pady=24, sticky=EW)

        Media.TopLevel.deiconify()
        Media.TopLevel.place_window_center()
        return text_widget,bar

    @staticmethod
    def label_ImageLoad(images_list):
        return_images = []
        for (img,width,height) in images_list:
            raw_img = Image.open(img)
            resize_img = raw_img.resize((width,height))
            return_images.append(ImageTk.PhotoImage(resize_img))
        return return_images

    @staticmethod
    def hover_label_button(event,img):
        label:tb.Label = event.widget
        label.config(image=img)

    def image_to_blob(file_path):
        with open(file_path, 'rb') as f:
            blob_data = f.read()
        return blob_data

    @staticmethod
    def get_image(image_blob_data): # Format za Canvas
        image = Image.open(io.BytesIO(image_blob_data))
        return image

    @staticmethod
    def resize_image(image, max_width, max_height, savescale=False):
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        scale_ratio = min(width_ratio, height_ratio)
        if savescale is True:
            Media.Image_Scale = scale_ratio

        new_width = int(image.width * scale_ratio)
        new_height = int(image.height * scale_ratio)
        return image.resize((new_width, new_height), Image.LANCZOS)

    @staticmethod
    def create_video_thumbnail(video_data):
        if not os.path.exists(os.path.join(directory,'temporary')):
            os.makedirs(os.path.join(directory,'temporary'))
        video_file = os.path.join(directory,'temporary/temp_video.mp4')
        with open(video_file, 'wb') as f:
            f.write(video_data)

        # Capture the first frame of the video
        cap = cv2.VideoCapture(video_file)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception('Failed to capture video frame')

        # Convert the frame to a PIL image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Add play button overlay
        width, height = image.size
        play_button_size = min(width, height) // 4
        play_button = Image.open(IMAGES['Play Video']).resize((play_button_size, play_button_size))
        play_button_pos = ((width - play_button_size) // 2, (height - play_button_size) // 2)
        image.paste(play_button, play_button_pos, play_button)

        return image,video_file

    @staticmethod
    def play_video(event,video_data):
        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(video_data))
        elif os.name == 'posix':  # For macOS and Linux
            if os.uname().sysname == 'Darwin':  # macOS
                subprocess.call(['open', os.path.abspath(video_data)])
            else:  # Linux
                subprocess.call(['xdg-open', os.path.abspath(video_data)])

    @staticmethod
    def open_image(event,image_data):
        # Save video data to a temporary file
        if not os.path.exists(os.path.join(directory,'temporary')):
            os.makedirs(os.path.join(directory,'temporary'))
        image_file = os.path.join(directory,'temporary/temp_image.png')
        with open(image_file, 'wb') as f:
            f.write(image_data)

        if not os.path.exists(image_file):
            return

        if os.name == 'nt':  # For Windows
            os.startfile(os.path.abspath(image_file))
        elif os.name == 'posix':  # For macOS and Linux
            if os.uname().sysname == 'Darwin':  # macOS
                subprocess.call(['open', os.path.abspath(image_file)])
            else:  # Linux
                subprocess.call(['xdg-open', os.path.abspath(image_file)])

    @staticmethod
    def make_cropped_part():
        X_scroll = Media.Slike_Viewer.xview()
        Y_scroll = Media.Slike_Viewer.yview()
        left,right = (X_scroll[0]*Media.Image_Zoomed_Width,
                   X_scroll[1]*Media.Image_Zoomed_Width) # (NW,NE) od WIDTH (left i right)
        top,bottom = (Y_scroll[0]*Media.Image_Zoomed_Height,
                     Y_scroll[1]*Media.Image_Zoomed_Height) # (NE,SE) od HEIGHT (top i bottom)
        Media.Slike_Viewer.configure(scrollregion=(0,0,Media.Image_Zoomed_Width,Media.Image_Zoomed_Height))

        image = Media.Image_Active.crop((left,top,right,bottom))
        bytes_image = io.BytesIO()
        image.save(bytes_image, format='png')
        byte_data = bytes_image.getvalue()
        Media.open_image(event=None,image_data=byte_data)

    @staticmethod
    def zoom(event):
        # Skaliranje slike
        temp_scale = Media.Image_Scale
        if event.delta > 0 or event.num == 4:
            temp_scale *= 1.18
        elif event.delta < 0 or event.num == 5:
            temp_scale /= 1.18
        if min(Media.Image_Active.width,Media.Image_Active.height)*temp_scale < 33: return
        if max(Media.Image_Active.width,Media.Image_Active.height)*temp_scale > 6000: return

        Media.Image_Scale = temp_scale
        Media.Image_Zoomed_Width = int(Media.Image_Active.width * Media.Image_Scale)
        Media.Image_Zoomed_Height = int(Media.Image_Active.height * Media.Image_Scale)

        image = Media.Image_Active.crop()
        image = Media.Image_Active.resize((Media.Image_Zoomed_Width, Media.Image_Zoomed_Height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        Media.Slike_Viewer.delete('all')

        Media.Slike_Viewer.create_image(Media.Slike_Viewer.winfo_width()//2, Media.Slike_Viewer.winfo_height()//2, anchor=CENTER, image=image)
        Media.Slike_Viewer.image = image
        Media.Slike_Viewer.config(scrollregion=Media.Slike_Viewer.bbox(ALL))

    @staticmethod
    def move_from(event):
        Media.Slike_Viewer.scan_mark(event.x, event.y)

    @staticmethod
    def move_to(event):
        if Media.Image_Zoomed_Height:
            Media.Slike_Viewer.scan_dragto(event.x, event.y, gain=1)

    @staticmethod
    def ajdust_About_logo(event):
        canvas_width = event.width
        canvas_height = event.height

        resized_image = Media.AboutImage.resize((canvas_width, canvas_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        
        Media.AboutCanvas.image = tk_image 
        Media.AboutCanvas.delete('all')
        Media.AboutCanvas.create_image(0, 0, anchor=NW, image=tk_image)