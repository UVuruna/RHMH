from A1_Variables import *
from B3_Media import Media
from C1_Controller import Controller

class TopPanel:
    Top_Frame = None

    title_image = None

    txt_X = None
    txt_Y = None
    title_txt = None

    @staticmethod
    def initializeTP(root:Tk) -> None:
        
        try:
            image, (TopPanel.title_txt, TopPanel.txt_X, TopPanel.txt_Y) = TITLE_IMAGE
        except Exception:
            image = TITLE_IMAGE

        TopPanel.title_image = Image.open(image)

        Controller.Top_Frame = tb.Canvas(root, height=int(TITLE_HEIGHT*HEIGHT))
        Controller.Top_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        Controller.Top_Frame.bind('<Button-1>' , Controller.lose_focus)
        Controller.Top_Frame.bind('<Configure>' , TopPanel.adjust_title_window)

        butt_color = ThemeColors['warning']
        Controller.Reconnect_Button = ctk.CTkButton(root, text='Connect', width=buttonX, height=buttonY//2, corner_radius=12, font=font_medium('bold'),
                                    fg_color=butt_color, text_color=ThemeColors['bg'],
                                    text_color_disabled=ThemeColors['secondary'], hover_color=Media.darken_color(butt_color),
                                    command=Controller.starting_application)

    @staticmethod
    def adjust_title_window(event):
        new_width = event.width
        new_height = event.height
        resized_image = TopPanel.title_image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        
        Controller.Top_Frame.image = tk_image 
        Controller.Top_Frame.delete('all')
        Controller.Top_Frame.create_image(0, 0, anchor=NW, image=tk_image)
        
        if TopPanel.title_txt:
            Controller.Top_Frame.create_text( new_width * TopPanel.txt_X,
                                        new_height * TopPanel.txt_Y,
                                        text = TopPanel.title_txt,
                                        anchor = NW, font = font_verybig(), fill = ThemeColors[color_titletext] )
        
        if Controller.Connected is False:
            Controller.Reconnect_window = Controller.Top_Frame.create_window(
                                                new_width*0.93, 10, anchor=N, window=Controller.Reconnect_Button)