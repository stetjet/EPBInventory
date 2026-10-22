import customtkinter as ctk
from schema import *
import yaml
from favorite_functions import debug_print, GridManager, proper_string_from_snake_case, force_csv_close_and_delete
import csv
from tkinter import messagebox as mb
from paths import FILTERS_PATH, REPORT_PATH
import os

# to do:
#settings to allow for changing filter options
#make create_shoes close on button click
#main_frame automatically updates after changes
#make student searchable instead of exact match


with open(FILTERS_PATH, 'r') as filters_file:
    filter_options = yaml.safe_load(filters_file)

minwidths = [50, 80, 100, 150, 100, 100, 100, 100, 60, 100, 120, 60, 460]
selected_shoes = [] #shoes with their checkbox checked
active_shoes = []   #all shoes displaying on the main screen

def update_selected():
    selected_shoes.clear()
    for shoe in active_shoes:
        if shoe.is_selected.get():
            selected_shoes.append(shoe)
    debug_print(active_shoes)
    debug_print(selected_shoes)



class ShoeFrame:
    def __init__(self, master, master_grid_manager:GridManager, shoe_id, bag, style, whole_size:int, width, shank, vamp, shape, sole, availability, student:str, comments:str):

        self.master = master
        self.shoe_id = shoe_id
        self.bag = bag
        self.style = style
        self.size = float(whole_size)
        self.width = width
        self.shank = shank
        self.vamp = vamp
        self.shape = shape
        self.sole = sole
        self.product_id = self._build_product_id()
        self.availability = availability
        self.comments = comments
        self.student = student
        self.grid_manager = master_grid_manager
        self.parameters = [self.shoe_id, self.bag, self.style, self.size, self.width, self.shank, self.vamp, self.shape, self.sole, self.availability, self.student, self.comments]
        self.is_selected = ctk.BooleanVar()
        if self.master:
            self.checkbox = ctk.CTkCheckBox(master, variable = self.is_selected, text = None, width = 20, command = lambda : update_selected())
            self.checkbox.grid(row = self.grid_manager.row, column = self.grid_manager.column, padx = 2)
            self.grid_manager.next_column()

            for parameter in self.parameters:
                parameter_label = ctk.CTkLabel(master, text = parameter)
                parameter_label.grid(row = self.grid_manager.row, column = self.grid_manager.column, sticky = 'ew')
                self.grid_manager.next_column()
        active_shoes.append(self)

    def _build_product_id(self):
        if self.style == 'EUROPEAN 3.0':
            style_abbr = '3.0'
        elif self.style == 'OLD ENCORE':
            style_abbr = 'EN'
        elif self.style == 'AMERICAN 4.0':
            style_abbr = '4.0'
        elif self.style == 'ENCORE 5.0':
            style_abbr = '5.0'
        else:
            style_abbr = self.style[:2] + self.style[-3:]

        product_id = (style_abbr + '-' + str(self.size) + self.width + self.shank[-2:] + self.vamp + self.shape).upper()
        debug_print(product_id)
        return product_id




class FilterDropdown(ctk.CTkFrame):
    def __init__(self, master, filter_name, options:list, variable = None, filters:dict = None):
        super().__init__(master = master)

        self.filter_name = filter_name
        self.label = ctk.CTkLabel(self, text = filter_name)
        self.label.grid(row = 0, column = 0)
        self.var = ctk.StringVar(value = variable.get())
        self.dropdown = ctk.CTkOptionMenu(self, values = options, variable=self.var, command = lambda e: filters.update({self.filter_name: self.var.get()}))
        self.dropdown.grid(row = 0, column = 1)






def _build_filtered_query(filters:dict = None):
    blank_query = f"""SELECT * FROM pointe_shoes"""
    debug_print(filters)
    if is_blank(filters):
        return blank_query

    raw_query = blank_query + ' WHERE'


    searchable_columns = []
    for key in filters.keys():
        if not is_blank({key: filters[key]}):

            if key == 'Sold':
                if filters[key] == 1:
                    searchable_columns.append(' available = 1 ')
                elif filters[key] == 2:
                    searchable_columns.append(' available = 0 ')
                    searchable_columns.append(' sold = 0 ')
                elif filters[key] == 3:
                    searchable_columns.append(' sold = 1 ')
            elif key == 'Size':
                searchable_columns.append(f" us_size = '{filters[key]}' ")  
            elif key == 'Style Option':
                searchable_columns.append(f" style = '{filters[key]}' ")
            else:

                searchable_columns.append(f" {key.lower().replace(' ', '_')} = '{filters[key]}' ")
    
    debug_print(searchable_columns)
    searchable_columns_string = "AND".join(searchable_columns)
    finished_query_string = raw_query + searchable_columns_string + ';'
    return finished_query_string






def is_blank(dictionary:dict) -> bool:
    if dictionary is None:
        return True
    for value in dictionary.values():
        if value is None or value == '' or value == 'None' or value == 0 or value == []:
            continue
        else:
            return False
    return True

    

def update_return_values(target_frame:ctk.CTkFrame, grid_manager:GridManager, filters:dict = None):
    selected_shoes.clear()
    active_shoes.clear()
    for index, child in enumerate(target_frame.winfo_children()):
        if index >= 12: #adjust this number to keep the column headers when populating the search results
            child.destroy()



    grid_manager.set_column(0)

    sql_query = _build_filtered_query(filters)
    debug_print(sql_query)

    
    cur.execute(sql_query)

    shoes = cur.fetchall()
    debug_print(shoes)

    results_frame = ctk.CTkScrollableFrame(target_frame, border_width = 1, border_color = 'blue')
    for index, num in enumerate(minwidths):
        results_frame.columnconfigure(index, minsize = num)
    results_frame.grid(row = 1, column = 0, columnspan = 14, sticky = 'nsew')

    for index, shoe in enumerate(shoes):



        #                                               shoe_id, bag,   style,     size,    width,   shank,   vamp,    shape,   sole, availability,    student, comments
        shoe_frame = ShoeFrame(results_frame, grid_manager, shoe[0], shoe[1], shoe[2], shoe[3], shoe[4], shoe[5], shoe[6], shoe[7], shoe[8], shoe[9], shoe[10], shoe[11])
        grid_manager.set_column(0)
        grid_manager.next_row()

def create_shoe(quantity, filters):
    debug_print(quantity)
    debug_print(filters)
    style = filters['Style Option']
    size = filters['Size']
    width = filters['Width']
    shank = filters['Shank']
    vamp = filters['Vamp']
    shape = filters['Shape']
    sole = filters['Sole']
    availability = filters['Availability']

    created = 0
    while created < quantity:
        try:
            cur.execute(f"""INSERT INTO pointe_shoes (style, us_size, width, shank, vamp, shape, sole, availability) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (style, size, width, shank, vamp, shape, sole, availability))
            conn.commit()
        except Exception as e:
            conn.rollback()
            debug_print(e)
            raise e
        created += 1

def receive_shoes():
    """Changes availability from 'Ordered' to 'Available'"""
    for shoe in selected_shoes:
        try:
            cur.execute("""UPDATE pointe_shoes SET availability = 'Available' WHERE shoe_pk = ?""", (shoe.shoe_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e


def reserve_shoes():
    for shoe in selected_shoes:
        reserve_shoe(shoe)

def reserve_shoe(shoe:ShoeFrame):
    student_input = ctk.CTkInputDialog(title = f'Reserve {shoe.product_id}', text = 'Reserve this shoe for:')

    student = student_input.get_input()
    debug_print(student)
    try:
        cur.execute("""UPDATE pointe_shoes SET student = ? WHERE shoe_pk = ?""", (student, shoe.shoe_id))
        conn.commit()
    except Exception as e:
        debug_print(e)
        raise e

def sell_shoes():
    for shoe in selected_shoes:
        sell_shoe(shoe)

def sell_shoe(shoe:ShoeFrame):
    sell_input = ctk.CTkInputDialog(title = f'Sell {shoe.product_id}', text = 'Sell this shoe to:')
    sell_to = sell_input.get_input()
    try:
        cur.execute(f"""UPDATE pointe_shoes SET student = '{sell_to}' WHERE shoe_pk = {shoe.shoe_id}""")
        cur.execute(f"""UPDATE pointe_shoes SET availability = 'Sold' WHERE shoe_pk = {shoe.shoe_id}""")
        conn.commit()
    except Exception as e:
        debug_print(e)
        raise e

def assign_bags():
    for shoe in selected_shoes:
        assign_bag(shoe)

def assign_bag(shoe:ShoeFrame):
    bag_input = ctk.CTkInputDialog(title = f"Assign bag to {shoe.product_id}", text = "Bag Number:")
    bag_number = bag_input.get_input()
    try:
        cur.execute(f"""UPDATE pointe_shoes SET bag = '{bag_number} WHERE shoe_pk = {shoe.shoe_id}""")
        conn.commit()
    except Exception as e:
        debug_print(e)
        raise e

def inventory_report():

    if force_csv_close_and_delete(REPORT_PATH):
        try:
            cur.execute(_build_filtered_query())
            shoes = cur.fetchall()
            for index, shoe in enumerate(shoes):
                #                                               shoe_id, bag,   style,     size,    width,   shank,   vamp,    shape,   sole, availability,    student, comments
                shoe_frame = ShoeFrame(None, None, shoe[0], shoe[1], shoe[2], shoe[3], shoe[4], shoe[5], shoe[6], shoe[7], shoe[8], shoe[9], shoe[10], shoe[11])

            shoe_report_dict = {}
            for shoe in active_shoes:
                shoe_dict = {'Total Unsold Inventory': 0, 'Total Sold': 0, 'Ordered': 0, 'Available': 0, 'Reserved': 0, 'Other': 0}
                if shoe.product_id not in shoe_report_dict.keys():
                    shoe_report_dict[shoe.product_id] = shoe_dict
                if shoe.availability == 'Ordered':
                    shoe_report_dict[shoe.product_id]['Ordered'] += 1
                    shoe_report_dict[shoe.product_id]['Total Unsold Inventory'] += 1
                if shoe.availability == 'Available':
                    shoe_report_dict[shoe.product_id]['Available'] += 1
                    shoe_report_dict[shoe.product_id]['Total Unsold Inventory'] += 1
                if shoe.availability == 'Reserved':
                    shoe_report_dict[shoe.product_id]['Reserved'] += 1
                    shoe_report_dict[shoe.product_id]['Total Unsold Inventory'] += 1
                if shoe.availability == 'Other':
                    shoe_report_dict[shoe.product_id]['Other'] += 1
                if shoe.availability == 'Sold':
                    shoe_report_dict[shoe.product_id]['Total Sold'] += 1

            debug_print(shoe_report_dict)
        except Exception as e:
            debug_print(e)
            raise e

        with open(REPORT_PATH, 'w') as report:
            pencil = csv.writer(report)
            pencil.writerow(['Product ID', 'Total Unsold Inventory', 'Total Sold', 'Ordered', 'Available', 'Reserved', 'Other'])
            for shoe in shoe_report_dict:
                pencil.writerow([shoe, shoe_report_dict[shoe]['Total Unsold Inventory'], shoe_report_dict[shoe]['Total Sold'], shoe_report_dict[shoe]['Ordered'], shoe_report_dict[shoe]['Available'], shoe_report_dict[shoe]['Reserved'], shoe_report_dict[shoe]['Other']])
            os.startfile(REPORT_PATH)
    else:
        mb.showerror('Report In Use', 'Close the inventory report in Excel and try again.')
        return

def retrieve_columns(tablename):
    cur.execute(f"""PRAGMA table_info({tablename});""")
    columns = []
    for col in cur.fetchall():
        columns.append(col[1])
    return columns

def _populate_filters():
    filters = {}
    for option in filter_options.keys():
        filters[option] = None
    filters['Bag'] = []
    filters['Student'] = None
    filters['Comments'] = None
    return filters

def open_shoe_create():
    shoe_create = ctk.CTkToplevel()
    filters = _populate_filters()

    creation_gridder = GridManager()

    search_terms = {}
    for filter in filter_options.keys():
        debug_print(filter)

        filter_input = FilterDropdown(shoe_create, filter, filter_options[filter][1:], ctk.StringVar(filters[filter]), filters)
        filter_input.grid(row = creation_gridder.row, column = creation_gridder.column, sticky = 'e', padx = 3, pady = 5)
        search_terms[filter] = filter_input.var.get()
        creation_gridder.next_row()

    student_frame = ctk.CTkFrame(shoe_create)
    student_frame.grid(row = creation_gridder.row, column = creation_gridder.column, sticky = 'e')
    
    student_label = ctk.CTkLabel(student_frame, text = 'Student')
    student_label.grid(row = 0, column = 0)
    student = ctk.StringVar()
    student_entry = ctk.CTkEntry(student_frame, textvariable=student)

    student_entry.bind('<KeyRelease>', lambda e: filters.update({'Student': student.get()}))
    student_entry.grid(row = 0, column = 1)
    
    creation_gridder.next_row()


    quantity_frame = ctk.CTkFrame(shoe_create)
    create_quantity = ctk.IntVar(value=1)
    quantity_label = ctk.CTkLabel(quantity_frame, text = 'Quantity:')
    quantity_entry = ctk.CTkEntry(quantity_frame, textvariable = create_quantity)
    quantity_label.grid(row = 0, column = 0)
    quantity_entry.grid(row = 0, column = 1)
    quantity_frame.grid(row = creation_gridder.row, column = creation_gridder.column, sticky = 'e')
    creation_gridder.next_row()


    create_button = ctk.CTkButton(shoe_create, text = 'Create Shoe', command = lambda: create_shoe(create_quantity.get(), filters))
    create_button.grid(row = creation_gridder.row, column = creation_gridder.column)
    creation_gridder.next_row()



def main():
    app = ctk.CTk()

    filters = _populate_filters()
    debug_print(filters)


    for row in range(0, 9):
        app.rowconfigure(row, weight = 1)

    for column in range(0, 7):
        app.columnconfigure(column, weight = 1)

    top_frame = ctk.CTkFrame(app, border_width = 1, border_color = 'blue', height = 100)
    top_frame.grid(row = 0, column = 0, columnspan = 8, sticky = 'nsew')
    inv_report_gen_button = ctk.CTkButton(top_frame, text = 'Generate Inventory Report', command = lambda: inventory_report())
    inv_report_gen_button.grid(row = 0, column = 0)
    open_shoe_create_butt = ctk.CTkButton(top_frame, text = 'Create New Shoes', command = lambda : open_shoe_create())
    open_shoe_create_butt.grid(row = 0, column = 1)

    receive_shoe_butt = ctk.CTkButton(top_frame, text = 'Receive Selected Shoes', command = lambda: receive_shoes())
    receive_shoe_butt.grid(row = 2, column = 2)

    reserve_shoe_butt = ctk.CTkButton(top_frame, text = 'Reserve Selected Shoes', command = lambda : reserve_shoes())
    reserve_shoe_butt.grid(row = 2, column = 3)

    mark_sold_butt = ctk.CTkButton(top_frame, text = 'Mark Selected as Sold', command = lambda : sell_shoes())
    mark_sold_butt.grid(row = 2, column = 4)

    left_frame = ctk.CTkFrame(app, border_width = 1, border_color = 'green')
    left_frame.grid(row = 1, column = 0, rowspan = 6, sticky = 'nsew')

    left_gridder = GridManager()

    search_terms = {}
    for filter in filter_options.keys():
        debug_print(filter)

        filter_input = FilterDropdown(left_frame, filter, filter_options[filter], ctk.StringVar(filters[filter]), filters)
        filter_input.grid(row = left_gridder.row, column = left_gridder.column, sticky = 'e', padx = 3, pady = 5)
        search_terms[filter] = filter_input.var.get()
        left_gridder.next_row()

    student_frame = ctk.CTkFrame(left_frame)
    student_frame.grid(row = left_gridder.row, column = left_gridder.column, sticky = 'e')

    student_label = ctk.CTkLabel(student_frame, text = 'Student')
    student_label.grid(row = 0, column = 0)
    student = ctk.StringVar()
    student_entry = ctk.CTkEntry(student_frame, textvariable=student)

    student_entry.bind('<KeyRelease>', lambda e: filters.update({'Student': student.get()}))
    student_entry.grid(row = 0, column = 1)
    
    left_gridder.next_row()


    search_button = ctk.CTkButton(left_frame, text = 'Apply Filters', command = lambda: update_return_values(main_frame, main_gridder, filters))
    search_button.grid(row = left_gridder.row, column = left_gridder.column)
    left_gridder.next_row()



    main_frame = ctk.CTkFrame(app, border_width = 1, border_color = 'red')
    main_frame.rowconfigure(1, weight = 1)
    main_frame.grid(row = 1, column = 1, columnspan = 7, rowspan = 5, sticky = 'nsew')
    for index, num in enumerate(minwidths):
        main_frame.columnconfigure(index, minsize = num)

    main_gridder = GridManager()
    main_gridder.set_column(1)
    for index, column in enumerate(retrieve_columns('pointe_shoes')):
        if column == 'shoe_pk':
            header = 'Shoe ID'
        elif column == 'us_size':
            header = 'US Size'
        elif column == 'us_half_size':
            continue
        else:
            header = proper_string_from_snake_case(column)
        column_label = ctk.CTkLabel(main_frame, text = header)
        column_label.grid(row = main_gridder.row, column = main_gridder.column, padx = 10)
        main_gridder.next_column()

    main_gridder.next_row()



    app.mainloop()

if __name__ == '__main__':
    main()
