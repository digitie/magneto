#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO

import smithplot
from matplotlib.figure import Figure					  
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import itertools as it

from core.listobject import *

CHART_COLORS = ('b','g','r','c','m','y','k','w',)

def draw_dc_field_vs_f(exp_ids = []):	
	datas = getDCFieldVsFrequency(exp_ids)

	fig = Figure(figsize=[8, 8])
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlabel('DC Field [Oe]')
	ax.set_ylabel('Resonant Frequency [Hz]')


	for data, color in zip(tuple(datas), it.cycle(CHART_COLORS)):
		ax.plot(data.get_x(), data.get_y(), color)
		ax.plot(data.get_x(), data.get_y(), color + '^', label = data.get_legend(), picker=5)  

	ax.legend(framealpha=0, prop={'size':8})
	ax.ticklabel_format(useOffset=False)
		
	canvas = FigureCanvasAgg(fig)
	buf = cStringIO.StringIO()
	canvas.print_png(buf)
	buf.seek(0)

	return buf

def draw_ar_vs_f(exp_ids = []):	
	datas = getPatchARVsFrequency(exp_ids)

	fig = Figure(figsize=[8, 8])
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlabel('Aspect Ratio')
	ax.set_ylabel('Resonant Frequency [Hz]')
	for data, color in zip(tuple(datas), it.cycle(CHART_COLORS)):
		ax.plot(data.get_x(), data.get_y(), color)
		ax.plot(data.get_x(), data.get_y(), color + '^', label = data.get_legend(), picker=5)  

	ax.legend(framealpha=0, prop={'size':8})
	ax.ticklabel_format(useOffset=False)
	canvas = FigureCanvasAgg(fig)
	buf = cStringIO.StringIO()
	canvas.print_png(buf)
	buf.seek(0)

	return buf

def draw_ar_vs_imp_re(exp_ids = []):	
	datas = getPatchARVsImpedance(exp_ids)

	fig = Figure(figsize=[8, 8])
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlabel('Aspect Ratio')
	ax.set_ylabel('Re(z) [Ohm]')
	for data, color in zip(tuple(datas), it.cycle(CHART_COLORS)):
		ax.plot(data.get_x(), data.get_y(), color)
		ax.plot(data.get_x(), data.get_y(), color + '^', label = data.get_legend())  

	ax.legend(framealpha=0, prop={'size':8})
	ax.ticklabel_format(useOffset=False)
	canvas = FigureCanvasAgg(fig)
	buf = cStringIO.StringIO()
	canvas.print_png(buf)
	buf.seek(0)

	return buf

def draw_f_vs_imp_re(datas):
	fig = Figure(figsize=[8, 8])
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlabel('Resonant Frequency [Hz]')
	ax.set_ylabel('Re(z) [Ohm]')
	for data, color in zip(tuple(datas), it.cycle(CHART_COLORS)):
		ax.plot(data.get_x(), data.get_y(), color, label = data.get_legend())
	ax.legend(framealpha=0, prop={'size':8})
	canvas = FigureCanvasAgg(fig)
	buf = cStringIO.StringIO()
	canvas.print_png(buf)
	buf.seek(0)

	return buf

def draw_smithchart(datas = []):
	fig = Figure(figsize=[8, 8])
	ax = fig.add_subplot(1, 1, 1, projection='smith', axes_norm=50)

	#val1 = data[:, 1] + data[:, 2] * 1j
	for data, color in zip(tuple(datas), it.cycle(CHART_COLORS)):
		ax.plot(data, color, markevery=1000, label="S11")
	canvas = FigureCanvasAgg(fig)
	buf = cStringIO.StringIO()
	canvas.print_png(buf)
	buf.seek(0)

	return buf