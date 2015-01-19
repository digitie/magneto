# -*- coding: UTF-8 -*-

import wx
import os
from ObjectListView import ObjectListView
from core.listobject import *
from expgraphframe import ImpedanceGraphFrame, DCvsFreqGraphFrame, ACvsFreqGraphFrame, ARvsFreqGraphFrame, SmithchartGraphFrame, ReturnLossGraphFrame
from matpropdialog import MaterialPropertyDialog
from fileprocessor import FileProcessor
from events import *

wildcard = "Excel Workbook (*.xlsx)|*.xlsx|"     \
           "All files (*.*)|*.*"

class MainExpListPopup(wx.Menu):
    def __init__(self, parent, expIds = []):
        wx.Menu.__init__(self)

        self.expIds = expIds
        self.parent = parent
        #self.viewMenu = MainExpViewPopup(parent, expIds)
        #exportMenu = MainExpExportPopup(None, expIds)

        if len(self.expIds) == 1:
            #self.AppendMenu(wx.NewId(), "View", self.viewMenu)

            item = wx.MenuItem(self, wx.NewId(), "View &SmithChart")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewSmithChart(event), item)
            item = wx.MenuItem(self, wx.NewId(), "View R&eturn Loss")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnReturnLossGraph(event), item)
            item = wx.MenuItem(self, wx.NewId(), "View &Re(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 're'), item)
            item = wx.MenuItem(self, wx.NewId(), "View &Im(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'im'), item)
            item = wx.MenuItem(self, wx.NewId(), "View &Mag(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'mag'), item)

            self.AppendSeparator()

            item = wx.MenuItem(self, wx.NewId(), "Export Data")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnExport(event), item)

            item = wx.MenuItem(self, wx.NewId(), "Calculate Stats")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnCalculate(event), item)

            item = wx.MenuItem(self, wx.NewId(), "Filter")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnFilter(event), item)
            item = wx.MenuItem(self, wx.NewId(), "Delete")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnDelete(event), item)
        else:
            item = wx.MenuItem(self, wx.NewId(), "Compare &SmithChart")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewSmithChart(event), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare R&eturn Loss")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnReturnLossGraph(event), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &Re(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 're'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &Im(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'im'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &Mag(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'mag'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &DC vs F Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewDCvsFreqGraph(event, 'dc'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &A/R vs F Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewARvsFreqGraph(event, 'ar'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &AC vs F Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewACvsFreqGraph(event, 'ac'), item)

            self.AppendSeparator()

            item = wx.MenuItem(self, wx.NewId(), "Export Data")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnExport(event), item)

            item = wx.MenuItem(self, wx.NewId(), "Calculate Stats")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnCalculate(event), item)

            item = wx.MenuItem(self, wx.NewId(), "Delete")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnDelete(event), item)

    def OnExport(self, event):
        calculateStatByExpIds(exp_ids = self.expIds)
        path = None 
        dlg = wx.FileDialog(
            wx.GetApp().TopWindow, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=wildcard, style=wx.SAVE
            )

        dlg.SetFilterIndex(0)


        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

        dlg.Destroy()

        if os.path.exists(path):
            dial = wx.MessageDialog(None, 'Invalid file name', 'Warning', 
                wx.NO_DEFAULT | wx.ICON_STOP)
            dial.ShowModal()
            return

        self.parent.ExportToExcel(path, self.expIds)

    def OnCalculate(self, event):
        calculateStatByExpIds(exp_ids = self.expIds)

    def OnViewSmithChart(self, event):
        frame = SmithchartGraphFrame(wx.GetApp().TopWindow, -1, 'Smith Chart Graph', exp_ids = self.expIds)
        frame.Show()

    def OnReturnLossGraph(self, event):
        frame = ReturnLossGraphFrame(wx.GetApp().TopWindow, -1, 'Return Loss Graph', exp_ids = self.expIds)
        frame.Show()

    def OnViewImpedanceGraph(self, event, type):
        frame = ImpedanceGraphFrame(wx.GetApp().TopWindow, -1, 'Impedance Graph', exp_ids = self.expIds, type = type)
        frame.Show()

    def OnViewDCvsFreqGraph(self, event, type):
        frame = DCvsFreqGraphFrame(wx.GetApp().TopWindow, -1, 'DC Excitation Power vs Frequency Graph', exp_ids = self.expIds)
        frame.Show()

    def OnViewARvsFreqGraph(self, event, type):
        frame = ARvsFreqGraphFrame(wx.GetApp().TopWindow, -1, 'A/R vs Frequency Graph', exp_ids = self.expIds)
        frame.Show()

    def OnViewACvsFreqGraph(self, event, type):
        frame = ACvsFreqGraphFrame(wx.GetApp().TopWindow, -1, 'AC Excitation Power vs Frequency Graph', exp_ids = self.expIds)
        frame.Show()

    def OnFilter(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to Filter?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            if len(self.expIds) != 1:
                dial = wx.MessageDialog(None, 'Filtering multiple exps not supported', 'Error', 
                    wx.NO_DEFAULT | wx.ICON_QUESTION)
                dial.ShowModal()
                return

            if isFiltered(self.expIds[0]):
                dial = wx.MessageDialog(None, 'Filtering multiple exps not supported', 'Warning', 
                    wx.NO_DEFAULT | wx.ICON_STOP)
                dial.ShowModal()

            self.parent.setData()

    def OnDelete(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to Delete?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            deleteExps(self.expIds)
            self.parent.setData()

class MagMainListCtrl(ObjectListView):
    def __init__(self, *args, **kwargs):        
        ObjectListView.__init__(self, *args, **kwargs)

    def GetSelectedObjects( self, state =  wx.LIST_STATE_SELECTED):
            objects = []
            lastFound = -1
            while True:
                    index = self.GetNextItem(
                            lastFound,
                            wx.LIST_NEXT_ALL,
                            state,
                    )
                    if index == -1:
                            break
                    else:
                            lastFound = index
                            objects.append( self.GetObjectAt(index) )
            return objects

    def GetSelectedIndices(self, state =  wx.LIST_STATE_SELECTED):
            indices = []
            lastFound = -1
            while True:
                    index = self.GetNextItem(
                            lastFound,
                            wx.LIST_NEXT_ALL,
                            state,
                    )
                    if index == -1:
                            break
                    else:
                            lastFound = index
                            indices.append( index )
            return indices

class MainExpList(MagMainListCtrl):
    def __init__(self, *args, **kwargs):        
        ObjectListView.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)

        self.Bind(EVT_XLS_WRITE_COMPLETED, self.OnComplete)
        self.Bind(EVT_XLS_WRITE_PROGRESS, self.OnProgress)
        self.Bind(EVT_XLS_WRITE_CANCELED, self.OnCanceled)

        self.SetColumns(ExpListColumnDefn)
        self.worker = None

    def ExportToExcel(self, path, expIds):
        # Trigger the worker thread unless it's already busy
        if not self.worker:
            #self.status.SetLabel('Starting computation')
            self.worker = FileProcessor(self, path, expIds)
            max = 100

            self.progress = wx.ProgressDialog("Export in Progress",
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

    def GetExpSelectedExpIds(self, state =  wx.LIST_STATE_SELECTED):        
        exp_ids = []
        objs = self.GetSelectedObjects(state)
        for o in objs:
            exp_ids.append(o.id)
        return exp_ids

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
        
    def OnProgress(self, event):
        self.progress.Update(event.step, event.message)

    def OnStop(self, event):
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            self.progress.Destroy()
            self.worker.abort()
        wx.MessageDialog(None, 'Operation Stopped', 'Error', 
            wx.NO_DEFAULT | wx.ICON_STOP)

    def OnComplete(self, event):
        """Show Result status."""
        # Process results here
        #self.status.SetLabel('Computation Result: %s' % event.data)
        # In either event, the worker is done
        self.progress.Destroy()
        self.worker = None
        wx.MessageBox('Operation completed', 'Info', wx.OK | wx.ICON_INFORMATION)

    def OnActivated(self, event):        
        #frame = GraphFrame()
        #frame.Show()
        #frame = ExpACCoilPropertyDialog(self)
        #frame.ShowModal()
        frame = ImpedanceGraphFrame(wx.GetApp().TopWindow, -1, 'Impedance Graph', exp_ids = self.GetExpSelectedExpIds())
        frame.Show()

    def OnRightClick(self, event):
        ### 2. Launcher creates wxMenu. ###
        menu = MainExpListPopup(self, expIds = self.GetExpSelectedExpIds())
        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def setData(self, ac_coils = [], src_powers = [], dc_currents = []):
        self.SetObjects(getAllExpsByFilter(ac_coils, src_powers, dc_currents))

class MaterialList(MagMainListCtrl):
    def __init__(self, *args, **kwargs):        
        ObjectListView.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.SetColumns(ExpMaterialListColumnDefn)

    def OnActivated(self, event):        
        index = event.GetIndex()
        o = self.GetObjectAt(index)
        #frame = GraphFrame()
        #frame.Show()
        frame = MaterialPropertyDialog(self, wx.GetApp().TopWindow, materialId = o.id)
        frame.ShowModal()
        frame.Destroy()

    def setData(self):
        self.SetObjects(getAllMaterials())


class PatchListPopup(wx.Menu):
    def __init__(self, expIds = []):
        wx.Menu.__init__(self)

        self.expIds = expIds

        if len(self.expIds) == 1:
            item = wx.MenuItem(self, wx.NewId(), "View &Re(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 're'), item)
            item = wx.MenuItem(self, wx.NewId(), "View &Im(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'im'), item)
            item = wx.MenuItem(self, wx.NewId(), "View &Mag(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'mag'), item)
        else:
            item = wx.MenuItem(self, wx.NewId(), "Compare &Re(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 're'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &Im(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'im'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &Mag(z) Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewImpedanceGraph(event, 'mag'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &DC vs F Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewDCvsFreqGraph(event, 'dc'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &A/R vs F Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewARvsFreqGraph(event, 'ar'), item)
            item = wx.MenuItem(self, wx.NewId(), "Compare &AC vs F Graph")
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, lambda event: self.OnViewACvsFreqGraph(event, 'ac'), item)

    def OnViewImpedanceGraph(self, event, type):
        frame = ImpedanceGraphFrame(wx.GetApp().TopWindow, exp_ids = self.expIds, type = type)
        frame.Show()

    def OnViewDCvsFreqGraph(self, event, type):
        frame = DCvsFreqGraphFrame(wx.GetApp().TopWindow, exp_ids = self.expIds)
        frame.Show()

    def OnViewARvsFreqGraph(self, event, type):
        frame = ARvsFreqGraphFrame(wx.GetApp().TopWindow, exp_ids = self.expIds)
        frame.Show()

    def OnViewACvsFreqGraph(self, event, type):
        frame = ACvsFreqGraphFrame(wx.GetApp().TopWindow, exp_ids = self.expIds)
        frame.Show()

class PatchList(MagMainListCtrl):
    def __init__(self, *args, **kwargs):        
        ObjectListView.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick)
        self.SetColumns(ExpPatchColumnDefn)

    def GetExpSelectedPatchIds(self, state =  wx.LIST_STATE_SELECTED):        
        patch_ids = []
        objs = self.GetSelectedObjects(state)
        for o in objs:
            patch_ids.append(o.patch_id)
        return patch_ids

    def OnRightClick(self, event):
        ### 2. Launcher creates wxMenu. ###
        menu = PatchListPopup(expIds = self.GetExpSelectedPatchIds())
        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def setData(self):
        self.SetObjects(getAllPatches())

class DCCoilList(ObjectListView):
    def __init__(self, *args, **kwargs):        
        ObjectListView.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.SetColumns(ExpDCCoilListColumnDefn)

    def GetSelectedIndices( self, state =  wx.LIST_STATE_SELECTED):
            indices = []
            lastFound = -1
            while True:
                    index = self.GetNextItem(
                            lastFound,
                            wx.LIST_NEXT_ALL,
                            state,
                    )
                    if index == -1:
                            break
                    else:
                            lastFound = index
                            indices.append( index )
            return indices
    def OnActivated(self, event):        
        #frame = GraphFrame()
        #frame.Show()
        frame = ExpACCoilPropertyDialog(self)
        frame.ShowModal()

    def OnRightClick(self, event):
        ### 2. Launcher creates wxMenu. ###
        menu = wx.Menu()
        for (id,title) in menu_title_by_id.items():
            ### 3. Launcher packs menu with Append. ###
            menu.Append( id, title )
            ### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
            menu.Bind(wx.EVT_MENU, self.OnPopupMenuSelected )

        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def OnPopupMenuSelected( self, event ):
        # do something
        operation = menu_title_by_id[ event.GetId() ]
        target    = self.list_item_clicked
        print 'Perform "%(operation)s" on "%(target)s."' % vars()

    def setData(self):
        self.SetObjects(getAllDCCoils())


class ACCoilList(ObjectListView):
    def __init__(self, *args, **kwargs):        
        ObjectListView.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.SetColumns(ExpACCoilListColumnDefn)

    def GetSelectedIndices( self, state =  wx.LIST_STATE_SELECTED):
            indices = []
            lastFound = -1
            while True:
                    index = self.GetNextItem(
                            lastFound,
                            wx.LIST_NEXT_ALL,
                            state,
                    )
                    if index == -1:
                            break
                    else:
                            lastFound = index
                            indices.append( index )
            return indices
    def OnActivated(self, event):        
        #frame = GraphFrame()
        #frame.Show()
        frame = ExpACCoilPropertyDialog(self)
        frame.ShowModal()

    def OnRightClick(self, event):
        ### 2. Launcher creates wxMenu. ###
        menu = wx.Menu()
        for (id,title) in menu_title_by_id.items():
            ### 3. Launcher packs menu with Append. ###
            menu.Append( id, title )
            ### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
            menu.Bind(wx.EVT_MENU, self.OnPopupMenuSelected )

        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def OnPopupMenuSelected( self, event ):
        # do something
        operation = menu_title_by_id[ event.GetId() ]
        target    = self.list_item_clicked
        print 'Perform "%(operation)s" on "%(target)s."' % vars()

    def setData(self):
        self.SetObjects(getAllACCoils())