import xlsxwriter
from core.listobject import *
import threading
from core.log import MainLogger
from events import *

CHART_COLORS = ('b','g','r','c','m','y','k',)

def index_to_int(index):
	s = 0
	pow = 1
	for letter in index[::-1]:
		d = int(letter,36) - 9
		s += pow * d
		pow *= 26
	# excel starts column numeration from 1
	return s

def number_to_column(num):
	dividend = num
	columnName = ""

	while (dividend > 0):
		modulo = (dividend - 1) % 26
		columnName = chr(65 + modulo) + columnName
		dividend = (int)((dividend - modulo) / 26)

	return columnName

def column_to_number(c):
	"""Return number corresponding to excel-style column."""
	number=-25
	for l in c:
		if not l in string.ascii_letters:
			return False
		number+=ord(l.upper())-64+25
	return number

def excel2num(x): 
	return reduce(lambda s,a:s*26+ord(a)-ord('A')+1, x, 0)

def to_excel_coord(row, col, row_abs = False, col_abs = False):
	col = '%s' % (number_to_column(col+1))
	if col_abs:
		col = '$' + col

	row = '%d' % (row+1)
	if row_abs:
		row = '$' + row

	return '%s%s' % (col, row)

DATA_OFFSET = 7
NORMALIZED_FACTOR_ROW_OFFSET = 2
NORMALIZED_FACTOR_COL_OFFSET = 23
L_OTHER_ROW_OFFSET = 3
L_OTHER_COL_OFFSET = 23
D_TOT_ROW_OFFSET = 4
D_TOT_COL_OFFSET = 23

RM_ROW_OFFSET = 5
RM_COL_OFFSET = 23
R_ROW_OFFSET = 6
R_COL_OFFSET = 23

LS_CAL_ROW_OFFSET = 3
LS_CAL_COL_OFFSET = 20
R_EFF_ROW_OFFSET = 4
R_EFF_COL_OFFSET = 20
L_ROW_OFFSET = 5
L_COL_OFFSET = 20
C_ROW_OFFSET = 6
C_COL_OFFSET = 20


K_ROW_OFFSET = 2
K_COL_OFFSET = 18
Q_EXP_ROW_OFFSET = 3
Q_EXP_COL_OFFSET = 18
Q_EXP_ADJ_ROW_OFFSET = 1
Q_EXP_ADJ_COL_OFFSET = 23
Q_ROW_OFFSET = 4
Q_COL_OFFSET = 18
FR_EXP_ROW_OFFSET = 5
FR_EXP_COL_OFFSET = 18
LC_ROW_OFFSET = 6
LC_COL_OFFSET = 18

class ExcelCell():
	def __init__(self, value, **kwargs):
		self.__value = value
		self.__type = kwargs['type']
		self.__location = kwargs['location']
		self.__header = kwargs['header']

	def getLocAsXY(self):
		pass

	def getLocAsExcel(self):
		pass

	def getColumnName(self):
		pass

class FileProcessor(threading.Thread):
	"""Worker Thread Class."""
	def __init__(self, notify_window, filepath, exp_ids = []):
		threading.Thread.__init__(self)
		self.filepath = filepath
		self.exp_ids = exp_ids
		self.notifyWindow = notify_window
		self.logger = MainLogger
		self.alive = threading.Event() 
		self.alive.set()
		self.start()

	def abort(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		self.alive.clear()

	def isAlive(self):
		# Method for use by main thread to signal an abort
		return self.alive.isSet() == False

	def checkAbort(self):
		if not self.alive.isSet():
			wx.PostEvent(self.notifyWindow, XlsxWriteCanceledEvent(-1, {'title':'Progress cancelled', 'message':'Progress is cancelled by user'}))
			self.ps.disable(ChannelTypes.CH1)
			return True
		else:
			return False

	def run(self):
		try:
			wx.PostEvent(self.notifyWindow, XlsxWriteProgressEvent(-1, 'Preparing Excel Template ...', 0))
			self.prepareExcel()
			if self.checkAbort():
				return
		except Exception as e:
			wx.PostEvent(self.notifyWindow, XlsxWriteCanceledEvent(-1, {'title':'Preparing Excel Template failed', 'message':str(e)}))

		try:
			wx.PostEvent(self.notifyWindow, XlsxWriteProgressEvent(-1, 'Writing in to Excel file ...', 0))
			self.setData()
			if self.checkAbort():
				return
		except Exception as e:
			wx.PostEvent(self.notifyWindow, XlsxWriteCanceledEvent(-1, {'title':'Writing in to Excel file failed', 'message':str(e)}))

		try:
			wx.PostEvent(self.notifyWindow, XlsxWriteProgressEvent(-1, 'Finalizing ...', 100))
			self.write()
		except Exception as e:
			wx.PostEvent(self.notifyWindow, XlsxWriteCanceledEvent(-1, {'title':'Finalizing failed', 'message':str(e)}))

		wx.PostEvent(self.notifyWindow, XlsxWriteCompletedEvent(-1, None))

	def prepareExcel(self):
		self.workbook = xlsxwriter.Workbook(self.filepath)
		defaultFormat = self.workbook.add_format()
		defaultFormat.set_font_name('Consolas')
		defaultFormat.set_font_size(10)
		self.summary = self.workbook.add_worksheet('Summary')
		self.data = self.workbook.add_worksheet('Data')

		self.dataHeaderFormat = self.workbook.add_format({
			'bold': 1,
			'border': 1,
			'font_name': 'Consolas',
			'font_size': 10,
			'align': 'center',
			'valign': 'vcenter',
			'pattern': 1,
			'bg_color': '#bebebe'})

		self.dataSeparatorFormat = self.workbook.add_format({
			'bold': 0,
			'border': 1,
			'font_name': 'Consolas',
			'font_size': 10,
			'align': 'center',
			'valign': 'vcenter',
			'pattern': 1,
			'bg_color': '#bebebe'})

		self.dataFormat = self.workbook.add_format({
			'bold': 0,
			'border': 1,
			'font_name': 'Consolas',
			'font_size': 10,
			'align': 'center',
			'valign': 'vcenter'})

		self.warningFormat = self.workbook.add_format({
			'bold': 0,
			'border': 1,
			'font_name': 'Consolas',
			'font_size': 10,
			'align': 'center',
			'valign': 'vcenter',
			'pattern': 1,
			'bg_color': '#ffc7ce'})

		self.inputFormat = self.workbook.add_format({
			'bold': 0,
			'border': 1,
			'font_name': 'Consolas',
			'font_size': 10,
			'align': 'center',
			'valign': 'vcenter',
			'pattern': 1,
			'bg_color': '#c6efce'})


	def writeSummaryHeader(self):
		cols = ['coil_no', 'type', 'width', 'height', 'length', 'wire_dia', 'turn', 'Power', 'X-sectional Area', 'Patch Area', 
			'A/Ac', 'exp_id', 'Environment', 'Density', 'abs. Vis', 'Weight %', 'PatchW', 'PatchL', 'max_imp_re', 'max_imp_im', 'max_imp_im_freq', 'max_imp_re_freq', 'max_imp_mag_freq', 
			'max_imp_mag', 'imp_q_freq0', 'max_imp_parallel_ind', 'imp_q_freq1', 'Q', 'Rm', 'R-', 'Lm', 'Lm_air', 'Cm', 'k', 'Lp_cal', '1/N_factor (experimental)', 
			'N_factor (winding ratio^2)', 'N_factor (winding ratio^2) Normalized', 'sqrt(1/N_factor)', 'sqrt(N_factor)', 
			'Ls_normalized', 'Lm_normalized', 'Cm_normalized', 'Rm_normalized', 'Damping', 'L_coil', 'L_coil/A_coil', 'L_s/L_coil', 'L_s/L_coil*Ap/Ac*1/Lp', 'L_coil_cal', 'L_s without_suscep', 'Susceptability','DC Current', 'DC Field', 'cSt', 'sqrt(cSt)', 'Adj f0', 'Adj f1', 'Adj Q', 'Ref0', 'Ref1', 'ReQ', 'Adj Ref0', 'Adj Ref1', 'Adj ReQ']
		i = 0
		for col in cols:
			self.summary.write_string(0,i, col, self.dataHeaderFormat)
			i+=1

	def setData(self):
		try:
			summaries, datas = getRawVNAData(self.exp_ids)
			self.writeSummary(summaries)
			self.writeData(datas)
		except Exception:
			import traceback
			print traceback.print_exc()
			raise

	def writeSummary(self, summaries):
		self.writeSummaryHeader()
		i = 1
		for summary in summaries:
			j = 0
			for elem in summary:
				if isinstance(elem, (int, long, float, complex)):
					self.summary.write_number(i,j, elem)
				else:
					self.summary.write_string(i,j, str(elem))

				j+=1
			i+= 1

	def writeDataHeader(self, row, col, title, column_names = []):
		total_cols = len(column_names)
		headerCellRange = '%s%d:%s%d' % (number_to_column(col+1), row+1, number_to_column(col+total_cols), row+1)
		self.data.merge_range(headerCellRange, title, self.dataHeaderFormat)
		for idx in range(total_cols):
			self.data.write_string(row+1, col + idx, column_names[idx], self.dataHeaderFormat)

		return row+2,col+total_cols


	def writeRawDataHeader(self, row, col, title):
		return self.writeDataHeader(row, col, title, column_names=['freq','re','im','imp_re','imp_im', 'inductance'])

	def writeRawData(self, row, col, data):
		nextRow, nextCol = self.writeRawDataHeader(row, col, data.title)

		for idx in range(len(data.freq)):
			self.data.write_number(nextRow+idx,col, data.freq[idx], self.dataSeparatorFormat)
		for idx in range(len(data.re)):
			self.data.write_number(nextRow+idx,col+1, data.re[idx], self.dataFormat)
		for idx in range(len(data.im)):
			self.data.write_number(nextRow+idx,col+2, data.im[idx], self.dataFormat)
		for idx in range(len(data.imp_re)):
			self.data.write_number(nextRow+idx,col+3, data.imp_re[idx], self.dataFormat)
		for idx in range(len(data.imp_im)):
			self.data.write_number(nextRow+idx,col+4, data.imp_im[idx], self.dataFormat)
		for idx in range(len(data.freq)):
			self.data.write_formula(nextRow+idx,col+5, '=%s/(2*PI()*%s)*50' % (to_excel_coord(nextRow+idx, col+4), to_excel_coord(nextRow+idx, col)))

		return nextRow + len(data.freq), nextCol

	def writeSubtractedDataHeader(self, row, col, title):
		return self.writeDataHeader(row, col, title, column_names=['freq','re','im','imp_re','imp_im', 'imp_mag'])

	def writeSubtractedData(self, row, col, data):
		nextRow, nextCol = self.writeSubtractedDataHeader(row, col, data.title + ' Subtracted')

		for idx in range(len(data.freq)):
			imp_re = to_excel_coord(nextRow+idx, col+3)
			imp_im = to_excel_coord(nextRow+idx, col+4)

			self.data.write_formula(nextRow+idx, col, '=%s' % (to_excel_coord(nextRow+idx, col-6)), self.dataSeparatorFormat)
			self.data.write_formula(nextRow+idx, col+1, '=(-1+{imp_re}^2+{imp_im}^2)/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+2, '=2*{imp_im}/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+3, '%s-%s' % (to_excel_coord(nextRow+idx, col+3-12), to_excel_coord(nextRow+idx, col+3-6)), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+4, '%s-%s' % (to_excel_coord(nextRow+idx, col+4-12), to_excel_coord(nextRow+idx, col+4-6)), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+5, '=SQRT(({imp_re}*50)^2+({imp_im}*50)^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)

		return nextRow + len(data.freq), nextCol

	def writeSubtractedNormalizedDataHeader(self, row, col, title):
		return self.writeDataHeader(row, col, title, column_names=['freq','re','im','imp_re','imp_im', 'imp_mag'])

	def getNormalizeFactorCell(self, col):
		return to_excel_coord(NORMALIZED_FACTOR_ROW_OFFSET, col+NORMALIZED_FACTOR_COL_OFFSET, row_abs=True)

	def writeSubtractedormalizedData(self, row, col, data, n):
		nextRow, nextCol = self.writeSubtractedDataHeader(row, col, data.title + ' Subtracted (Normalized)')

		for idx in range(len(data.freq)):
			imp_re = to_excel_coord(nextRow+idx, col+3)
			imp_im = to_excel_coord(nextRow+idx, col+4)

			self.data.write_formula(nextRow+idx, col, '=%s' % (to_excel_coord(nextRow+idx, col-6)), self.dataSeparatorFormat)
			self.data.write_formula(nextRow+idx, col+1, '=(-1+{imp_re}^2+{imp_im}^2)/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+2, '=2*{imp_im}/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+3, '{subtracted_imp_re}*{n}'.format(subtracted_imp_re = to_excel_coord(nextRow+idx, col+3-6), n = n), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+4, '{subtracted_imp_im}*{n}'.format(subtracted_imp_im = to_excel_coord(nextRow+idx, col+4-6), n = n), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+5, '=SQRT(({imp_re}*50)^2+({imp_im}*50)^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)

		return nextRow + len(data.freq), nextCol

	def writeCalculatedDataHeader(self, row, col, title):
		return self.writeDataHeader(row, col, title, column_names=['freq','re','im','imp_re','imp_im', 'imp_mag'])

	def writeCalculatedData(self, row, col, title, freq, r, l, c, ls):
		nextRow, nextCol = self.writeCalculatedDataHeader(row, col, title + ' Calculated')

		for idx in range(len(freq)):
			f = to_excel_coord(nextRow+idx, col)
			imp_re_expr = '=(1/({r}*(1/{r}^2+(-1/({l}*2*PI()*{f})+{c}*2*PI()*{f})^2)))/50'.format(r = r, l = l, c = c, f = f)
			imp_im_expr = '=(1/({l}*2*PI()*{f}*((1/{r}^2+(-1/({l}*2*PI()*{f})+{c}*2*PI()*{f})^2)))-{c}*{f}*PI()*2/(1/{r}^2+(-1/({l}*2*PI()*{f})+{c}*2*PI()*{f})^2)+{ls}*2*PI()*{f})/50'.format(r = r, l = l, c = c, ls = ls, f = f)
			imp_re = to_excel_coord(nextRow+idx, col+3)
			imp_im = to_excel_coord(nextRow+idx, col+4)

			self.data.write_formula(nextRow+idx, col, '=%s' % (to_excel_coord(nextRow+idx, col-6)), self.dataSeparatorFormat)
			self.data.write_formula(nextRow+idx, col+1, '=(-1+{imp_re}^2+{imp_im}^2)/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+2, '=2*{imp_im}/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+3, imp_re_expr, self.dataFormat)
			self.data.write_formula(nextRow+idx, col+4, imp_im_expr, self.dataFormat)
			self.data.write_formula(nextRow+idx, col+5, '=SQRT(({imp_re}*50)^2+({imp_im}*50)^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)

		return nextRow + len(freq), nextCol

	def writeCalculatedNormalizedDataHeader(self, row, col, title):
		return self.writeDataHeader(row, col, title, column_names=['freq','re','im','imp_re','imp_im', 'imp_mag'])

	def writeCalculatedNormalizedData(self, row, col, title, freq, r, l, c, ls, n):
		nextRow, nextCol = self.writeSubtractedDataHeader(row, col, title + ' Calculated (Normalized)')

		for idx in range(len(freq)):
			f = to_excel_coord(nextRow+idx, col)
			imp_re_expr = '=(1/({r}*(1/{r}^2+(-1/({l}*2*PI()*{f})+{c}*2*PI()*{f})^2)))/50*{n}'.format(r = r, l = l, c = c, f = f, n = n)
			imp_im_expr = '=(1/({l}*2*PI()*{f}*((1/{r}^2+(-1/({l}*2*PI()*{f})+{c}*2*PI()*{f})^2)))-{c}*{f}*PI()*2/(1/{r}^2+(-1/({l}*2*PI()*{f})+{c}*2*PI()*{f})^2)+{ls}*2*PI()*{f})/50*{n}'.format(r = r, l = l, c = c, ls = ls, f = f, n = n)
			imp_re = to_excel_coord(nextRow+idx, col+3)
			imp_im = to_excel_coord(nextRow+idx, col+4)

			self.data.write_formula(nextRow+idx, col, '=%s' % (to_excel_coord(nextRow+idx, col-6)), self.dataSeparatorFormat)
			self.data.write_formula(nextRow+idx, col+1, '=(-1+{imp_re}^2+{imp_im}^2)/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+2, '=2*{imp_im}/(1+2*{imp_re}+{imp_re}^2+{imp_im}^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)
			self.data.write_formula(nextRow+idx, col+3, imp_re_expr, self.dataFormat)
			self.data.write_formula(nextRow+idx, col+4, imp_im_expr, self.dataFormat)
			self.data.write_formula(nextRow+idx, col+5, '=SQRT(({imp_re}*50)^2+({imp_im}*50)^2)'.format(imp_re = imp_re, imp_im = imp_im), self.dataFormat)

		return nextRow + len(freq), nextCol

	def writeData(self, datas):
		nextCol = 0
		smithSummaryChart = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
		smithSummaryChart.set_legend({'position': 'bottom'})
		smithSummaryChart.set_size({'x_scale': 2, 'y_scale': 2})


		impSummaryChart = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})
		impSummaryChart.set_legend({'position': 'bottom'})
		impSummaryChart.set_x_axis({'min': 95000, 'max': 115000})
		impSummaryChart.set_size({'x_scale': 2, 'y_scale': 2})
		i = 1
		for data in datas:
			wx.PostEvent(self.notifyWindow, XlsxWriteProgressEvent(-1, 'Writing in to Data %d of %d ...' % (i, len(datas)), 100*i/len(datas)))
			if self.checkAbort():
				return
			orig = data['orig']
			without_patch = data['to_subtract']
			startCol = nextCol
			nextRow, nextCol = self.writeRawData(DATA_OFFSET, nextCol, orig)
			nextRow, nextCol = self.writeRawData(DATA_OFFSET, nextCol, without_patch)
			nextRow, nextCol = self.writeSubtractedData(DATA_OFFSET, nextCol, without_patch)
			nextRow, nextCol = self.writeSubtractedormalizedData(DATA_OFFSET, nextCol, without_patch, self.getNormalizeFactorCell(startCol))
			self.generateDataAuxData(0, startCol)
			r = to_excel_coord(R_ROW_OFFSET, startCol + R_COL_OFFSET)
			r = to_excel_coord(R_EFF_ROW_OFFSET, startCol + R_EFF_COL_OFFSET)
			l = to_excel_coord(L_OTHER_ROW_OFFSET, startCol + L_OTHER_COL_OFFSET) # L_OTHER_ROW_OFFSET, col + L_OTHER_COL_OFFSET
			c = to_excel_coord(C_ROW_OFFSET, startCol + C_COL_OFFSET)
			ls = to_excel_coord(LS_CAL_ROW_OFFSET, startCol + LS_CAL_COL_OFFSET)
			nextRow, nextCol = self.writeCalculatedData(DATA_OFFSET, nextCol, without_patch.title, without_patch.freq, r = r, l = l, c = c, ls = ls)
			nextRow, nextCol = self.writeCalculatedNormalizedData(DATA_OFFSET, nextCol, without_patch.title, without_patch.freq, r = r, l = l, c = c, ls = ls, n = self.getNormalizeFactorCell(startCol))
			self.generateSummaryData(0, startCol)

			impChart = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})
			impChart.set_legend({'position': 'bottom'})
			impChart.set_x_axis({'min': 95000, 'max': 115000})
			impChart.set_size({'x_scale': 2, 'y_scale': 2})
			self.createImpMagChart(impChart, 0, startCol)
			self.data.insert_chart(to_excel_coord(DATA_OFFSET+15, startCol + 12), impChart)


			smithChart = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
			smithChart.set_legend({'position': 'bottom'})
			smithChart.set_size({'x_scale': 2, 'y_scale': 2})
			self.createSmithChart(smithChart, 0, startCol)
			self.data.insert_chart(to_excel_coord(DATA_OFFSET+15, startCol + 1), smithChart)

			self.createImpMagChart(impSummaryChart, 0, startCol)
			self.createSmithChart(smithSummaryChart, 0, startCol)
			nextCol += 1
			i += 1

		self.summary.insert_chart(to_excel_coord(DATA_OFFSET+15, 5), impSummaryChart)
		self.summary.insert_chart(to_excel_coord(DATA_OFFSET+15, 25), smithSummaryChart)

		#self.summary.autofilter('A%d:AW%d' % (1, len(datas) + 1))

	def generateDataAuxData(self, row, col):
		order = (col / 37) + 1
		l = to_excel_coord(L_ROW_OFFSET, col + L_COL_OFFSET)
		l_air = to_excel_coord(L_OTHER_ROW_OFFSET, col + L_OTHER_COL_OFFSET)
		r = to_excel_coord(R_ROW_OFFSET, col + R_COL_OFFSET)
		c = to_excel_coord(C_ROW_OFFSET, col + C_COL_OFFSET)
		k = to_excel_coord(K_ROW_OFFSET, col + K_COL_OFFSET)
		self.data.write_string(NORMALIZED_FACTOR_ROW_OFFSET, col + NORMALIZED_FACTOR_COL_OFFSET - 1, 'Normalizing Factor', self.warningFormat)
		self.data.write_formula(NORMALIZED_FACTOR_ROW_OFFSET, col + NORMALIZED_FACTOR_COL_OFFSET, "='{summary_sheet}'!AJ{n_factor}".format(summary_sheet = self.summary.get_name(), n_factor = order+1), self.warningFormat)

		self.data.write_string(L_OTHER_ROW_OFFSET, col + L_OTHER_COL_OFFSET - 1, 'L from Air', self.warningFormat)
		self.data.write_formula(L_OTHER_ROW_OFFSET, col + L_OTHER_COL_OFFSET, "='{summary_sheet}'!AF{lm_air}".format(summary_sheet = self.summary.get_name(), lm_air = order+1), self.warningFormat)

		self.data.write_string(D_TOT_ROW_OFFSET, col + D_TOT_COL_OFFSET - 1, 'Damping', self.warningFormat)
		self.data.write_formula(D_TOT_ROW_OFFSET, col + D_TOT_COL_OFFSET, "=1/({r}*{c})".format(r = r, c = c), self.warningFormat)

		self.data.write_string(LS_CAL_ROW_OFFSET, col + LS_CAL_COL_OFFSET - 1, 'Lp_cal', self.warningFormat)
		self.data.write_formula(LS_CAL_ROW_OFFSET, col + LS_CAL_COL_OFFSET, '={l}*1/{k}^2*PI()^2/8'.format(l = l_air, k = k), self.warningFormat)

		R = "'{summary_sheet}'!S{r}".format(summary_sheet = self.summary.get_name(), r = order+1)
		Reff = to_excel_coord(R_EFF_ROW_OFFSET, col + R_EFF_COL_OFFSET)
		C = '1/({l}*{fr}^2*PI()^2*4)'.format(l = l_air, fr=to_excel_coord(FR_EXP_ROW_OFFSET, col + FR_EXP_COL_OFFSET))
		Q_exp = "'{summary_sheet}'!BG{q}".format(summary_sheet = self.summary.get_name(), q = order+1)
		Q_exp_adj = "'{summary_sheet}'!BJ{q}".format(summary_sheet = self.summary.get_name(), q = order+1)
		Fr = "'{summary_sheet}'!W{fr}".format(summary_sheet = self.summary.get_name(), fr = order+1)

		self.data.write_string(R_EFF_ROW_OFFSET, col + R_EFF_COL_OFFSET - 1, 'Reff', self.warningFormat)
		self.data.write_formula(R_EFF_ROW_OFFSET, col + R_EFF_COL_OFFSET, "={r}-{rm}".format(rm=to_excel_coord(RM_ROW_OFFSET, col + RM_COL_OFFSET), r = r), self.warningFormat)

		self.data.write_string(RM_ROW_OFFSET, col + RM_COL_OFFSET - 1, 'R-', self.inputFormat)
		self.data.write_number(RM_ROW_OFFSET, col + RM_COL_OFFSET, 0, self.inputFormat)

		self.data.write_string(R_ROW_OFFSET, col + R_COL_OFFSET - 1, 'Rm', self.warningFormat)
		self.data.write_formula(R_ROW_OFFSET, col + R_COL_OFFSET, "=" + R, self.warningFormat)
		
		self.data.write_string(L_ROW_OFFSET, col + L_COL_OFFSET - 1, 'Lm', self.warningFormat)
		#self.data.write_formula(L_ROW_OFFSET, col + L_COL_OFFSET, "=sqrt(1/({Fr})^2 * (({R})/({Q_exp})^2)".format(Fr = Fr, R = R, Q_exp = Q_exp), self.inputFormat)
		self.data.write_formula(L_ROW_OFFSET, col + L_COL_OFFSET, "=sqrt(1/({Fr}*2*pi())^2 * (({R})/({Q_exp}))^2)".format(Fr = Fr, R = Reff, Q_exp = Q_exp_adj), self.warningFormat)
		
		self.data.write_string(C_ROW_OFFSET, col + C_COL_OFFSET - 1, 'Cm', self.warningFormat)
		self.data.write_formula(C_ROW_OFFSET, col + C_COL_OFFSET, "=" + C, self.warningFormat)

		self.data.write_string(LC_ROW_OFFSET, col + LC_COL_OFFSET - 1, 'Lc', self.warningFormat)
		self.data.write_formula(LC_ROW_OFFSET, col + LC_COL_OFFSET, '=AVERAGE({start}:{end})'.format(start=to_excel_coord(DATA_OFFSET+2, col + 11), end=to_excel_coord(DATA_OFFSET+2+801, col + 11)), self.warningFormat)

		self.data.write_string(K_ROW_OFFSET, col + K_COL_OFFSET - 1, 'k', self.inputFormat)
		self.data.write_number(K_ROW_OFFSET, col + K_COL_OFFSET, 0.24, self.inputFormat)

		self.data.write_string(Q_EXP_ROW_OFFSET, col + Q_EXP_COL_OFFSET - 1, 'Q_exp', self.warningFormat)
		self.data.write_formula(Q_EXP_ROW_OFFSET, col + Q_EXP_COL_OFFSET, "=" + Q_exp, self.warningFormat)

		self.data.write_string(Q_EXP_ADJ_ROW_OFFSET, col + Q_EXP_ADJ_COL_OFFSET - 1, 'Q_exp_adj', self.warningFormat)
		self.data.write_formula(Q_EXP_ADJ_ROW_OFFSET, col + Q_EXP_ADJ_COL_OFFSET, "=" + Q_exp_adj, self.warningFormat)

		self.data.write_string(Q_ROW_OFFSET, col + Q_COL_OFFSET - 1, 'Q', self.warningFormat)
		self.data.write_formula(Q_ROW_OFFSET, col + Q_COL_OFFSET, '={r}*SQRT({c}/{l})'.format(r = Reff, l = l_air, c = c), self.warningFormat)

		self.data.write_string(FR_EXP_ROW_OFFSET, col + FR_EXP_COL_OFFSET - 1, 'Fr_exp', self.warningFormat)
		self.data.write_formula(FR_EXP_ROW_OFFSET, col + FR_EXP_COL_OFFSET, "=" + Fr, self.warningFormat)

	def generateSummaryData(self, dataRow, dataCol):
		order = (dataCol /37) + 1
		r = to_excel_coord(R_ROW_OFFSET, dataCol + R_COL_OFFSET)
		l = to_excel_coord(L_ROW_OFFSET, dataCol + L_COL_OFFSET)
		rm = to_excel_coord(RM_ROW_OFFSET, dataCol + RM_COL_OFFSET)
		c = to_excel_coord(C_ROW_OFFSET, dataCol + C_COL_OFFSET)
		ls = to_excel_coord(LS_CAL_ROW_OFFSET, dataCol + LS_CAL_COL_OFFSET)
		k = to_excel_coord(K_ROW_OFFSET, dataCol + K_COL_OFFSET)
		lc = to_excel_coord(LC_ROW_OFFSET, dataCol + LC_COL_OFFSET)
		self.summary.write_formula('AC%d' % (order + 1), "='{data_sheet}'!{r}".format(data_sheet = self.data.get_name(), r = r))
		self.summary.write_formula('AD%d' % (order + 1), "='{data_sheet}'!{rm}".format(data_sheet = self.data.get_name(), rm = rm))
		self.summary.write_formula('AE%d' % (order + 1), "='{data_sheet}'!{l}".format(data_sheet = self.data.get_name(), l = l))
		self.summary.write_formula('AF%d' % (order + 1), "=AE%d" % (order + 1))
		self.summary.write_formula('AG%d' % (order + 1), "='{data_sheet}'!{c}".format(data_sheet = self.data.get_name(), c = c))
		self.summary.write_formula('AI%d' % (order + 1), "='{data_sheet}'!{ls}".format(data_sheet = self.data.get_name(), ls = ls))
		self.summary.write_formula('AH%d' % (order + 1), "='{data_sheet}'!{k}".format(data_sheet = self.data.get_name(), k = k))
		self.summary.write_formula('AT%d' % (order + 1), "='{data_sheet}'!{lc}".format(data_sheet = self.data.get_name(), lc = lc))
		self.summary.write_formula('AB%d' % (order + 1), "={fr}/({f1}-{f0})".format(fr = 'W%d' % (order + 1), f0 = 'Y%d' % (order + 1), f1 = 'AA%d' % (order + 1)))

		self.summary.write_formula('AK%d' % (order + 1), "=1/{one_over_n_factor}".format(one_over_n_factor = 'AJ%d' % (order + 1)))
		self.summary.write_formula('AM%d' % (order + 1), "=SQRT({one_over_n_factor})".format(one_over_n_factor = 'AJ%d' % (order + 1)))
		self.summary.write_formula('AN%d' % (order + 1), "=1/{one_over_n_factor}".format(one_over_n_factor = 'AM%d' % (order + 1)))
		self.summary.write_formula('AK%d' % (order + 1), "={one_over_n_factor}*{ls_cal}".format(one_over_n_factor = 'AJ%d' % (order + 1), ls_cal = 'AI%d' % (order + 1)))
		self.summary.write_formula('AP%d' % (order + 1), "={lm}*{one_over_n_factor}".format(lm = 'AE%d' % (order + 1), one_over_n_factor = 'AJ%d' % (order + 1)))
		
		self.summary.write_formula('AQ%d' % (order + 1), "={cm}*1/{one_over_n_factor}".format(cm = 'AG%d' % (order + 1), one_over_n_factor = 'AJ%d' % (order + 1)))
		self.summary.write_formula('AR%d' % (order + 1), "={rm}*{one_over_n_factor}".format(rm = 'AC%d' % (order + 1), one_over_n_factor = 'AJ%d' % (order + 1)))
		self.summary.write_formula('AS%d' % (order + 1), "=1/({cm_nor}*{rm_nor})".format(cm_nor = 'AQ%d' % (order + 1), rm_nor = 'AR%d' % (order + 1)))
		self.summary.write_formula('AY%d' % (order + 1), "=AT%d*R%d*10^-3*K%d" % (order + 1, order + 1, order + 1))
		self.summary.write_formula('AV%d' % (order + 1), "=AI%d/AY%d" % (order + 1, order + 1))
		self.summary.write_formula('K%d' % (order + 1), "=J%d/I%d" % (order + 1, order + 1))
		self.summary.write_formula('J%d' % (order + 1), "=0.030*Q%d" % (order + 1))
		self.summary.write_formula('AU%d' % (order + 1), "=0.030*Q%d" % (order + 1))
		self.summary.write_formula('BG%d' % (order + 1), "={fr}/({f1}-{f0})".format(fr = 'W%d' % (order + 1), f0 = 'BE%d' % (order + 1), f1 = 'BF%d' % (order + 1)))
		self.summary.write_formula('BJ%d' % (order + 1), "={fr}/({f1}-{f0})".format(fr = 'V%d' % (order + 1), f0 = 'BH%d' % (order + 1), f1 = 'BI%d' % (order + 1)))
		self.summary.write_formula('BM%d' % (order + 1), "={fr}/({f1}-{f0})".format(fr = 'V%d' % (order + 1), f0 = 'BK%d' % (order + 1), f1 = 'BJ%d' % (order + 1)))

	def createImpMagChart(self, chart, dataRow, dataCol):
		# subtracted
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 12, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 12, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 17, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 17, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 12, row_abs = True, col_abs = True)),
			'line':	   {'color': 'red'},
		})
		# calculated
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 18, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 18, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 23, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 23, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 18, row_abs = True, col_abs = True)),
			'line':	   {'color': 'blue'},
		})
		# subtracted normalized
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 24, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 24, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 29, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 29, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 24, row_abs = True, col_abs = True)),
			'line':	   {'color': 'cyan'},
		})
		# calculated normalized
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 30, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 30, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 35, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 35, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 30, row_abs = True, col_abs = True)),
			'line':	   {'color': 'green'},
		})

	def createSmithChart(self, chart, dataRow, dataCol):
		# subtracted
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 13, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 13, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 14, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 14, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 12, row_abs = True, col_abs = True)),
			'line':	   {'color': 'red'},
		})
		# calculated
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 19, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 19, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 20, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 20, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 18, row_abs = True, col_abs = True)),
			'line':	   {'color': 'blue'},
		})
		# subtracted normalized
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 25, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 25, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 26, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 26, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 24, row_abs = True, col_abs = True)),
			'line':	   {'color': 'cyan'},
		})
		# calculated normalized
		chart.add_series({
			'categories': "='{data_sheet}'!{freq_start}:{freq_end}".format(data_sheet = self.data.get_name(), freq_start = to_excel_coord(DATA_OFFSET+2, dataCol + 31, row_abs = True, col_abs = True), freq_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 31, row_abs = True, col_abs = True)),
			'values':	 "='{data_sheet}'!{imp_mag_start}:{imp_mag_end}".format(data_sheet = self.data.get_name(), imp_mag_start = to_excel_coord(DATA_OFFSET+2, dataCol + 32, row_abs = True, col_abs = True), imp_mag_end = to_excel_coord(DATA_OFFSET+2+801, dataCol + 32, row_abs = True, col_abs = True)),
			'name':		"='{data_sheet}'!{header}".format(data_sheet = self.data.get_name(), header = to_excel_coord(DATA_OFFSET, dataCol + 30, row_abs = True, col_abs = True)),
			'line':	   {'color': 'green'},
		})

	def write(self):
		self.workbook.close()

if __name__ == "__main__":
	p = FileProcessor('test.xlsx')
	p.setData([8544, 8507, 8470, 8433])
	p.write()