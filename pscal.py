from optparse import OptionParser
from serial import Serial
import sys

from core.labpid import Labpid
from instruments.powersupply import TwoChannelPowersupply


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-v", "--voltage", dest="voltage", type="float",
                      help="set voltage")
    parser.add_option("-i", "--current", dest="current", type="float",
                      help="set current")
    parser.add_option("-o", "--voltage-dac", dest="voltageDac", type="int",
                      help="set voltage as dac value")
    parser.add_option("-u", "--current-dac", dest="currentDac", type="int",
                      help="set current as dac value")
    parser.add_option("-c", "--channel", dest="channel", type="int",
                      help="set channel of ps")
    parser.add_option("-p", "--port", dest="port", default = "COM5",
                      help="COM Port of Labpid device (e.g. COM5)")
    parser.add_option("-e", "--enable",
                      action="store_true", dest="enable", default=False,
                      help="output enable")

    (options, args) = parser.parse_args()

    if options.voltage and options.voltageDac:
    	sys.stderr.write("-v and -o conflicts")
    	raise SystemExit(1)

    if options.current and options.currentDac:
    	sys.stderr.write("-i and -u conflicts")
    	raise SystemExit(1)

    labpidserial = Serial()
    labpidserial.baudrate = 115200
    labpidserial.port = options.port
    labpidserial.timeout = 0.5   #make sure that the alive event can be checked from time to time

    labpidserial.open()
    labpid = Labpid(bus = labpidserial)
    ps = TwoChannelPowersupply(labpid, 0)


    if options.channel > 3 or options.channel < 1:
        labpidserial.close()
        sys.stderr.write("Invalid Channel\n")

    if options.voltage:
        sys.stdout.write("Voltage %f\n" % options.voltage)
        ps.setVoltage(options.channel, options.voltage)

    if options.current:
        sys.stdout.write("Current %f\n" % options.current)
        ps.setCurrent(options.channel, options.current)

    if options.voltageDac:
        sys.stdout.write("Voltage as dac %d\n" % options.voltageDac)
        ps.setVoltageDacValue(options.channel, options.voltageDac)

    if options.currentDac:
        sys.stdout.write("Current as dac %d\n" % options.currentDac)
        ps.setCurrentDacValue(options.channel, options.currentDac)

    if options.enable:
        sys.stdout.write("Enabled\n")
        ps.enable(options.channel)
    else:
        sys.stdout.write("Disabled\n")
        ps.disable(options.channel)

    labpidserial.close()

