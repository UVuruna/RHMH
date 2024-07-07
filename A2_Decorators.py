from A1_Variables import *
from B3_Media import Media
from B2_SQLite import RHMH

def spam_stopper(button:ctk.CTkButton,root:Tk):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            button.configure(state=DISABLED)
            root.after(BUTTON_LOCK, lambda: button.configure(state=NORMAL))
            return result
        return wrapper
    return decorator

def method_efficency():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_perf = time.perf_counter_ns()
            start_process = time.process_time_ns()
            result = func(*args, **kwargs)
            
            end_process = time.process_time_ns()
            end_perf = time.perf_counter_ns()
            
            process_time_elapsed = (end_process - start_process) / 10**6  # ms
            perf_time_elapsed = (end_perf - start_perf) / 10**6  # ms

            try:
                Class,Method = func.__qualname__.split('.')
            except ValueError:
                Class = 'Initializing'
                Method = func.__qualname__
            if not Class in UserSession:
                UserSession[Class] = {}
            if Method in UserSession[Class]:
                UserSession[Class][Method]['ProccessingTime']['count'] += 1
                UserSession[Class][Method]['ProccessingTime']['time'] += process_time_elapsed

                UserSession[Class][Method]['TotalTime']['count'] += 1
                UserSession[Class][Method]['TotalTime']['time'] += perf_time_elapsed

            else:
                UserSession[Class][Method] = {'ProccessingTime': {}, 'TotalTime': {}}
                UserSession[Class][Method]['ProccessingTime'] = {'count':1 , 'time': process_time_elapsed}
                UserSession[Class][Method]['TotalTime'] = {'count':1 , 'time': perf_time_elapsed}
            return result
        return wrapper
    return decorator

def error_catcher():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(str(e))
                print(traceback.format_exc())
                Time = f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.{datetime.now().strftime('%f')[:3]}' 
                fullerror = traceback.format_exc()
                RHMH.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['User'],
                                        'Query':func.__qualname__, 'Full Query':RHMH.LoggingQuery,
                                        'Error':str(e), 'Full Error': fullerror})
                return
        return wrapper
    return decorator

class PasswordDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.password = None
        self.eye_image = None
        super().__init__(parent, title)

    def body(self, master):
        self.eye_image = Media.label_ImageLoad(IMAGES['Password'])
        lbl = tb.Label(master, image=self.eye_image)
        lbl.grid(row=0, column=0, padx=6, pady=6, sticky=NSEW)
        self.password_entry = tb.Entry(master, show='*')
        self.password_entry.grid(row=1, column=0, padx=13, pady=13)
        return self.password_entry

    def apply(self):
        self.password = self.password_entry.get()

def money():
    return f'MUVS {(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).total_seconds()//13*13:,.0f} $'