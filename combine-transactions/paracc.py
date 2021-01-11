import datetime
from dateutil.parser import parse
import operator
import os
from os import path
from typing import List, Dict

from transaction_info import TransactionInfo
from file_readers import *

def combine_all(transactions:List[List[TransactionInfo]]):
    combined:Dict[str, TransactionInfo] = {}

    for l in transactions:
        for tran in l:
            if tran.id not in combined or combined[tran.id].cat is None:
                combined[tran.id] = tran

    return list(combined.values())

def fuzzy_match(first:datetime.datetime, second:datetime.datetime):
    threshold = datetime.timedelta(days=4)
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
    budget_file = "/Users/kenneth/Documents/OneDrive/Documents/Finances/Budget/2021/BudgetPlanningV0.xlsx"
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

