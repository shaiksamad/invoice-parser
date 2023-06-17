import math


class Round:
    """
    custom round function for accounting purposes

    rounds the number item to the nearest integer or decimal (if provided).
    if remainder is less than 0.5 then return floor.
    if remainder is greater than or equal to 0.5 then return ceil

    Parameters
    ----------
    n : int or float
        the number to round
    decimals: int, optional
        rounds upto the decimal (default is 0)

    no need to round
    >>> Round.round(10)
    10

    rounded to nearest int i.e 10
    >>> Round.round(10.49)
    10

    round after two decimals, so no change
    >>> Round.round(10.49, 2)
    10.49

    round after 1 decimal
    >>> Round.round(10.49, 1)
    10.5

    round to nearest int, i.e 11
    >>> Round.round(10.5)
    11

    round after 1 decimal, no change
    >>> Round.round(10.5, 1)
    10.5

    """

    def __init__(self, n: int | float, decimals: int = 0):
        self.n = self.round(n, decimals)

    def __repr__(self):
        return str(self.n)

    def __float__(self):
        return float(self.n)

    def __int__(self):
        return int(self.n)

    @staticmethod
    def round(n: int | float, decimal: int = 0) -> int | float:
        # TODO: add >= to 0.5
        sign = 1 if abs(n) == n else -1
        n = abs(n)
        if decimal:
            n = Round.round(n * (10 ** decimal)) / (10 ** decimal)
        elif n > 1 and n % int(n) >= 0.5:
            n = math.ceil(n)
        else:
            n = math.ceil(n) if 1 > n >= 0.5 else math.floor(n)
        return n * sign

    def get(self):
        return self.n


rnd = Round.round
