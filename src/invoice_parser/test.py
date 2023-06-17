"""Checking if all the items are pickable"""
import dill

from gst import GSTBase, GST, SGST, CGST
from invoices import Invoices, InvoiceParser, Table, Item, MergedItems
# from table import Table
from export import Export
from round import Round, rnd

import dill as pickle

to_pickle = [GSTBase, GST, SGST, CGST, Invoices, InvoiceParser, Table, Item, MergedItems, Export, Round, rnd]

def is_pickleable(cls):
    try:
        pickle.dumps(cls)
        return True
    except dill.PickleError:
        return False

    # for item in to_pickle:
    #     try:
    #         pd = pickle.dumps(item)
    #         pl = pickle.loads(pd)
    #         print(f"Succesfully pickled: {item}")
    #     except Exception as e:
    #         print(f"Unsuccessful {item}, err: {e}")

import multiprocessing as mp

if __name__ == '__main__':
    with mp.Pool(1) as pool:
        result = pool.map(is_pickleable, tuple(cls for cls in to_pickle))
        print(result)

