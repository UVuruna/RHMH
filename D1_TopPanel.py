from A1_Variables import *
from B1_GoogleDrive import GoogleDrive
from C1_Controller import Controller

class TopPanel:
    Top_Frame = None

    title_image = None

    txt_X = None
    txt_Y = None
    title_txt = None

    @staticmethod
    def initialize(root:Tk) -> None:
        
        try:
            image, (TopPanel.title_txt, TopPanel.txt_X, TopPanel.txt_Y) = TITLE_IMAGE
        except Exception:
            image = TITLE_IMAGE if not isinstance(TITLE_IMAGE,list) else TITLE_IMAGE[0]

        TopPanel.title_image = Image.open(image)

        Controller.Top_Frame = tb.Canvas(root, height=title_height)
        Controller.Top_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        Controller.Top_Frame.bind('<Button-1>' , Controller.lose_focus)
        Controller.Top_Frame.bind('<Configure>' , TopPanel.adjust_title_window)

        Controller.Reconnect_Button = ctk.CTkButton(root, text='Connect', width=buttonX, height=buttonY//2, corner_radius=12, font=font_medium(),
                                    fg_color=ThemeColors['warning'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
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

if __name__=='__main__':
    pass