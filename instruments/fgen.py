from time import sleep

import struct

import binascii
import gpib
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

TriggerModeTypes = enum(
	NORM = 'M1', 
	TRIG = 'M2', 
	GATE = 'M3', 
	EWID = 'M4',
	LSWP = 'M5',
	ESWP = 'M6',
	IBUR = 'M7',
	EBUR = 'M8',
)

TriggerControlTypes = enum(
	TRIG_OFF = 'T0', 
	POS_TRIG_SLOPE = 'T1', 
	NEG_TRIG_SLOPE = 'T2', 

)

ControlModeTypes = enum(
	OFF = 'CT0', 
	FM = 'CT1', 
	AM = 'CT2', 
	PWM = 'CT3', 
	VCO = 'CT4', 

)

OutputWaveformTypes = enum(
	DC = 'W0', 
	SINE = 'W1', 
	TRIANGLE = 'W2', 
	SQUARE = 'W3', 
	PULSE = 'W4', 

)
OutputWaveformPhaseTypes = enum(
	DEG0 = 'H0', 
	DEGNEG90 = 'H1', 

)


class HP8116A(object):
	def __init__(self, controller, addr,
				 delay=0.1, auto=True):
		self.addr = addr
		self.auto = auto
		self.delay = delay
		self.controller = controller

		self.controller.read_timeout_ms = 3000
		self.controller.term_chars_for_xmit = gpib.TermChars.LF 
		self.controller.eot = True

	def get_priority(self):
		"""
		configure the controller to address this instrument

		"""
		# configure instrument-specific settings
		if self.auto != self.controller._auto:
			self.controller.auto = self.auto
		# switch the controller address to the
		# address of this instrument
		if self.addr != self.controller._addr:
			self.controller.addr = self.addr


	def read_data(self):
		#response_type = ResponseTypes.reverse_mapping[response_type]
		if not self.auto:
			# explicitly tell instrument to talk.
			self.controller.write('++read eoi', lag=self.delay)

			buffer = ''
			while True:
				buffer = buffer + self.readBytes(1)
				if '\x0a\x00' in buffer[-2:]:
					break
			#print binascii.hexlify(buffer)
			return buffer[:-2]

	@property 
	def frequency(self):
		self.write('IFRQ')
		r = self.read_data()
		return float(r)

	@frequency.setter
	def frequency(self, freq):
		self.write('FRQ %d' % (freq))
		self.controller.serial_poll()

	@property 
	def duty(self):
		self.write('IDTY')
		r = self.read_data()
		return float(r)

	@duty.setter
	def duty(self, duty):
		self.write('DTY %d %' % (duty))
		self.controller.serial_poll()

	@property 
	def pulse_width(self):
		self.write('IWID')
		r = self.read_data()
		return float(r)

	@pulse_width.setter
	def pulse_width(self, duty):
		self.write('WID %d %' % (duty))
		self.controller.serial_poll()

	@property 
	def amplitude(self):
		self.write('IAMP')
		r = self.read_data()
		return float(r)

	@amplitude.setter
	def amplitude(self, amplitude):
		self.write('AMP %d %' % (duty))
		self.controller.serial_poll()

	@property 
	def pulse_width(self):
		self.write('IWID')
		r = self.read_data()
		return float(r)

	@pulse_width.setter
	def pulse_width(self, duty):
		self.write('WID %d %' % (duty))
		self.controller.serial_poll()



	@property 
	def srq(self):
		self.write('++srq')
		try:
			srq = int(self.readBytes(3))
			if srq == 1:
				return True
			else:
				return False
		except ValueError:
			print "pass"
			sleep(0.1)
			return True

	def readBytes(self, size): # behaves like readall
		""" read response from instrument.  """
		self.get_priority()
		return self.controller.read(size)

	def write(self, command):
		self.get_priority()
		self.controller.write(command, lag=self.delay)
