from __future__ import print_function
import Milter
from time import strftime
import email

class ReplaceReturnPathMilter(Milter.Base):
    def __init__(self):
        self.id = Milter.uniqueID()
        self.from_address = None
        self.message_from_address = None
        self.headers_to_remove = ["X-Sieve", "X-Sieve-Redirected-From", "X-Gmail-Forwarded", "X-Rspamd-Pre-Result", "X-Spamd-Result"]
        self.gmail_forwarded = False

    def log(self, *msg):
        print("%s [%d]" % (strftime('%Y%b%d %H:%M:%S'), self.id), end=" ", flush=True)
        print(*msg, flush=True)

    def connect(self, IPname, family, hostaddr):
        self.log("Connect from", IPname, hostaddr)
        return Milter.CONTINUE

    def envfrom(self, mailfrom, *str):
        self.log("MAIL FROM:", mailfrom)
        self.from_address = mailfrom
        return Milter.CONTINUE

    def header(self, name, value):
        if name.lower() == "from":
            self.message_from_address = value.strip()
        if name.lower() == "x-gmail-forwarded" and value.strip().lower() == "yes":
            self.log("X-Gmail-Forwarded header detected.")
            self.gmail_forwarded = True
        return Milter.CONTINUE

    def eom(self):
        if not self.gmail_forwarded:
            self.log("X-Gmail-Forwarded header not YES. Continuing.")
            return Milter.ACCEPT

        if self.message_from_address:
            self.log("Setting MAIL FROM to From address:", self.message_from_address)
            self.changefrom(self.message_from_address, "")  # Update the envelope sender to the From address

        self.log("Removing headers:", ", ".join(self.headers_to_remove))
        for header in self.headers_to_remove:
            self.chgheader(header, 0, None)  # Remove the header

        return Milter.ACCEPT

    def abort(self):
        self.log("Abort called.")
        return Milter.CONTINUE

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 12345
    socketname = f"inet:{port}@{host}"
    Milter.factory = ReplaceReturnPathMilter
    Milter.set_flags(Milter.ADDHDRS + Milter.CHGHDRS)
    print("Starting ReplaceReturnPathMilter on", host, "port", port, flush=True)
    Milter.runmilter("ReplaceReturnPathMilter", socketname, 600)
    print("ReplaceReturnPathMilter shutdown", flush=True)
