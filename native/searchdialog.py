import wx
from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpPatchInfo, ExpMaterialProp, ExpVisProp
from db.schema import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core.listobject import *
import datetime
from sqlalchemy import func
from sqlalchemy.sql import label
from sqlalchemy import desc

class ListBoxItem():
    def __init__(self, idx, id, string):
        self.id = id
        self.string = string

    def __str__(self):
        return self.string

class SearchDialog(wx.Dialog):
    def CreateACCoilSizer(self):
        self.ac_coil_list = []
        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.acCoilLabel = wx.StaticText(self.panel, wx.ID_ANY, 'AC Coil Type', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.acCoilBox = wx.CheckListBox(self.panel, -1, (50, 50))

        session = scoped_session(sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=engine))

        rows = session.query(ExpACCoilProp).order_by(ExpACCoilProp.id).all()
        j = 0
        for row in rows:
            self.ac_coil_list.append(row.id)
            self.acCoilBox.Insert(item = ('#%d - %.2fx%.2fx%.2f (%s) (%dturn of %.2fmm wire)' % \
            (row.id, row.width, row.height, row.length, row.typeAsString, row.turn, row.wire_diameter)), 
            pos = j)
            j += 1

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.acCoilLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.acCoilBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        session.close()

        return sizer

    def CreateSourcePowerSizer(self):
        self.src_power_list = []
        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.sourcePowerLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Source Power', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.sourcePowerBox = wx.CheckListBox(self.panel, -1, (50, 50))

        j = 0
        for i in range(15,-16,-1):
            self.src_power_list.append(i)
            self.sourcePowerBox.Insert(item = ('%d dBm' % (i)), pos = j)
            j += 1

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.sourcePowerLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.sourcePowerBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateDCCurrentSizer(self):
        self.dc_current_list = []
        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.dcCurrentLabel = wx.StaticText(self.panel, wx.ID_ANY, 'DC Current', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.dcCurrentBox = wx.CheckListBox(self.panel, -1, (50, 50))

        session = scoped_session(sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=engine))

        rows = session.query(Exp.id, Exp.dc_current, label('count', func.count(Exp.dc_current))).group_by(Exp.dc_current).order_by(desc('count')).all()

        j = 0
        for row in rows:
            self.dc_current_list.append(row.dc_current)
            self.dcCurrentBox.Insert(item = ('%.2f A (%d results)' % (row.dc_current, row.count)), pos = j)
            j += 1

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.dcCurrentBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        session.close()

        return sizer

    def __init__(self, parent):
        #self.settings = TerminalSetup() #placeholder for the settings
        self.parent = parent
        wx.Dialog.__init__(self, None, wx.ID_ANY, title='Form')
        # And indicate we don't have a worker thread yet
        self.src_powers = []

        self.ac_coils = []

        self.dc_currents = []

        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        #bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
        #titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        #title = wx.StaticText(self.panel, wx.ID_ANY, 'My Title')

        okBtn = wx.Button(self.panel, wx.ID_OK, 'OK')
        cancelBtn = wx.Button(self.panel, wx.ID_CANCEL, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.OnStart, okBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        #titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        acCoilSizer   = self.CreateACCoilSizer()
        sourcePowerSizer   = self.CreateSourcePowerSizer()
        dcCurrentSizer = self.CreateDCCurrentSizer()
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

        #titleSizer.Add(titleIco, 0, wx.ALL, 5)
        #titleSizer.Add(title, 0, wx.ALL, 5)

        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        #topSizer.Add(titleSizer, 0, wx.CENTER)
        #topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(acCoilSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(sourcePowerSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(dcCurrentSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Bind(wx.EVT_CHECKLISTBOX, self.OnSourcePowerListBox, self.sourcePowerBox)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnACCoilBox, self.acCoilBox)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnDCCurrentBox, self.dcCurrentBox)
        #self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
        #if not self.worker.isAlive():
        #    self.Close()

    def OnDCCurrentBox(self, event):
        index = event.GetSelection()
        if self.dcCurrentBox.IsChecked(index):
            self.dc_currents.append(index)
        else:
            self.dc_currents.remove(index)
        self.dcCurrentBox.SetSelection(index)    # so that (un)checking also selects (moves the highlight)

    def OnSourcePowerListBox(self, event):
        index = event.GetSelection()
        if self.sourcePowerBox.IsChecked(index):
            self.src_powers.append(index)
        else:
            self.src_powers.remove(index)
        self.sourcePowerBox.SetSelection(index)    # so that (un)checking also selects (moves the highlight)
        
    def OnACCoilBox(self, event):
        index = event.GetSelection()
        if self.acCoilBox.IsChecked(index):
            self.ac_coils.append(index)
        else:
            self.ac_coils.remove(index)
        self.acCoilBox.SetSelection(index)    # so that (un)checking also selects (moves the highlight)
        
    def OnStart(self, event):
        """Start Computation."""
        '''
        if len(self.src_powers) == 0:            
            dlg = wx.MessageDialog(None, "Select one VNA Source Power at least", "Invalid Value.", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.ac_coils) == 0: 
            dlg = wx.MessageDialog(None, "Select AC Coil", "Invalid Value.", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        '''
        self.EndModal(wx.ID_OK)

    def onCancel(self, event):
        self.Destroy()


# Run the program
if __name__ == '__main__':

    engine.echo = True
    app = wx.PySimpleApp()
    frame = VNAInputFrame().Show()
    app.MainLoop()