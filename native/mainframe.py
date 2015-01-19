# -*- coding: UTF-8 -*-

import wx
from listcontrol import MaterialList, PatchList, DCCoilList, ACCoilList, MainExpList

from matpropdialog import MaterialPropertyDialog
from inputframe import VNAInputFrame
from logframe import LoggingFrame
from core.listobject import *

from core.log import MainLogger
from searchdialog import SearchDialog
from statdialog import StatDialog

class MainExpTree(wx.TreeCtrl):
    ''' LazyTree is a simple "Lazy Evaluation" tree, that is, it only adds 
        items to the tree view when they are needed.'''

    def AppendObject(self, parent, name, data):
        item = self.AppendItem(parent, name)
        itemData = wx.TreeItemData(data)
        self.SetPyData(item, itemData)
        return item

    def __init__(self, *args, **kwargs):
        super(MainExpTree, self).__init__(*args, **kwargs)

        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpandItem)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.OnCollapseItem)
        self.__collapsing = True   
        self._generateTree()

    def _generateTree(self):
        self.root = self.AddRoot('root')
        self.SetItemHasChildren(self.root)   
        expSettings = self.AppendItem(self.root, 'Experiment Settings')
        self.AppendObject(expSettings, 'Patch Material', None)
        self.AppendObject(expSettings, 'Patch Spec', None)
        self.AppendObject(expSettings, 'DC Coil Spec', None)
        self.AppendObject(expSettings, 'AC Coil Spec', None)

        expData = self.AppendItem(self.root, 'VNA Experiment Data')
        viewAll = self.AppendObject(expData, 'View All', None)

        byPatch = self.AppendObject(expData, 'Filter by Patch', None)
        self.SetItemHasChildren(byPatch)

        byACCoil = self.AppendObject(expData, 'Filter by AC Coil', None)
        self.SetItemHasChildren(byACCoil)

        byDCCoil = self.AppendObject(expData, 'Filter by DC Coil', None)
        self.SetItemHasChildren(byDCCoil)

        byDCField = self.AppendObject(expData, 'Filter by DC Field', None)
        self.SetItemHasChildren(byDCField)

        bySourcePower = self.AppendObject(expData, 'Filter by Source Power', None)
        self.SetItemHasChildren(bySourcePower)

        self.AppendObject(expData, 'Search History', None)

        self.SelectItem(viewAll)

    def OnExpandItem(self, event):
        item = event.GetItem()
        data = self.GetPyData(item)
        if data is not None:
            pass

        # Add a random number of children and randomly decide which 
        # children have children of their own.
        pass

    def OnCollapseItem(self, event):
        '''
        # Be prepared, self.CollapseAndReset below may cause
        # another wx.EVT_TREE_ITEM_COLLAPSING event being triggered.
        if self.__collapsing:
            event.Veto()
        else:
            self.__collapsing = True
            item = event.GetItem()
            self.CollapseAndReset(item)
            self.SetItemHasChildren(item)
            self.__collapsing = False
        '''
        pass

class MainSplitter(wx.SplitterWindow):
    def __init__(self, *args, **kwargs):
        super(MainSplitter, self).__init__(*args, **kwargs) 
            
        self.InitUI()

    def InitUI(self):    
        self.treeMenuCtrl = MainExpTree(self, id = wx.ID_ANY, style=wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        self.treeMenuCtrl.SetMaxSize((100, -1))

        self.treeMenuCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)

        self.dataCtrl = MainExpList(self, id = wx.ID_ANY, style=wx.LC_REPORT)
        self.dataCtrl.SetEmptyListMsg("No Records Found")
        self.SplitVertically(self.treeMenuCtrl, self.dataCtrl)
        self.SetMinimumPaneSize(100)
        self.SetSashGravity(0.5)

        #self.treeMenuCtrl.SetDataList(self.dataCtrl)
        self.dataCtrl.setData()

    def OnNewItem(self, event):
        item = self.treeMenuCtrl.GetSelection()
        name = self.treeMenuCtrl.GetItemText(item)

        if name == 'Patch Material':
            dlg = MaterialPropertyDialog(None)
            dlg.ShowModal()
            dlg.Destroy()
        elif name =='View All':
            frame = VNAInputFrame(self.dataCtrl).Show()

    def OnSelChanged(self, event):
        item = event.GetItem()
        data = self.treeMenuCtrl.GetPyData(item)
        name = self.treeMenuCtrl.GetItemText(item)

        if name == 'Patch Material':
            oldCtrl = self.dataCtrl
            self.dataCtrl = MaterialList(self, id = wx.ID_ANY, style=wx.LC_REPORT)
            self.dataCtrl.setData()
            self.ReplaceWindow(oldCtrl, self.dataCtrl)
            oldCtrl.Destroy()

        elif name == 'View All':
            oldCtrl = self.dataCtrl
            self.dataCtrl = MainExpList(self, id = wx.ID_ANY, style=wx.LC_REPORT)
            self.dataCtrl.setData()
            self.ReplaceWindow(oldCtrl, self.dataCtrl)
            oldCtrl.Destroy()

        elif name == 'Patch Spec':
            oldCtrl = self.dataCtrl
            self.dataCtrl = PatchList(self, id = wx.ID_ANY, style=wx.LC_REPORT)
            self.dataCtrl.setData()
            self.ReplaceWindow(oldCtrl, self.dataCtrl)
            oldCtrl.Destroy()

        elif name == 'DC Coil Spec':
            oldCtrl = self.dataCtrl
            self.dataCtrl = DCCoilList(self, id = wx.ID_ANY, style=wx.LC_REPORT)
            self.dataCtrl.setData()
            self.ReplaceWindow(oldCtrl, self.dataCtrl)
            oldCtrl.Destroy()

        elif name == 'AC Coil Spec':
            oldCtrl = self.dataCtrl
            self.dataCtrl = ACCoilList(self, id = wx.ID_ANY, style=wx.LC_REPORT)
            self.dataCtrl.setData()
            self.ReplaceWindow(oldCtrl, self.dataCtrl)
            oldCtrl.Destroy()

class MainFrame(wx.Frame):    
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs) 
        self.logFrame = LoggingFrame(parent = wx.GetApp().TopWindow, logger = MainLogger)
            
        self.InitUI()
        
    def InitUI(self):    
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        self.splitter = MainSplitter(self, id = wx.ID_ANY) 
        self.splitter.SetMinimumPaneSize(100)

        toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        #view-refresh.png
        newItemTool = toolbar.AddSimpleTool(1, wx.Bitmap('resource/icon/actions/list-add.png'), 'New', '')
        toolbar.AddSimpleTool(2, wx.Bitmap('resource/icon/actions/list-remove.png'), 'Open', '')
        searchTool = toolbar.AddSimpleTool(3, wx.Bitmap('resource/icon/actions/system-search.png'), 'Search', '')
        refreshTool = toolbar.AddSimpleTool(4, wx.Bitmap('resource/icon/actions/view-refresh.png'), 'Refresh', '')
        statTool = toolbar.AddSimpleTool(5, wx.Bitmap('resource/icon/actions/document-save.png'), 'Set No Coil Data', '')
        toolbar.AddSeparator()
        viewLogTool = toolbar.AddSimpleTool(6, wx.Bitmap('resource/icon/mimetypes/text-x-generic.png'), 'View Log', '')
        toolbar.AddSeparator()
        quitTool = toolbar.AddSimpleTool(7, wx.Bitmap('resource/icon/actions/system-log-out.png'), 'Exit', '')
        toolbar.Realize()
        self.SetToolBar(toolbar)

        self.Bind(wx.EVT_TOOL, self.splitter.OnNewItem, newItemTool) 
        self.Bind(wx.EVT_TOOL, self.OnSearch, searchTool) 
        self.Bind(wx.EVT_TOOL, self.OnStat, statTool) 
        self.Bind(wx.EVT_TOOL, self.OnQuit, quitTool) 
        self.Bind(wx.EVT_TOOL, self.OnRefresh, refreshTool) 
        self.Bind(wx.EVT_TOOL, self.OnViewLog, viewLogTool) 
        #frame = VNAInputFrame().Show()

        self.statusbar = self.CreateStatusBar()    
        self.SetSize((1000, 600))
        self.SetTitle('Mageto - Magnetostrictive Data Analyzer')
        self.Centre()   
        self.Show(True)

    def OnStat(self, e):
        dlg = StatDialog(parent = wx.GetApp().TopWindow)
        if dlg.ShowModal() == wx.ID_OK:
            exp_id = dlg.woPatchChoice.GetClientData(dlg.woPatchChoice.GetSelection())
            exp_ids = []
            for exp in dlg.with_patch_exps:
                exp_ids.append(dlg.exp_list[exp])
            setWOPatch(exp_id, exp_ids)
            wx.MessageBox('Operation completed', 'Info', wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox('Operation Canceled', 'Info', wx.OK | wx.ICON_INFORMATION)

        dlg.Destroy()

    def OnSearch(self, e):   
        dlg = SearchDialog(parent = wx.GetApp().TopWindow)

        if dlg.ShowModal() == wx.ID_OK:
            src_power_vals = []
            ac_coil_vals = []
            dc_current_vals = []
            for src_power in dlg.src_powers:
                src_power_vals.append(dlg.src_power_list[src_power])
            for ac_coil in dlg.ac_coils:
                ac_coil_vals.append(dlg.ac_coil_list[ac_coil])
            for dc_current in dlg.dc_currents:
                dc_current_vals.append(dlg.dc_current_list[dc_current])
            self.splitter.dataCtrl.setData(ac_coils = ac_coil_vals, src_powers = src_power_vals, dc_currents = dc_current_vals)
        else:
            self.splitter.dataCtrl.setData()
        dlg.Destroy()

    def OnViewLog(self, e):   
        self.logFrame.Show(True)

    def OnRefresh(self, e):
        self.splitter.dataCtrl.setData()

    def OnQuit(self, e):
        self.Close()

class Magnificient(wx.App):
    def OnInit(self):
        self.InitUI()
        return True

    def InitUI(self):
        self.frame = MainFrame(None)
        self.frame.Show()
        #self.logFrame.Show(True)