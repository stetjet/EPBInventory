import inspect
import re
import string
import inflect
import unicodedata as unicode
import os
import win32com.client
import customtkinter as customtkinter
from docx import Document
import time

def spell_number(number:int):
    """Returns a the number spelled out as a string with all lower case letters"""
    number_to_text_converter = inflect.engine()
    text_superscript = number_to_text_converter.number_to_words(number)
    return text_superscript

def superscript(number:int):

    strung = str(number)
    nums_list = []
    for char in strung:
        lower = spell_number(int(char))
        proper = lower.capitalize() 
        supered = unicode.lookup(f'Superscript {proper}')
        nums_list.append(supered)

    returnable = ''.join(nums_list)
    return returnable

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




def flip_bool(boolean:bool):
    if boolean == True:
        return False
    if boolean == False:
        return True




def hex_from_RGB(r, g, b):
    rgb = (r, g, b)
    hex = '{:02X}{:02X}{:02X}'.format(*rgb)
    return hex


class ColumnList:
    def __init__(self, index:int = None, symbol:str = None):
        if index and symbol:
            raise ValueError("Only one identifier per column")

        if index:
            self.index = index
            self.symbol = get_excel_column_label(index)

        if symbol:
            self.symbol = symbol
            self.index = get_excel_column_number(symbol)

    def __str__(self):
        return self.symbol
    
    def __repr__(self):
        return self.symbol


    def __add__(self, other):
        answer = ColumnList(index = self.index + other)
        return answer

def get_excel_column_label(number, upper_case = True, iteration = 1):
    if upper_case:
        letters = list(string.ascii_uppercase)
    else:
        letters = list(string.ascii_lowercase)

    index = number%26
    leftover = (number - 1)//26
    output = [letters[index-1]]

    if leftover:

        output.extend(get_excel_column_label(leftover, iteration = iteration +1))

    if iteration == 1:
        output.reverse()


    symbol = ''.join(output)

    return symbol

def get_excel_column_number(symbol:str):
    upper_symbol = symbol.upper()
    upper_symbol_list = []
    for letter in upper_symbol:
        upper_symbol_list.append(letter)

    upper_symbol_list.reverse()
    factors = 0
    for letter_index, letter in enumerate(upper_symbol_list):
        for index, LETTER in enumerate(string.ascii_uppercase):
            if letter == LETTER:
                factors += ((index +1) * (26 ** letter_index)) 
    

    return factors

class ExCell:
    def __init__(self, column:str|int = None, row:int = None, contents = None):

        self.row = row

        if type(column) == str:
            self.column = ColumnList(symbol = column)
        elif type(column) == int:
            self.column = ColumnList(index = column)
        else:
            raise TypeError(f'{type(column)}')
        self.contents = contents

        self.cell = f'{self.column}{self.row}'


    def __repr__(self):
        return self.cell
    def __str__(self):
        return self.cell

    def add_rows(self, number_of_rows):
        answer = ExCell(self.column.index, row = self.row + number_of_rows)
        return answer

    def add_columns(self, number_of_columns):

        answer = ExCell(self.column.index + number_of_columns, row = self.row)
        return answer
    def set_contents(self, new_contents):
        self.contents = new_contents


def force_document_close_and_delete(app_string, target_path):

    try:
        word_docs = win32com.client.GetActiveObject(app_string, target_path)
        for word_doc in word_docs.Documents:
            debug_print(word_doc.FullName)
            if word_doc.FullName[-9:] == target_path:
                debug_print('FOUND!')
                word_doc.Close(SaveChanges = False)
                for attempt in range(10):
                    try:
                        os.remove('demo.docx')
                        break
                    except FileNotFoundError:
                        break
                    except PermissionError as e:
                        debug_print(e)
                        time.sleep(0.5)
            else:
                debug_print('File Not Found')
    except Exception as e:
        debug_print(e)
        return
    debug_print(f'Successfully closed and deleted {target_path}')
    return


def place_widget_under(summon_widget: customtkinter.CTkBaseClass, wizard_widget):
    toplevel = summon_widget.winfo_toplevel()

    scaling = customtkinter.ScalingTracker.get_widget_scaling(summon_widget)
    global_wizard_placement = (wizard_widget.winfo_rootx(), 
                        wizard_widget.winfo_rooty())
    global_window_placement = (toplevel.winfo_rootx(), toplevel.winfo_rooty())
    button_height = wizard_widget.winfo_height()

    local_wizard_placement = (global_wizard_placement[0] - global_window_placement[0], global_wizard_placement[1] - global_window_placement[1])
    x=(local_wizard_placement[0] + 15)/scaling
    y=(button_height + local_wizard_placement[1]+5)/scaling
    summon_widget.place(x=x, y=y)

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


