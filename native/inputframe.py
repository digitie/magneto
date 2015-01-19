import wx
from deviceconfigdialog import DeviceConfigDialog
from core.util import Serial
import serial
import threading
from instruments.gpib import prologix
from instruments.vna import HP8751A, FrequencySweepModes
import time
from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpDCCoilProp, ExpPatchInfo, ExpMaterialProp, ExpVisProp
from db.schema import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core.listobject import *
import datetime

from core.labpid import Labpid
from instruments.powersupply import TwoChannelPowersupply

from inputworker import WorkerThread
from events import *
from pstestframe import PowerSupplyTestDialog

class VNAInputFrame(wx.Frame):

    def CreatePatchSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.noPatchCheck = wx.CheckBox(self.panel, label='Without Patch', pos=(90, -1))
        self.patchLabel = wx.StaticText(self.panel, wx.ID_ANY, '  Patch Type', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.patchChoice = wx.Choice(self.panel, -1, (100, 50))

        session = scoped_session(sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=engine))

        rows = session.query(ExpPatchInfo).order_by(ExpPatchInfo.patch_id).all()
        for row in rows:
            self.patchChoice.Append(('#%d - %s %.2fx%.2f (%s)' % \
            (row.patch_id, row.name, row.width, row.height, row.grainAsString)), row.patch_id)

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.patchLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.noPatchCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.patchChoice, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        session.close()

        return sizer

    def CreateDCCoilSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.dcCoilLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Coil Type', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.dcCoilChoice = wx.Choice(self.panel, -1, (100, 50))

        session = scoped_session(sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=engine))

        rows = session.query(ExpDCCoilProp).order_by(ExpDCCoilProp.id).all()
        for row in rows:
            self.dcCoilChoice.Append(
                ('#%d - %.1fR (%dturn of %.2fmm wire)' % \
            (row.id, row.radius, row.turn, row.wire_diameter)), 
            row.id)

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCoilLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCoilChoice, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateACCoilSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.acCoilLabel = wx.StaticText(self.panel, wx.ID_ANY, 'AC Coil Type', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.acCoilChoice = wx.Choice(self.panel, -1, (100, 50))

        session = scoped_session(sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=engine))

        rows = session.query(ExpACCoilProp).order_by(ExpACCoilProp.id).all()
        for row in rows:
            self.acCoilChoice.Append(('#%d - %.2fx%.2fx%.2f (%s) (%dturn of %.2fmm wire)' % \
            (row.id, row.width, row.height, row.length, row.typeAsString, row.turn, row.wire_diameter)), 
            row.id)

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.acCoilLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.acCoilChoice, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        session.close()

        return sizer

    def CreateEnvironmentSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.envLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Environment', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.envChoice = wx.Choice(self.panel, -1, (100, 50))

        session = scoped_session(sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=engine))

        rows = session.query(ExpVisProp).order_by(ExpVisProp.id).all()
        for row in rows:
            self.envChoice.Append(('#%d - %s' % \
            (row.id, row.name)), 
            row.id)

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.envLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.envChoice, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        session.close()

        return sizer

    def CreateSourcePowerSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.sourcePowerLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Source Power', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.sourcePowerBox = wx.CheckListBox(self.panel, -1, (50, 50))

        j = 0
        for i in range(15,-16,-1):
            self.sourcePowerBox.Insert(item = ('%d dBm' % (i)), pos = j)
            j += 1

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.sourcePowerLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.sourcePowerBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateDCCurrentSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.dcCurrentStartLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Current Start', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.dcCurrentStartText = wx.TextCtrl(self.panel, wx.ID_ANY, '')
        self.dcCurrentStepLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Current Step', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.dcCurrentStepText = wx.TextCtrl(self.panel, wx.ID_ANY, '')
        self.dcCurrentEndLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Current End', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.dcCurrentEndText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentStartLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentStartText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentStepLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentStepText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentEndLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentEndText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateDCFieldSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.dcFieldLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Field', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.dcFieldText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcFieldLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcFieldText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateTemperatureSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.tempLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Temperature', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.tempText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.tempLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.tempText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateCommentSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.commentLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Comment', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.commentText = wx.TextCtrl(self.panel, wx.ID_ANY, '', style=wx.TE_MULTILINE)

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.commentLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.commentText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateCenterFrequencySizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.centFreqLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Center Frequency', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.centFreqText = wx.TextCtrl(self.panel, wx.ID_ANY, '')
        self.freqSpanLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Span', size = (50, -1), style=wx.ALIGN_RIGHT)
        self.freqSpanText = wx.TextCtrl(self.panel, wx.ID_ANY, '')
        self.freq2ndSpanLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Span2', size = (50, -1), style=wx.ALIGN_RIGHT)
        self.freq2ndSpanText = wx.TextCtrl(self.panel, wx.ID_ANY, '')
        self.findCenterFreqBtn = wx.Button(self.panel, wx.ID_ANY, 'Find')

        self.Bind(wx.EVT_BUTTON, self.OnFindCenterFreqBtn, self.findCenterFreqBtn)

        sizer.Add(ico, 0, wx.ALL, 5)
        sizer.Add(self.centFreqLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.centFreqText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freqSpanLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freqSpanText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freq2ndSpanLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freq2ndSpanText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.findCenterFreqBtn, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def OnFindCenterFreqBtn(self, event):
        center_freq = self.vna.find_center_freq()
        self.centFreqText.SetValue(str(center_freq))
        self.freqSpanText.SetValue(str(20000))

    def __init__(self, parent):
        self.gpibserial = Serial()
        self.gpibserial.baudrate = 115200
        self.gpibserial.por = 'COM7'
        self.gpib = prologix()
        self.gpibserial.timeout = 0.5   #make sure that the alive event can be checked from time to time


        self.labpidserial = Serial()
        self.labpidserial.baudrate = 115200
        self.labpidserial.por = 'COM7'
        self.labpidserial.timeout = 0.5   #make sure that the alive event can be checked from time to time
        #self.settings = TerminalSetup() #placeholder for the settings
        self.parent = parent
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Form')
        # And indicate we don't have a worker thread yet
        self.worker = None
        self.src_powers = []

        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        #bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
        #titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        #title = wx.StaticText(self.panel, wx.ID_ANY, 'My Title')

        okBtn = wx.Button(self.panel, wx.ID_ANY, 'OK')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, 'Cancel')
        testPsBtn = wx.Button(self.panel, wx.ID_ANY, 'Test DC Powersupply')
        self.Bind(wx.EVT_BUTTON, self.OnStart, okBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)
        self.Bind(wx.EVT_BUTTON, self.OnTestPs, testPsBtn)

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        #titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        patchSizer   = self.CreatePatchSizer()
        acCoilSizer   = self.CreateACCoilSizer()
        dcCoilSizer   = self.CreateDCCoilSizer()
        envSizer   = self.CreateEnvironmentSizer()
        sourcePowerSizer   = self.CreateSourcePowerSizer()
        centerFreqSizer   = self.CreateCenterFrequencySizer()
        dcCurrentSizer   = self.CreateDCCurrentSizer()
        dcFieldSizer   = self.CreateDCFieldSizer()
        tempSizer   = self.CreateTemperatureSizer()
        commentSizer   = self.CreateCommentSizer()
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

        #titleSizer.Add(titleIco, 0, wx.ALL, 5)
        #titleSizer.Add(title, 0, wx.ALL, 5)

        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
        btnSizer.Add(testPsBtn, 0, wx.ALL, 5)

        #topSizer.Add(titleSizer, 0, wx.CENTER)
        #topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(patchSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(acCoilSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(dcCoilSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(envSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(sourcePowerSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(centerFreqSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(dcCurrentSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(dcFieldSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(tempSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(commentSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Bind(EVT_HP8751A_COMPLETED, self.OnComplete)
        self.Bind(EVT_HP8751A_PROGRESS, self.OnProgress)
        self.Bind(EVT_HP8751A_CANCELED, self.OnCanceled)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnSourcePowerListBox, self.sourcePowerBox)        
        self.Bind(wx.EVT_CHECKBOX, self.OnWithoutPatchCheck)
        #self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
        self.OnPortSettings(None)       #call setup dialog on startup, opens port
        #if not self.worker.isAlive():
        #    self.Close()

    def OnWithoutPatchCheck(self, event):
        state = self.noPatchCheck.GetValue()
        if state:
            self.patchChoice.Enable(False)
        else:
            self.patchChoice.Enable(True)

    def OnCanceled(self, event):  
        self.worker = None  
        dlg = wx.MessageDialog(self, event.data['message'],
                               event.data['title'],
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()    
        self.progress.Destroy()

    def OnSourcePowerListBox(self, event):
        index = event.GetSelection()
        if self.sourcePowerBox.IsChecked(index):
            self.src_powers.append(index)
        else:
            self.src_powers.remove(index)
        self.sourcePowerBox.SetSelection(index)    # so that (un)checking also selects (moves the highlight)
        

    def OnPortSettings(self, event=None):
        """Show the portsettings dialog. The reader thread is stopped for the
           settings change."""
        if event is not None:           #will be none when called on startup
            #self.StopThread()
            self.worker.abort()
            self.gpibserial.close()
            self.labpidserial.close()
        ok = False
        while not ok:

            dialog_serial_cfg = DeviceConfigDialog(None, -1, "", gpib=self.gpibserial, labpid=self.labpidserial)
            result = dialog_serial_cfg.ShowModal()
            dialog_serial_cfg.Destroy()
            #open port if not called on startup, open it on startup and OK too
            if result == wx.ID_OK or event is not None:
                try:
                    self.gpibserial.open()
                    self.gpib.bus = self.gpibserial
                    self.gpib.init_gpib()
                    self.vna = HP8751A(self.gpib, 17, delay = 0.3, auto = False)
                except serial.SerialException, e:
                    dlg = wx.MessageDialog(None, str(e), "GPIB Serial Port Error", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()

                try:
                    self.labpidserial.open()
                    self.labpid = Labpid(bus = self.labpidserial)
                    self.ps = TwoChannelPowersupply(self.labpid, 0)
                except serial.SerialException, e:
                    dlg = wx.MessageDialog(None, str(e), "Labpid Serial Port Error", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    #self.StartThread()
                    self.SetTitle("GPIB Device (HP8751A) on %s [%s, %s%s%s%s%s]" % (
                        self.gpibserial.portstr,
                        self.gpibserial.baudrate,
                        self.gpibserial.bytesize,
                        self.gpibserial.parity,
                        self.gpibserial.stopbits,
                        self.gpibserial.rtscts and ' RTS/CTS' or '',
                        self.gpibserial.xonxoff and ' Xon/Xoff' or '',
                        )
                    )
                    ok = True
            else:
                #on startup, dialog aborted
                if self.worker:
                    self.worker.abort()
                ok = True

    def OnTestPs(self, event):
        dlg = PowerSupplyTestDialog(self, self.ps)
        dlg.ShowModal()
        dlg.Destroy()

    def OnStart(self, event):
        """Start Computation."""
        if len(self.src_powers) == 0:            
            dlg = wx.MessageDialog(None, "Select one VNA Source Power at least", "Invalid Value.", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.dcCoilChoice.GetSelection() == wx.NOT_FOUND:
            dlg = wx.MessageDialog(None, "Select DC Coil", "Invalid Value.", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.acCoilChoice.GetSelection() == wx.NOT_FOUND:
            dlg = wx.MessageDialog(None, "Select AC Coil", "Invalid Value.", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        state = self.noPatchCheck.GetValue()
        if not state:
            if self.patchChoice.GetSelection() == wx.NOT_FOUND:
                dlg = wx.MessageDialog(None, "Select Patch", "Invalid Value.", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            #self.status.SetLabel('Starting computation')
            self.worker = WorkerThread(self, self.vna, self.ps)
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