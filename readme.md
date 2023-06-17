# Invoice parser
### parses vyapar invoice and converts into Excel format in a preferred format 

---

#### Quick Start Template

```
from invoice_parser import Invoices, Export

invoices = Invoices(vyapar_invoice.pdf)
export = Export(invoices.table)
export.save(invoice.filename.replace(".pdf", ".xlsx"))

```

---
