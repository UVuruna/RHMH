from A1_Variables import *
from C2_ManageDB import ManageDB

class TopPanel:
    Top_Frame = None

    title_image = None

    txt_X = None
    txt_Y = None
    title_txt = None

    @staticmethod
    def initialize(root:Tk) -> None:

        image, (TopPanel.title_txt, TopPanel.txt_X, TopPanel.txt_Y) = IMAGES['Title']

        TopPanel.title_image = Image.open(image)

        TopPanel.Top_Frame = tb.Canvas(root, height=title_height)
        TopPanel.Top_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        TopPanel.Top_Frame.bind('<Button-1>' , ManageDB.lose_focus)
        TopPanel.Top_Frame.bind('<Configure>' , TopPanel.adjust_title_window)

        TopPanel.reconect_button = ctk.CTkButton(root, text='Reconect', width=buttonX,height=buttonY//2, corner_radius=12, font=font_medium(),
                                    fg_color=ThemeColors['warning'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                    command=TopPanel.reconecting)

    @staticmethod    
    def reconecting():
        print('RECONECTING...')

    @staticmethod
    def adjust_title_window( event):
        new_width = event.width
        new_height = event.height
        resized_image = TopPanel.title_image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        
        TopPanel.Top_Frame.image = tk_image 
        TopPanel.Top_Frame.delete('all')
        TopPanel.Top_Frame.create_image(0, 0, anchor=NW, image=tk_image)
        TopPanel.Top_Frame.create_text( new_width * TopPanel.txt_X,
                                    new_height * TopPanel.txt_Y,
                                    text = TopPanel.title_txt,
                                    anchor = NW, font = font_verybig(), fill = ThemeColors[color_titletext] )

        TopPanel.Top_Frame.create_window(new_width*0.93, 10, anchor=N, window=TopPanel.reconect_button) # position of button

if __name__=='__main__':
    pass