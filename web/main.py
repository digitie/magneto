#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, render_template, send_file, jsonify, abort
from werkzeug import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_wtf.csrf import CsrfProtect
import datetime
import hashlib
import os
from time import sleep

from db.schema import Exp, ExpSmith, ExpSmithStats, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchInfo, ExpMaterialProp
from db.schema import exp, exp_smith, exp_smith_stats, exp_vna, exp_ac_coil_prop, exp_dc_coil_prop, exp_patch_prop, exp_material_prop
from db.schema import session
import cStringIO
from sqlalchemy import func, desc
from sqlalchemy.sql import or_

from core import json

from form import ExpInfoForm
import chart
import numpy as np

from instruments.gpib import prologix
from instruments.vna import HP8751A, FrequencySweepModes

from core.listobject import *

na = None
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

def MainLoop(debug, port = '\\.\COM7'):
	global na
	plx = prologix(port = port)
	na = HP8751A(plx, 17, delay = 0.05, auto = False)
	app.run(host='0.0.0.0')
	app.debug = debug

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
CsrfProtect(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	print(request.files)
	if request.method == 'POST':
		file = request.files['Filedata']
		filename = secure_filename(file.filename)
		print(filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#f.save('/var/www/uploads/uploaded_file.txt')
		return "1"

@app.route('/exp/list')
def exp_list():
	return render_template('list.html')

@app.route('/exp/view/vna')
def exp_view_vna():
	return render_template('vnaview.html')

@app.route('/exp/view')
def exp_view():
	exp_ids = request.args.getlist('exp_ids', None)
	return render_template('view.html', exp_ids = exp_ids)

@app.route('/exp/preview')
def exp_preview():
	exp_id = request.args.get('exp_id', None)
	return render_template('preview.html', exp_ids = [exp_id])

@app.route('/api/exp/delete')
def delete_exp():
	exp_ids = request.args.getlist('exp_id', None)
	if not exp_ids:
		abort(404)
	exp_ids = map(int, exp_ids)
	deleteExps(exp_ids)

FLOAT_SEARCHABLES = ['patch_width', 'patch_length', 'dc_current', 'dc_field', 'imp_re']

@app.route('/api/exp/list')
def get_exp_list():
	d = {}
	start = int(request.args.get('iDisplayStart', '0'))
	length = int(request.args.get('iDisplayLength', '12'))
	all_search_keyword = request.args["sSearch"]
	sort_cols = []
	search_cols = []
	if "iSortCol_0" in request.args:	
		for i in range(int(request.args['iSortingCols'])):
			sort_col = int(request.args["iSortCol_%d" % (i)])
			sort_name = request.args["mDataProp_%d" % (sort_col)]
			sort_order = request.args["sSortDir_%d" % (i)]
			is_sortable = bool(request.args['bSortable_%d' % (sort_col)] == 'true')
			if is_sortable:
				col = getColumnByName([Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpPatchInfo, ExpSmith], sort_name)
				if col:
					sort_cols.append([col, sort_order])

	for i in range(int(request.args['iColumns'])):
		is_searchable = bool(request.args['bSearchable_%d' % (i)].lower() == 'true')
		searchable_name = request.args["mDataProp_%d" % (i)]
		if not all_search_keyword:
			search_keyword = request.args["sSearch_%d" % (i)]
		else:
			search_keyword = all_search_keyword

		if is_searchable and search_keyword:
			col = getColumnByName([Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpPatchInfo, ExpSmith], searchable_name)
			if col:
				if searchable_name in FLOAT_SEARCHABLES:
					try:
						search_keyword = float(search_keyword)
					except ValueError:
						continue

					search_cols.append([col, search_keyword])
				else:
					search_cols.append([col, search_keyword])


	total_count = session.query(func.count('*')).select_from(Exp).scalar()
	q = getAllExpsQuery()
	if all_search_keyword:
		all_search_fields = []
		for col in search_cols:
			all_search_fields.append(col[0] == col[1])
		q = q.filter(or_(*all_search_fields))
		#print q
	else:
		for col in search_cols:
			if str(col[0].type) == 'DATE':
				try:
					col[1] = datetime.datetime.strptime(col[1], "%Y-%m-%d").date()
				except ValueError:
					continue
			q = q.filter(col[0] == col[1])
	for col in sort_cols:
		if col[1] == "desc":
			q = q.order_by(desc(col[0]))
		else:
			q = q.order_by(col[0])

	q = q.offset(start).limit(start + length).all()
	d['sEcho'] = int(request.args.get('sEcho', '1'))
	d['iTotalRecords'] = total_count
	d['iTotalDisplayRecords'] = total_count
	d['aaData'] = []
	for exp, exp_vna, exp_dc_coil, exp_ac_coil, patch, exp_smith in q:
		d['aaData'].append(
				{ 
					'detail': '<img src="/static/img/details_open.png">',
					'ac_coil_id': exp_ac_coil.id,
					'dc_coil_id': exp_dc_coil.id,
					'exp_date': exp.exp_date.strftime('%Y-%m-%d'),
					'patch_material': patch.name,
					'patch_width': patch.width,
					'patch_height': patch.height,
					'dc_current': exp.dc_current,
					'dc_field': round(exp.dc_field, 3),
					'comment': exp.comment,
					'if_bandwidth': exp_vna.if_bandwidth,
					'number_of_points': exp_vna.number_of_points,
					'sweep_type': exp_vna.sweep_type,
					'channel': exp_vna.channel,
					'source_power': exp_vna.source_power,
					'measure_type': exp_vna.measure_type,
					'sweep_time': exp_vna.sweep_time,
					'imp_re': round(exp_smith.imp_re, 3),
					'freq': round(float(exp_smith.freq) / 1000, 3) ,
					'id': exp.id
				}
			) 

	response = make_response(jsonify(d))
	response.headers['Content-Type'] = 'application/json'
	return response

@app.route('/exp/plot/ar_resonance')
def exp_ar_vs_resonance():
	exp_ids = request.args.getlist('exp_id', None)
	if not exp_ids:
		abort(404)

	buf = chart.draw_ar_vs_f(exp_ids)

	return send_file(buf,
		mimetype="image/png",
		attachment_filename="ar_vs_resonance.png",
		as_attachment=True)

@app.route('/exp/plot/ar_imp_re')
def exp_ar_vs_imp_re():
	exp_ids = request.args.getlist('exp_id', None)
	if not exp_ids:
		abort(404)

	buf = chart.draw_ar_vs_imp_re(exp_ids)

	return send_file(buf,
		mimetype="image/png",
		attachment_filename="ar_imp_re.png",
		as_attachment=True)

@app.route('/exp/plot/field_resonance')
def exp_field_vs_resonance():
	exp_ids = request.args.getlist('exp_id', None)
	if not exp_ids:
		abort(404)

	buf = chart.draw_dc_field_vs_f(exp_ids)

	return send_file(buf,
		mimetype="image/png",
		attachment_filename="testing.png",
		as_attachment=True)

@app.route('/exp/plot/freq_re')
def exp_f_vs_re():
	exp_ids = request.args.getlist('exp_id', None)
	if not exp_ids:
		abort(404)
	
	datas = getImpedanceData(exp_ids, 're')
	buf = chart.draw_f_vs_imp_re(datas)

	return send_file(buf,
		mimetype="image/png",
		attachment_filename="testing.png",
		as_attachment=True)


@app.route('/exp/plot/freq_re/vna')
def exp_f_vs_re_vna():	
	srcpwr = request.args.get('srcpwr', '0')
	center_freq = request.args.get('center_freq', 100000)
	freq_span = request.args.get('freq_span', 20000)
	datas = []


	na.source_power = int(srcpwr)	
	#na.find_center_freq()
	na.sweep_mode = FrequencySweepModes.SINGLE
	#na.set_num_of_points(201)

	na.set_frequency_span(center = float(center_freq), span = float(freq_span))
	freq, im, re, imp_re, imp_im = na.read_impedance()	
	freq = np.array(freq)
	imp_re = np.array(imp_re)
	imp_re = imp_re * 50


	data = MplXYPlotData()
	data.x = freq
	data.y = imp_re
	data.set_legend('Source Power = %s' % (srcpwr))
	buf = chart.draw_f_vs_imp_re([data])

	filename = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
	na.sweep_mode = FrequencySweepModes.CONTINUOUS

	return send_file(buf,
		mimetype="image/png",
		attachment_filename=filename + ".png", cache_timeout = 0,
		as_attachment=True)

@app.route('/api/exp/data/freq_re/vna')
def exp_data_f_vs_re_vna():	
	srcpwr = request.args.get('srcpwr', '0')
	datas = []

	na.source_power = int(srcpwr)	
	#na.find_center_freq()
	na.sweep_mode = FrequencySweepModes.SINGLE
	#na.set_num_of_points(201)
	freq, im, re, imp_re, imp_im = na.read_impedance()
	imp_re = imp_re * 50

	for data in zip(freq, imp_re):
		datas.append([data[0], data[1]])

	na.sweep_mode = FrequencySweepModes.CONTINUOUS

	resp = make_response(jsonify(json.make_json_data(datas)))
	resp.status_code = 200

	return resp

@app.route('/exp/plot/smithchart/vna')
def smithchart_vna():
	srcpwr = request.args.get('srcpwr', '0')
	datas = []
	data = []
	na.set_source_power(int(srcpwr))	
	#na.find_center_freq()
	#na.set_num_of_points(201)
	freq, im, re, imp_re, imp_im = na.read_impedance()	
	for item in zip(imp_re, imp_im):		

		data.append(item[0] + item[1] * 1j)
	data = np.array(data)
	datas.append(data)
	buf = chart.draw_smithchart(datas)

	filename = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")

	return send_file(buf,
		mimetype="image/png",
		attachment_filename=filename+".png", cache_timeout = 0,
		as_attachment=True)

@app.route('/exp/plot/smithchart')
def smithchart():
	exp_ids = request.args.getlist('exp_id', None)
	if not exp_ids:
		abort(404)

	datas = getExpSmithByExpIds(exp_ids)
	buf = chart.draw_smithchart(datas)

	return send_file(buf,
		mimetype="image/png",
		attachment_filename="testing.png",
		as_attachment=True)

@app.route('/api/exp/vna', methods=['GET'])
def vna():
	method = request.args.get('method', 'init')


	resp = jsonify({})
	resp.status_code = 200

	return resp

@app.route('/exp/insert', methods=['GET', 'POST'])
def insert_data():
	exp_id = request.args.get('exp_id', None)
	if exp_id:
		exp = session.query(Exp).filter(Exp.id == exp_id).first()
		form = ExpInfoForm(request.form, exp)
	else:
		form = ExpInfoForm(request.form)
		na.source_power = 7
		center_freq = int(na.find_center_freq())
		form.center_freq.data = center_freq
		form.freq_span.data = int(20000)

	if request.method == "POST" and form.validate():
		if form.id.data:
			exp = session.query(Exp).filter(Exp.id == int(form.id.data)).first()
			exp.ac_coil_id = form.ac_coil_id.data
			exp.dc_coil_id = form.dc_coil_id.data
			exp.patch_id = form.patch_id.data
			exp.exp_date = form.exp_date_submit.data
			exp.dc_current = form.dc_current.data
			exp.dc_field = form.dc_field.data
			exp.comment = form.comment.data
		else:
			exp = Exp(
				ac_coil_id = form.ac_coil_id.data.id,
				dc_coil_id = form.dc_coil_id.data.id,
				patch_id = form.patch_id.data.patch_id,
				exp_date = form.exp_date_submit.data,
				dc_current = form.dc_current.data,
				dc_field = form.dc_field.data,
				comment = form.comment.data
			)
		session.add(exp)
		session.flush()

		vna_data = []
		na.source_power = form.source_power.data
		#na.find_center_freq()

		na.set_frequency_span(center = form.center_freq.data, span = form.freq_span.data)
		na.autoscale()
		na.num_of_points = 801
		na.sweep_mode = FrequencySweepModes.SINGLE
		sleep(0.5)
		freq, re, im, imp_re, imp_im = na.read_impedance()
		for freq, re, im in zip(freq, re, im):
			smith = ExpSmith(exp.id, freq, re, im)
			vna_data.append(smith)

		vna_properties = ExpVNA(
			exp.id,
			float(0), 
			na.num_of_points, 
			'SMITH CHART', 
			na.sweep_type, 
			int(1), 
			float(form.source_power.data), 
			'A/R', 
			float(na.sweep_time) * 100
		)
		session.add(vna_properties)
		session.add_all(vna_data)
		session.commit()
		na.sweep_mode = FrequencySweepModes.CONTINUOUS

		resp = make_response(
			jsonify(
				json.make_json_data(
					{'id': exp.id}
				)
			)
		)
		resp.status_code = 200

		return resp

	na.sweep_mode = FrequencySweepModes.CONTINUOUS
	return render_template('insert.html', form=form)
'''
@app.route('/update')
def update():
	now = datetime.datetime.now()
	ret = now.strftime("%Y%m%dT%H%M%S")
	ret_hash = hashlib.md5(ret.encode()).hexdigest()
	response = make_response(ret)
	response.headers.add("ETag", ret_hash)
	if request.headers.get('If-None-Match') == ret_hash:
		xheader = '{"timeout":"5000"}'
		response.headers.add("X-Smartupdater", xheader)
	else:
		xheader = '{"timeout":"1000"}'
		response.headers.add("X-Smartupdater", xheader)
	return response

if __name__ == "__main__":
	app.run()
'''