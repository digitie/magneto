# -*- coding: utf-8 -*-

# to workaround sqlalchemy's get_characterset_info bug, which only applies to py2k.
#import mysql.connector
#mysql.connector.MySQLConnection.get_characterset_info=lambda cls:cls.charset

import matplotlib
matplotlib.use('WX')
import sys
from optparse import OptionParser
import web.main as MagWeb
from native.main import Magnificient

import logging

# create logger with 'spam_application'
'''
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
'''

from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchProp, ExpMaterialProp, ExpPatchInfo
from db.schema import exp, exp_smith, exp_vna, exp_ac_coil_prop, exp_dc_coil_prop, exp_patch_prop, exp_material_prop
from db.schema import meta, engine, session

def parse_opt():
    usage = "usage: %prog [options] arg"

    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose", default = False,
                      action="store_true", dest="verbose")

    parser.add_option("-w", "--web", default = False,
                      action="store_true", dest="web",
                      help="Initializes new database.")

    (options, args) = parser.parse_args()
    return options, args


if __name__ == "__main__":
    options, args = parse_opt()
    
    engine.echo = options.verbose
    
    if options.web:
        MagWeb.app.logger.addHandler(ch)
        MagWeb.MainLoop(debug = options.verbose)
    else:
        app = Magnificient(False)
        app.MainLoop()
