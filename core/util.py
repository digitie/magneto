# -*- coding: UTF-8 -*-

from time import sleep
import logging
import serial
import sys
import binascii
from log import MainLogger

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

"""This file provides useful utilities for the wanglib package."""


class InstrumentError(Exception):
    """Raise this when talking to instruments fails."""
    pass

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def show_newlines(string):
    """
    replace CR+LF with the words "CR" and "LF".
    useful for debugging.

    """
    if is_ascii(string):
        try:
            return string.replace('\r', '<CR>').replace('\n', '<LF>')
        except AttributeError:
            return binascii.hexlify(bytearray(string))
    else:
        try:
            return binascii.hexlify(string)
        except TypeError:
            return binascii.hexlify(bytearray(string))
class Serial(serial.Serial):
    """
    Extension of the standard serial class.
    
    to log whatever's written or read, pass a filename into
    the 'log' kwarg.


    """

    def __init__(self, *args, **kwargs):
        # make an event logger
        self.logger = MainLogger
        # take 'log' kwarg.
        self.logfile = kwargs.pop('log', False)
        if self.logfile:
            self.start_logging(self.logfile)
        # take default termination character
        # by default, append empty string
        self.term_chars = kwargs.pop('term_chars', '')
        # hand off to standard serial init function
        super(Serial, self).__init__(*args, **kwargs)

    def start_logging(self):
        """ start logging read/write data to file. """
        # make log file handler
        lfh = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(lfh)
        # make log file formatter
        lff = logging.Formatter('%(asctime)s %(message)s')
        lfh.setFormatter(lff)
        # set level low to log everything
        self.logger.setLevel(1)
        self.logger.debug('opened serial port')

    def write(self, data):
        data += self.term_chars
        super(Serial, self).write(data)
        self.logger.debug('write: ' + show_newlines(data))

    def read(self, size=1):
        resp = super(Serial, self).read(size)
        #self.logger.debug(' read: ' + show_newlines(resp))
        return resp
    
    def readall(self):
        """Automatically read all the bytes from the serial port."""
        return self.read(self.inWaiting())

    def ask(self, query, lag=0.05):
        """
        Write to the bus, then read response.

        This doesn't seem to work very well.

        """
        self.write(query)
        sleep(lag)
        return self.readall()


# ------------------------------------------------------
# up to this point, this file has dealt with customizing
# communication interfaces (GPIB / RS232). What follows
# are more random (though useful) utilities.
# 
# The two halves of this file serve rather disparate
# needs, and should probably be broken in two pieces.
# Before I actually do that I'd like to trim down 
# dependencies in the rest of the library - I think that
# will go a long way in reducing complexity.
# ------------------------------------------------------

def num(string):
    """
    convert string to number. decide whether to convert to int or float.
    """
    if '.' not in string:
        return int(string)
    else:
        return float(string)