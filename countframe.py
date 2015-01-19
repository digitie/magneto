import wx
import wxSerialConfigDialog
from core.util import Serial
import serial
from core.listobject import *

from core.labpid import Labpid
from struct import *


class FunctionGeneratorFrame(wx.Frame):
    def CreateFrequencySizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.freqLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Frequency', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.freqText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freqLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.freqText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateCountSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.countLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Count', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.countText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.countLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.countText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def OnStartBtn(self, event):
        count = self.countText.GetValue()
        try:
            count = int(count)
        except ValueError:
            dlg = wx.MessageDialog(None, str(e), "Count Value Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        pkt = pack('>l', count)
        self.labpid.sendData(1, 16, 4, pkt)
        self.labpid.getData()

    def OnResetBtn(self, event):
        self.labpid.sendData(1, 17, 0, None)
        self.labpid.getData()


    def __init__(self, parent):
        self.serial = Serial()
        self.serial.baudrate = 921600
        self.serial.por = 'COM7'
        self.labpid = None
        self.serial.timeout = 0.5   #make sure that the alive event can be checked from time to time
        #self.settings = TerminalSetup() #placeholder for the settings
        self.parent = parent
        wx.Frame.__init__(self, None, wx.ID_ANY, title='My Form')
        # And indicate we don't have a worker thread yet

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

        #self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
        self.OnPortSettings(None)       #call setup dialog on startup, opens port
        #if not self.worker.isAlive():
        #    self.Close()


    def OnPortSettings(self, event=None):
        """Show the portsettings dialog. The reader thread is stopped for the
           settings change."""
        if event is not None:           #will be none when called on startup
            #self.StopThread()
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
                    self.serial.baudrate = 921600
                    self.labpid = Labpid(bus = self.serial)
                except serial.SerialException, e:
                    dlg = wx.MessageDialog(None, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    #self.StartThread()
                    self.SetTitle("LABPID Device on %s [%s, %s%s%s%s%s]" % (
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
                ok = True



# Run the program
if __name__ == '__main__':

    engine.echo = True
    app = wx.PySimpleApp()
    frame = FunctionGeneratorFrame(None).Show()
    app.MainLoop()