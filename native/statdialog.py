import wx
from db.schema import Exp, ExpSmith, ExpVNA, ExpACCoilProp, ExpPatchInfo, ExpMaterialProp, ExpVisProp
from db.schema import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from core.listobject import *
import datetime
from sqlalchemy import func
from sqlalchemy.sql import label
from sqlalchemy import desc

class StatDialog(wx.Dialog):
    def CreateWOPatchExpSizer(self):

        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.woPatchLabel = wx.StaticText(self.panel, wx.ID_ANY, 'w/o Patch Exp', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.woPatchChoice = wx.Choice(self.panel, -1, (100, 50))
        
        result = getAllExps(patch_inclusion = PatchInclusion.WITHOUT_PATCH)

        for row in result:
            self.woPatchChoice.Append(('#%d - AC Coil #%d (%s)' % \
            (row.id, row.ac_coil_id, row.comment)), row.id)

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.woPatchLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.woPatchChoice, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def CreateWPatchExpSizer(self):
        self.exp_list = []
        sizer   = wx.BoxSizer(wx.HORIZONTAL)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        ico = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.wPatchLabel = wx.StaticText(self.panel, wx.ID_ANY, 'WithPatch', size = (90, -1), style=wx.ALIGN_RIGHT)  
        self.wPatchBox = wx.CheckListBox(self.panel, -1, (50, 50))

        result = getAllExps(patch_inclusion = PatchInclusion.WITH_PATCH, empty_only = True)

        j = 0
        for row in result:
            self.exp_list.append(row.id)
            self.wPatchBox.Insert(item = ('#%d - DC%d (%.2fA), AC#%d (%.2fdBm), Patch#(%d) - %s' % \
            (row.id, row.dc_coil_id, row.dc_current, row.ac_coil_id, row.source_power, row.patch_id, row.comment)), 
            pos = j)
            j += 1

        sizer.Add(ico, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.wPatchLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.wPatchBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)

        return sizer

    def __init__(self, parent):
        #self.settings = TerminalSetup() #placeholder for the settings
        self.parent = parent
        wx.Dialog.__init__(self, None, wx.ID_ANY, title='Stat Matching Dialog')
        # And indicate we don't have a worker thread yet

        self.with_patch_exps = []

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
        woPatchSizer   = self.CreateWOPatchExpSizer()
        wPatchSizer   = self.CreateWPatchExpSizer()
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

        #titleSizer.Add(titleIco, 0, wx.ALL, 5)
        #titleSizer.Add(title, 0, wx.ALL, 5)

        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        #topSizer.Add(titleSizer, 0, wx.CENTER)
        #topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(woPatchSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wPatchSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Bind(wx.EVT_CHECKLISTBOX, self.OnWPatchBox, self.wPatchBox)
        #self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
        #if not self.worker.isAlive():
        #    self.Close()
        
    def OnWPatchBox(self, event):
        index = event.GetSelection()
        if self.wPatchBox.IsChecked(index):
            self.with_patch_exps.append(index)
        else:
            self.with_patch_exps.remove(index)
        self.wPatchBox.SetSelection(index)    # so that (un)checking also selects (moves the highlight)
        
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

