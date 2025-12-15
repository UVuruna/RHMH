
import ttkbootstrap as tb
from tkinter import CENTER,BOTH,YES
import os
from itertools import cycle
from pathlib import Path
from PIL import Image, ImageTk
import threading

class Loading_Splash:
    def __init__(self, folder, color='#ffffff', dimension=850,  fps=12):
        self.folder = folder
        self.dimension = dimension
        self.fps = fps
        self.color = color

        self.splash = None
        self.images = [None for _ in range(32)]
        threads = []
        self.lock = threading.Lock()
        for i in range(32):
            threads.append(threading.Thread(target=self.load_image, args=(i,)))

        for t in threads:
            t:threading.Thread
            t.start()

        self.image_cycle = None
        self.framerate = 1000 // fps
        self.animation_id = None
        self.is_playing = False

    def load_image(self,i):
        file_path = Path(self.folder) / f"{i}.gif"
        image = Image.open(file_path)
        if self.dimension != 850:
            image = image.resize((self.dimension, self.dimension), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)
        with self.lock:
            self.images[i] = image_tk

    def create_splash(self, widget, alpha=1):
        if self.splash is not None:
            return
        
        if isinstance(widget, tb.Window):
            self.splash = tb.Toplevel(size=(self.dimension,self.dimension), alpha=alpha)
            self.splash.place_window_center()
            self.splash.transient(widget)
            if os.name == 'nt':
                self.splash.wm_attributes('-transparentcolor', self.color)
            self.splash.overrideredirect(True)
        else:
            self.splash = widget

        self.image_cycle = cycle(self.images)
        self.img_container = tb.Label(self.splash, image=next(self.image_cycle), anchor=CENTER)
        self.img_container.pack(fill=BOTH, expand=YES)
        self.play()

    def play(self):
        if not self.is_playing:
            self.is_playing = True
            self._animate()

    def stop(self):
        if self.is_playing:
            self.is_playing = False
            if self.animation_id:
                self.splash.after_cancel(self.animation_id)
                self.animation_id = None
        if self.splash:
            self.splash.destroy()
            self.splash = None

    def _animate(self):
        if self.is_playing:
            self.img_container.configure(image=next(self.image_cycle))
            self.animation_id = self.splash.after(self.framerate, self._animate)

if __name__ == '__main__':
    from ttkbootstrap import Colors
    import time
    start = time.time()
    def splash():
        root = tb.Window(alpha=0)

        ThemeColors = {}
        directory = os.path.dirname(os.path.abspath(__file__))

        style = tb.Style(theme='Sea')
        for color_label in Colors.label_iter():
            color = style.colors.get(color_label)
            ThemeColors[color_label] = color

        folder = os.path.join(directory,f'Slike/gif_MUVS')
        gif = Loading_Splash(folder=folder, color=ThemeColors['bg'])
        gif.create_splash(root)

        root.after(5000, gif.stop)
        print(time.time()-start)
        root.mainloop()

    splash()