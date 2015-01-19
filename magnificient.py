# -*- coding: utf-8 -*-

# to workaround sqlalchemy's get_characterset_info bug, which only applies to py2k.
#import mysql.connector
#mysql.connector.MySQLConnection.get_characterset_info=lambda cls:cls.charset

import sys
from sqlalchemy import *
from optparse import OptionParser
from sqlalchemy.exc import OperationalError

import logging
import csv
import datetime
from vnaparser import VNADataParser

# create logger with 'spam_application'
logger = logging.getLogger('read_dewe')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchProp, ExpMaterialProp, ExpPatchInfo
from db.schema import exp, exp_smith, exp_vna, exp_ac_coil_prop, exp_dc_coil_prop, exp_patch_prop, exp_material_prop
from db.schema import meta, engine, session

def parse_opt():
    usage = "usage: %prog [options] arg"

    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose", default = False,
                      action="store_true", dest="verbose")

    parser.add_option("-i", "--init", default = False,
                      action="store_true", dest="init",
                      help="Initializes new database.")

    parser.add_option("-f", "--force", default = False,
                      action="store_true", dest="force",
                      help="Force delete existing database when initialize.")

    (options, args) = parser.parse_args()
    '''
    if options.append and options.force:
        sys.stderr.write("Invalid options. -a, --append and -f, --force can't be enabled both")
        sys.exit(1)
    '''
    return options, args

def create_db(meta, force_delete = False):    
    if force_delete:
        try:
            meta.drop_all()
        except OperationalError as e:
            sys.stderr.write("Error while force deleting current database")
            sys.stderr.write(str(e))
            #sys.exit(1)
    meta.create_all()

def check_db(meta):
    if not engine.has_table(exp.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)
    if not engine.has_table(exp_vna.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)
    if not engine.has_table(exp_smith.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)
    if not engine.has_table(exp_material_prop.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)
    if not engine.has_table(exp_patch_prop.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)
    if not engine.has_table(exp_ac_coil_prop.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)
    if not engine.has_table(exp_dc_coil_prop.name):
        sys.stderr.write("Table does not exists")
        sys.exit(1)

if __name__ == "__main__":
    options, args = parse_opt()
    
    engine.echo = options.verbose
    
    if options.init:
        create_db(meta, options.force)

    check_db(meta)

    dc_coil = ExpDCCoilProp(
        radius = 50,
                wire_diameter = 0.4,
                turn = 168, \
                comment  = 'First'
    )
    session.add(dc_coil)


    ac_coils = []
    #1
    ac_coil = ExpACCoilProp(
        type = 0,
        width = 6,
        height = 6, \
        length = 25, \
        wire_diameter = 0.23, \
        turn = 60, \
        comment  = 'Circle'
    )
    ac_coils.append(ac_coil)
    #2
    ac_coil = ExpACCoilProp(
        type = 1,
        width = -1,
        height = -1, \
        length = -1, \
        wire_diameter = -1, \
        turn = -1, \
        comment  = 'Ellipse'
    )
    ac_coils.append(ac_coil)
    #3
    ac_coil = ExpACCoilProp(
        type = 1,
        width = 6,
        height = 6, \
        length = 15, \
        wire_diameter = 0.4, \
        turn = 35, \
        comment  = 'Ellipse'
    )
    ac_coils.append(ac_coil)
    #4
    ac_coil = ExpACCoilProp(
        type = 1,
                width = 6,
                height = 6, \
                length = 25, \
                wire_diameter = 0.4, \
                turn = 60, \
                comment  = 'Ellipse'
    )
    ac_coils.append(ac_coil)
    #5
    ac_coil = ExpACCoilProp(
        type = 1,
                width = 6,
                height = 6, \
                length = 25, \
                wire_diameter = 0.4, \
                turn = 60, \
                comment  = 'Ellipse'
    )
    ac_coils.append(ac_coil)
    #6
    ac_coil = ExpACCoilProp(
        type = 0,
                width = 7,
                height = 7, \
                length = 15, \
                wire_diameter = 0.1, \
                turn = 60, \
                comment  = 'Circle'
    )
    ac_coils.append(ac_coil)
    #7
    ac_coil = ExpACCoilProp(
        type = 0,
                width = 7,
                height = 7, \
                length = 15, \
                wire_diameter = 0.23, \
                turn = 60, \
                comment  = 'Circle'
    )
    ac_coils.append(ac_coil)
    #8
    ac_coil = ExpACCoilProp(
        type = 0,
                width = 18,
                height = 18, \
                length = 32, \
                wire_diameter = 0.23, \
                turn = 100, \
                comment  = 'Circle'
    )
    ac_coils.append(ac_coil)
    session.add_all(ac_coils)


    mats = []
    mat1 = ExpMaterialProp(
        name = '2826MB',
                youngs_modulus = 105,
                density = 7900, \
                poissons_ratio = 0.3, \
                shear_modulus = -1, \
                comment  = 'test'
    )
    mats.append(mat1)
    session.add_all(mats)
    session.flush()
    session.commit()

    patches = []
    #4-1
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 12.5,
            grain_orientation = 2,
            comment  = '4-1'
        )
    )
    #4-2
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 10,
            grain_orientation = 2,
            comment  = '4-2'
        )
    )
    #4-3
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 7.5,
            grain_orientation = 2,
            comment  = '4-3'
        )
    )
    #4-4
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 7.2,
            grain_orientation = 2,
            comment  = '4-4'
        )
    )
    #4-5
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 5.5,
            grain_orientation = 2,
            comment  = '4-5'
        )
    )
    #4-6
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 4.8,
            grain_orientation = 2,
            comment  = '4-6'
        )
    )
    #4-7
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 3.8,
            grain_orientation = 2,
            comment  = '4-7'
        )
    )
    #4-8
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 3.5,
            grain_orientation = 2,
            comment  = '4-8'
        )
    )
    #4-9
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 2.5,
            grain_orientation = 2,
            comment  = '4-9'
        )
    )
    #4-10
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 2,
            grain_orientation = 2,
            comment  = '4-10'
        )
    )
    #4-11
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 1,
            grain_orientation = 2,
            comment  = '5-11'
        )
    )
    #6-1 (12)
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 2.16,
            height = 16.81,
            grain_orientation = 1,
            comment  = '6-1'
        )
    )
    #6-2 (13)
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 2.1,
            height = 14.73,
            grain_orientation = 1,
            comment  = '6-2'
        )
    )
    #6-3 (14)
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 2.17,
            height = 12.66,
            grain_orientation = 1,
            comment  = '6-3'
        )
    )
    #6-4 (15)
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 2.23,
            height = 10.12,
            grain_orientation = 1,
            comment  = '6-4'
        )
    )
    #?-? (16)
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 5.19,
            grain_orientation = 1,
            comment  = '?-?'
        )
    )
    #?-? (17)
    patches.append(
        ExpPatchProp(
            material_id = 1,
            width = 12.5,
            height = 1.2,
            grain_orientation = 1,
            comment  = '?-?'
        )
    )
    session.add_all(patches)
    session.flush()
    session.commit()

    with open('exp.csv', 'rb') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in rows:
            if i == 0:
                i += 1
                continue
            print row
            i += 1
            try:
                if not row[7]:
                    comment = ''
                else:
                    comment = row[7]
            except IndexError:
                comment = ''
            exp = Exp(
                exp_date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date(),
                ac_coil_id = int(row[1]),
                dc_coil_id = int(row[2]),
                patch_id = float(row[3]),
                dc_current = float(row[4]),
                dc_field = float(row[5]),
                comment = comment
            )
            session.add(exp)
            session.flush()
            filename = row[6] + '.txt'
            #f.save('/var/www/uploads/uploaded_file.txt')

            p = VNADataParser(exp.id, filename)
            p.parse()
            session.add(p.vna_properties)
            session.add_all(p.vna_data)
        session.commit()
    result = \
        session.query(
            Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpPatchInfo
            ).join(ExpVNA).join(ExpDCCoilProp).join(ExpACCoilProp).join(ExpPatchInfo, Exp.patch_id == ExpPatchInfo.patch_id).order_by(Exp.id)
    for exp, exp_vna, exp_dc_coil, exp_ac_coil, patch in result:
        print exp, exp_vna, exp_dc_coil, exp_ac_coil, patch