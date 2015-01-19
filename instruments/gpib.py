from core.util import Serial
from time import sleep

import struct

import binascii

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

TermChars = enum(CRLF = 0, CR = 1, LF = 2, NONE = 3)

class prologix(object):
    def __init__(self, port=None, log=False):
        self.bus = Serial()
        self.logfile = log
        if port is not None:
            self.bus.port = port
            self.bus.baudrate = 115200
            self.bus.rtscts=0
            self.bus.timeout = 3
            self.bus.open()
            self.init_gpib()

    def init_gpib(self):
        self.bus.flushInput()

        # flush whatever is hanging out in the buffer
        self.bus.readall()
        self.bus.start_logging()
        # if this doesn't work, try settin rtscts=0

        # don't save settings (to avoid wearing out EEPROM)
        self.savecfg = False

        self._addr = self.addr
        self._auto = self.auto


    @property
    def addr(self):
        """ which GPIB address is currently selected? """
        # query the controller for the current address
        # and save it in the _addr variable (why not)
        self._addr = int(self.ask("++addr"))
        return self._addr
    @addr.setter
    def addr(self, new_addr):
        # update local record
        self._addr = new_addr
        # change to the new address
        resp = self.ask("++addr %d" % new_addr)
        if resp == 'Unrecognized command':
            raise Exception("""
                Prologix controller does not support ++savecfg
                update firmware or risk wearing out EEPROM
                            """)
        # we update the local variable first because the 'write'
        # command may have a built-in lag. if we intterupt a program
        # during this period, the local attribute will be wrong

    @property
    def auto(self):
        self._auto = bool(int(self.ask("++auto")))
        return self._auto
    @auto.setter
    def auto(self, val):
        self._auto = bool(val)
        self.write("++auto %d" % self._auto)

    @property
    def eot(self):
        self._eot = bool(int(self.ask("++eot_enable")))
        return self._eot
    @eot.setter
    def eot(self, val):
        self._eot = bool(val)
        self.write("++eot_enable %d" % self._eot)

    @property
    def term_chars_for_xmit(self):
        self._term_chars_for_xmit = ResponseTypes.reverse_mapping[int(self.ask("++eos"))]
        return self._term_chars_for_xmit
        
    @term_chars_for_xmit.setter
    def term_chars_for_xmit(self, val):
        self._term_chars_for_xmit = val
        self.write("++eos %d" % self._term_chars_for_xmit)

    @property
    def read_timeout_ms(self):
        self._read_timeout_ms = bool(int(self.ask("++read_tmo_ms")))
        return self._read_timeout_ms

    @read_timeout_ms.setter
    def read_timeout_ms(self, val):
        self._read_timeout_ms = int(val)
        self.write("++read_tmo_ms %d" % self._read_timeout_ms)

    def version(self):
        """ Query the Prologix firmware version """
        return self.ask("++ver")

    def serial_poll(self):
        self.write("++spoll")        
        buffer = ''
        while True:
            buffer = buffer + self.read(1)
            if '\r\n' in buffer[-2:]:
                break
        return int(buffer)

    def wait_srq(self):
        self.write("++srq")
        srq = self.read(3)
        return bool(int(srq))

    @property
    def savecfg(self):
        """ should the controller save settings in EEPROM?  """
        resp = self.ask("++savecfg")
        if resp == 'Unrecognized command':
            raise Exception("""
                Prologix controller does not support ++savecfg
                update firmware or risk wearing out EEPROM
                            """)
        return bool(int(resp))
    @savecfg.setter
    def savecfg(self, val):
        d = bool(val)
        self.write("++savecfg %d" % d)

    def instrument(self, addr, **kwargs):
        return instrument(self, addr, **kwargs)

    def write(self, command, lag=0.1):
        self.bus.write("%s\r" % command)
        sleep(lag)

    def readall(self):
        resp = self.bus.readall()
        return resp.rstrip()

    def read(self, size):
        resp = self.bus.read(size)
        return resp

    def readline(self, size):
        resp = self.bus.readline(size)
        return resp

    def ask(self, query, *args, **kwargs):
        """ Write to the bus, then read response. """
        #self.bus.log_something('note', 'clearing buffer - expect no result')
        self.readall()  # clear the buffer
        self.write(query, *args, **kwargs)
        return self.readall()
