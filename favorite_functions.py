import inspect
import re
import os
from win32com.client import GetActiveObject
import customtkinter as customtkinter
import time



def _get_module(frame):
    path:str = frame.f_code.co_filename
    filename = path.rsplit('\\')[-1]
    test = filename.removesuffix('.py')
    return test

def debug_print(*args):
    """Print each argument's source name, type, and value, prefixed with the calling line number."""
    frame = inspect.currentframe().f_back
    module = _get_module(frame)
    line_number = frame.f_lineno
    context = inspect.getframeinfo(frame).code_context
    call_line = context[0] if context else ''
    match = re.search(r'debug_print\s*\((.*)\)', call_line)
    arg_names = [a.strip() for a in match.group(1).split(',')] if match else []

    for i, value in enumerate(args):
        name = arg_names[i] if i < len(arg_names) else f'arg{i}'
        print(f'Line [{line_number}] in {module}: {type(value)}: {name} = {value!r}')





def force_csv_close_and_delete(target_path):
    """Close target_path in Excel without saving (if it's open there), then delete it.
    Returns True if target_path no longer exists afterward, False otherwise."""
    target_path = os.path.abspath(target_path)

    try:
        excel = GetActiveObject('Excel.Application')
    except Exception:
        excel = None  # Excel isn't running, so nothing has the file open

    if excel:
        try:
            for workbook in excel.Workbooks:
                debug_print(workbook.FullName)
                if os.path.normcase(workbook.FullName) == os.path.normcase(target_path):
                    debug_print('FOUND!')
                    workbook.Close(SaveChanges = False)
                    break
        except Exception as e:
            debug_print(e)  # e.g. Excel is busy with a dialog; the delete below decides the result

    for attempt in range(10):
        try:
            os.remove(target_path)
            debug_print(f'Successfully closed and deleted {target_path}')
            return True
        except FileNotFoundError:
            return True
        except PermissionError as e:
            debug_print(e)
            time.sleep(0.5)
        except OSError as e:
            debug_print(e)
            return False

    debug_print(f'Could not delete {target_path}')
    return False



class GridManager:
    def __init__(self):

        self.column = 0
        self.row = 0

    def next_row(self):
        self.row += 1

    def next_column(self):
        self.column += 1

    def set_column(self, column:int):
        self.column = column

    def set_row(self, row:int):
        self.row = row

def proper_string_from_snake_case(snakey_string:str):
    lowercase_list = snakey_string.split('_')
    proper_list = [word.capitalize() for word in lowercase_list]
    proper_string = ' '.join(proper_list)
    return proper_string

if __name__ == '__main__':
    pass


