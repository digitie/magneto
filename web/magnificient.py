# -*- coding: utf-8 -*-
import os, fnmatch
import sys

# to workaround sqlalchemy's get_characterset_info bug, which only applies to py2k.
#import mysql.connector
#mysql.connector.MySQLConnection.get_characterset_info=lambda cls:cls.charset

from sqlalchemy import *
from optparse import OptionParser
from sqlalchemy.exc import OperationalError

import logging
import datetime
import sys
import csv
from vnaparser import VNADataParser

from web import app


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

from tabledef import exp, Exp
from tabledef import exp_vna, ExpVNA
from tabledef import exp_smith, ExpSmith
from tabledef import meta, engine, session

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

    parser.add_option("-c", "--csv", default = None,
                      dest="csv",
                      help="Force delete existing database when initialize.")

    parser.add_option("-b", "--verbosedb", default = False,
                      action="store_true", dest="verbosedb")

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
            sys.exit(1)
    meta.create_all()

def check_db(meta):
    if not engine.has_table(exp.name) or not engine.has_table(exp_vna.name) or not engine.has_table(exp_smith.name):
            sys.stderr.write("Table does not exists")
            sys.exit(1)

if __name__ == "__main__":
    options, args = parse_opt()
    
    engine.echo = options.verbosedb
    
    if options.init:
        create_db(meta, options.force)
        exit(0)

    check_db(meta)

    if options.csv:
        print options.csv
        with open(options.csv, 'rb') as csvfile:
            rows = csv.reader(csvfile, delimiter=',')
            i = 0
            for row in rows:
                if i == 0:
                    i += 1
                    continue
                print row
                i += 1
                try:
                    if not row[9]:
                        comment = ''
                    else:
                        comment = row[9]
                except IndexError:
                    comment = ''
                exp = Exp(
                    exp_date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date(),
                    coil_num = int(row[1]),
                    patch_material = int(row[2]),
                    patch_width = float(row[3]),
                    patch_length = float(row[4]),
                    patch_grain_direction = int(row[5]),
                    dc_current = float(row[6]),
                    dc_field = float(row[7]),
                    comment = comment
                )
                session.add(exp)
                session.flush()
                filename = row[8] + '.txt'
                #f.save('/var/www/uploads/uploaded_file.txt')

                p = VNADataParser(exp.id, filename)
                p.parse()
                session.add(p.vna_properties)
                session.add_all(p.vna_data)
            session.commit()
    else:
        app.run(host='0.0.0.0', use_reloader = False, debug=True)

    
    #before = datetime.datetime.now()

    #ip = VNADataParser('1007001.TXT')
    #ip.parse()
    #session.add_all(ip._data)
