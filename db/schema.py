# -*- coding: utf-8 -*-

# to workaround sqlalchemy's get_characterset_info bug, which only applies to py2k.
#import mysql.connector
#mysql.connector.MySQLConnection.get_characterset_info=lambda cls:cls.charset

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from sqlalchemy.ext import compiler
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
#import pystaggrelite3

Base = declarative_base()
meta = MetaData()


class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable

class DropView(DDLElement):
    def __init__(self, name):
        self.name = name
    
@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (element.name, compiler.sql_compiler.process(element.selectable)) 

@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return "DROP VIEW %s" % (element.name)


def view(name, metadata, selectable):
    t = table(name)
    
    for c in selectable.c:
        c._make_proxy(t)
    
    CreateView(name, selectable).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
    return t

def on_connect(dbapi_conn, connection_rec):
    '''
    dbapi_conn.create_aggregate("stdev", 1, pystaggrelite3.stdev)
    dbapi_conn.create_aggregate("stdevp", 1, pystaggrelite3.stdevp)
    dbapi_conn.create_aggregate("var", 1, pystaggrelite3.var)
    dbapi_conn.create_aggregate("varp", 1, pystaggrelite3.varp)
    dbapi_conn.create_aggregate("median", 1, pystaggrelite3.median)
    for (name,arity,func) in pystaggrelite3.getaggregators():
        dbapi_conn.create_aggregate(name,arity,func)
    '''
    pass



'''
class ExpDCCoilProp(Base):
    __tablename__ = 'exp_dc_coil_prop'
    id = Column(Integer, primary_key=True)
    exp = relationship("Exp", backref="dc_coil")
    radius = Column(Float, nullable=False)
    wire_diameter = Column(Float, nullable=False)
    turn = Column(Float, nullable=False)
    comment = Column(String(1000))

    def __init__(self, \
                radius, \
                wire_diameter, \
                turn, \
                comment = None):
        self.radius = radius
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment
'''

exp_smith_stats = Table('exp_smith_stats',meta,
    Column('exp_id', Integer, ForeignKey('exp.id'), nullable=False, primary_key=True),
    Column('max_imp_re', Float, nullable=True), #1
    Column('max_adj_imp_re', Float, nullable=True), #1
    Column('max_imp_re_freq', Float, nullable=True), #1
    Column('max_imp_im', Float, nullable=True), #1
    Column('max_imp_im_freq', Float, nullable=True), #1
    Column('max_imp_mag', Float, nullable=True), #1
    Column('max_adj_imp_mag', Float, nullable=True), #1
    Column('max_imp_mag_freq', Float, nullable=True), #1
    Column('max_adm_re', Float, nullable=True), #1
    Column('max_adm_re_freq', Float, nullable=True), #1
    Column('max_adm_im', Float, nullable=True), #1
    Column('max_adm_im_freq', Float, nullable=True), #1
    Column('max_adm_mag', Float, nullable=True), #1
    Column('max_adm_mag_freq', Float, nullable=True), #1

    Column('imp_q_freq0', Float, nullable=True), #1
    Column('imp_q_freq1', Float, nullable=True), #1

    Column('adj_imp_q_freq0', Float, nullable=True), #1
    Column('adj_imp_q_freq1', Float, nullable=True), #1

    Column('res_q_freq0', Float, nullable=True), #1
    Column('res_q_freq1', Float, nullable=True), #1

    Column('adj_res_q_freq0', Float, nullable=True), #1
    Column('adj_res_q_freq1', Float, nullable=True), #1

    Column('adm_q_freq0', Float, nullable=True), #1
    Column('adm_q_freq1', Float, nullable=True), #1

    Column('max_imp_parallel_ind', Float, nullable=True), #1
)

class ExpSmithStats(Base):
    __table__ = exp_smith_stats

    def __init__(self, \
                exp_id, \
                max_imp_re = None, \
                max_adj_imp_re = None, \
                max_imp_re_freq = None, \
                max_imp_im = None, \
                max_imp_im_freq = None, \
                max_imp_mag = None, \
                max_adj_imp_mag = None, \
                max_imp_mag_freq = None, \
                max_adm_re = None, \
                max_adm_re_freq = None, \
                max_adm_im = None, \
                max_adm_im_freq = None, \
                max_adm_mag = None, \
                max_adm_mag_freq = None,\

                imp_q_freq0 = None, \
                imp_q_freq1 = None, \

                adj_imp_q_freq0 = None, \
                adj_imp_q_freq1 = None, \

                res_q_freq0 = None, \
                res_q_freq1 = None, \

                adj_res_q_freq0 = None, \
                adj_res_q_freq1 = None, \

                adm_q_freq0 = None, \
                adm_q_freq1 = None, \

                max_imp_parallel_ind = None):

        self.exp_id = exp_id
        
        self.max_imp_re = max_imp_re
        self.max_adj_imp_re = max_adj_imp_re
        self.max_imp_re_freq = max_imp_re_freq

        self.max_imp_im = max_imp_im
        self.max_imp_im_freq = max_imp_im_freq

        self.max_imp_mag = max_imp_mag
        self.max_adj_imp_mag = max_adj_imp_mag
        self.max_imp_mag_freq = max_imp_mag_freq

        self.max_adm_re = max_adm_re
        self.max_adm_re_freq = max_adm_re_freq

        self.max_adm_im = max_adm_im
        self.max_adm_im_freq = max_adm_im_freq

        self.max_adm_mag = max_adm_mag
        self.max_adm_mag_freq = max_adm_mag_freq

        self.imp_q_freq0 = imp_q_freq0
        self.imp_q_freq1 = imp_q_freq1

        self.adj_imp_q_freq0 = adj_imp_q_freq0
        self.adj_imp_q_freq1 = adj_imp_q_freq1

        self.res_q_freq0 = res_q_freq0
        self.res_q_freq1 = res_q_freq1

        self.adj_res_q_freq0 = adj_res_q_freq0
        self.adj_res_q_freq1 = adj_res_q_freq1

        self.adm_q_freq0 = adm_q_freq0
        self.adm_q_freq1 = adm_q_freq1

        self.max_imp_parallel_ind = max_imp_parallel_ind

    def __repr__(self):
        return "<ExpSmithStats(ExpId = %d, Max Re(z) = %f@%fHz, Max Im(z) = %f@%fHz,, Max Mag(z) = %f@%fHz,, Max Re(y) = %f@%fHz,, Max Im(y) = %f@%fHz,, Max Mag(y) = %f@%fHz,)>" % \
            (self.exp_id, \
                self.max_imp_re, self.max_imp_re_freq, \
                self.max_imp_im, self.max_imp_im_freq, \
                self.max_imp_mag, self.max_imp_mag_freq, \
                self.max_adm_re, self.max_adm_re_freq, \
                self.max_adm_im, self.max_adm_im_freq, \
                self.max_adm_mag, self.max_adm_mag_freq)

exp_dc_coil_prop = Table('exp_dc_coil_prop',meta,
    Column('id', Integer, primary_key=True),
    Column('radius', Float, nullable=False), #1
    Column('wire_diameter', Float, nullable=False), #1
    Column('turn', Float, nullable=False), #1
    Column('comment', String(1000)), #1
)

class ExpDCCoilProp(Base):
    __table__ = exp_dc_coil_prop

    def __init__(self, \
                radius, \
                wire_diameter, \
                turn, \
                comment = None):
        self.radius = radius
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment

    def __repr__(self):
        return "<ExpDCCoilProp(Rad = %f, Wire Dia = %f, turn = %d, %s)>" % \
            (self.radius, self.wire_diameter, self.turn, self.comment)

exp_ac_coil_prop = Table('exp_ac_coil_prop',meta,
    Column('id', Integer, primary_key=True),
    Column('type', Integer, nullable=False), #1
    Column('width', Float, nullable=False), #1
    Column('height', Float, nullable=False), #1
    Column('length', Float, nullable=False), #1
    Column('wire_diameter', Float, nullable=False), #1
    Column('turn', Integer, nullable=False), #1
    Column('comment', String(1000)), #1
)

class ExpACCoilProp(Base):
    __table__ = exp_ac_coil_prop

    def __init__(self, type, width, height, length, wire_diameter, turn, comment = None):
        self.type = type
        self.width = width
        self.height = height
        self.length = length
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment

    def __repr__(self):
        return "<ExpACCoilProp(%d, WxHxL = %fx%fx%f, Wire Dia = %d, turn = %d, %s)>" % \
            (self.type, self.width, self.height, self.length, self.wire_diameter, self.turn, self.comment)
    @property
    def typeAsString(self):
        if self.type == 1:
            return "Circle"
        elif self.type == 2:
            return "Ellipse"
        elif self.type == 3:
            return "Square"
'''
class ExpACCoilProp(Base):
    __tablename__ = 'exp_ac_coil_prop'
    id = Column(Integer, primary_key=True)
    exp = relationship("Exp", backref="ac_coil")
    type = Column(Enum('','','','','',''), nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    wire_diameter = Column(Float, nullable=False)
    turn = Column(Integer, nullable=False)
    comment = Column(String(1000))

    def __init__(self, type, width, height, length, wire_diameter, turn, comment = None):
        self.type = type
        self.width = width
        self.height = height
        self.length = length
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment
'''

exp_material_prop = Table('exp_material_prop',meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), nullable=False), #1
    Column('youngs_modulus', Float, nullable=False), #1
    Column('density', Float, nullable=False), #1
    Column('poissons_ratio', Float, nullable=False), #1
    Column('shear_modulus', Float, nullable=False), #1
    Column('comment', String(1000)), #1
)
class ExpMaterialProp(Base):
    __table__ = exp_material_prop

    def __init__(self, name, youngs_modulus, density, poissons_ratio, shear_modulus, comment = None):
        self.name = name
        self.youngs_modulus = youngs_modulus
        self.density = density
        self.poissons_ratio = poissons_ratio
        self.shear_modulus = shear_modulus
        self.comment = comment

    def __repr__(self):
        return "<ExpMaterialProp(%s, %f, %f, %f, %f, %s)>" % \
            (self.name, self.youngs_modulus, self.density, self.poissons_ratio, self.shear_modulus, self.comment)
'''
class ExpMaterialProp(Base):
    __tablename__ = 'exp_material_prop'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    youngs_modulus = Column(Float, nullable=False)
    density = Column(Float, nullable=False)
    poissons_ratio = Column(Float, nullable=False)
    shear_modulus = Column(Float, nullable=False)
    patch = relationship("ExpPatchProp", backref="material")
    comment = Column(String(1000))

    def __init__(self, name, youngs_modulus, density, poissons_ratio, shear_modulus, comment = None):
        self.name = name
        self.youngs_modulus = youngs_modulus
        self.density = density
        self.poissons_ratio = poissons_ratio
        self.shear_modulus = shear_modulus
        self.comment = comment
'''

exp_patch_prop = Table('exp_patch_prop',meta,
    Column('id', Integer, primary_key=True),
    Column('material_id',Integer, ForeignKey('exp_material_prop.id'), nullable=False),
    Column('width', Float, nullable=False), #1
    Column('height', Float, nullable=False), #1
    Column('grain_orientation', String(20), nullable=False), #1
    Column('comment', String(1000)), #1
)


class ExpPatchProp(Base):
    __table__ = exp_patch_prop

    def __init__(self, material_id, width, height, grain_orientation, comment = None):
        self.material_id = material_id
        self.width = width
        self.height = height
        self.grain_orientation = grain_orientation
        self.comment = comment

    @hybrid_property
    def aspect_ratio(self):
        return self.width / self.height

    def __repr__(self):
        return "<ExpPatchProp(%d, WxL = %fx%f, %s, %s)>" % \
            (self.material_id, self.width, self.height, self.grain_orientation, self.comment)

exp_vis_prop = Table('exp_vis_prop',meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), nullable=False), #1
    Column('kinetic_vis', Float, nullable=True), #1
    Column('density', Float, nullable=True), #1
    Column('weight_percent', Float, nullable=True), #1
    Column('comment', String(1000)), #1
)


class ExpVisProp(Base):
    __table__ = exp_vis_prop

    def __init__(self, name, kinetic_vis = None, density = None, weight_percent = None, comment = None):
        self.name = name
        self.kinetic_vis = kinetic_vis
        self.density = density
        self.weight_percent = weight_percent
        self.comment = comment

    def __repr__(self):
        return "<ExpVisProp(name = %s, kv = %f, comment = %s)>" % \
            (self.name, self.kinetic_vis, self.comment)


'''
class ExpPatchProp(Base):
    __tablename__ = 'exp_patch_prop'
    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('material.id'))
    width = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    grain_orientation = Column(Enum(u'Horizontally', u'Vertically', name = 'grain_orientation'), nullable=False)
    exp = relationship("Exp", uselist=False, backref="patch")
    comment = Column(String(1000))

    def __init__(self, material_id, width, length, grain_orientation, comment = None):
        self.material_id = material_id
        self.width = width
        self.length = length
        self.grain_orientation = grain_orientation
        self.comment = comment

    @hybrid_property
    def aspect_ratio(self):
        return self.width / self.length
'''
exp = Table('exp',meta,
    Column('id', Integer, primary_key=True),
    Column('ac_coil_id', Integer, ForeignKey('exp_ac_coil_prop.id'), nullable=False),
    Column('dc_coil_id', Integer, ForeignKey('exp_dc_coil_prop.id'), nullable=False),
    Column('patch_id', Integer, ForeignKey('exp_patch_prop.id'), nullable=False),
    Column('vis_id', Integer, ForeignKey('exp_vis_prop.id'), nullable=False),
    Column('dc_current', Float(precision=3), nullable=False), #1
    Column('dc_field', Float, nullable=False), #1
    Column('temperature', Float, nullable=False), #1
    Column('comment', String(1000)), #1
    Column('exp_date', Date, nullable=False),
    Column('patch_included', Enum(u'Y', u'N'), nullable=True, default = 'Y'),
    Column('subtract_exp_id', Integer, ForeignKey('exp.id'), nullable=True),
)
class Exp(Base):
    __table__ = exp

    def __init__(self, ac_coil_id, dc_coil_id, patch_id, vis_id, exp_date, dc_current, dc_field, temperature, comment = None, patch_included = 'Y', subtract_exp_id = None):
        self.ac_coil_id = ac_coil_id
        self.dc_coil_id = dc_coil_id
        self.patch_id = patch_id
        self.vis_id = vis_id
        self.exp_date = exp_date
        self.dc_current = dc_current
        self.dc_field = dc_field
        self.temperature = temperature
        self.comment = comment
        self.patch_included = patch_included
        self.subtract_exp_id = subtract_exp_id

    def __repr__(self):
        if self.id is not None:            
            return "<Exp(#%d, AC#%d, DC#%d, P#%d, %s, %f, %f, %s)>" % \
                (self.id, self.ac_coil_id, self.dc_coil_id, self.patch_id, self.exp_date, self.dc_current, self.dc_field, self.comment)
 
        return "<Exp(#AC#%d, DC#%d, P#%d, %s, %f, %f, %s)>" % \
            (self.ac_coil_id, self.dc_coil_id, self.patch_id, self.exp_date, self.dc_current, self.dc_field, self.comment)
'''
class Exp(Base):
    __tablename__ = 'exp'
    id = Column(Integer, primary_key=True)
    ac_coil_id = Column(Integer, ForeignKey('ac_coil.id'))
    dc_coil_id = Column(Integer, ForeignKey('dc_coil.id'))
    patch_id = Column(Integer, ForeignKey('patch.id'))
    exp_date = Column(Date, nullable=False)
    dc_current = Column(Integer, nullable=False)
    dc_field = Column(Integer, nullable=False)
    comment = Column(String(1000))
    exp_vna = relationship("ExpVNA", uselist=False, backref="exp", cascade="all, delete-orphan")
    exp_smith = relationship("ExpSmith", backref="exp", cascade="all, delete-orphan")

    def __init__(self, ac_coil_id, dc_coil_id, patch_id, exp_date, dc_current, dc_field, comment = None):
        self.ac_coil_id = ac_coil_id
        self.dc_coil_id = dc_coil_id
        self.patch_id = patch_id
        self.exp_date = exp_date
        self.dc_current = dc_current
        self.dc_field = dc_field
        self.comment = comment
'''

exp_vna = Table('exp_vna',meta,
    Column('id', Integer, primary_key=True),
    Column('exp_id',Integer, ForeignKey('exp.id'), nullable=False),
    Column('if_bandwidth', Float, nullable=False), #1
    Column('number_of_points', Integer, nullable=False), #1
    Column('format_type', String(40), nullable=False), #1
    Column('sweep_type', String(40), nullable=False), #1
    Column('channel', Integer, nullable=False), #1
    Column('source_power', Float, nullable=False), #1
    Column('measure_type', String(10), nullable=False), #1
    Column('sweep_time', Float, nullable=False), #1
)

class ExpVNA(Base):
    __table__ = exp_vna

    def __init__(self, exp_id, \
        if_bandwidth, number_of_points, format_type, sweep_type, channel, \
        source_power, measure_type, sweep_time):
        self.exp_id = exp_id
        self.if_bandwidth = if_bandwidth
        self.number_of_points = number_of_points
        self.format_type = format_type
        self.sweep_type = sweep_type
        self.channel = channel
        self.source_power = source_power
        self.measure_type = measure_type
        self.sweep_time = sweep_time

'''
class ExpVNA(Base):
    __tablename__ = 'exp_vna'
    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer, ForeignKey('exp.id'))
    if_bandwidth = Column(Float, nullable=False)
    number_of_points = Column(Integer, nullable=False)
    format_type = Column(String(40), nullable=False)
    sweep_type = Column(String(40), nullable=False)
    channel = Column(Integer, nullable=False)
    source_power = Column(Float, nullable=False)
    measure_type = Column(String(10), nullable=False)
    sweep_time = Column(Float, nullable=False)

    def __init__(self, exp_id, if_bandwidth, number_of_points, format_type, sweep_type, channel, source_power, measure_type, sweep_time):
        self.exp_id = exp_id
        self.if_bandwidth = if_bandwidth
        self.number_of_points = number_of_points
        self.format_type = format_type
        self.sweep_type = sweep_type
        self.channel = channel
        self.source_power = source_power
        self.measure_type = measure_type
        self.sweep_time = sweep_time
'''

exp_smith = Table('exp_smith',meta,
    Column('id', Integer, primary_key=True),
    Column('exp_id',Integer, ForeignKey("exp.id"), nullable=False),
    Column('freq',Float, nullable=False),
    Column('re',Float, nullable=False),
    Column('im',Float, nullable=False), #1
    Column('imp_re',Float, nullable=False),
    Column('imp_im',Float, nullable=False), #1
)

class ExpSmith(Base):
    __table__ = exp_smith

    def __init__(self, exp_id, freq, re, im):
        self.exp_id = exp_id
        self.freq = freq
        self.re = re
        self.im = im
        self.imp_re = (1-re**2-im**2)/((1-re)**2+im**2)
        self.imp_im = 2*im/((1-re)**2+im**2)

    def __repr__(self):
        return "<ExpSmith(Exp#%d, %.3f+%.3fi @ %.2fHz)>" % (self.exp_id, self.imp_re * 50, self.imp_im * 50, self.freq)

exp_smith_filtered = Table('exp_smith_filtered',meta,
    Column('id', Integer, primary_key=True),
    Column('exp_id',Integer, ForeignKey("exp.id"), nullable=False),
    Column('freq',Float, nullable=False),
    Column('imp_re',Float, nullable=False),
    Column('imp_im',Float, nullable=False), #1
)

class ExpSmithFiltered(Base):
    __table__ = exp_smith_filtered

    def __init__(self, exp_id, freq, imp_re, imp_im):
        self.exp_id = exp_id
        self.freq = freq
        self.imp_re = (1-re**2-im**2)/((1-re)**2+im**2)
        self.imp_im = 2*im/((1-re)**2+im**2)

    def __repr__(self):
        return "<ExpSmith(Exp#%d, %.3f+%.3fi @ %.2fHz)>" % (self.exp_id, self.imp_re * 50, self.imp_im * 50, self.freq)

'''
class ExpSmith(Base):
    __tablename__ = 'exp_smith'
    id = Column(Integer, primary_key=True)
    exp_id = Column(Integer, ForeignKey('exp.id'))
    freq = Column(Float, nullable=False)
    re = Column(Float, nullable=False)
    im = Column(Float, nullable=False)
    imp_re = Column(Float, nullable=False)
    imp_im = Column(Float, nullable=False)
    mem_re = Column(Float, nullable=False)
    mem_im = Column(Float, nullable=False)

    def __init__(self, exp_id, freq, re, im, mem_re, mem_im):
        self.exp_id = exp_id
        self.freq = freq
        self.re = re
        self.im = im
        self.imp_re = (1-re**2-im**2)/((1-re)**2+im**2)
        self.imp_im = 2*im/((1-re)**2+im**2)

    def __repr__(self):
        return "<ExpSmith(%d, %03f %03fi @ %f)>" % (self.exp_id, self.imp_re * 50, self.imp_im * 50, self.freq)

'''
'''
        self.name = name
        self.youngs_modulus = youngs_modulus
        self.density = density
        self.poissons_ratio = poissons_ratio
        self.shear_modulus = shear_modulus
        self.comment = comment

        self.width = width
        self.length = length
        self.grain_orientation = grain_orientation
        self.comment = comment

        self.exp_id = exp_id
        self.if_bandwidth = if_bandwidth
        self.number_of_points = number_of_points
        self.format_type = format_type
        self.sweep_type = sweep_type
        self.channel = channel
        self.source_power = source_power
        self.measure_type = measure_type
        self.sweep_time = sweep_time
'''
patch_info = view("exp_patch_info", meta, 
    select([
        exp_material_prop.c.id.label('material_id'), 
        exp_material_prop.c.name, 
        exp_material_prop.c.density, 
        exp_material_prop.c.poissons_ratio, 
        exp_material_prop.c.youngs_modulus, 
        exp_material_prop.c.shear_modulus, 
        exp_material_prop.c.comment.label('material_comment'), 
        exp_patch_prop.c.id.label('patch_id'), 
        exp_patch_prop.c.width, 
        exp_patch_prop.c.height, 
        exp_patch_prop.c.grain_orientation, 
        exp_patch_prop.c.comment.label('patch_comment'), 
        ]).select_from(\
            exp_material_prop.join(exp_patch_prop, exp_material_prop.c.id == exp_patch_prop.c.material_id)
        )
    )

class ExpPatchInfo(Base):
    __table__ = patch_info

    def __repr__(self):
        return "<ExpPatchInfo(%s)>" % (self.name)

    @property 
    def grainAsString(self):
        if self.grain_orientation == 1:
            return "Vertically"
        elif self.grain_orientation == 2:
            return "Horizontally"
        else:
            return "Unknown"

    @property 
    def proper_ar(self):
        ar = self.width / self.height
        if ar < 1:
            ar = 1/ar
        return ar


exp_vna_info = view("exp_vna_info", meta, 
    select([
        exp.c.id,
        exp.c.patch_id,
        exp.c.exp_date,
        exp.c.dc_current,
        exp.c.dc_field,
        exp.c.comment.label('exp_comment'),
        exp.c.ac_coil_id,
        exp.c.dc_coil_id,
        exp.c.patch_included,
        exp.c.subtract_exp_id,
        exp_vna.c.if_bandwidth, 
        exp_vna.c.number_of_points, 
        exp_vna.c.format_type, 
        exp_vna.c.sweep_type, 
        exp_vna.c.channel, 
        exp_vna.c.source_power, 
        exp_vna.c.measure_type, 
        exp_vna.c.sweep_time, 
        ]).select_from(exp.\
            join(exp_vna, exp.c.id == exp_vna.c.exp_id)
        )
    )
exp_info = view("exp_info", meta, 
    select([
        exp_vna_info.c.id,
        exp_vna_info.c.patch_id,
        exp_vna_info.c.exp_date,
        exp_vna_info.c.dc_current,
        exp_vna_info.c.dc_field,
        exp_vna_info.c.exp_comment,
        exp_vna_info.c.ac_coil_id,
        exp_vna_info.c.dc_coil_id,
        exp_vna_info.c.patch_included,
        exp_vna_info.c.subtract_exp_id,
        patch_info.c.material_id, 
        patch_info.c.name, 
        patch_info.c.density, 
        patch_info.c.poissons_ratio, 
        patch_info.c.shear_modulus, 
        patch_info.c.material_comment, 
        patch_info.c.width, 
        patch_info.c.height, 
        patch_info.c.grain_orientation, 
        patch_info.c.patch_comment, 
        ]).select_from(exp_vna_info.\
            join(patch_info, exp_vna_info.c.patch_id == patch_info.c.patch_id).\
            join(exp_ac_coil_prop, exp_vna_info.c.ac_coil_id == exp_ac_coil_prop.c.id).\
            join(exp_dc_coil_prop, exp_vna_info.c.dc_coil_id == exp_dc_coil_prop.c.id)\
    ))
'''
exp_info = view("exp_info", meta, 
    select([
        exp.c.id, 
        exp.c.engine_load, 
        exp.c.rpm, 
        exp.c.ign, 
        exp.c.volt, 
        exp.c.efstart, 
        exp.c.efend, 
        exp.c.comment, 
        func.avg(expcycle.c.rpm).label("rpm_avg"),
        func.avg(expcycle.c.pmax).label("pmax_avg"),
        func.avg(expcycle.c.pmax_pos).label("pmax_pos_avg"),
        func.avg(expcycle.c.soc).label("soc_avg"),
        func.avg(expcycle.c.i05).label("i05_avg"),
        func.avg(expcycle.c.i10).label("i10_avg"),
        func.avg(expcycle.c.i50).label("i50_avg"),
        func.avg(expcycle.c.i90).label("i90_avg"),
        func.avg(expcycle.c.eoc).label("eoc_avg"),

        func.avg(expcycle.c.pmep).label("pmep_avg"),
        (func.stdev(expcycle.c.pmep) / func.avg(expcycle.c.pmep)).label("pmep_cov"),

        func.avg(expcycle.c.imepg).label("imepg_avg"),
        (func.stdev(expcycle.c.imepg) / func.avg(expcycle.c.imepg)).label("imepg_cov"),

        func.avg(expcycle.c.imepn).label("imepn_avg"),
        (func.stdev(expcycle.c.imepn) / func.avg(expcycle.c.imepn)).label("imepn_cov"),

        func.avg(expcycle.c.power).label("power_avg"),
        func.avg(expcycle.c.torque).label("torque_avg"),
        func.avg(expcycle.c.work).label("work_avg"),
        ]).select_from(exp.join(exp_vna, exp.c.id == exp_vna.c.exp_id)).group_by(exp.c.id)
        #where(exp.c.rpm != None).
    )
'''
engine = create_engine('mysql://magneto:2848@147.46.78.183/magneto')
event.listen(engine, 'connect', on_connect)

meta.bind = engine
session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
