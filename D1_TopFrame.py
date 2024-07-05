from A1_Variables import *
from A2_Decorators import method_efficency
from C1_DBMS import Buttons

class TopFrame:
    def __init__(self, root) -> None: 
        self.BUTT = Buttons()
        image, (title_txt, txt_X, txt_Y) = IMAGES['Title']
        
        self.title_image = Image.open(image)
        self.txt_X = txt_X
        self.txt_Y = txt_Y
        self.title_txt = title_txt
    
        self.Title_Frame = tb.Canvas(root, height=title_height)
        self.Title_Frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        self.Title_Frame.bind('<Button-1>' , self.BUTT.lose_focus)
        self.Title_Frame.bind('<Configure>' , self.adjust_title_window)
        
        self.reconect_button = ctk.CTkButton(root, text='Reconect', width=form_butt_width,height=form_butt_height//2, corner_radius=12, font=font_label(),
                                 fg_color=ThemeColors['warning'], text_color=ThemeColors['dark'], text_color_disabled=ThemeColors['secondary'],
                                 command=self.reconecting)
        
    def reconecting(self):
        print('RECONECTING...')

    def remove_title_frame(self,event):
        self.Title_Frame.grid_forget()

    def adjust_title_window(self, event):
        new_width = event.width
        new_height = event.height
        resized_image = self.title_image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        
        self.Title_Frame.image = tk_image 
        self.Title_Frame.delete('all')
        self.Title_Frame.create_image(0, 0, anchor=NW, image=tk_image)
        self.Title_Frame.create_text( new_width * self.txt_X,
                                    new_height * self.txt_Y,
                                    text = self.title_txt,
                                    anchor = NW, font = font_title(), fill = ThemeColors[titleTxtColor] )

        self.Title_Frame.create_window(new_width*0.93, 10, anchor=N, window=self.reconect_button) # position of button