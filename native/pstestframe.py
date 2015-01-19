import wx

from instruments.powersupply import ChannelTypes


class PowerSupplyTestDialog(wx.Dialog):
    def CreateVoltageSizer(self):
        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.voltageLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Voltage (V)', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.voltageText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.voltageLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.voltageText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateCurrentSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.currentLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Current (A)', size = (90, -1), style=wx.ALIGN_RIGHT)
        self.currentText = wx.TextCtrl(self.panel, wx.ID_ANY, '')

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.currentLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.currentText, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def OnSetBtn(self, event):
        voltage = self.voltageText.GetValue()
        current = self.currentText.GetValue()
        try:
            current = float(current)
        except ValueError as e:
            dlg = wx.MessageDialog(None, str(e), "Invalid Current Value.", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        try:
            voltage = float(voltage)
        except ValueError as e:
            #dlg = wx.MessageDialog(None, str(e), "Invalid Voltage Value.", wx.OK | wx.ICON_ERROR)
            #dlg.ShowModal()
            #dlg.Destroy()
            voltage = current * 20
        self.ps.setCurrent(ChannelTypes.CH1, current)
        self.ps.setVoltage(ChannelTypes.CH1, voltage)
        self.ps.enable(ChannelTypes.CH1)


    def OnResetBtn(self, event):
        self.ps.disable(ChannelTypes.CH1)

    def OnUpdateCurrent(self, event):
        voltage = self.voltageText.GetValue()
        current = self.currentText.GetValue()
        try:
            voltage = float(voltage)
        except ValueError:
            voltage = 0
        try:
            current = float(current)
        except ValueError:
            current = 0

        if voltage <= 0:
            voltage = current * 20

    def OnCloseBtn(self, event):
        self.ps.disable(ChannelTypes.CH1)

        self.Destroy()

    def __init__(self, parent, ps):
        self.ps = ps
        self.parent = parent
        wx.Dialog.__init__(self, None, wx.ID_ANY, title='Power Supply Test Window')
        # And indicate we don't have a worker thread yet

        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
        titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        title = wx.StaticText(self.panel, wx.ID_ANY, 'My Title')

        setBtn = wx.Button(self.panel, wx.ID_ANY, 'Set')
        resetBtn = wx.Button(self.panel, wx.ID_ANY, 'Reset')
        closeBtn = wx.Button(self.panel, wx.ID_ANY, 'Close')

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        voltageSizer   = self.CreateVoltageSizer()
        currentSizer   = self.CreateCurrentSizer()
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer.Add(titleIco, 0, wx.ALL, 5)
        titleSizer.Add(title, 0, wx.ALL, 5)

        btnSizer.Add(setBtn, 0, wx.ALL, 5)
        btnSizer.Add(resetBtn, 0, wx.ALL, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL, 5)

        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(voltageSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(currentSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)


        self.Bind(wx.EVT_BUTTON, self.OnSetBtn, setBtn)
        self.Bind(wx.EVT_BUTTON, self.OnResetBtn, resetBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCloseBtn, closeBtn)
        #self.currentText.Bind(wx.EVT_KILL_FOCUS, self.OnUpdateCurrent)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)


# Run the program
if __name__ == '__main__':

    engine.echo = True
    app = wx.PySimpleApp()
    frame = FunctionGeneratorFrame(None).Show()
    app.MainLoop()