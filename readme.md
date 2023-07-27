# Invoice parser
### parses vyapar invoice and converts into Excel format in a preferred format 

---

#### Installation

```
pip install git+https://github.com/shaiksamad/invoice-parser#egg=invoice-parser-shaiksamad
```

---

#### Quick Start Template

```
from invoice_parser import Invoices, Export

invoices = Invoices("vyapar_invoice.pdf")
export = Export(invoices.table)
export.save("vyapar_invoice.xlsx")

```

---
