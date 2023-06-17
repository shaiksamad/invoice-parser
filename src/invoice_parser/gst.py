from errors import *


class GSTBase(object):
    """
    Auto calculates gst with arguments rate and sub_total

    auto calculates gst returns the CGST/SGST class according to the type
    on change of sub_total auto calculates amount

    either amount should be provided or sub_total. otherwise,
    gst will amount will be 0 and sub_total will be 0

    you have to change sub_total to change amount
    only sub_total is allowed to change once assigned


    Parameters
    ----------
    type: str
        type of gst CGST/SGST

    rate: float
        percentage of gst

    sub_total: float, optional
        subtotal on which gst is calculated (default is None)

    amount: float, optional
        amount of gst (default is 0)


    Raises
    ------
    RateChangeError:
        when try to change rate once assigned.
        rate cannot be changed once assigned

    GstAmountChangeError:
        when try to change amount.
        amount is calculated if not provided, and then cannot be changed

    """

    def __new__(cls, type: str, rate: float, sub_total: float = None, amount: float = 0):
        if cls is GSTBase:
            return CGST(rate, sub_total, amount) if type.lower()[0] == 'c' else SGST(rate, sub_total, amount)
        else:
            return super().__new__(cls)

    def __init__(self, type: str, rate: float, sub_total: float = None, amount: float = 0):
        if type.lower()[0] not in ('c', 's'):
            raise InvalidGstType(f"not '{type}'")
        elif len(type) == 1:
            type = (type + 'gst').upper()

        self.type = type
        self.rate = float(rate.replace('%', '')) if isinstance(rate, str) else rate
        self.amount = float(amount.replace(',', '')) if isinstance(amount, str) else amount
        self.sub_total = float(sub_total.replace(',', '')) if isinstance(sub_total, str) else sub_total

    def __setattr__(self, key, value):
        if key == 'rate' and key in self.__dict__:
            raise RateChangeError
        if key == 'amount' and value:
            if key in self.__dict__:
                raise GstAmountChangeError
            else:
                self.__dict__['sub_total'] = round(value * 100 / 1.5, 2)
        if key == 'sub_total':
            if value:
                self.__dict__['amount'] = round(value * self.rate / 100, 2)
            elif self.sub_total:
                return

        self.__dict__[key] = value

    def __eq__(self, other):
        return self.rate == other.rate and self.amount == other.amount \
            if isinstance(other, GSTBase) else False

    def __add__(self, other):
        if not isinstance(other, GSTBase):
            return self
        if self.rate == other.rate and self.type != other.type and self.amount == other.amount:
            return GST(cgst=self, sgst=other) if self.type[0].lower() == 'c' else GST(cgst=other, sgst=self)

    def __radd__(self, other):
        if not isinstance(other, GSTBase):
            return self
        return other.__add__(self)

    def __repr__(self):
        return f"{self.type} {self.rate} {self.amount}"


class CGST(GSTBase):
    """
    CGST object of GSTBase


    read GSTBase.__doc__ for more info
    """

    def __init__(self, rate: float, sub_total: float = None, amount: float = 0, **kwargs):
        if not self.__dict__:
            super().__init__(type='c', rate=rate, sub_total=sub_total, amount=amount)


class SGST(GSTBase):
    """SGST object of GSTBase

    read GSTBase.__doc__ for more info
    """

    def __init__(self, rate: float, sub_total: float = None, amount: float = 0, **kwargs):
        if not self.__dict__:
            super().__init__(type='s', rate=rate, sub_total=sub_total, amount=amount)


class GST:
    """
    GST is combination of CGST and SGST

    adding CGST and SGST returns GST
    it inherits the rate and adds the amount and sub_total

    Parameters
    ----------
    rate: float
        percentage of gst

    sub_total: float
        sub_total or cost of the item
        auto calculates amount

    amount: float, optional
        gst amount of the item

    """

    def __init__(self, rate: float = None, sub_total: float = None, amount: float = 0, cgst: CGST | GSTBase = None, sgst: SGST | GSTBase = None):
        if rate and (sub_total or amount):
            cgst = CGST(rate, sub_total, amount)
            sgst = SGST(rate, sub_total, amount)
        if not (cgst and sgst):
            raise GSTInsufficientArgs
        if cgst.rate != sgst.rate:
            raise IncorrectGSTRates(f"{cgst.rate} != {sgst.rate}")
        self.rate = cgst.rate
        self.type = "GST"
        self.amount = cgst.amount + sgst.amount
        self.sub_total = cgst.sub_total

        self.cgst = cgst
        self.sgst = sgst

        self.total = self.sub_total + self.amount

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise GSTChangeError
        self.__dict__[key] = value

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return other + self.amount
        elif isinstance(other, GST):
            if self.rate == other.rate:
                return GST(self.rate, self.sub_total + other.sub_total)

    def __radd__(self, other):
        if isinstance(other, (GST, int, float)):
            return self.__add__(other)
        return self

    def __repr__(self):
        return f"GST -> {self.cgst.rate + self.sgst.rate}% {self.amount}"

    def __eq__(self, other):
        return self.rate == other.rate and self.amount == other.amount if isinstance(other, GST) else False

    def __iter__(self):
        for gst in (self.sgst, self.cgst):
            yield gst
