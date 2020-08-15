import datetime
from dateutil.parser import parse

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
        self.id = smartstrip(id) if id is not None else "{}|{}|{}".format(self.formatted_date(), account, amount).strip()
        self.outlay = smartstrip(outlay)
        self.cat = smartstrip(cat)

    def __repr__(self):
        # return "{},{},{},{},{},{},{}".format(self.id, self.account, self.date, self.payee, self.amount, self.memo, self.outlay)
        if self.outlay:
            return f'"{self.account}","{self.formatted_date()}","{self.id}","{self.payee}","{self.amount}","{self.cat if self.cat is not None else ""}"'
        else:
            return f'"{self.account}","{self.formatted_date()}","{self.id}","{self.payee}","{self.amount}","{self.cat if self.cat is not None else ""}"'

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