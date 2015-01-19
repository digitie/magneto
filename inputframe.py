import wx
import wxSerialConfigDialog
from core.util import Serial
import serial
import threading
from instruments.gpib import prologix
from instruments.vna import HP8751A, FrequencySweepModes
import time
from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchInfo, ExpMaterialProp
from db.schema import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core.listobject import *
import datetime




HP8751A_COMPLETED = wx.NewEventType()
# bind to serial data receive events
EVT_HP8751A_COMPLETED = wx.PyEventBinder(HP8751A_COMPLETED, 0)

class HP8751ACompletedEvent(wx.PyCommandEvent):
    eventType = HP8751A_COMPLETED
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

HP8751A_CANCELED = wx.NewEventType()
# bind to serial data receive events
EVT_HP8751A_CANCELED = wx.PyEventBinder(HP8751A_CANCELED, 0)

class HP8751ACanceledEvent(wx.PyCommandEvent):
    eventType = EVT_HP8751A_CANCELED
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data

    def Clone(self):
        self.__class__(self.GetId(), self.data)

HP8751A_PROGRESS = wx.NewEventType()
# bind to serial data receive events
EVT_HP8751A_PROGRESS = wx.PyEventBinder(HP8751A_PROGRESS, 0)

class HP8751AProgressEvent(wx.PyCommandEvent):
    eventType = HP8751A_PROGRESS
    def __init__(self, windowID, message, step):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.step = step
        self.message = message

    def Clone(self):
        self.__class__(self.GetId(), self.message, self.step)

# Thread class that executes processing
class WorkerThread(threading.Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, vna):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self._notify_window = notify_window
        self._vna = vna
        self.alive = threading.Event() 
        self.alive.set()
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        selections = self._notify_window.src_powers
        selections.sort(reverse=True)
        per_max = float(100)/len(selections)
        center_freq = float(self._notify_window.centFreqText.GetValue())
        freq_span = float(self._notify_window.freqSpanText.GetValue())
        current_step = 0

        wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Setting Center Frequency %d Hz of span %d Hz...' % (center_freq, freq_span), current_step))
        self._vna.set_frequency_span(center = center_freq, span = freq_span)
        if not self.alive.isSet():
            wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
            return    
                
        datas = []
        #while True:
        try:
            session = scoped_session(sessionmaker(
                autoflush=False,
                autocommit=False,
                bind=engine))
            
            for i in selections:
                src_power = 15 - i
                per_step = per_max / 7
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Setting Source Power as %d dBm...' % src_power, current_step))
                self._vna.source_power = src_power
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return


                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Auto Scaling...', current_step))
                self._vna.autoscale()
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Settings Number of Points as 801 ...', current_step))
                self._vna.number_of_points = 801
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                for i in range(5):
                    time.sleep(0.1)
                    if not self.alive.isSet():
                        wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                        return

                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Settings Sweep mode as Single ...', current_step))
                self._vna.sweep_mode = FrequencySweepModes.SINGLE
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                for i in range(5):
                    time.sleep(0.1)
                    if not self.alive.isSet():
                        wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                        return

                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Reading Impedance data ...', current_step))
                freq, re, im, imp_re, imp_im = self._vna.read_impedance()
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Saving ...', current_step))
                exp = Exp(
                    ac_coil_id = self._notify_window.acCoilChoice.GetClientData(self._notify_window.acCoilChoice.GetSelection()),
                    dc_coil_id = self._notify_window.dcCoilChoice.GetClientData(self._notify_window.dcCoilChoice.GetSelection()),
                    patch_id = self._notify_window.patchChoice.GetClientData(self._notify_window.patchChoice.GetSelection()),
                    exp_date = datetime.date.today(),
                    dc_current = float(self._notify_window.dcCurrentText.GetValue()),
                    dc_field = float(self._notify_window.dcFieldText.GetValue()),
                    comment = self._notify_window.commentText.GetValue()
                )
                session.add(exp)
                session.flush()

                vna_data = []
                for freq, re, im in zip(freq, re, im):
                    smith = ExpSmith(exp.id, freq, re, im)
                    vna_data.append(smith)

                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                vna_properties = ExpVNA(
                    exp.id,
                    float(0), 
                    self._vna.number_of_points, 
                    'SMITH CHART', 
                    self._vna.sweep_type, 
                    int(1), 
                    float(src_power), 
                    'A/R', 
                    float(self._vna.sweep_time) * 100
                )
                session.add(vna_properties)
                session.add_all(vna_data)


                datas.append(exp.id)

                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                current_step += per_step
                wx.PostEvent(self._notify_window, HP8751AProgressEvent(-1, 'Finalizing ...', current_step))
                self._vna.sweep_mode = FrequencySweepModes.CONTINUOUS
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                self._vna.number_of_points = 101
                if not self.alive.isSet():
                    wx.PostEvent(self._notify_window, HP8751ACanceledEvent(-1, None))
                    return

                # Here's where the result would be returned (this is an
                # example fixed result of the number 10, but it could be
                # any Python object)
                #freq = np.array(freq)
                #imp_re = np.array(imp_re)
                #imp_re = imp_re * 50
            session.commit()
            session.flush()
            session.close()
        except Exception as e:
            print e
            session.rollback()
            session.flush()
            session.close()
            wx.PostEvent(self._notify_window, HP8751ACompletedEvent(-1, None))
            return

        wx.PostEvent(self._notify_window, HP8751ACompletedEvent(-1, None))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self.alive.clear()

    def isAlive(self):
        # Method for use by main thread to signal an abort
        return self.alive.isSet() == False

class FunctionGeneratorFrame(wx.Frame):
    def CreateFrequencySizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.freqLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Field', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.freqText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freqLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freqText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateCountSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.countLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Field', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.countText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.countLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.countText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def OnStartBtn(self, event):
        center_freq = self.vna.find_center_freq()
        self.centFreqText.SetValue(str(center_freq))
        self.freqSpanText.SetValue(str(20000))

    def OnResetBtn(self, event):
        center_freq = self.vna.find_center_freq()
        self.centFreqText.SetValue(str(center_freq))
        self.freqSpanText.SetValue(str(20000))

    def __init__(self, parent):
        self.serial = Serial()
        self.serial.baudrate = 921600
        self.serial.por = 'COM7'
        self.gpib = prologix()
        self.serial.timeout = 0.5   #make sure that the alive event can be checked from time to time
        #self.settings = TerminalSetup() #placeholder for the settings
        self.parent = parent
        wx.Frame.__init__(self, None, wx.ID_ANY, title='My Form')
        # And indicate we don't have a worker thread yet
        self.worker = None
        self.src_powers = []

        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
        titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        title = wx.StaticText(self.panel, wx.ID_ANY, 'My Title')

        startBtn = wx.Button(self.panel, wx.ID_ANY, 'Start')
        resetBtn = wx.Button(self.panel, wx.ID_ANY, 'Reset')
        self.Bind(wx.EVT_BUTTON, self.OnStartBtn, startBtn)
        self.Bind(wx.EVT_BUTTON, self.OnResetBtn, resetBtn)

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        frequencySizer   = self.CreateFrequencySizer()
        countSizer   = self.CreateCountSizer()
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer.Add(titleIco, 0, wx.ALL, 5)
        titleSizer.Add(title, 0, wx.ALL, 5)

        btnSizer.Add(startBtn, 0, wx.ALL, 5)
        btnSizer.Add(resetBtn, 0, wx.ALL, 5)

        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(frequencySizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(countSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Bind(EVT_HP8751A_COMPLETED, self.OnComplete)
        self.Bind(EVT_HP8751A_PROGRESS, self.OnProgress)
        #self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
        self.OnPortSettings(None)       #call setup dialog on startup, opens port
        #if not self.worker.isAlive():
        #    self.Close()


    def OnPortSettings(self, event=None):
        """Show the portsettings dialog. The reader thread is stopped for the
           settings change."""
        if event is not None:           #will be none when called on startup
            #self.StopThread()
            self.worker.abort()
            self.serial.close()
        ok = False
        while not ok:
            dialog_serial_cfg = wxSerialConfigDialog.SerialConfigDialog(None, -1, "",
                show=wxSerialConfigDialog.SHOW_BAUDRATE|wxSerialConfigDialog.SHOW_FORMAT|wxSerialConfigDialog.SHOW_FLOW,
                serial=self.serial
            )
            result = dialog_serial_cfg.ShowModal()
            dialog_serial_cfg.Destroy()
            #open port if not called on startup, open it on startup and OK too
            if result == wx.ID_OK or event is not None:
                try:
                    self.serial.open()
                    self.gpib.bus = self.serial
                    self.gpib.init_gpib()
                    self.vna = HP8751A(self.gpib, 17, delay = 0.3, auto = False)
                except serial.SerialException, e:
                    dlg = wx.MessageDialog(None, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    #self.StartThread()
                    self.SetTitle("GPIB Device (HP8751A) on %s [%s, %s%s%s%s%s]" % (
                        self.serial.portstr,
                        self.serial.baudrate,
                        self.serial.bytesize,
                        self.serial.parity,
                        self.serial.stopbits,
                        self.serial.rtscts and ' RTS/CTS' or '',
                        self.serial.xonxoff and ' Xon/Xoff' or '',
                        )
                    )
                    ok = True
            else:
                #on startup, dialog aborted
                if self.worker:
                    self.worker.abort()
                ok = True

    def OnStart(self, event):
        """Start Computation."""
        if len(self.src_powers) == 0:
            return
        if self.dcCoilChoice.GetSelection() == wx.NOT_FOUND:
            return
        if self.acCoilChoice.GetSelection() == wx.NOT_FOUND:
            return
        if self.patchChoice.GetSelection() == wx.NOT_FOUND:
            return
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            #self.status.SetLabel('Starting computation')
            self.worker = WorkerThread(self, self.vna)
            max = 100

            self.progress = wx.ProgressDialog("Measurement in Progress",
                                   "Preparing ...",
                                   maximum = max,
                                   parent=self,
                                   style = 0
                                    | wx.PD_APP_MODAL
                                    | wx.PD_CAN_ABORT
                                    #| wx.PD_CAN_SKIP
                                    #| wx.PD_ELAPSED_TIME
                                    | wx.PD_ESTIMATED_TIME
                                    | wx.PD_REMAINING_TIME
                                    #| wx.PD_AUTO_HIDE
                                    )

    def OnProgress(self, event):
        self.progress.Update(event.step, event.message)

    def OnStop(self, event):
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            self.progress.Destroy()
            self.worker.abort()

    def OnComplete(self, event):
        """Show Result status."""
        # Process results here
        #self.status.SetLabel('Computation Result: %s' % event.data)
        # In either event, the worker is done
        self.progress.Destroy()
        self.worker = None
        self.parent.setData()

    def onCancel(self, event):
        self.closeProgram()

    def closeProgram(self):
        self.Close()


# Run the program
if __name__ == '__main__':

    engine.echo = True
    app = wx.PySimpleApp()
    frame = VNAInputFrame().Show()
    app.MainLoop()