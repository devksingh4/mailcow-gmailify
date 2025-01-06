from __future__ import print_function
import Milter
from time import strftime

class ReplaceReturnPathMilter(Milter.Base):
    def __init__(self):
        self.id = Milter.uniqueID()
        self.from_address = None
        self.message_from_address = None
        self.x_mail_from_address = None
        self.headers_to_remove = ["X-Sieve", "X-Sieve-Redirected-From", "X-Gmail-Forwarded", "X-Rspamd-Pre-Result", "X-Spamd-Result"]
        self.gmail_forwarded = False
        self.client_ip = None

    def log(self, *msg):
        print("%s [%d]" % (strftime("%b %e %H:%M:%S"), self.id), end=" ", flush=True)
        print(*msg, flush=True)

    def connect(self, IPname, family, hostaddr):
        self.log("Connect from", IPname, hostaddr)
        self.client_ip = hostaddr
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
        if name.lower() == "x-box-realfrom":
            self.x_mail_from_address = value.strip()
        return Milter.CONTINUE

    def eom(self):
        if self.gmail_forwarded:
            if self.x_mail_from_address:
                self.log("X-Gmail-Forwarded - replacing Envelope From with X-Box-RealFrom:", self.x_mail_from_address)
                self.chgfrom(self.x_mail_from_address, "")
                self.chgheader("X-Box-RealFrom", 0, None)
        else:
            if self.from_address and self.client_ip[0] == "172.22.1.1": # only store when coming from the incoming gateway
                self.log("No X-Gmail-Forwarded header. Adding X-Box-RealFrom header with MAIL FROM:", self.from_address)
                self.addheader("X-Box-RealFrom", self.from_address)  # Add the X-Box-RealFrom header with the MAIL FROM address

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
