import wx
from events import *
import threading
from instruments.gpib import prologix
from instruments.vna import HP8751A, FrequencySweepModes
from instruments.powersupply import ChannelTypes
import time
from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchInfo, ExpMaterialProp
from db.schema import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core.listobject import *
import datetime
from core.log import MainLogger

import pylab as pl


# Thread class that executes processing
class WorkerThread(threading.Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, vna, ps):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.notifyWindow = notify_window
        self.vna = vna
        self.ps = ps
        self.current_step = 0
        self.logger = MainLogger
        self.alive = threading.Event() 
        self.alive.set()
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def getExpParameters(self):
        self.center_freq = float(self.notifyWindow.centFreqText.GetValue())
        self.freq_span = float(self.notifyWindow.freqSpanText.GetValue())
        self.center_2nd_freq = self.center_freq
        self.freq_2nd_span = float(self.notifyWindow.freq2ndSpanText.GetValue())
        if self.center_2nd_freq and self.freq_2nd_span:
            self.measureTwice = True
        else:
            self.measureTwice = False
        self.dc_power_start = float(self.notifyWindow.dcCurrentStartText.GetValue())
        self.dc_power_step = float(self.notifyWindow.dcCurrentStepText.GetValue())
        self.dc_power_end = float(self.notifyWindow.dcCurrentEndText.GetValue())
        self.temperature = float(self.notifyWindow.tempText.GetValue())
        self.patch_included = 'N' if self.notifyWindow.noPatchCheck.GetValue() else 'Y'
        self.dc_currents = pl.frange(self.dc_power_start, self.dc_power_end, self.dc_power_step).tolist()
        self.selections = self.notifyWindow.src_powers
        self.selections.sort(reverse=True)

    def checkAbort(self):
        if not self.alive.isSet():
            wx.PostEvent(self.notifyWindow, HP8751ACanceledEvent(-1, {'title':'Progress cancelled', 'message':'Progress is cancelled by user'}))
            self.ps.disable(ChannelTypes.CH1)
            return True
        else:
            return False

    def getProgressStep(self):
        self.current_step += 1
        return self.current_step

    def setVNASourcePower(self, dc_current, src_power):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, '(%.3f) Setting Source Power as %d dBm...' % (dc_current, src_power), self.getProgressStep())
        )
        self.vna.source_power = src_power
        if self.checkAbort():
            return False

        return True

    def setAutoScale(self, dc_current):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, '(%.3f) Auto Scaling...' % (dc_current), self.getProgressStep())
        )
        self.vna.autoscale()
        if self.checkAbort():
            return False

        return True

    def setNumberOfPoints(self, dc_current, num):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, '(%.3f) Settings Number of Points as 801 ...' % (dc_current), self.getProgressStep())
        )
        self.vna.number_of_points = num
        if self.checkAbort():
            return False

        return True
        
    def setSweepModeAsSingle(self, dc_current):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, '(%.3f) Settings Sweep mode as Single ...' % (dc_current), self.getProgressStep())
        )
        self.vna.sweep_mode = FrequencySweepModes.SINGLE
        if self.checkAbort():
            return False

        return True
        
    def setSweepModeAsCont(self, dc_current):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, '(%.3f) Settings Sweep mode as Continuous ...' % (dc_current), self.getProgressStep())
        )
        self.vna.sweep_mode = FrequencySweepModes.CONTINUOUS
        if self.checkAbort():
            return False

        return True

    def setDcCurrent(self, dc_current):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, 'Setting DC Current as %f mA...' % dc_current, self.getProgressStep())
        )
        self.ps.setCurrent(ChannelTypes.CH1, dc_current)
        if self.checkAbort():
            return False

        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, 'Setting DC Voltage as %f V...' % dc_current * 20, self.getProgressStep())
        )
        self.ps.setVoltage(ChannelTypes.CH1, dc_current * 20)

        if self.checkAbort():
            return False

        return True

    def setCenterFrequency(self, center_freq, freq_span):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, 'Setting Center Frequency %d Hz of span %d Hz...' % (self.center_freq, self.freq_span), self.getProgressStep())
        )
        self.vna.set_frequency_span(center = center_freq, span = freq_span)
        if self.checkAbort():
            return False

        return True

    def setSweepTime(self, sweep_time):
        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, 'Setting Sweep Time as %fs...' % (sweep_time), self.getProgressStep())
        )
        self.vna.sweep_time = sweep_time
        if self.checkAbort():
            return False

        return True

    def wait(self, num):        
        for i in range(num):
            time.sleep(0.1)
            if self.checkAbort():
                return False

        return True

    def prepareVNA(self, dc_current, src_power):                    
        if not self.setVNASourcePower(dc_current, src_power): # +1
            return False

        if not self.setAutoScale(dc_current): # +1
            return False

        # wait for settle
        if not self.wait(10):
            return False

        if not self.setNumberOfPoints(dc_current, 801): # +1
            return False

        # wait for settle
        if not self.wait(10):
            return False

        return True

    def saveVNAData(self, session, dc_current, src_power, center_freq, freq_span):
        sweep_time = 34
        wait_time = int(sweep_time * 0.6)
        
        if not self.setCenterFrequency(center_freq, freq_span): # +1
            return False

        if not self.setSweepTime(float(sweep_time)/10):
            return False

        # wait for settle
        if not self.wait(wait_time):
            return False

        if not self.setSweepModeAsSingle(dc_current): # +1
            return False

        # wait for settle
        if not self.wait(wait_time):
            return False

        wx.PostEvent(
            self.notifyWindow, 
            HP8751AProgressEvent(-1, '(%.3f) Reading Impedance data ...' % (dc_current), self.getProgressStep())
        )
        freq, re, im, imp_re, imp_im = self.vna.read_impedance() # +1
        if self.checkAbort():
            return False

        if not self.saveToDatabase(session, dc_current, src_power, freq, re, im): # +1
            return False
        
        if not self.setSweepModeAsCont(dc_current): # +1
            return False
        # wait for settle

        if not self.wait(wait_time):
            return False

        return True

    def saveToDatabase(self, session, dc_current, src_power, freq, re, im):
        wx.PostEvent(self.notifyWindow, HP8751AProgressEvent(-1, '(%.3f) Saving ...' % (dc_current), self.getProgressStep()))
        if self.notifyWindow.noPatchCheck.GetValue():
            patch_id = 1
        else:
            patch_id = self.notifyWindow.patchChoice.GetClientData(self.notifyWindow.patchChoice.GetSelection())
        exp = Exp(
            ac_coil_id = self.notifyWindow.acCoilChoice.GetClientData(self.notifyWindow.acCoilChoice.GetSelection()),
            dc_coil_id = self.notifyWindow.dcCoilChoice.GetClientData(self.notifyWindow.dcCoilChoice.GetSelection()),
            patch_id = patch_id,
            vis_id = self.notifyWindow.envChoice.GetClientData(self.notifyWindow.envChoice.GetSelection()),
            temperature = self.temperature,
            exp_date = datetime.date.today(),
            dc_current = dc_current,
            dc_field = float(self.notifyWindow.dcFieldText.GetValue()),
            comment = self.notifyWindow.commentText.GetValue(),
            patch_included = self.patch_included
        )
        session.add(exp)
        session.flush()

        vna_data = []
        for freq, re, im in zip(freq, re, im):
            smith = ExpSmith(exp.id, freq, re, im)
            vna_data.append(smith)

        if self.checkAbort():
            return False

        vna_properties = ExpVNA(
            exp.id,
            float(0), 
            self.vna.number_of_points, 
            'SMITH CHART', 
            self.vna.sweep_type, 
            int(1), 
            float(src_power), 
            'A/R', 
            float(self.vna.sweep_time) * 100
        )
        session.add(vna_properties)
        session.add_all(vna_data)

        if self.checkAbort():
            return False

        return True

    def run(self):
        self.getExpParameters()
        per_max = float(100) / (len(self.selections) * len(self.dc_currents))

        try:
            wx.PostEvent(self.notifyWindow, HP8751AProgressEvent(-1, 'Output Enabling Power Supply', 0))
            self.ps.enable(ChannelTypes.CH1)
            current = 0.05
            self.setDcCurrent(current)
        except Exception as e:
            wx.PostEvent(self.notifyWindow, HP8751ACanceledEvent(-1, {'title':'Power supply operation failed', 'message':str(e)}))
            return

        self.checkAbort()
                
        try:
            per_step = per_max / 17
            for dc_current in self.dc_currents:
                self.logger.debug("DC Current %f" %(dc_current))
                dc_current = round(dc_current, 3)
                session = scoped_session(sessionmaker(
                    autoflush=False,
                    autocommit=False,
                    bind=engine))
                
                self.setDcCurrent(dc_current) # +2

                for i in self.selections:
                    src_power = 15 - i
                    if self.checkAbort():
                        return

                    if not self.prepareVNA(dc_current, src_power):
                        return

                    if not self.saveVNAData(session, dc_current, src_power, self.center_freq, self.freq_span): # +5
                        return

                    if self.measureTwice:
                        # wait for settle
                        if not self.wait(10):
                            return False
                        if not self.saveVNAData(session, dc_current, src_power, self.center_2nd_freq, self.freq_2nd_span): # +5
                            return

                if not self.setNumberOfPoints(dc_current, 101): # +1
                    return

                # wait for settle
                if not self.wait(10):
                    return False

                session.commit()
                session.flush()
                session.close()
        except Exception as e:
            session.rollback()
            session.flush()
            session.close()
            self.ps.disable(ChannelTypes.CH1)
            wx.PostEvent(self.notifyWindow, HP8751ACanceledEvent(-1, {'title':'Operation failed', 'message':str(e)}))
            return

        self.ps.disable(ChannelTypes.CH1)
        wx.PostEvent(self.notifyWindow, HP8751ACompletedEvent(-1, None))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self.alive.clear()

    def isAlive(self):
        # Method for use by main thread to signal an abort
        return self.alive.isSet() == False