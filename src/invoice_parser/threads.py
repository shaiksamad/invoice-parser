from threading import Thread


class InvoiceThread(Thread):
    def __init__(self, target, args=(), kwargs=None, daemon=True):
        super().__init__()
        self.daemon = daemon
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.result = None

    def run(self):
        self.result = self.target(*self.args, **self.kwargs)
