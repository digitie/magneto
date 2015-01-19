# -*- coding: utf-8 -*-

from sqlalchemy import func

from db.schema import Exp, ExpSmith, ExpSmithStats, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchInfo, ExpMaterialProp, ExpVisProp, ExpSmithFiltered
from db.schema import exp, exp_smith, exp_smith_stats, exp_vna, exp_ac_coil_prop, exp_dc_coil_prop, exp_patch_prop, exp_material_prop, exp_vis_prop, exp_smith_filtered
from db.schema import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from ObjectListView import ColumnDefn
import numpy as np
from scipy.signal import kaiserord, lfilter, firwin, freqz
import math

from util import enum

class MplXYPlotKey(object):
    def __init__(self,key1,key2,key3):
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3

    def __hash__(self):
        return hash((self.key1, self.key2, self.key3))

    def __eq__(self, other):
        return (self.key1, self.key2, self.key3) == (other.key1, other.key2, other.key3)

class MplXYPlotData(object):
    def __init__(self):
        self.x = []
        self.y = []
        self.xmin = None
        self.xmax = None

        self.ymin = None
        self.ymax = None
        self.legend = ''

    def append_x(self, data):
        self.x.append(data)
        if type(data) != type(0+0j):
            if self.xmax is None:
                self.xmax = data
            else:
                self.xmax = data if data > self.xmax else self.xmax

            if self.xmin is None:
                self.xmin = data
            else:
                self.xmin = data if self.xmin > data else self.xmin

    def append_y(self, data):
        self.y.append(data)
        if type(data) != type(0+0j):
            if self.ymax is None:
                self.ymax = data
            else:
                self.ymax = data if data > self.ymax else self.ymax
                
            if self.ymin is None:
                self.ymin = data
            else:
                self.ymin = data if self.ymin > data else self.ymin

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_legend(self, legend):
        self.legend = legend

    def get_legend(self):
        return self.legend

    def convert(self):
        self.x = np.array(self.x)
        self.y = np.array(self.y)

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def fir_filter(x, y, ripple_db = 60.0, cutoff_hz = 0.01):
    #------------------------------------------------
    # Create a FIR filter and apply it to x.
    #------------------------------------------------
    sample_rate = 1/(x[1] - x[0])

    # The Nyquist rate of the signal.
    nyq_rate = sample_rate / 2.0

    # The desired width of the transition from pass to stop,
    # relative to the Nyquist rate.  We'll design the filter
    # with a 5 Hz transition width.
    width = 5.0/nyq_rate

    # Compute the order and Kaiser parameter for the FIR filter.
    N, beta = kaiserord(ripple_db, width)

    # Use firwin with a Kaiser window to create a lowpass FIR filter.
    taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))

    delay = 0.5 * (N-1) / sample_rate

    # Use lfilter to filter x with the FIR filter.
    return x[N-1:] - delay, lfilter(taps, 1.0, y)[N-1:]

def isFiltered(exp_id):
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    r = session.query(ExpSmithFiltered).\
            filter(ExpSmithFiltered.exp_id == exp_id).all()
    if len(r) > 0:
        res = True
    else:
        res = False
    session.close()

    return res

def addFIRFiltered(exp_id):
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    session.query(ExpSmithFiltered).\
            filter(ExpSmithFiltered.exp_id == exp_id).delete(synchronize_session='fetch')
    smiths = getExpSmithByExpId(exp_id)
    freq = []
    imp_re = []
    imp_im = []
    for row in smiths:
        freq.append(row.freq)
        imp_re.append(row.imp_re)
        imp_im.append(row.imp_im)

    freq = np.array(freq)
    imp_re = np.array(imp_re)
    imp_im = np.array(imp_im)

    freq1, filtered_imp_re = fir_filter(freq, imp_re)
    freq2, filtered_imp_im = fir_filter(freq, imp_im)

    if freq1 != freq2:
        raise Exception()

    freq1 = freq1.tolist()
    filtered_imp_re = filtered_imp_re.tolist()
    filtered_imp_im = filtered_imp_im.tolist()

    smiths_filtered = []
    for freq, re, im in zip(freq1, filtered_imp_re, filtered_imp_im):
        smith_filtered = ExpSmithFiltered(exp_id, freq, re, im)
        smiths_filtered.append(smith_filtered)
    session.add_all(smiths_filtered)
    session.flush()
    session.commit()
    session.close()


def getReflectionData(exp_ids = []):
    datas = []
    for exp_id in exp_ids:
        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smit_stats = getExpDetailInfoByExpId(exp_id)

        if exp.subtract_exp_id is not None:
            exp_subtracted = getExpSmithByExpId(exp.subtract_exp_id)
            orig = MplXYPlotData()
            to_subtract = MplXYPlotData()
            subtracted = MplXYPlotData()
            for row, row_to_subtract in zip(smiths, exp_subtracted):
                orig.append_x(row.freq)
                to_subtract.append_x(row.freq)
                subtracted.append_x(row.freq)

                orig_y = math.sqrt((row.re)**2 + (row.im)**2)
                to_subtract_y = math.sqrt((row_to_subtract.re)**2 + (row_to_subtract.im)**2)
                subtracted_y = orig_y - to_subtract_y

                orig.append_y(orig_y)
                to_subtract.append_y(to_subtract_y)
                subtracted.append_y(subtracted_y)


            orig.y = 20* np.log10(orig.y)
            to_subtract.y = 20* np.log10(to_subtract.y)
            subtracted.y = 20* np.log10(subtracted.y)

            t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
            orig.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            to_subtract.set_legend('Exp No.%d Coil Only' % (exp_id))
            subtracted.set_legend('Exp No.%d Subtracted' % (exp_id))
            #data.set_legend(exp_id)
            orig.convert()
            to_subtract.convert()
            subtracted.convert()
            #filtered_data = MplXYPlotData()
            #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
            #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            datas.append(orig)
            datas.append(to_subtract)
            datas.append(subtracted)
        else:
            data = MplXYPlotData()
            for row in smiths:
                data.append_x(row.freq)
                y = math.sqrt((row.re)**2 + (row.im)**2)

                data.append_y(y)

            data.y = 20* np.log10(data.y)

            t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
            data.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            #data.set_legend(exp_id)
            data.convert()
            #filtered_data = MplXYPlotData()
            #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
            #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            datas.append(data)
            #datas.append(filtered_data)
    return datas
'''
def getReflectionData(exp_ids = []):
    datas = []
    for exp_id in exp_ids:
        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith = getExpDetailInfoByExpId(exp_id)

        data = MplXYPlotData()
        for row in smiths:
            data.append_x(row.freq)
            y = math.sqrt((row.re)**2 + (row.im)**2)

            data.append_y(y)

        data.y = 20* np.log10(data.y)

        t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
        data.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
        #data.set_legend(exp_id)
        data.convert()
        #filtered_data = MplXYPlotData()
        #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
        #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
        datas.append(data)
        #datas.append(filtered_data)
    return datas
'''

class RawVNAData():
    def __init__(self):
        self.freq = []
        self.re = []
        self.im = []
        self.imp_re = []
        self.imp_im = []
        self.title = None

    def set_title(self, title):
        self.title = title

def generateSummary(exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats, dc_field):
    if exp_ac_coil.type == 1:
        area = (exp_ac_coil.width/2)*(exp_ac_coil.width/2)*math.pi
    else:
        area = exp_ac_coil.width * exp_ac_coil.height
    return [
        exp_ac_coil.id,
        exp_ac_coil.comment,
        exp_ac_coil.width,
        exp_ac_coil.height,
        exp_ac_coil.length,
        exp_ac_coil.wire_diameter,
        exp_ac_coil.turn,
        0.001*math.pow(10, exp_vna.source_power/10),
        area,
        0,
        0,
        exp.id,
        exp_vis.name,
        exp_vis.density,
        exp_vis.kinetic_vis,
        exp_vis.weight_percent,
        patch.width,
        patch.height,
        exp_smith_stats.max_imp_re,
        exp_smith_stats.max_imp_im,
        exp_smith_stats.max_imp_im_freq,
        exp_smith_stats.max_imp_re_freq,
        exp_smith_stats.max_imp_mag_freq,
        exp_smith_stats.max_imp_mag,
        exp_smith_stats.imp_q_freq0,
        exp_smith_stats.max_imp_parallel_ind,
        exp_smith_stats.imp_q_freq1,
        0, # Q
        0, # R
        0, # R-
        0, # L
        0, # L_air
        0, # C
        0, # k
        0, #lp_cal
        1,
        0,
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        exp.dc_current,
        dc_field,
        exp_vis.density * exp_vis.kinetic_vis,
        math.sqrt(exp_vis.density * exp_vis.kinetic_vis),

        exp_smith_stats.adj_imp_q_freq0,
        exp_smith_stats.adj_imp_q_freq1,    
        '',
        exp_smith_stats.res_q_freq0,
        exp_smith_stats.res_q_freq1,     
        '',
        exp_smith_stats.adj_res_q_freq0,
        exp_smith_stats.adj_res_q_freq1,     
        ]

def getRawVNAData(exp_ids = []):
    datas = []
    summaries = []
    for exp_id in exp_ids:
        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats = getExpDetailInfoByExpId(exp_id)

        exp_subtracted = getExpSmithByExpId(exp.subtract_exp_id)
        orig = RawVNAData()
        to_subtract = RawVNAData()
        for row, row_to_subtract in zip(smiths, exp_subtracted):
            orig.freq.append(row.freq)
            to_subtract.freq.append(row.freq)

            # orig

            orig.re.append(row.re)
            orig.im.append(row.im)
            orig.imp_re.append(row.imp_re)
            orig.imp_im.append(row.imp_im)

            # without patch
            to_subtract.re.append(row_to_subtract.re)
            to_subtract.im.append(row_to_subtract.im)
            to_subtract.imp_re.append(row_to_subtract.imp_re)
            to_subtract.imp_im.append(row_to_subtract.imp_im)

        t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
        field = t * 7.943 * 10**5
        orig.set_title('Exp No.%d (Coil#%d) #%d %.2fx%.2f (%s) %.0fdBm (%.0fA/m)' % (exp_id, exp_ac_coil.id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, field))
        to_subtract.set_title('Exp No.%d (Coil#%d)' % (exp_id, exp_ac_coil.id))
        datas.append({
            'orig': orig,
            'to_subtract': to_subtract,
            })
        summaries.append(generateSummary(exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats, field))
    return summaries, datas

def getImpedanceData(exp_ids = [], type = None):
    datas = []
    for exp_id in exp_ids:
        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats = getExpDetailInfoByExpId(exp_id)

        if exp.subtract_exp_id is not None:
            exp_subtracted = getExpSmithByExpId(exp.subtract_exp_id)
            orig = MplXYPlotData()
            to_subtract = MplXYPlotData()
            subtracted = MplXYPlotData()
            for row, row_to_subtract in zip(smiths, exp_subtracted):
                orig.append_x(row.freq)
                to_subtract.append_x(row.freq)
                subtracted.append_x(row.freq)

                if type == 'im':
                    orig_y = row.imp_im * 50
                    to_subtract_y = row_to_subtract.imp_im * 50
                    subtracted_y = orig_y - to_subtract_y
                elif type == 're':
                    orig_y = row.imp_re * 50
                    to_subtract_y = row_to_subtract.imp_re * 50
                    subtracted_y = orig_y - to_subtract_y
                elif type == 'mag':
                    orig_y = math.sqrt((row.imp_re * 50)**2 + (row.imp_im * 50)**2)
                    to_subtract_y = math.sqrt((row_to_subtract.imp_re * 50)**2 + (row_to_subtract.imp_im * 50)**2)
                    subtracted_y = math.sqrt((row.imp_re * 50 -row_to_subtract.imp_re * 50)**2 +(row.imp_im * 50 -row_to_subtract.imp_im * 50)**2)
                else:
                    raise Exception()

                orig.append_y(orig_y)
                to_subtract.append_y(to_subtract_y)
                subtracted.append_y(subtracted_y)

            t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
            orig.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            to_subtract.set_legend('Exp No.%d Coil Only' % (exp_id))
            subtracted.set_legend('Exp No.%d Subtracted' % (exp_id))
            #data.set_legend(exp_id)
            orig.convert()
            to_subtract.convert()
            subtracted.convert()
            #filtered_data = MplXYPlotData()
            #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
            #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            datas.append(orig)
            datas.append(to_subtract)
            datas.append(subtracted)
        else:
            data = MplXYPlotData()
            for row in smiths:
                data.append_x(row.freq)
                if type == 'im':
                    y = row.imp_im * 50
                if type == 'mag':
                    y = math.sqrt((row.imp_re * 50)**2 + (row.imp_im * 50)**2)
                else:
                    y = row.imp_re * 50

                data.append_y(y)

            t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
            data.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            #data.set_legend(exp_id)
            data.convert()
            #filtered_data = MplXYPlotData()
            #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
            #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            datas.append(data)
        #datas.append(filtered_data)
    return datas

def getExpSmithByExpId(exp_id):  
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))

    result = session.query(ExpSmith).filter(ExpSmith.exp_id == exp_id).order_by(ExpSmith.freq).all()

    session.close()
    return result

def calculateStatByExpIds(exp_ids = []):
    for exp_id in exp_ids:
        freqs = []
        resistances = []
        adj_res = []
        reactances = []        
        imp_mags = []
        adj_imp_msgs = []

        conductances = []
        susceptances = []
        adm_mags = []

        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats = getExpDetailInfoByExpId(exp_id)

        if exp.subtract_exp_id is not None:
            exp_subtracted = getExpSmithByExpId(exp.subtract_exp_id)
            for row, row_to_subtract in zip(smiths, exp_subtracted):
                imp_re = (row.imp_re - row_to_subtract.imp_re)* 50
                imp_im = (row.imp_im - row_to_subtract.imp_im)* 50                
                img_mag_sqaure = imp_re**2 + imp_im**2
                imp_mag = math.sqrt(img_mag_sqaure)

                freqs.append(row.freq)

                resistances.append(imp_re)
                reactances.append(imp_im)
                imp_mags.append(imp_mag)
                '''
                conductances.append(imp_re/(img_mag_sqaure))
                susceptances.append(-imp_im/(img_mag_sqaure))
                adm_mags.append(1/imp_mag)
                '''
            min_imp_mag = min(imp_mags)
            min_res_mag = min(resistances)
            freqs = np.array(freqs)

            resistances = np.array(resistances)
            reactances = np.array(reactances)
            imp_mags = np.array(imp_mags)
            adj_imp_msgs = np.array(imp_mags) - min_imp_mag
            adj_res = np.array(resistances) - min_res_mag
            '''
            conductances = np.array(conductances)
            susceptances = np.array(susceptances)
            adm_mags = np.array(adm_mags)
            '''

            max_imp_re = np.max(resistances)
            max_re_freq_idx = np.argmax(resistances)
            max_imp_re_freq = freqs[max_re_freq_idx]
            max_imp_im = np.max(reactances)
            max_imp_im_freq = freqs[np.argmax(reactances)]
            max_imp_mag = np.max(imp_mags)

            max_imp_freq_idx = np.argmax(imp_mags)
            max_imp_mag_freq = freqs[max_imp_freq_idx]

            imp_three_db_val = 0.70721 * max_imp_mag
            adj_imp_three_db_val = 0.70721 * np.max(adj_imp_msgs)

            imp_f0_idx = (np.abs(imp_mags[:max_imp_freq_idx]-imp_three_db_val)).argmin()
            imp_f1_idx = (np.abs(imp_mags[max_imp_freq_idx:]-imp_three_db_val)).argmin()

            imp_adj_f0_idx = (np.abs(adj_imp_msgs[:max_imp_freq_idx]-adj_imp_three_db_val)).argmin()
            imp_adj_f1_idx = (np.abs(adj_imp_msgs[max_imp_freq_idx:]-adj_imp_three_db_val)).argmin()

            res_three_db_val = 0.70721 * max_imp_re
            adj_res_three_db_val = 0.70721 * np.max(adj_res)

            res_f0_idx = (np.abs(resistances[:max_re_freq_idx]-res_three_db_val)).argmin()
            res_f1_idx = (np.abs(resistances[max_re_freq_idx:]-res_three_db_val)).argmin()

            res_adj_f0_idx = (np.abs(adj_res[:max_re_freq_idx]-adj_res_three_db_val)).argmin()
            res_adj_f1_idx = (np.abs(adj_res[max_re_freq_idx:]-adj_res_three_db_val)).argmin()


            #print imp_mags[imp_f0_idx], max_imp_freq_idx, imp_mags[imp_f1_idx], freqs[max_imp_freq_idx]
            #print max_imp_mag, three_db_val
            '''
            max_adm_re = np.max(conductances)
            max_adm_re_freq = freqs[np.argmax(conductances)]
            max_adm_im = np.max(susceptances)
            max_adm_im_freq = freqs[np.argmax(susceptances)]
            max_adm_mag = np.max(adm_mags)

            max_adm_freq_idx = np.argmax(adm_mags)
            max_adm_mag_freq = freqs[max_adm_freq_idx]

            three_db_val = 0.70721 * max_adm_mag

            print adm_mags
            print max_adm_mag, max_adm_freq_idx, max_adm_mag_freq

            adm_f0_idx = (np.abs(adm_mags[:max_adm_freq_idx]-three_db_val)).argmin()
            adm_f1_idx = (np.abs(adm_mags[max_adm_freq_idx:]-three_db_val)).argmin()
            '''
            max_adm_re = None
            max_adm_re_freq = None
            max_adm_im = None
            max_adm_im_freq = None
            max_adm_mag = None
            max_adm_mag_freq = None
            adm_f0_idx = None
            adm_f1_idx = None
            stats = ExpSmithStats(
                exp_id,
                max_imp_re, 
                max_imp_re - min_res_mag, 
                max_imp_re_freq, 
                max_imp_im, 
                max_imp_im_freq, 
                max_imp_mag, 
                max_imp_mag - min_imp_mag, 
                max_imp_mag_freq, 
                max_adm_re, 
                max_adm_re_freq, 
                max_adm_im, 
                max_adm_im_freq, 
                max_adm_mag, 
                max_adm_mag_freq, 

                freqs[imp_f0_idx],
                freqs[max_imp_freq_idx + imp_f1_idx],

                freqs[imp_adj_f0_idx],
                freqs[max_imp_freq_idx + imp_adj_f1_idx],

                freqs[res_f0_idx],
                freqs[max_re_freq_idx + res_f1_idx],

                freqs[res_adj_f0_idx],
                freqs[max_re_freq_idx + res_adj_f1_idx],
                #freqs[adm_f0_idx],
                #freqs[adm_f1_idx],
                None,
                None,
                max_imp_im
            )

            session = scoped_session(sessionmaker(
                autoflush=False,
                autocommit=False,
                bind=engine))

            result = \
                session.query(ExpSmithStats).\
                    filter(ExpSmithStats.exp_id == (exp_id)).all()

            if result:
                for row in result:
                    session.delete(row)
            session.add(stats)
            session.commit()
            session.close()

def getExpSmithByExpIds(exp_ids = []):
    datas = []
    for exp_id in exp_ids:
        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats = getExpDetailInfoByExpId(exp_id)

        if exp.subtract_exp_id is not None:
            exp_subtracted = getExpSmithByExpId(exp.subtract_exp_id)
            orig = MplXYPlotData()
            to_subtract = MplXYPlotData()
            subtracted = MplXYPlotData()
            for row, row_to_subtract in zip(smiths, exp_subtracted):
                orig.append_x(row.freq)
                to_subtract.append_x(row.freq)
                subtracted.append_x(row.freq)

                orig_y = row.imp_re + row.imp_im * 1j
                to_subtract_y = row_to_subtract.imp_re + row_to_subtract.imp_im * 1j
                subtracted_y = orig_y - to_subtract_y

                orig.append_y(orig_y)
                to_subtract.append_y(to_subtract_y)
                subtracted.append_y(subtracted_y)

            t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
            orig.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            to_subtract.set_legend('Exp No.%d Coil Only' % (exp_id))
            subtracted.set_legend('Exp No.%d Subtracted' % (exp_id))
            #data.set_legend(exp_id)
            orig.convert()
            to_subtract.convert()
            subtracted.convert()
            #filtered_data = MplXYPlotData()
            #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
            #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            datas.append(orig)
            datas.append(to_subtract)
            datas.append(subtracted)
        else:
            data = MplXYPlotData()
            for row in smiths:
                data.append_x(row.freq)
                data.append_y(row.imp_re + row.imp_im * 1j)

            t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
            data.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            #data.set_legend(exp_id)
            data.convert()
            #filtered_data = MplXYPlotData()
            #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
            #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
            datas.append(data)
            #datas.append(filtered_data)
    return datas
'''
def getExpSmithByExpIds(exp_ids = []):
    datas = []
    for exp_id in exp_ids:
        smiths = getExpSmithByExpId(exp_id)
        exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith = getExpDetailInfoByExpId(exp_id)

        data = MplXYPlotData()
        for row in smiths:
            data.append_x(row.freq)

            #imp_re = (1-row.re**2-row.im**2)/((1-row.re)**2+row.im**2)
            #imp_im = 2*row.im/((1-row.re)**2+row.im**2)
            data.append_y(row.imp_re + row.imp_im * 1j)
            
        t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
        data.set_legend('Exp No.%d #%d %.2fx%.2f (%s) %.0fdBm (%.0fOe)' % (exp_id, patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
        #data.set_legend(exp_id)
        data.convert()
        #filtered_data = MplXYPlotData()
        #filtered_data.x, filtered_data.y = fir_filter(data.x, data.y)
        #filtered_data.set_legend('#%d %.2fx%.2f (%s) %.0fdBm (%.0fOe) (filtered)' % (patch.patch_id, patch.width, patch.height, patch.name, exp_vna.source_power, t * 7.943 * 10**5))
        datas.append(data)
        #datas.append(filtered_data)

    return datas
'''
def getACFieldVsFrequency(exp_ids = []):
    datas = []
    datadict = {}

    addStat(exp_ids)  
    result = getExpDetailInfo(exp_ids, ExpVNA.source_power)

    for exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats in result:

        t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
        key = MplXYPlotKey(patch.material_id, patch.proper_ar, t)
        if key not in datadict.keys():
            datadict[key] = MplXYPlotData()
        data = datadict[key]

        #return t * 7.943 * 10**5
        data.append_x(exp_vna.source_power)
        data.append_y(exp_smith_stats.max_imp_mag_freq)
        data.set_legend('%.2fx%.2f (%s) %.0fA/m' % (patch.width, patch.height, patch.name, t * 7.943 * 10**5))

    for v in datadict.values():
        v.convert()
        datas.append(v)

    return datas

def getDCFieldVsFrequency(exp_ids = []):
    datas = []
    datadict = {}

    addStat(exp_ids)  
    result = getExpDetailInfo(exp_ids, Exp.dc_current)

    for exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats in result:
        key = MplXYPlotKey(patch.material_id, patch.proper_ar, exp_vna.source_power)
        if key not in datadict.keys():
            datadict[key] = MplXYPlotData()
        data = datadict[key]

        t = 0.7155417527999328 * mu_0 * exp_dc_coil.turn*exp.dc_current/exp_dc_coil.radius*1000
        #return t * 7.943 * 10**5
        data.append_x(t * 7.943 * 10**5)
        data.append_y(exp_smith_stats.max_imp_mag_freq)
        data.set_legend('%.2fx%.2f (%s) %.0fdBm' % (patch.width, patch.height, patch.name, exp_vna.source_power))

    for v in datadict.values():
        v.convert()
        datas.append(v)

    return datas

def getPatchARVsFrequency(exp_ids = []):
    datas = []
    datadict = {}

    addStat(exp_ids)  
    result = getExpDetailInfo(exp_ids, ExpPatchInfo.width)

    for exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats in result:
        key = MplXYPlotKey(exp.dc_current, patch.material_id, exp_vna.source_power)
        if key not in datadict.keys():
            datadict[key] = MplXYPlotData()
        data = datadict[key]

        data.append_x(patch.proper_ar)
        data.append_y(exp_smith_stats.max_imp_mag_freq)
        data.set_legend('%.2fx%.2f (%s) %.0fdBm' % (patch.width, patch.height, patch.name, exp_vna.source_power))

    for v in datadict.values():
        v.convert()
        datas.append(v)

    return datas

def getPatchARVsImpedance(exp_ids = []):
    datas = []
    datadict = {}

    addStat(exp_ids)  
    result = getExpDetailInfo(exp_ids, ExpPatchInfo.width)

    for exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats in result:
        key = MplXYPlotKey(exp.dc_current, patch.material_id, exp_vna.source_power)
        if key not in datadict.keys():
            datadict[key] = MplXYPlotData()
        data = datadict[key]

        data.append_x(patch.proper_ar)
        data.append_y(exp_smith_stats.max_imp_mag)
        data.set_legend('%.2fx%.2f (%s) %.0fdBm, %.2f' % (patch.width, patch.height, patch.name, exp_vna.source_power, exp_smith_stats.max_imp_mag_freq))

    for v in datadict.values():
        v.convert()
        datas.append(v)

    return datas

ExpListColumnDefn = [
    ColumnDefn("ID", "right", 60, "id"),
    ColumnDefn("Date", "center", 80, "date"),
    ColumnDefn("AC Coil#", "right", 30, "ac_coil_id"),
    ColumnDefn("Patch Info", "left", 170, "patch_info_as_string"),
    #ColumnDefn("DC Field", "right", 80, "dc_field", stringConverter="%.2f Oe"),
    ColumnDefn("Max Mag(z)", "right", 80, "max_imp_mag", stringConverter="%.2f Ohm"),
    ColumnDefn("Max Mag(z)@", "right", 80, "max_imp_mag_freq", stringConverter="%.2f Hz"),
    ColumnDefn("Surrounding Mat", "right", 80, "vis_name"),
    #ColumnDefn("Patch Ori", "center", 40, "patch_grain_orientation"),
    ColumnDefn("DC Current", "center", 70, "dc_current", stringConverter="%.2f A"),
    ColumnDefn("DC F (Cal)", "center", 70, "dc_field_cal", stringConverter="%.1f A/m"),
    ColumnDefn("Source Power", "left", 80, "source_power", stringConverter="%.2f dBm"),
    ColumnDefn("# of pts", "center", 50, "number_of_points"),
    ColumnDefn("Sweep Time", "center", 50, "sweep_time_as_sec", stringConverter="%.3f s"),
    ColumnDefn("Comment", "left", 250, "comment"),
]

mu_0 = 4 * math.pi * 10 ** -7

class ExpListItem(object):
    def __init__(self,\
            id, exp_date, dc_current, dc_field, vis_name, material_name, number_of_points, source_power, sweep_time, \
            patch_id, patch_width, patch_height, patch_grain_orientation,\
            ac_coil_id, \
            dc_coil_id, dc_coil_radius, dc_coil_wire_diameter, dc_coil_turn, \
            patch_included, \
            max_imp_re, max_imp_re_freq, \
            max_imp_im, max_imp_im_freq, \
            max_imp_mag, max_imp_mag_freq, \
            max_adm_re, max_adm_re_freq, \
            max_adm_im, max_adm_im_freq, \
            max_adm_mag, max_adm_mag_freq, \
            imp_q_freq0, imp_q_freq1, \
            adm_q_freq0, adm_q_freq1, \
            max_imp_parallel_ind, \
            comment
        ):
        self.id = id
        self.exp_date = exp_date
        self.dc_current = dc_current
        self.dc_field = dc_field
        self.vis_name = vis_name
        self.material_name = material_name
        self.number_of_points = number_of_points
        self.source_power = source_power
        self.sweep_time = sweep_time
        self.patch_id = patch_id
        self.patch_width = patch_width
        self.patch_height = patch_height
        self.patch_grain_orientation = patch_grain_orientation
        self.ac_coil_id = ac_coil_id
        self.dc_coil_id = dc_coil_id
        self.dc_coil_radius = dc_coil_radius
        self.dc_coil_wire_diameter = dc_coil_wire_diameter
        self.dc_coil_turn = dc_coil_turn
        self.patch_included = patch_included
        self.max_imp_re = max_imp_re
        self.max_imp_re_freq = max_imp_re_freq
        self.max_imp_im = max_imp_im
        self.max_imp_im_freq = max_imp_im_freq
        self.max_imp_mag = max_imp_mag
        self.max_imp_mag_freq = max_imp_mag_freq
        self.max_adm_re = max_adm_re
        self.max_adm_re_freq = max_adm_re_freq
        self.max_adm_im = max_adm_im
        self.max_adm_im_freq = max_adm_im_freq
        self.max_adm_mag = max_adm_mag
        self.imp_q_freq0 = imp_q_freq0
        self.imp_q_freq1 = imp_q_freq1
        self.adm_q_freq0 = adm_q_freq0
        self.adm_q_freq1 = adm_q_freq1
        self.max_imp_parallel_ind = max_imp_parallel_ind
        self.max_adm_mag = max_adm_mag
        self.comment = comment

    @property 
    def dc_field_cal(self):
        t = 0.7155417527999328 * mu_0 * self.dc_coil_turn*self.dc_current/self.dc_coil_radius*1000
        return t * 7.943 * 10**5
        #return self.dc_coil_turn*self.dc_current/self.dc_coil_radius * 32 * math.pi / (5 *math.sqrt(5)*self.dc_coil_radius) * 10**-7

    @property 
    def date(self):
        return self.exp_date.strftime('%Y-%m-%d')

    @property 
    def sweep_time_as_sec(self):
        return self.sweep_time / 100

    @property 
    def patch_info_as_string(self):
        #return "[%d] %s %0.2fx%0.2fmm (%d)" % (self.patch_id, self.material_name, self.patch_width, self.patch_height, self.patch_grain_orientation)
        #print 
        if self.patch_included == 'Y':
            return "[#%d] %s %0.1fx%0.1fmm (%s)" % (self.patch_id, self.material_name, self.patch_width, self.patch_height, self.patch_grain_orientation)
        else:
            return "None"



def mapExpResult(exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats):
    if exp_smith_stats:
        item = ExpListItem(exp.id, exp.exp_date, exp.dc_current, exp.dc_field, exp_vis.name, patch.name,\
            exp_vna.number_of_points, exp_vna.source_power, exp_vna.sweep_time, \
            patch.patch_id, patch.width, patch.height, patch.grain_orientation,\
            exp_ac_coil.id,\
            exp_dc_coil.id, exp_dc_coil.radius, exp_dc_coil.wire_diameter, exp_dc_coil.turn, \
            exp.patch_included, \
            exp_smith_stats.max_imp_re, exp_smith_stats.max_imp_re_freq, \
            exp_smith_stats.max_imp_im, exp_smith_stats.max_imp_im_freq, \
            exp_smith_stats.max_imp_mag, exp_smith_stats.max_imp_mag_freq, \
            exp_smith_stats.max_adm_re, exp_smith_stats.max_adm_re_freq, \
            exp_smith_stats.max_adm_im, exp_smith_stats.max_adm_im_freq, \
            exp_smith_stats.max_adm_mag, exp_smith_stats.max_adm_mag_freq, \
            exp_smith_stats.imp_q_freq0, exp_smith_stats.imp_q_freq1, \
            exp_smith_stats.adm_q_freq0, exp_smith_stats.adm_q_freq1, \
            exp_smith_stats.max_imp_parallel_ind, \
            exp.comment
            )
    else:
        item = ExpListItem(exp.id, exp.exp_date, exp.dc_current, exp.dc_field, exp_vis.name, patch.name,\
            exp_vna.number_of_points, exp_vna.source_power, exp_vna.sweep_time, \
            patch.patch_id, patch.width, patch.height, patch.grain_orientation,\
            exp_ac_coil.id,\
            exp_dc_coil.id, exp_dc_coil.radius, exp_dc_coil.wire_diameter, exp_dc_coil.turn, \
            exp.patch_included, \
            0, 0, \
            0, 0, \
            0, 0, \
            0, 0, \
            0, 0, \
            0, 0, \
            0, 0, \
            0, 0, \
            0, \
            exp.comment
            )

    return item

ExpMaterialListColumnDefn = [
    ColumnDefn("Name", "right", 30, "material_name"),
    ColumnDefn("Young's Modulus, E (GPa)", "center", 80, "youngs_modulus", stringConverter="%.2f GPa"),
    ColumnDefn("Shear Modulus, G (GPa)", "left", 80, "shear_modulus", stringConverter="%.2f GPa"),
    ColumnDefn(u"Density, ρ (kg/m^3)", "right", 80, "density", stringConverter="%.2f kg/m^3"),
    ColumnDefn(u"Poisson's Ratio, ν", "left", 80, "poissons_ratio", stringConverter="%.4f"),
]

class ExpMaterialListItem(object):
    def __init__(self,\
            id, \
            name, \
            youngs_modulus, \
            shear_modulus, \
            poissons_ratio, \
            density, \
            comment, \
        ):
        self.id = id
        self.name = name
        self.youngs_modulus = youngs_modulus
        self.shear_modulus = shear_modulus
        self.poissons_ratio = poissons_ratio
        self.density = density
        self.comment = comment

ExpDCCoilListColumnDefn = [
    ColumnDefn("Name", "right", 30, "material_name"),
    ColumnDefn("R (mm)", "center", 80, "radius", stringConverter="%.2f mm"),
    ColumnDefn("Wire Dia (mm)", "left", 80, "wire_diameter", stringConverter="%.2f mm"),
    ColumnDefn("Turn", "right", 80, "turn", stringConverter="%d"),
    ColumnDefn("Info", "left", 80, "comment"),
]

class ExpDCCoilListItem(object):
    def __init__(self,\
            id, \
            radius, \
            wire_diameter, \
            turn, \
            comment, \
        ):
        self.id = id
        self.radius = radius
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment

ExpACCoilListColumnDefn = [
    ColumnDefn("Type", "right", 30, "type"),
    ColumnDefn("Width (mm)", "center", 80, "width", stringConverter="%.2f mm"),
    ColumnDefn("Height (mm)", "center", 80, "height", stringConverter="%.2f mm"),
    ColumnDefn("Length (mm)", "left", 80, "length", stringConverter="%.2f mm"),
    ColumnDefn(u"Wire Dia (mm)", "right", 80, "wire_diameter", stringConverter="%.2f"),
    ColumnDefn(u"Turn", "left", 80, "turn", stringConverter="%d"),
    ColumnDefn("Patch Info", "left", 80, "comment"),
]

class ExpACCoilListItem(object):
    def __init__(self,\
            id, \
            type, \
            width, \
            height, \
            length, \
            wire_diameter, \
            turn, \
            comment, \
        ):
        self.id = id
        self.type = type
        self.width = width
        self.height = height
        self.length = length
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment

ExpPatchColumnDefn = [
    ColumnDefn("Name", "right", 30, "material_name"),
    ColumnDefn("Young's Modulus, E (GPa)", "center", 80, "youngs_modulus", stringConverter="%.2f GPa"),
    ColumnDefn("Shear Modulus, G (GPa)", "left", 80, "shear_modulus", stringConverter="%.2f GPa"),
    ColumnDefn(u"Density, ρ (kg/m^3)", "right", 80, "density", stringConverter="%.2f kg/m^3"),
    ColumnDefn(u"Poisson's Ratio, ν", "left", 80, "poissons_ratio", stringConverter="%.4f"),
]

class ExpPatchListItem(object):
    def __init__(self,\
            id, \
            material_id, \
            name, \
            youngs_modulus, \
            shear_modulus, \
            poissons_ratio, \
            density, \
            grain_orientation, \
            width, \
            height, \
            material_comment, \
            patch_comment, \
        ):
        self.id = id
        self.name = name
        self.youngs_modulus = youngs_modulus
        self.shear_modulus = shear_modulus
        self.poissons_ratio = poissons_ratio
        self.density = density
        self.grain_orientation = grain_orientation
        self.width = width
        self.height = height
        self.material_comment = material_comment
        self.patch_comment = patch_comment
 
def mapPatchResult(patch_info):
    item = ExpPatchListItem(
        patch_info.patch_id, \
        patch_info.material_id, \
        patch_info.name, \
        patch_info.youngs_modulus, \
        patch_info.shear_modulus, \
        patch_info.poissons_ratio, \
        patch_info.density, \
        patch_info.grain_orientation, \
        patch_info.width, \
        patch_info.height, \
        patch_info.material_comment, \
        patch_info.patch_comment)
    return item

def mapMaterialResult(material):
    item = ExpMaterialListItem(
        material.id, \
        material.name, \
        material.youngs_modulus, \
        material.shear_modulus, \
        material.poissons_ratio, \
        material.density, \
        material.comment)
    return item
'''

        self.id = id
        self.type = type
        self.width = width
        self.height = height
        self.length = length
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment'''
def mapACCoilResult(ac_coil):
    item = ExpACCoilListItem(
        ac_coil.id, \
        ac_coil.type, \
        ac_coil.width, \
        ac_coil.height, \
        ac_coil.length, \
        ac_coil.wire_diameter, \
        ac_coil.turn, \
        ac_coil.comment)
    return item
'''

        self.id = id
        self.radius = radius
        self.wire_diameter = wire_diameter
        self.turn = turn
        self.comment = comment'''
def mapDCCoilResult(dc_coil):
    item = ExpDCCoilListItem(
        dc_coil.id, \
        dc_coil.radius, \
        dc_coil.wire_diameter, \
        dc_coil.turn, \
        dc_coil.comment)
    return item


def getAllMaterials():
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    
    result = \
        session.query(
            ExpMaterialProp
            ).all()
    mats = []
    for mat in result:
        data = mapMaterialResult(mat)
        mats.append(data)

    session.close()
    return mats

def getMaterialById(id):
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))

    result = \
        session.query(
            ExpMaterialProp
            ).filter(ExpMaterialProp.id == id).first()
    data = mapMaterialResult(result)

    session.close()
    return data

def getAllPatches():
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    
    result = \
        session.query(
            ExpPatchInfo
            ).all()
    pats = []
    for mat in result:
        data = mapPatchResult(mat)
        pats.append(data)

    session.close()
    return pats

def getAllACCoils():
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))

    result = \
        session.query(
            ExpACCoilProp
            ).all()
    mats = []
    for mat in result:
        data = mapACCoilResult(mat)
        mats.append(data)

    session.close()
    return mats

def getAllDCCoils():
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))

    result = \
        session.query(
            ExpDCCoilProp
            ).all()
    mats = []
    for mat in result:
        data = mapDCCoilResult(mat)
        mats.append(data)

    session.close()
    return mats

def getPatchIds(exp_ids = []):
    ids = []
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    
    result = session.query(Exp).group_by(Exp.patch_id).filter(Exp.id.in_(exp_ids)).all()
    for row in result:
        ids.append(row.patch_id)
    session.close()

    return ids

def getDCFields(exp_ids = []):
    ids = []
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    
    result = session.query(Exp).group_by(Exp.dc_current).filter(Exp.id.in_(exp_ids)).all()
    for row in result:
        ids.append(row.dc_current)
    session.close()

    return ids


def getACPowers(exp_ids = []):
    ids = []
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    result = session.query(ExpVNA).group_by(ExpVNA.source_power).filter(ExpVNA.exp_id.in_(exp_ids)).all()
    for row in result:
        ids.append(row.source_power)
    session.close()

    return ids

def getAllExpsQuery():

    result = \
        session.query(
            Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpPatchInfo, ExpSmithStats
            ).join(ExpVNA).join(ExpDCCoilProp).join(ExpACCoilProp).join(ExpVisProp).join(ExpPatchInfo, Exp.patch_id == ExpPatchInfo.patch_id).\
            outerjoin(ExpSmithStats)
            #filter(ExpSmith.imp_re.in_(func.max(ExpSmith.imp_re).select().group_by(ExpSmith.exp_id))).\
    return result

def addStat(exp_ids = [], force = False):
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    uncalculatedExpIds = []
    if not force:
        for exp_id in exp_ids:
            result = \
                session.query(ExpSmithStats).\
                    filter(ExpSmithStats.exp_id == exp_id).all()

            if not result:
                uncalculatedExpIds = exp_ids
            else:
                r = result[0]
                if not r.max_imp_mag:
                    uncalculatedExpIds.append(r.exp_id)
    else:
        uncalculatedExpIds = exp_ids
    
    session.close()
    if len(uncalculatedExpIds) > 0:
        calculateStatByExpIds(uncalculatedExpIds)

def getExpDetailInfo(exp_ids = [], order_by = None): 
    #addStat(exp_ids)  
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))


    result = \
        session.query(
            Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpVisProp, ExpPatchInfo, ExpSmithStats
            ).join(ExpVNA).join(ExpDCCoilProp).join(ExpACCoilProp).join(ExpVisProp).join(ExpPatchInfo, Exp.patch_id == ExpPatchInfo.patch_id).\
            outerjoin(ExpSmithStats).\
            filter(Exp.id.in_(exp_ids)).order_by(order_by).all()

    return result


def getExpDetailInfoByExpId(exp_id):   
    #addStat([exp_id])
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    
    result = \
        session.query(
            Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpVisProp, ExpPatchInfo, ExpSmithStats).\
            join(ExpVNA).\
            join(ExpDCCoilProp).\
            join(ExpACCoilProp).\
            join(ExpVisProp).\
            join(ExpPatchInfo, Exp.patch_id == ExpPatchInfo.patch_id).\
            outerjoin(ExpSmithStats).\
            filter(Exp.id == exp_id).first()
    session.close()

    return result

PatchInclusion = enum(WITHOUT_PATCH = 'without_patch', WITH_PATCH = 'with_patch', BOTH = 'both')

def getAllExps(patch_inclusion = PatchInclusion.BOTH, empty_only = False):
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))


    q = \
        session.query(
            Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpVisProp, ExpPatchInfo, ExpSmithStats).\
            join(ExpVNA).\
            join(ExpDCCoilProp).\
            join(ExpACCoilProp).\
            join(ExpVisProp).\
            join(ExpPatchInfo, Exp.patch_id == ExpPatchInfo.patch_id).\
            outerjoin(ExpSmithStats).\
            order_by(Exp.id.desc())

    if patch_inclusion == PatchInclusion.WITHOUT_PATCH:
        q = q.filter(Exp.patch_included == 'N')
    elif patch_inclusion == PatchInclusion.WITH_PATCH:
        q = q.filter(Exp.patch_included == 'Y')
    elif empty_only:
        q = q.filter(Exp.subtract_exp_id == None)

    result = q.all()
    exps = []
    for exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats in result:
        data = mapExpResult(exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats)
        exps.append(data)

    session.close()

    return exps


def setWOPatch(wo_patch_exp_id, w_patch_exp_ids):
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))


    q = session.query(Exp).order_by(Exp.id.desc())

    q = q.filter(Exp.patch_included == 'Y')
    q = q.filter(Exp.id.in_(w_patch_exp_ids))
        
    result = q.all()
    for row in result:
        row.subtract_exp_id = wo_patch_exp_id
        session.add(row)

    session.flush()
    session.close()

def getAllExpsByFilter(ac_coils = [], src_powers = [], dc_currents = []):
    """
    Get all records and return them
    """
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    #.filter(Exp.id.in_(exp_ids))
    q = \
        session.query(
            Exp, ExpVNA, ExpDCCoilProp, ExpACCoilProp, ExpVisProp, ExpPatchInfo, ExpSmithStats).\
            join(ExpVNA).\
            join(ExpDCCoilProp).\
            join(ExpACCoilProp).\
            join(ExpVisProp).\
            join(ExpPatchInfo, Exp.patch_id == ExpPatchInfo.patch_id).\
            outerjoin(ExpSmithStats).\
            order_by(Exp.id.desc())
    if ac_coils:
        q = q.filter(ExpACCoilProp.id.in_(ac_coils))
    if src_powers:
        q = q.filter(ExpVNA.source_power.in_(src_powers))
    if dc_currents:
        print dc_currents
        q = q.filter(Exp.dc_current.in_(dc_currents))
    result = q.all()
    exps = []
    for exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats in result:
        data = mapExpResult(exp, exp_vna, exp_dc_coil, exp_ac_coil, exp_vis, patch, exp_smith_stats)
        exps.append(data)

    session.close()

    return exps


def get_imp_re(exp_ids = []):
    datas = []
    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))
    for exp_id in exp_ids:
        smiths = session.query(ExpSmith).filter(ExpSmith.exp_id == exp_id).order_by(ExpSmith.freq).all()

        data = { 'x': [], 'y' : []}
        for row in smiths:
            data['x'].append(row.freq)
            data['y'].append(row.imp_re)
        data['x'] = np.array(data['x'])
        data['y'] = np.array(data['y'])
        datas.append(data)
        
    session.close()

    return datas

def deleteExps(exp_ids = []):  
    exp_ids = list(set(exp_ids))

    session = scoped_session(sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine))

    for exp_id in exp_ids:  
        session.query(ExpSmith).\
                filter(ExpSmith.exp_id == exp_id).delete(synchronize_session='fetch')
        session.query(ExpVNA).\
                filter(ExpVNA.exp_id == exp_id).delete(synchronize_session='fetch')
        session.query(Exp).\
                filter(Exp.id == exp_id).delete(synchronize_session='fetch')
        session.commit()

    session.close()

def getColumnByName(tables, column_name):
    cols = []
    if not isinstance(tables, list):
        tables = [tables]
    for table in tables:
        try:
            col = getattr(table, column_name)
            cols.append(col)
        except AttributeError:
            continue
    if len(cols) > 1:
        raise AttributeError('Column(%s) is duplicated' % (column_name))
    if len(cols) == 0:
        return None
    return cols[0]