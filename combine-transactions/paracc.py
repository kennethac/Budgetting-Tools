import csv
import datetime
from dateutil.parser import parse
import operator
import os
from os import path
from typing import List, Dict
import xlrd


def smartstrip(s):
    if type(s) == str:
        return s.strip()
    else:
        return s

class TransactionInfo:
    def __init__(self, amount, account, date, payee, memo, id, outlay=True, cat=None):
        self.amount = amount
        self.account = smartstrip(account)
        self.date = smartstrip(date)
        self.payee = smartstrip(payee)
        self.memo = smartstrip(memo)
        self.id = smartstrip(id) if id is not None else "{}|{}|{}".format(date, account, amount).strip()
        self.outlay = smartstrip(outlay)
        self.cat = smartstrip(cat)

    def __repr__(self):
        # return "{},{},{},{},{},{},{}".format(self.id, self.account, self.date, self.payee, self.amount, self.memo, self.outlay)
        return f"{self.account}, {self.formatted_date()}, {self.id}, {self.payee}, {self.amount}, {self.cat if self.cat is not None else ''}"

    def __str__(self):
        return self.__repr__()

    def transfer_rep(self):
        return f"{self.account}, {self.formatted_date()}, {self.id}, {self.payee}, {self.amount}"

    def parsedDate(self) -> datetime:
        if type(self.date) == str:
            return parse(self.date)
        elif type(self.date) == datetime.datetime:
            return self.date
        else:
            raise Exception("Unknown date type")

    def formatted_date(self) -> str:
        return self.parsedDate().strftime("%m/%d/%Y")

filter_noop = lambda rows: rows

def zions_credit_filter(rows:List[List[object]]):
    return list(filter(lambda row: len(row) > 4 and row[0] is not None and row[0] != "", rows[1:]))

def zions_credit_select(row:List[object]):
    if float(row[4]) < 0: # is payment
        return TransactionInfo(-float(row[4]), "Zions Credit", row[0], row[3], None, row[2], outlay=False)
    else:
        return TransactionInfo(float(row[4]), "Zions Credit", row[0], row[3], None, row[2])

def zions_checking_select(row:List[object]):
    # print(row)
    if float(row[5]) < 0: # is outlay
        return TransactionInfo(-float(row[5]), "Zions Checking", row[1], row[4], None, row[2])
    else:
        return TransactionInfo(float(row[5]), "Zions Checking", row[1], row[4], None, row[2], outlay=False)

def usaa_credit_select(row:List[object]):
    amt = float(row[6])
    if amt < 0:
        return TransactionInfo(-amt, "USAA Credit", row[2], row[4], None, None)
    else:
        return TransactionInfo(amt, "USAA Credit", row[2], row[4], None, None, outlay=False)

def usaa_checking_select(row:List[object]):
    print(row)
    amt = float(row[6])
    if amt < 0:
        t = TransactionInfo(-amt, "USAA Checking", row[2], row[4], None, None)
    else:
        t = TransactionInfo(amt, "USAA Checking", row[2], row[4], None, None, outlay=False)
    print(t)
    return t

def budget_filter(rows:List[List[object]]):
    return list(rows)[1:]

def transaction_select(outlay:bool):
    def selector(row:List[object]):
        amt = float(row[4])
        return TransactionInfo(amt, row[0], row[1], row[3], '', row[2], cat=row[5], outlay=outlay)
    return selector

def transfer_select(row:List[object]):
    amt = float(row[4])
    t1 = TransactionInfo(amt, row[0], row[1], row[3], '', row[2], cat='transfer', outlay=True)
    amt2 = float(row[10])
    t2 = TransactionInfo(amt2, row[6], row[7], row[9], '', row[8], cat='transfer', outlay=False)
    return [t1, t2]

def read_csv(file_loc:str):
    # print("Reading {}".format(file_loc))
    with open(file_loc, "r") as f:
        reader = csv.reader(f, delimiter=',')
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
    elif dir_name == "Zions_Checking":
        r_filter = filter_noop
        r_select = zions_checking_select
    elif dir_name == "USAA_Credit":
        r_filter = filter_noop
        r_select = usaa_credit_select
    elif dir_name == "USAA_Checking":
        r_filter = filter_noop
        r_select = usaa_checking_select
    else:
        r_filter = lambda rows: []
        r_select = lambda row: row

    return [import_file(file_name, r_filter, r_select) for file_name in all_files]


def listify(item):
    if type(item) == list:
        return item
    else:
        return [item]

def import_file(file_name:str, r_filter, r_select, sheet_name=None) -> List[TransactionInfo]:
    print(f"{file_name}")
    file_res = read_spreadsheet(file_name, sheet_name=sheet_name) if "xls" in file_name else read_csv(file_name)
    results = [r_select(row) for row in r_filter(file_res)]
    return [ tran for res in results for tran in listify(res) ]

def import_all(dirs:List[str]):
    print(dirs)
    imported = [import_dir(d) for d in dirs]
    flattened = [entry for file in imported for entry in file]
    return flattened

def combine_all(transactions:List[List[TransactionInfo]]):
    combined:Dict[str, TransactionInfo] = {}

    for l in transactions:
        for tran in l:
            if tran.id not in combined or combined[tran.id].cat is None:
                combined[tran.id] = tran

    return list(combined.values())

def fuzzy_match(first:datetime.datetime, second:datetime.datetime):
    threshold = datetime.timedelta(days=3)
    return abs(first - second) < threshold

def separate(trans:List[TransactionInfo]):
    trans = sorted(trans, key=lambda t: t.parsedDate())
    outlays = []
    inlays = []
    for t in trans:
        if t.outlay:
            outlays.append(t)
        else:
            inlays.append(t)

    # Now to find transfers
    # They are sorted by date.
    transfers = []
    transfer_pairs = []

    for o in outlays:
        for i in inlays:
            if i not in transfers:
                if fuzzy_match(o.parsedDate(), i.parsedDate()) and o.amount == i.amount:
                    transfers.append(o)
                    transfers.append(i)
                    transfer_pairs.append((o, i))
    outlays = list(filter(lambda t: t not in transfers, outlays))
    inlays = list(filter(lambda t: t not in transfers, inlays))

    return outlays, inlays, transfer_pairs




if __name__ == "__main__":
    import sys
    g = import_all(list(filter(lambda d: not d.startswith(".") , os.listdir())))

    # Read in budget one.
    budget_file = "/Users/kenneth/Documents/OneDrive - BYU Office 365/Google Drive/Finances/Budget/2020/BudgetPlanningV1.xlsx"
    outlay_trans = import_file(budget_file, budget_filter, transaction_select(True), sheet_name="Outlays")
    inlay_trans = import_file(budget_file, budget_filter, transaction_select(False), sheet_name="Inlays")
    transfer_trans = import_file(budget_file, budget_filter, transfer_select, sheet_name="Transfers")
    g = [*g, outlay_trans, inlay_trans, transfer_trans]

    g = combine_all(g)

    new_years = parse("1/1/2020")
    g = list(filter(lambda t: t.parsedDate() >= new_years, g))
    outlays, inlays, transfer_pairs = separate(g)

    # o = "\n".join([str(l) for s in g for l in s])
    o = "\n".join([str(s) for s in g])
    with open("/tmp/g.csv", "w") as f:
        f.write(o)

    with open("/tmp/outlays.csv", "w") as f:
        o = "\n".join([str(s) for s in outlays])
        f.write(o)

    with open("/tmp/inlays.csv", "w") as f:
        o = "\n".join([str(s) for s in inlays])
        f.write(o)

    with open("/tmp/transfers.csv", "w") as f:
        o = "\n".join(
            [", ,".join(
                [a.transfer_rep(), b.transfer_rep() ]
                ) for a, b in transfer_pairs
            ])
        f.write(o)

