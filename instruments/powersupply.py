from time import sleep

from struct import pack

import binascii
from core import labpid
'''
class VNA(object):
    def __init__(self, port = 7):
        self.port = port

    def open(self):
        plx = gpib.prologix(port = self.port)
        self.vna = gpib.HP8751A(plx, 17, delay = 0.05, auto = False)
'''

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

ChannelTypes = enum(
    CH1 = 1,
    CH2 = 2

)

PacketTypes = enum(
    ENABLE_OUTPUT = 17,
    DISABLE_OUTPUT = 18,
    SET_VOLTAGE = 33,
    SET_CURRENT = 34,
)

class TwoChannelPowersupply(object):
    def __init__(self, controller, addr,
                 delay=0.1):
        self.addr = addr
        self.delay = delay
        self.controller = controller

    def write(self, type, data):
        self.controller.sendData(self.addr, type, len(data), data)

    def read(self):
        return self.controller.getData()

    def setVoltage(self, channel, value):

        if value < 2:
            dac = 0
        else:
            if channel == ChannelTypes.CH1:
                dac = int(round(74.59 * value + 2.9111, 0))
            elif channel == ChannelTypes.CH2:
                dac = int(round(74.969 * value + 6.7875, 0))

        #print "setVoltage %f, %d" % (value, dac)

        self.write(PacketTypes.SET_VOLTAGE, pack('>BH', channel, dac))
        if self.read().type != 0:
            raise Exception('setVoltage Setting Failed')

    def setCurrent(self, channel, value):
        if value < 0.05:
            dac = 4096
        else:
            if channel == ChannelTypes.CH1:
                if value <= 0.22:
                    dac = int(round(183.58*value**4-446.99*value**3+441.41*value**2-411.13*value+3966.4, 0))

                else:
                    dac = int(round(-26.128*value**3+74.711*value**2-487.65*value+3987.8, 0))
                #dac = int(round(183.588*value**4-446.99*value**3+441.41*value**2-597.11*value+4000.6, 0))
            elif channel == ChannelTypes.CH2:
                dac = int(round(-415.8 * value + 3982.8, 0))


        #print "setCurrent %f, %d" % (value, dac)

        self.write(PacketTypes.SET_CURRENT, pack('>BH', channel, dac))
        if self.read().type != 0:
            raise Exception('setCurrent Setting Failed')

    def setVoltageDacValue(self, channel, dac):

        if dac < 0 or dac > 4095:
            dac = 0

        #print "setVoltage %f, %d" % (value, dac)

        self.write(PacketTypes.SET_VOLTAGE, pack('>BH', channel, dac))
        if self.read().type != 0:
            raise Exception('setVoltage Setting Failed')

    def setCurrentDacValue(self, channel, dac):
        if dac < 0 or dac > 4095:
            dac = 0

        #print "setCurrent %f, %d" % (value, dac)

        self.write(PacketTypes.SET_CURRENT, pack('>BH', channel, dac))
        if self.read().type != 0:
            raise Exception('setCurrent Setting Failed')

    def enable(self, channel):
        self.write(PacketTypes.ENABLE_OUTPUT, pack('>B', channel))
        if self.read().type != 0:
            raise Exception('enable Setting Failed')

    def disable(self, channel):
        self.write(PacketTypes.DISABLE_OUTPUT, pack('>B', channel))
        if self.read().type != 0:
            raise Exception('disable Setting Failed')


def main():
    pass

if __name__ == "__main__":
    main()