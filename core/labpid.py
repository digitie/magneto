#!/usr/bin/env python
# generated by wxGlade 0.3.1 on Fri Oct 03 23:23:45 2003

#from wxPython.wx import *
import wx
import serial
import threading
from struct import *
import binascii
import argparse

def toStr(s):
    return s and chr(int(s[:2])) + toStr(s[2:]) or ''

class LabpidPacket(object):
    def __init__(self, bytes):
        self.bytes = bytes
        self._parse()

    def _parse(self):
        self.stx = self.bytes[0]
        self.length = ord(self.bytes[3])
        self.type = ord(self.bytes[2])
        self.address = ord(self.bytes[1])
        self.data = self.bytes[4:-3]
        self.checksum = self.bytes[-2]
        self.etx = self.bytes[-1]

    def __str__(self):
        return binascii.hexlify(self.data)

class Labpid(object):
    def __init__(self, bus):
        self.serial = bus

    def open(self):
        self.serial.open()

    def sendData(self, address, type, length, data):

        pkt = []

        pkt.append(chr(2))
        pkt.append(chr(address))
        pkt.append(chr(type))
        pkt.append(chr(length))
        if data is not None:
            pkt += data
        checksum = sum(bytearray(pkt[1:]))
        checksum = pack('B', checksum & 0xFF)
        pkt.append((checksum))
        pkt.append(chr(3))
        #print pkt
        self.serial.write(pkt)

    def getData(self):
        header = self.serial.read(4)
        if len(header) < 4:
            raise Exception('Data receive from LABPID Device is failed. Timed out?')

        if header[0] != chr(2):
            raise Exception()

        length = ord(header[3])
        body = self.serial.read(length + 2)
        data = header + body
        pkt = LabpidPacket(data)
        print pkt
        return pkt



    def _readHeader(self):
        pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('count', type=int, help='count')

    args = parser.parse_args()
    labpid = Labpid()
    labpid.open()
    pkt = pack('>l', args.count)
    labpid.sendData(1, 16, 4, pkt)
    labpid.getData()