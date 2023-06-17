from invoices import Invoices
from export import Export
from time import time


if __name__ == '__main__':
    start = time()

    invoices = Invoices("C:\\Users\\samad\\Downloads\\vyapar_print16_06_2023_15_15_31.pdf", parallel=0)
    invoice_time = time()
    table = invoices.make_table(force_invoice_data=False)
    table_time = time()
    export = Export(table)
    export_time = time()
    # print(export, export.__dict__)
    export.save(invoices.filename.replace('.pdf', '') + "" + '.xlsx')
    save_time = time()

    print(
        "Time taken to:\n"
        f"load invoice: {invoice_time-start}\n"
        f"make table: {table_time - invoice_time}\n"
        f"load Export: {export_time - table_time}\n"
        f"save: {save_time - export_time}\n"
        f"total time taken: {save_time - start}\n"
    )
    input()