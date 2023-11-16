import datetime
from operator import itemgetter


class Table:
    """
    Table is a 2d list with extra function for Excel

    sort and filter table rows, check if table is empty
    change header and footer

    Parameters
    ----------
    rows: list[list], optional
        2d list of items (default is None)

    header: list, optional
        header of the table (default header)

    footer: list, optional
        footer of the table (default adds =SUM() formula for excel)

    row_start: int, optional
        starting cell number of row, (default is None)


    """
    def __init__(self, rows: list[list] = None, header: list = None, footer: list = None, row_start: int = None, row_end: int = None, num_cols: int = 9):
        # setting footer default values
        self.num_cols = num_cols
        self.header = header
        self.rows = rows
        self.row_start = row_start
        self.row_end = row_end
        self.footer = footer

    @property
    def is_empty(self):
        return len(self.rows) == 0

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, head: list):
        self._header = head if head and len(head) == self.num_cols else [
            'BILL NO', 'ITEM', 'DATE', 'QUANTITY', 'TAXABLE\nAMOUNT', 'SGST', 'CGST', 'ROUND\nOFF', 'TOTAL', None, None, None, "VALID"
        ]

    @property
    def footer(self):
        return self._footer

    @footer.setter
    def footer(self, foot: list):
        self._footer = foot or [None, None, None, None,
                                f'=SUM(E{self.row_start}:E{self.row_end or 1})',
                                f'=SUM(F{self.row_start}:F{self.row_end or 1})',
                                f'=SUM(G{self.row_start}:G{self.row_end or 1})',
                                f'=SUM(H{self.row_start}:H{self.row_end or 1})',
                                f'=SUM(I{self.row_start}:I{self.row_end or 1})']

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, rows: list[list] = None):
        self._rows = rows or list()

    @property
    def row_start(self):
        return self._row_start

    @row_start.setter
    def row_start(self, row=1):
        self._row_start = row or 1
        if hasattr(self, '_row_end'):
            self.footer = None  # resetting footer

    @property
    def row_end(self):
        return self._row_end

    @row_end.setter
    def row_end(self, end):
        self._row_end = end or self.row_start + len(self.rows) - 1
        self.footer = None  # resetting footer

    @property
    def table(self) -> list[list]:
        return [self.header, *self.rows]

    def add_row(self, row: list) -> None:
        """Append a list/row to the table"""
        self._rows.append(row) if len(row) == len(self._header) else None

    def _find_index(self, field: str) -> int:
        try:
            return self.header.index(field)
        except ValueError:
            match field:
                case "BILL NO":
                    return 0
                case "DATE":
                    return 1
                case "ITEM":
                    return 2
                case _:
                    return 0

    def _sort(self, field_index: int, reverse=False) -> None:
        self.rows.sort(key=itemgetter(field_index), reverse=reverse)

    def sort_by_item(self, reverse: bool = False) -> None:
        self._sort(self._find_index("ITEM"), reverse=reverse)

    def sort_by_date(self, reverse=False) -> None:
        self._sort(self._find_index('DATE'), reverse=reverse)

    def sort_by_invoice(self, reverse=False) -> None:
        self._sort(self._find_index("BILL NO"), reverse=reverse)

    def _filter(self, field, value, key=None) -> filter:
        return filter(key or (lambda x: x[self._find_index(field)] == value), self.rows)

    def filter_by_item(self, item: str) -> filter:
        return self._filter("ITEM", item)

    def filter_by_date(self, from_date: datetime.datetime, to_date: datetime.datetime = None) -> filter | list[list]:
        if to_date and to_date < from_date:
            return self.rows

        if to_date:
            return self._filter("DATE", None, lambda row: from_date <= row[self._find_index("DATE")] <= to_date)
        return self._filter("DATE", None, lambda row: from_date <= row[self._find_index("DATE")])

    def __iter__(self):
        for row in (self.header, *self.rows):
            yield row

    def __repr__(self):
        r = f"{self.header}"
        for row in self.rows:
            r += '\n' + str(row)
        return r
