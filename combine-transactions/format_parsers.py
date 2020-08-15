from typing import List, Dict
from transaction_info import TransactionInfo

filter_noop = lambda rows: rows

filter_header = lambda rows: rows[1:]

def zions_credit_new_filter(rows:List[List[object]]):
    return list(filter(lambda row: len(row) == 4 and row[0] is not None and row[0] != "", rows[1:]))

def zions_credit_new_select(row:List[object]):
    if float(row[3]) < 0: # is payment
        return TransactionInfo(-float(row[3]), "Zions Credit", row[0], row[2], None, None, outlay=False)
    else:
        return TransactionInfo(float(row[3]), "Zions Credit", row[0], row[2], None, None)

def zions_credit_filter(rows:List[List[object]]):
    return list(filter(lambda row: len(row) > 4 and row[0] is not None and row[0] != "", rows[1:]))

def zions_credit_select(row:List[object]):
    if float(row[4]) < 0: # is payment
        return TransactionInfo(-float(row[4]), "Zions Credit", row[0], row[3], None, row[2], outlay=False)
    else:
        return TransactionInfo(float(row[4]), "Zions Credit", row[0], row[3], None, row[2])

def zions_checking_select(row:List[object]):
    if float(row[5]) < 0: # is outlay
        return TransactionInfo(-float(row[5]), "Zions Checking", row[1], row[4], None, None)
    else:
        return TransactionInfo(float(row[5]), "Zions Checking", row[1], row[4], None, None, outlay=False)

def usaa_credit_select(row:List[object]):
    amt = float(row[6])
    if amt < 0:
        return TransactionInfo(-amt, "USAA Credit", row[2], row[4], None, None)
    else:
        return TransactionInfo(amt, "USAA Credit", row[2], row[4], None, None, outlay=False)

def usaa_checking_select(row:List[object]):
    amt = float(row[6])
    if amt < 0:
        t = TransactionInfo(-amt, "USAA Checking", row[2], row[4], None, None)
    else:
        t = TransactionInfo(amt, "USAA Checking", row[2], row[4], None, None, outlay=False)
    return t

def usaa_checking_select_new(row:List[object]):
    amt = float(row[4])
    if amt < 0:
        t = TransactionInfo(-amt, "USAA Checking", row[0], row[2], None, None)
    else:
        t = TransactionInfo(amt, "USAA Checking", row[0], row[2], None, None, outlay=False)
    return t

def budget_filter(rows:List[List[object]]):
    return list(filter(lambda r: len(r[0]) != 0, list(rows)[1:]))

def transaction_select(outlay:bool):
    if outlay:  
        def selector(row:List[object]):
            amt = float(row[4])
            return TransactionInfo(amt, row[0], row[1], row[3], '', row[2], cat=row[5], outlay=outlay)
        return selector
    else:
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