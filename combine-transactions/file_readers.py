import xlrd
import csv
from typing import List, Dict
from transaction_info import TransactionInfo
import os
from os import path

from format_parsers import *

def listify(item):
    if type(item) == list:
        return item
    else:
        return [item]

def read_csv(file_loc:str):
    with open(file_loc, "r") as f:
        reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        # print(file_loc)
        # for l in reader:
            # print(l)
        return [*reader]

def parse_cell_value(cell:xlrd.sheet.Cell):
    if cell.ctype == xlrd.XL_CELL_DATE:
        return xlrd.xldate_as_datetime(cell.value, 0)
    else:
        return cell.value

def read_spreadsheet(file_loc:str, sheet_name:str=None):
    wb = xlrd.open_workbook(file_loc)
    sheet = wb.sheet_by_index(0) if not sheet_name else wb.sheet_by_name(sheet_name)
    return [[parse_cell_value(c) for c in r] for r in sheet.get_rows()]
    # return [TransactionInfo(acc, date, id, payee, amount, cat) for acc, date, id, payee, amount, cat in sheet.get_rows()]


def import_dir(dir_name:str) -> List[TransactionInfo]:
    files = os.listdir(dir_name)
    all_files = [path.join(dir_name, file) for file in list(filter(lambda x: not x.startswith("."), files))]

    if dir_name == "Zions_Credit":
        r_filter = zions_credit_filter
        r_select = zions_credit_select
    elif dir_name == "Zions_Credit_New":
        r_filter = zions_credit_new_filter
        r_select = zions_credit_new_select
    elif dir_name == "Zions_Checking":
        r_filter = filter_noop
        r_select = zions_checking_select
    elif dir_name == "USAA_Credit":
        r_filter = filter_noop
        r_select = usaa_credit_select
    elif dir_name == "USAA_Checking":
        r_filter = filter_noop
        r_select = usaa_checking_select
    elif dir_name == "USAA_Checking_New":
        r_filter = filter_header
        r_select = usaa_checking_select_new
    else:
        r_filter = lambda rows: []
        r_select = lambda row: row

    return [import_file(file_name, r_filter, r_select) for file_name in all_files]

def import_file(file_name:str, r_filter, r_select, sheet_name=None) -> List[TransactionInfo]:
    print(file_name)
    file_res = read_spreadsheet(file_name, sheet_name=sheet_name) if "xls" in file_name else read_csv(file_name)
    results = [r_select(row) for row in r_filter(file_res)]
    return [ tran for res in results for tran in listify(res) ]

def import_all(dirs:List[str]):
    imported = [import_dir(d) for d in dirs]
    flattened = [entry for file in imported for entry in file]
    return flattened