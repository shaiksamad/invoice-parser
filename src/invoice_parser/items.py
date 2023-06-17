from round import rnd
from gst import GST


class Item:
    """
    A single item of invoice

    Parameters
    ----------
    invoice_no : int
        invoice number of the item

    type : str
        type of item either gold or silver

    quantity: float
        quantity of the item

    sub_total: float
        subtotal of the item, or rate * quantity of the item

    gst_rate: float, optional
        gst percentage applied to the item (default is 1.5)
    """

    def __init__(self,
                 invoice_no: int,
                 type: str,
                 quantity: float,
                 sub_total: float,
                 gst_rate: float = 1.5):

        self.invoice_no = invoice_no
        self.type = type
        self.quantity = rnd(quantity, 3)
        self.sub_total = rnd(sub_total, 2)
        self.gst_rate = gst_rate

        # calculated values
        self.gst = GST(gst_rate, sub_total)
        self.total = float(rnd(self.gst.total))
        self.round_off = rnd(self.total - self.gst.total, 2)

    def __str__(self):
        return self.type

    def __add__(self, other):
        if isinstance(other, Item) and self.invoice_no == other.invoice_no and self.gst_rate == other.gst_rate:
            if other.type == self.type:
                return Item(self.invoice_no, self.type, self.quantity + other.quantity,
                            self.sub_total + other.sub_total, self.gst_rate)
            return MergedItems([self, other])  # if Item but not same item, one is gold and other is silver
        return self  # if not Item then return self

    def __radd__(self, other):
        if not isinstance(other, Item):
            return self  # return self if other is not Item

    def __repr__(self):
        return f"Item({self.type}: {self.quantity} gm - {self.sub_total})"


class MergedItems:
    """
    Combination of Gold and Silver of same invoice

    Parameters
    ----------
    items: list[Item]
        list of Item objects contain
    """

    def __init__(self, items: list[Item]):
        if not items:
            self.items = []
            return
        self.non_merged_items = items

        self.silver = None
        self.gold = None

        # extracts gold and silver from items list
        for item in items:
            if item.type == 'gold':
                self.gold += item
            else:
                self.silver += item

        # for type hinting purpose
        self.silver: Item
        self.gold: Item

        gold, silver = self.gold, self.silver  # for ease of use
        both = gold and silver

        # filling data
        self.invoice_no = (gold or silver).invoice_no
        self.sub_total = silver.sub_total + gold.sub_total if both else (gold or silver).sub_total
        self.gst = gold.gst + silver.gst if both else (gold or silver).gst
        self.round_off = rnd(silver.round_off + gold.round_off, 2) if both else (gold or silver).round_off
        self.total = silver.total + gold.total if both else (gold or silver).total

        self.items: tuple[Item] = tuple(
            item for item in (self.silver, self.gold) if item)  # adding only non-None type item

    def __add__(self, other):
        if isinstance(other, Item) and self.invoice_no == other.invoice_no:
            return MergedItems([
                self.gold + other if other.type == 'gold' else self.gold,
                self.silver + other if other.type == 'silver' else self.silver
            ])
        elif isinstance(other, MergedItems) and self.invoice_no == other.invoice_no:
            return MergedItems([
                self.gold + other.gold,
                self.silver + other.silver
            ])

    def __repr__(self):
        return "MergedItems" + repr(self.items)

    def __iter__(self):
        for item in self.items:
            yield item
