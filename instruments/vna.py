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

ResponseTypes = enum(FLOAT = 'FORM2', DOUBLE = 'FORM3', ASCII = 'FORM4')
ChartTypes = enum(
	SMITH_CHART = 'SMIC', 
	LIN_MAG = 'LINM', 
	LOG_MAG = 'LOGM', 
	REAL_ONLY = 'REAL',
	IMAGENARY_ONLY = 'IMAG',
	DELAY = 'DELA',
	PHASE = 'PHAS',
	INV_SMITH_CHART = 'INVSCHAR'

)
FrequencySweepTypes = enum(LINEAR_SWEEP = 'LINFREQ', LOG_SWEEP = 'LOGFREQ')
FrequencySweepModes = enum(SINGLE = 'SING', CONTINUOUS = 'CONT', HOLD = 'HOLD')

class HP8751A(object):
	def __init__(self, controller, addr,
				 delay=0.1, auto=True):
		self.addr = addr
		self.auto = auto
		self.delay = delay
		self.controller = controller

		self.controller.read_timeout_ms = 3000
		self.controller.term_chars_for_xmit = gpib.TermChars.LF 
		self.controller.eot = True
		self.number_of_points = 801
		self.sweep_type = FrequencySweepTypes.LINEAR_SWEEP

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


	def read_data(self, response_type = ResponseTypes.DOUBLE):
		#response_type = ResponseTypes.reverse_mapping[response_type]
		if not self.auto:
			# explicitly tell instrument to talk.
			self.controller.write('++read eoi', lag=self.delay)

		if response_type == ResponseTypes.DOUBLE or \
			response_type == ResponseTypes.FLOAT:
			header = self.readBytes(8)
			#print binascii.hexlify(header)

			data_size = int(header[2:8])
			#print binascii.hexlify(header)
			r  = self.readBytes(data_size)
			tail = self.controller.read(2) # 0a00 (LF, NULL)
			#print binascii.hexlify(tail)
			return r
		elif response_type == ResponseTypes.ASCII:			
			buffer = ''
			while True:
				buffer = buffer + self.readBytes(1)
				if '\x0a\x00' in buffer[-2:]:
					break
			#print binascii.hexlify(buffer)
			return buffer[:-2]

	@property 
	def source_power(self):
		self.write('POWE?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		return float(r)

	@source_power.setter
	def source_power(self, power):
		self.write('POWE %d' % (power))
		self.controller.serial_poll()
		sleep(self.calculate_delay())

	@property 
	def sweep_mode(self):
		self.write('SING?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		if int(r) == 1:
			return FrequencySweepModes.SINGLE

		self.write('CONT?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		if int(r) == 1:
			return FrequencySweepModes.CONTINUOUS

		self.write('HOLD?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		if int(r) == 1:
			return FrequencySweepModes.HOLD

	@sweep_mode.setter 
	def sweep_mode(self, mode):
		self.write(mode)
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		sleep(1)


	def set_frequency_range(self, start = 100000, stop = 300000):
		self.write('STAR %d' % (start))
		self.write('STOP %d' % (stop))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		while self.srq:
			pass

	def set_frequency_span(self, center = 150000, span = 10000):
		self.write('CENT %d' % (center))
		self.write('SPAN %d' % (span))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		while self.srq:
			pass

	@property 
	def start_frequency(self):
		self.write('STAR?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		return float(r)
	'''
	@start_frequency.setter
	def start_frequency(self, freq):
		self.write('STAR %d' % (freq))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		sleep(self.calculate_delay())
	'''

	@property 
	def stop_frequency(self):
		self.write('STOP?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		return float(r)

	'''
	@stop_frequency.setter
	def stop_frequency(self, freq):
		self.write('STOP %d' % (freq))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		sleep(self.calculate_delay())
	'''

	'''
	def center_frequency(self, freq):
		self.write('CENT %d' % (freq))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		sleep(self.calculate_delay())

	def frequency_span(self, freq):
		self.write('SPAN %d' % (freq))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		sleep(self.calculate_delay())
	'''

	def set_marker_to_min(self):
		self.write('SEAMIN')

	def set_marker_to_max(self):
		self.write('SEAMAX')

	def set_marker_to_min_peak(self):
		self.write('SEALMIN')

	def set_marker_to_max_peak(self):
		self.write('SEALMAX')

	def marker_on(self, marker_num):
		self.write('MARK%d' % (marker_num))

	def autoscale(self):
		self.write('AUTO')

	@property
	def chart_type(self):
		return False

	@chart_type.setter
	def chart_type(self, chart_type):
		self.write(chart_type)

	@property
	def sweep_type(self):
		self.write('LINFREQ?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		if int(r) == 1:
			return FrequencySweepTypes.LINEAR_SWEEP

		self.write('LOGFREQ?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		if int(r) == 1:
			return FrequencySweepTypes.LOG_SWEEP


	@sweep_type.setter
	def sweep_type(self, sweep_type):
		self.write(sweep_type)

	@property
	def response_type(self):
		return self._response_type

	@response_type.setter
	def response_type(self, response_type):
		self._response_type = response_type
		self.write(response_type)


	@property
	def sweep_time(self):
		self.write('SWET?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		return float(r)

	@sweep_time.setter
	def sweep_time(self, time):
		self.write('SWET %d' % (time))

	@property
	def number_of_points(self):
		self.write('POIN?')
		r = self.read_data(response_type = ResponseTypes.ASCII)
		return int(r)

	@number_of_points.setter
	def number_of_points(self, pts):
		self.write('POIN %d' % (pts))
		self.write('CLES')
		self.write('*SRE 4;ESNB 1')
		self.controller.serial_poll()
		while self.srq:
			pass
		#sleep(pts * 0.002)

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

	def calculate_delay(self):
		return float(self.number_of_points) * 0.003

	def read_marker_value(self):
		self.write('OUTPMARK?')
		r = self.read_data(response_type = ResponseTypes.ASCII).split(',')
		value1 = float(r[0])
		value2 = float(r[1])
		freq = float(r[2])
		return {
			'stim_freq' : freq,
			'value1' : value1,
			'value2' : value2
		}

	def read_impedance(self):
		self.chart_type = ChartTypes.SMITH_CHART
		self.response_type = ResponseTypes.DOUBLE
		re_list = []
		im_list = []
		imp_re_list = []
		imp_im_list = []
		freq_list = []
		self.write('OUTPFORM?')

		r = self.read_data()
		num_of_points = len(r)/16

		for i in range(num_of_points):
			rb = r[i*16 : i*16+16]
			re, im = struct.unpack('>dd', rb)
			re_list.append(re)
			im_list.append(im)
			imp_re = (1-re**2-im**2)/((1-re)**2+im**2)
			imp_im = 2*im/((1-re)**2+im**2)
			imp_re_list.append(imp_re)
			imp_im_list.append(imp_im)

		self.write('OUTPSTIM?')

		r = self.read_data()
		num_of_points = len(r)/8

		for i in range(num_of_points):
			rb = r[i*8 : i*8+8]
		   
			freq_list.append(struct.unpack('>d', rb)[0])
		return (freq_list, re_list, im_list, imp_re_list, imp_im_list)

	def read_trace_impedance(self):
		re_list = []
		im_list = []
		self.write('OUTPFORM?')

		r = self.read_data()
		num_of_points = len(r)/16

		for i in range(num_of_points):
			rb = r[i*16 : i*16+16]
			re, im = struct.unpack('>dd', rb)
			re_list.append(re)
			im_list.append(im)
		return (re_list, im_list)

	def read_mem_impedance(self):
		re_list = []
		im_list = []
		self.write('OUTPTMEM?')

		r = self.read_data()
		num_of_points = len(r)/16

		for i in range(num_of_points):
			rb = r[i*16 : i*16+16]
			re, im = struct.unpack('>dd', rb)
			re_list.append(re)
			im_list.append(im)
		return (re_list, im_list)

	def read_stim_frequency(self):
		self.write('OUTPSTIM?')
		result = []

		r = self.read_data()
		num_of_points = len(r)/8

		for i in range(num_of_points):
			rb = r[i*8 : i*8+8]
		   
			result.append(struct.unpack('>d', rb)[0])
		return result

	def find_center_freq(self):
		self.chart_type = ChartTypes.REAL_ONLY
		self.number_of_points = 101
		#print("Number of Points : %d" %(self.vna.number_of_points))
		#print("Sweep Time : %d" %(self.vna.sweep_time))
		#print("Setting Frequency Span...")
		'''
		self.start_frequency = 100000
		self.stop_frequency = 300000		
		'''
		self.set_frequency_range(start = 100000, stop = 300000)
		sleep(0.5)
		#print("Initial Frequency Span as %d ~ %d Hz" % (self.vna.start_frequency, self.vna.stop_frequency))
		#print("Finding Peak...")
		self.marker_on(1)
		self.autoscale()
		self.set_marker_to_max_peak()
		result = self.read_marker_value()
		print("Peak Log Magnitude Value@%d" %(float(result['stim_freq'])))
		self.set_frequency_span(center = float(result['stim_freq']), span = 20000)
		sleep(0.5)
		#print("Frequency Span as %d ~ %d Hz" % (int(result['stim_freq']) - 10000, int(result['stim_freq']) + 10000))
		self.autoscale()
		return float(result['stim_freq'])

	def readBytes(self, size): # behaves like readall
		""" read response from instrument.  """
		self.get_priority()
		return self.controller.read(size)

	def write(self, command):
		self.get_priority()
		self.controller.write(command, lag=self.delay)

def main():
	plx = prologix(port = '\\.\COM7')
	inst = HP8751A(plx, 17, delay = 0.05, auto = False)
	inst.write('++read_tmo_ms 3000')
	inst.write('++eos 2')
	inst.write('++eot_enable 1')
	inst.response_type = ResponseTypes.DOUBLE
	inst.chart_type = ChartTypes.REAL_ONLY
	inst.number_of_points = 101
	print("Number of Points : %d" %(inst.number_of_points))
	print("Sweep Time : %d" %(inst.sweep_time))
	print("Setting Frequency Span...")
	inst.set_frequency_range(start = 100000, stop = 300000)
	print("Initial Frequency Span as %d ~ %d Hz" % (inst.start_frequency, inst.stop_frequency))
	print("Finding Peak...")
	inst.marker_on(1)
	inst.set_marker_to_max_peak()
	result = inst.read_marker_value()
	print("Peak Log Magnitude Value@%d" %(float(result['stim_freq'])))
	inst.set_frequency_span(center = float(result['stim_freq']), span = 10000)
	print("Frequency Span as %d ~ %d Hz" % (int(result['stim_freq']) - 10000, int(result['stim_freq']) + 10000))
	inst.autoscale()


	inst.number_of_points = 801
	#for i in range(-15, 16):
	#	inst.source_power = i
	#	print inst.source_power
	sleep(1)
	d = inst.read_impedance()
	#print zip(f, t, m)
	#inst.chart_type = ChartTypes.LOG_MAG

if __name__ == "__main__":
	main()