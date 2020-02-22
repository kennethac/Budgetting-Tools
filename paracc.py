import csv
import os
from os import path
from typing import List, Dict

class TransactionInfo:
    def __init__(self, amount, account, date, payee, memo, id, outlay=True, cat=None):
        self.amount = amount
        self.account = account
        self.date = date
        self.payee = payee
        self.memo = memo
        self.id = id if id is not None else "{}|{}|{}".format(date, account, amount)
        self.outlay = outlay
        self.cat = cat

    def __repr__(self):
        # return "{},{},{},{},{},{},{}".format(self.id, self.account, self.date, self.payee, self.amount, self.memo, self.outlay)
        return f"{self.account}, {self.date}, {self.id}, {self.payee}, {self.amount}, {self.cat if self.cat is not None else ''}"

    def __str__(self):
        return self.__repr__()

filter_noop = lambda rows: rows

def zions_credit_filter(rows:List[List[object]]):
    return list(filter(lambda row: len(row) > 4 and row[0] is not None and row[0] != "", rows[1:]))

def zions_credit_select(row:List[object]):
    if float(row[4]) < 0: # is payment
        return TransactionInfo(-float(row[4]), "Zions Credit", row[0], row[3], None, row[2], outlay=False)
    else:
        return TransactionInfo(float(row[4]), "Zions Credit", row[0], row[3], None, row[2])

def usaa_credit_select(row:List[object]):
    amt = float(row[6])
    if amt < 0:
        return TransactionInfo(-amt, "USAA Credit", row[2], row[4], None, None)
    else:
        return TransactionInfo(amt, "USAA Credit", row[2], row[4], None, None, outlay=False)

def usaa_checking_select(row:List[object]):
    amt = float(row[6])
    if amt < 0:
        return TransactionInfo(-amt, "USAA Checking", row[2], row[4], None, None)
    else:
        return TransactionInfo(amt, "USAA Checking", row[2], row[4], None, None, outlay=False)

def read_csv(file_loc:str):
    # print("Reading {}".format(file_loc))
    with open(file_loc, "r") as f:
        reader = csv.reader(f, delimiter=',')
        return [*reader]

def read_spreadsheet(file_loc:str):
    pass

def import_dir(dir_name:str) -> List[TransactionInfo]:
    files = os.listdir(dir_name)
    all_files = [read_spreadsheet(file) if "xls" in file else read_csv(file) for file in [path.join(dir_name, file) for file in list(filter(lambda x: not x.startswith("."), files))]]

    if dir_name == "Zions_Credit":
        r_filter = zions_credit_filter
        r_select = zions_credit_select
    # elif dir_name == "Zions_Checking":
    #     r_filter = zions_checking_filter
    #     r_select = zions_checking_select
    elif dir_name == "USAA_Credit":
        r_filter = filter_noop
        r_select = usaa_credit_select
    elif dir_name == "USAA_Checking":
        r_filter = filter_noop
        r_select = usaa_checking_select
    else:
        r_filter = lambda rows: []
        r_select = lambda row: row

    return [r_select(filtered) for file_res in all_files for filtered in r_filter(file_res)]

def import_all(dirs:List[str]):
    print(dirs)
    imported = [import_dir(d) for d in dirs]
    return imported

def combine_all(transactions:List[List[TransactionInfo]]):
    combined:Dict[str, TransactionInfo] = {}

    for l in transactions:
        for tran in l:
            if tran.id not in combined or combined[tran.id].cat is None:
                combined[tran.id] = tran

    return list(combined.values())

if __name__ == "__main__":
    import sys
    g = import_all(list(filter(lambda d: not d.startswith(".") , os.listdir())))
    g = combine_all(g)
    # o = "\n".join([str(l) for s in g for l in s])
    print(g)
    o = "\n".join([str(s) for s in g])
    with open("/tmp/o.csv", "w") as f:
        f.write(o)