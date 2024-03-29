import datetime
import re
from io import BytesIO
from os import path
from pathlib import Path

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from errors import *
from gst import GSTBase, GST
from items import MergedItems, Item
from table import Table
from typing import Callable


class Invoices:
    """
    converts invoices in pdf into each Invoice object, for accessing parts of invoices

    reads the pdf

    Parameters
    ----------
    pdf : str
        the path of pdf (containing invoices)

    password: str | bytes, optional
        password for pdf, if any (default is None)


    Raises
    ------
        NotAVyaparPDF:
            if the given pdf is not generated by Vyapar app

        FileNotFoundError:
            if the given path is incorrect


    Returns
    -------
    returns iterators of invoices

    """

    def __init__(self, pdf: str | Path | BytesIO, password: None | str | bytes = None, parallel=False):

        if type(pdf) in (str, Path):
            if path.isfile(pdf):
                self.filename = path.basename(pdf)
            else:
                raise FileNotFoundError(f"Invalid file path, '{path.abspath(pdf)}' is not a valid path")

        try:
            pdf = PdfReader(pdf, strict=True, password=password)

            if "Vyaparapp" not in pdf.metadata.creator:
                raise NotAVyaparPDF(f'"{self.filename}"')

        except PdfReadError as e:
            raise VyaparPDFReadError(
                f"File ({self.filename}) is {'a corrupt pdf.' if self.filename.endswith('.pdf') else 'not a pdf.'}\n{e}"
            ) from None

        else:
            self.invoices = []
            for page in pdf.pages:
                page = page.extract_text()
                try:
                    self.invoices.append(InvoiceParser(page))
                except:
                    pass
            # self._header = ['BILL NO', 'DATE', 'ITEM', 'TAXABLE\nAMOUNT', 'SGST', 'CGST', 'ROUND\nOFF', 'TOTAL']
            self.table = self.make_table()

    def make_table(self, header: list = None, footer: list = None, force_invoice_data: bool = False) -> Table:
        """
        creates a 2d list of items in invoices

        same type of items are merged in each invoice
        so max of two rows per invoice either gold or silver

        Parameters
        ----------
        header: list, optional
            header values of invoice items

        footer: list, optional
            footer values of invoice table

        force_invoice_data: bool
            overwrite calculated data with invoice data (default is False)

        Returns
        -------
        Table:
            a table object, where you can
            sort and filter rows

        """

        header = header

        rows = list()

        for invoice in self.invoices:
            single_item_not_valid = len(invoice.items_raw) == 1 and (not invoice.isvalid) and force_invoice_data
            for item in invoice.items:
                row = [
                    item.invoice_no,
                    item.type,
                    invoice.date,
                    item.quantity,
                    item.sub_total,
                    item.gst.sgst.amount if not single_item_not_valid else invoice.gst.sgst.amount,
                    item.gst.cgst.amount if not single_item_not_valid else invoice.gst.cgst.amount,
                    item.round_off if not single_item_not_valid else invoice.round_off,
                    item.total if not single_item_not_valid else invoice.total,
                    None, # Extra rows
                    invoice.round_off,  # remove this two rows
                    item.round_off,
                    invoice.isvalid,
                ]

                rows.append(row)

        return Table(rows=rows, header=header, footer=footer)

    def __iter__(self):
        for invoice in self.invoices:
            yield invoice


class InvoiceParser:
    """
    parses the invoice data into specific objects

    converts all the required data to objects and creates Item objects
    each invoice can have one or more Item objects
    all the same item type objects are merged
        i.e. all silver items merged into one item and same for gold
    these items are stored in items
    you can iterate InvoiceParser for items

    Parameters
    ----------
    invoice: str
        extracted text of pdf invoice

    """

    def __init__(self, invoice: str | Callable) -> None:
        if callable(invoice):
            invoice = invoice.__call__()

        print(invoice.split('\n')[13])

        RS = '₹'
        RI = '₨'
        RE_AMOUNT = r'\d*,?\d*,?\d*,?\d+\.?\d*'
        # RE_ITEM = rf"(?P<n>\d)\s*(?P<item>gold|silver)(?P<desc>\s[\w.\d\s&]*\s)(?P<hsn>7113)\s*(\?P<quantity>\d+\.?\d*)\s?(?P<unit>gm|Gm)\s?[{RS}.]*\s(?P<unitprice>\d*,?\d*,?\d*,?\d+\.?\d*)\s?[{RS}.]*\s?(\?P<amount>{RE_AMOUNT}) "
        # item without discount
        # RE_ITEM = rf"(?P<n>\d)\s*(?P<item>gold|silver)(?P<desc>\s[\w.\d\s&]*\s)\s*(?P<quantity>\d+\.?\d*)\s?(?P<unit>gm|Gm)\s?[{RS+RI}.]*\s(?P<unitprice>{RE_AMOUNT})\s?[{RS+RI}.]*\s?(?P<amount>{RE_AMOUNT})"
        # Item with discount
        RE_ITEM = rf"(?P<n>\d)\s*(?P<item>gold|silver)(?P<desc>\s[\w.\d\s&]*\s)\s*(?P<quantity>\d+\.?\d*)\s?(?P<unit>gm|Gm)\s?[{RS+RI}.]*\s(?P<unitprice>{RE_AMOUNT})\s?[{RS+RI}.]*\s((?P<discount>{RE_AMOUNT})\s?\(\d%\))*[{RS+RI}\s.]*(?P<amount>{RE_AMOUNT})+"
        # RE_ITEM_RI = rf"(?P<n>\d)\s*(?P<item>gold|silver)(?P<desc>\s[\w.\d\s&]*\s)\s*(?P<quantity>\d+\.?\d*)\s?(?P<unit>gm|Gm)\s?[{RI}.]*\s(?P<unitprice>\d*,?\d*,?\d*,?\d+\.?\d*)\s?[{RI}.]*\s?(?P<amount>{RE_AMOUNT})"
        RE_GST = rf"(?:(?P<type>SGST|CGST)@(?P<rate>\d+.?\d*%?)\W*(?P<amount>{RE_AMOUNT}))"
        RE_ROUND = rf"Round\s*off\s*(?P<minus>-?)\s*\W*(?P<roundoff>{RE_AMOUNT})"
        RE_SUBTOTAL = rf"(?:Sub Total)\W*(?P<subtotal>{RE_AMOUNT})"
        RE_TOTAL = rf"(?:(?<!Sub\s)Total(?=\s*{RS}|{RI}))\W*(?P<total>{RE_AMOUNT})"
        # RE_TOTAL_RI = rf"(?:(?<!Sub\s)Total(?=\s*{RI}))\W*(?P<total>{RE_AMOUNT})"
        RE_DATE = r"(?:(?:Date\s*:\s*)(?P<date>\d{2}-\d{2}-\d{4}))"
        RE_INVOICE = r"(?:(?:Invoice No.\s*:\s*)(?P<no>\d+))"

        self.invoice_no = int(re.findall(RE_INVOICE, invoice)[0])
        self.date = datetime.datetime.strptime(re.findall(RE_DATE, invoice)[0], '%d-%m-%Y')
        self.sub_total = float(re.findall(RE_SUBTOTAL, invoice)[0].replace(',', ''))
        self.gst: GST | GSTBase = sum([
            GSTBase(type=gst.groupdict()['type'], rate=float(gst.groupdict()['rate'].replace('%', '')), amount=float(gst.groupdict()['amount'].replace(',', ''))) for gst in re.finditer(RE_GST, invoice)
        ])
        try:
            self.round_off = float("".join(re.findall(RE_ROUND, invoice)[0]))
        except IndexError:
            self.round_off = 0.0

        try:
            self.total = float(re.findall(RE_TOTAL, invoice)[0].replace(',', ''))
        except IndexError:
            # self.total = float(re.findall(RE_TOTAL_RI, invoice)[0].replace(',', ''))
            pass

        try:
            self.items_raw = items_raw = [item.groupdict() for item in re.finditer(RE_ITEM, invoice)]
        except IndexError:
            # self.items_raw = items_raw = [item.groupdict() for item in re.finditer(RE_ITEM_RI, invoice)]
            pass

        self.items = MergedItems(
            [Item(self.invoice_no,
                  i['item'],
                  float(i['quantity'].replace(',', '')),
                  float(i['amount'].replace(',', '')),
                  self.gst.rate)

             for i in items_raw]
        )


    @property
    def isvalid(self) -> bool:
        return self.sub_total == self.items.sub_total and self.gst == self.items.gst

    def print_validate(self) -> None:
        print(self.invoice_no, self.invoice_no == self.items.invoice_no)
        print(self.sub_total, self.sub_total == self.items.sub_total)
        print(self.gst, self.gst == self.items.gst)
        print(self.round_off, self.round_off == self.items.round_off)
        print(self.total, self.total == self.items.total)
        print(f'------------------{self.isvalid}------------------------')

    def print(self):
        for item in self.items:
            print(item.invoice_no, item.type, item.quantity, "Gm", item.sub_total, *[gst for gst in item.gst], item.round_off, item.total, sep='\t')
