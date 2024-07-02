from A_Variables import *

def spam_stopper(button:ctk.CTkButton,root:Tk):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            button.configure(state='disabled')
            root.after(BUTTON_LOCK, lambda: button.configure(state='normal'))
            return result
        return wrapper
    return decorator

def method_efficency(session:dict=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_process = time.process_time_ns()
            start_perf = time.perf_counter_ns()
            
            result = func(*args, **kwargs)
            
            end_process = time.process_time_ns()
            end_perf = time.perf_counter_ns()
            
            process_time_elapsed = (end_process - start_process) / 10**3  # mikrosekunde
            perf_time_elapsed = (end_perf - start_perf) / 10**3  # mikrosekunde
            if session:
                try:
                    process = session[func.__name__]

                    process['ProccessingTime']['count'] += 1
                    process['ProccessingTime']['time'] += process_time_elapsed
                    if process['ProccessingTime']['max'] < process_time_elapsed:
                        process['ProccessingTime']['max'] = process_time_elapsed
                    if process['ProccessingTime']['min'] > process_time_elapsed:
                        process['ProccessingTime']['min'] = process_time_elapsed

                    process['TotalTime']['count'] += 1
                    process['TotalTime']['time'] += perf_time_elapsed
                    if process['TotalTime']['max'] < perf_time_elapsed:
                        process['TotalTime']['max'] = perf_time_elapsed
                    if process['TotalTime']['min'] > perf_time_elapsed:
                        process['TotalTime']['min'] = perf_time_elapsed

                except KeyError:
                    session[func.__name__] = {'ProccessingTime': {}, 'TotalTime': {}}
                    session[func.__name__]['ProccessingTime'] = {'count':1 ,
                                                                 'time':process_time_elapsed,
                                                                 'max':process_time_elapsed,
                                                                 'min':process_time_elapsed}
                    session[func.__name__]['TotalTime'] = {'count':1 ,
                                                           'time':perf_time_elapsed,
                                                           'max':perf_time_elapsed,
                                                           'min':perf_time_elapsed}
            return result
        return wrapper
    return decorator

def error_catcher(CLASS=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if CLASS:
                    # Ovo je da bi dobio 1 ms preciznost (0.000 s)
                    Time = f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.{datetime.now().strftime('%f')[:3]}' 
                    fullerror = traceback.format_exc()
                    def execute():
                        CLASS.execute_Insert('logs',**{'ID Time':Time, 'Email':CLASS.UserSession['User'],
                                                'Query':func.__name__, 'Full Query':CLASS.LoggingQuery,
                                                'Error':str(e), 'Full Error': fullerror})
                    threading.Thread(target=execute).start()
                else:
                    print(str(e))
                    print(traceback.format_exc())
                return
        return wrapper
    return decorator

def password():
    return f'MUVS {(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).total_seconds()//13*13:,.0f} $'

class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance
    
if __name__=='__main__':
    print(password())