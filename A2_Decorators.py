from A1_Variables import *
from B2_SQLite import RHMH,LOGS

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


            Class,Method = func.__qualname__.split('.')
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
                print(e)
                Time = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}'
                fullerror = traceback.format_exc()
                LOGS.execute_Insert('logs',**{'ID Time':Time, 'Email':UserSession['Email'],
                                        'Query':func.__qualname__, 'Full Query':RHMH.LoggingQuery,
                                        'Error':str(e), 'Full Error': fullerror})
                raise # Da bi radio try-except unutar metoda
        return wrapper
    return decorator

def print_dict(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            print_dict(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))

class PC:
    @staticmethod
    def get_available_fonts():
        flist = findSystemFonts()
        font_names = {FontProperties(fname=font).get_name() for font in flist}
        font_names = list(font_names)
        font_names.sort()
        return font_names

    @staticmethod
    def get_cpu_info():
        cpu = cpuinfo.get_cpu_info() # OVO JE SPORO JAKO oko 1.5 sec ali thread ce resiti stvar
        cpu_info = {
            'Processor Name': cpu['brand_raw'],
            'Physical Cores': psutil.cpu_count(logical=False),
            'Total Cores': psutil.cpu_count(logical=True),
            'Frequency': f'{psutil.cpu_freq().max:.0f} Mhz',
            }
        return cpu_info

    @staticmethod
    def get_gpu_info():
        gpu_info = dict()

        if os.name == 'nt':
            gpus = GPUtil.getGPUs()
            if not gpus:
                return 'No GPU found.'
            for gpu in gpus:
                gpu_info = {
                'GPU Name': gpu.name,
                'VRAM': f'{gpu.memoryTotal:,.0f} MB'
                }
            return gpu_info
        
        elif os.name == 'posix':  # macOS
            gpu_info_str = subprocess.check_output(['system_profiler', 'SPDisplaysDataType'], text=True)
            pattern = re.compile(r'Chipset Model:\s+(.*?)\n.*?VRAM \(Total\):\s+(\d+)\s+GB', re.DOTALL)
            match = pattern.search(gpu_info_str)
            
            if match:
                gpu_name = match.group(1).strip()
                vram = f'{int(match.group(2).strip())*1024:,.0f} MB'
                gpu_info = {
                    'GPU Name': gpu_name,
                    'VRAM': vram}
                return gpu_info
            else:
                return 'No GPU found.'

    @staticmethod
    def get_ram_info():
        svmem = psutil.virtual_memory()
        ram_info = {
            'Total RAM': f'{svmem.total / (1024 ** 2):,.0f} MB'
            }
        return ram_info

if __name__=='__main__':
    a = time.time()