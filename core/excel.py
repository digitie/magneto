import string
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

'''
import re


MAX_ROW = 65536
MAX_COL = 256
_re_cell_ex = re.compile(r"(\$?)([A-I]?[A-Z])(\$?)(\d+)", re.IGNORECASE)
'''


'''
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
'''

def col_by_name(colname):
	"""'A' -> 0, 'Z' -> 25, 'AA' -> 26, etc
	"""
	col = 0
	power = 1
	for i in xrange(len(colname)-1, -1, -1):
		ch = colname[i]
		col += (ord(ch) - ord('A') + 1) * power
		power *= 26
	return col - 1

def cell_to_rowcol(cell):
	"""Convert an Excel cell reference string in A1 notation
	to numeric row/col notation.
	Returns: row, col, row_abs, col_abs
	"""
	m = _re_cell_ex.match(cell)
	if not m:
		raise Exception("Ill-formed single_cell reference: %s" % cell)
	col_abs, col, row_abs, row = m.groups()
	row_abs = bool(row_abs)
	col_abs = bool(col_abs)
	row = int(row) - 1
	col = col_by_name(col.upper())
	return row, col, row_abs, col_abs


def rowcol_to_cell(row, col, row_abs=False, col_abs=False):
	"""Convert numeric row/col notation to an Excel cell reference string in
	A1 notation.
	"""
	assert 0 <= row < MAX_ROW # MAX_ROW counts from 1
	assert 0 <= col < MAX_COL # MAX_COL counts from 1
	d = col // 26
	m = col % 26
	chr1 = "" # Most significant character in AA1
	if row_abs:
		row_abs = '$'
	else:
		row_abs = ''
	if col_abs:
		col_abs = '$'
	else:
		col_abs = ''
	if d > 0:
		chr1 = chr(ord('A') + d - 1)
	chr2 = chr(ord('A') + m)
	# Zero index to 1-index
	return col_abs + chr1 + chr2 + row_abs + str(row + 1)

class Cell(object):
	def __init__(self, row, col, value, row_abs=False, col_abs=False):
		self.row = row
		self.col = col
		self.row_abs = row_abs
		self.col_abs = col_abs
		self.value = value

	@property
	def cell(self):
		return xl_rowcol_to_cell(self.row, self.col, self.row_abs, self.col_abs)

	def __repr__(self):
		return "<{cell} {value}>".format(cell = self.cell, value = self.value)

class CellGroup(object):
	def add_header(self, title, title_format, data_format):
		self.__headers = {}
		self.__headers[title] = {
			'title_format' : title_format,
			'data_format' : data_format,
			'data' : []
		}


print xl_rowcol_to_cell(14, 14, True, True)
#print cell_to_rowcol('o15')

print Cell(14, 14, None, True, True)