#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_wtf import Form
from wtforms import DateField, SelectField, FileField, HiddenField, TextAreaField, BooleanField, IntegerField, FloatField, TextField, PasswordField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from db.schema import ExpPatchInfo, ExpACCoilProp, ExpDCCoilProp
from db.schema import session

class ExpInfoForm(Form):
    id = HiddenField(
    	id='id'
    )
    '''
    ac_coil_id = QuerySelectField(
        label=u'AC 코일', 
        id='ac_coil_id', 
        query_factory = session.query(ExpACCoilProp).order_by(ExpACCoilProp.id),
        get_pk = lambda info: info.id,
        get_label = lambda info: ('#%d - %.2fx%.2fx%.2f (%s) (%dturn of %.2fmm wire)' % \
            (info.id, info.width, info.height, info.length, info.typeAsString, info.turn, info.wire_diameter))
    )
    dc_coil_id = QuerySelectField(
        label=u'DC 코일', 
        id='dc_coil_id', 
        query_factory = session.query(ExpDCCoilProp).order_by(ExpDCCoilProp.id),
        get_pk = lambda info: info.id,
        get_label = lambda info: ('#%d - %.1fR (%dturn of %.2fmm wire)' % \
            (info.id, info.radius, info.turn, info.wire_diameter))
    )
    patch_id = QuerySelectField(
        label=u'패치', 
        id='patch_id',
        query_factory = session.query(ExpPatchInfo).order_by(ExpPatchInfo.patch_id),
        get_pk = lambda info: info.patch_id,
        get_label = lambda info: ('#%d - %s %.2fx%.2f (%s)' % \
            (info.id, info.name, info.width, info.height, info.grainAsString))
    )
    '''
    ac_coil_id = QuerySelectField(
        label=u'AC 코일', 
        id='ac_coil_id', 
        query_factory = session.query(ExpACCoilProp).order_by(ExpACCoilProp.id).all,
        get_pk = lambda info: info.id,
        get_label = lambda info: ('#%d - %.2fx%.2fx%.2f (%s) (%dturn of %.2fmm wire)' % \
            (info.id, info.width, info.height, info.length, info.typeAsString, info.turn, info.wire_diameter))

    )
    dc_coil_id = QuerySelectField(
        label=u'DC 코일', 
        id='dc_coil_id', 
        query_factory = session.query(ExpDCCoilProp).order_by(ExpDCCoilProp.id).all,
        get_pk = lambda info: info.id,
        get_label = lambda info: ('#%d - %.1fR (%dturn of %.2fmm wire)' % \
            (info.id, info.radius, info.turn, info.wire_diameter))
    )
    patch_id = QuerySelectField(
        label=u'패치', 
        id='patch_id',
        query_factory = session.query(ExpPatchInfo).order_by(ExpPatchInfo.patch_id).all,
        get_pk = lambda info: info.patch_id,
        get_label = lambda info: ('#%d - %s %.2fx%.2f (%s)' % \
            (info.patch_id, info.name, info.width, info.height, info.grainAsString))
    )

    exp_date_submit = DateField(
    	format='%Y-%m-%d',
    	validators = [
    		validators.InputRequired()
    	]
    )

    exp_date = TextField(
    	label = u'실험 날짜', 
    	id='exp_date', 
    	validators = [
    		validators.InputRequired()
    	]
    )

    dc_current = FloatField(
    	label=u'DC 필드 전류 (I)', 
    	id='dc_current', 
    	validators = [ 
    		validators.InputRequired()
    	]
    )
    

    dc_field = FloatField(
    	label=u'계측된 필드 (Oe)', 
    	id='dc_field', 
    	validators = [ 
    		validators.InputRequired()
    	]
    )

    comment = TextAreaField(
    	label=u'메모', 
    	id='comment'
    )

    source_power = IntegerField(
        label=u'소스파워 (dBm)', 
        id='source_power',
        validators = [ 
            validators.InputRequired()
        ]
    )

    center_freq = IntegerField(
        label=u'센터주파수 (Hz)', 
        id='center_freq',
        validators = [ 
            validators.InputRequired()
        ]
    )

    freq_span = IntegerField(
        label=u'스팬 (Hz)', 
        id='freq_span',
        validators = [ 
            validators.InputRequired()
        ]
    )