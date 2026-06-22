import os
import inspect
from datetime import datetime

def read_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def write_to_file(filename, contents, type = 'w'):
    with open(filename, type) as file:
        file.write(contents)

def debug(message : str, filename : str = None):
    os.makedirs("debug", exist_ok=True)
    if not filename:
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename
        gamemode = os.path.basename(caller_filename)
        
        base_filename = os.path.splitext(gamemode)[0] + "-" + datetime.now().strftime("%m%d%y")
        filename = base_filename
        suffix = 0
        
        while os.path.exists(f"debug/{filename}.log"):
            suffix += 1
            filename = base_filename + "-" + str(suffix)
        
        filename += ".log"
    
    write_to_file(f"debug/{filename}", message + "\n", type = 'a')
    return filename